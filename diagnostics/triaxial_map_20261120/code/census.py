"""census.py -- stationary-point census for one triaxial shape L = diag(1, s, s t).
Non-interval floating point.  DIAGNOSTIC_ONLY / NOT_EVIDENCE.
Implements PLAN.md, Run A items 1-6."""
import numpy as np
from scipy.optimize import brentq, root
import triax

EYE = np.eye(3)
HIDX = {(0, 0): 4, (1, 1): 5, (2, 2): 6, (0, 1): 7, (1, 0): 7, (0, 2): 8, (2, 0): 8, (1, 2): 9, (2, 1): 9}


def nq(l):
    a = max(l)/min(l)
    for lim, n in ((2, 96), (3.5, 128), (6, 192), (12, 256), (20, 384), (32.001, 512)):
        if a <= lim:
            return (n, n)
    return (768, 768)


def hsub(o, dims):
    m = len(dims)
    H = np.empty(o.shape[:-1] + (m, m))
    for a, i in enumerate(dims):
        for b, j in enumerate(dims):
            H[..., a, b] = o[..., HIDX[(i, j)]]
    return H


def index_of(eigs, tol=1e-7):
    return int(np.sum(eigs < -tol)), int(np.sum(np.abs(eigs) <= tol))


def newton2(l, n, q0, dims):
    """two-stage Newton: converge at reduced nodes, de-duplicate, polish at full nodes (algo 2)."""
    ns = (max(96, n[0]//2),)*2
    if ns[0] >= n[0]:
        return newton(l, n, q0, dims)
    P = newton(l, ns, q0, dims, gtol=1e-8)
    uniq = []
    for p in P:
        if not any(np.linalg.norm(p - u) < 1e-4 for u in uniq):
            uniq.append(p)
    if not uniq:
        return np.zeros((0, 3))
    return newton(l, n, np.array(uniq), dims)


def newton(l, n, q0, dims, maxit=40, gtol=1e-11):
    """batched Newton in the coordinates `dims` (others frozen). Returns converged points."""
    dims = list(dims)
    q = np.array(q0, float)
    alive = np.ones(len(q), bool); conv = np.zeros(len(q), bool)
    for _ in range(maxit):
        idx = np.where(alive)[0]
        if len(idx) == 0:
            break
        o = triax.ev(l, q[idx], n)
        g = o[:, [1 + i for i in dims]]
        H = hsub(o, dims)
        gn = np.linalg.norm(g, axis=1)
        done = gn < gtol
        conv[idx[done]] = True; alive[idx[done]] = False
        idx = idx[~done]; g = g[~done]; H = H[~done]
        if len(idx) == 0:
            break
        det = np.linalg.det(H)
        bad = np.abs(det) < 1e-14
        alive[idx[bad]] = False
        idx = idx[~bad]; g = g[~bad]; H = H[~bad]
        if len(idx) == 0:
            break
        d = -np.linalg.solve(H, g[..., None])[..., 0]
        dn = np.linalg.norm(d, axis=1)
        d *= np.minimum(1.0, 0.25/np.maximum(dn, 1e-300))[:, None]
        step = np.zeros((len(idx), 3)); step[:, dims] = d
        qn = q[idx] + step
        rn = np.linalg.norm(qn, axis=1); r0 = np.linalg.norm(q[idx], axis=1)
        out = rn >= 1.0
        if out.any():
            # fraction-to-boundary: land at distance 0.5*(1-r0) from the sphere
            for m in np.where(out)[0]:
                tgt = 1.0 - 0.5*(1.0 - r0[m])
                lo, hi = 0.0, 1.0
                for _b in range(40):
                    mid = 0.5*(lo + hi)
                    if np.linalg.norm(q[idx[m]] + mid*step[m]) < tgt:
                        lo = mid
                    else:
                        hi = mid
                qn[m] = q[idx[m]] + lo*step[m]
            dead = out & (1.0 - r0 < 1e-9)
            alive[idx[dead]] = False
        q[idx] = qn
    return q[conv]


def dedupe(P, tol=1e-6):
    out = []
    for p in P:
        p = np.abs(p)
        if not any(np.linalg.norm(p - o) < tol for o in out):
            out.append(p)
    return out


def classify(p, tol=1e-7):
    z = [i for i in range(3) if abs(p[i]) < tol]
    if len(z) == 3:
        return "center"
    if len(z) == 2:
        return "axis%d" % (1 + [i for i in range(3) if i not in z][0])
    if len(z) == 1:
        ij = [i for i in range(3) if i not in z]
        return "plane%d%d" % (ij[0] + 1, ij[1] + 1)
    return "general"


def census(s, t, n=None, verbose=False):
    l = np.array([1.0, s, s*t])
    n = n or nq(l)
    edge_s = (s == 1.0); edge_t = (t == 1.0)
    res = dict(s=s, t=t, n=n[0], edge=("sphere" if edge_s and edge_t else "prolate" if edge_s else "oblate" if edge_t else ""))
    ev1 = lambda q: triax.ev(l, np.asarray(q, float), n)
    nseed = (max(96, n[0]//2),)*2
    evs = lambda q: triax.ev(l, np.asarray(q, float), nseed)
    res["algo"] = 2
    # 1. centre
    oc = ev1([0, 0, 0])
    h = oc[4:7]
    res["h"] = h.tolist(); res["E0"] = float(oc[0])
    pts = []   # interior stationary points other than the centre

    def record(p, kind=None):
        o = ev1(p)
        eig = np.linalg.eigvalsh(triax.hess_matrix(o))
        ind, nul = index_of(eig)
        pts.append(dict(kind=kind or classify(p), q=[float(x) for x in p], E=float(o[0]),
                        gradnorm=float(np.linalg.norm(o[1:4])), eig=eig.tolist(),
                        hdiag=o[4:7].tolist(), index=ind, nullity=nul))

    # 2. axes
    r = np.sin(np.pi*np.arange(65)/128.0); r[64] = 1.0
    Q = np.concatenate([r[:, None]*EYE[i] for i in range(3)])
    oa = ev1(Q).reshape(3, 65, 10)
    res["pole_trace"] = [float(oa[i, 64, 1 + i]) for i in range(3)]
    axis_roots = [[], [], []]
    for i in range(3):
        g = oa[i, :, 1 + i]
        f = lambda rr, i=i: float(ev1(rr*EYE[i])[1 + i])
        br = []
        if h[i]*g[1] < 0:
            ga = f(1e-4)
            if ga*g[1] < 0:
                br.append((1e-4, r[1]))
        for j in range(1, 64):
            if g[j] == 0.0:
                br.append((r[j] - 1e-9, r[j] + 1e-9))
            elif g[j]*g[j + 1] < 0:
                br.append((r[j], r[j + 1]))
        for a, b in br:
            rr = brentq(f, a, b, xtol=1e-13, rtol=1e-14)
            if rr < 1.0 - 1e-10:
                axis_roots[i].append(rr)
                record(rr*EYE[i], "axis%d" % (i + 1))
    res["axis_roots"] = axis_roots
    res["axis_profile_min_abs"] = [float(np.min(np.abs(oa[i, 1:, 1 + i]))) for i in range(3)]
    # 3. coordinate planes
    found = []
    rp = np.sin(np.pi*np.arange(1, 20)/40.0)
    ps = (np.arange(9) + 0.5)*(np.pi/2)/9
    for (i, j) in ((0, 1), (0, 2), (1, 2)):
        if (edge_s and (i, j) == (0, 1)) or (edge_t and (i, j) == (1, 2)):
            continue
        R, PS = np.meshgrid(rp, ps, indexing="ij")
        Q = (R*np.cos(PS))[..., None]*EYE[i] + (R*np.sin(PS))[..., None]*EYE[j]
        Q = Q.reshape(-1, 3)
        o = evs(Q)
        g = o[:, [1 + i, 1 + j]]; H = hsub(o, (i, j))
        ok = np.abs(np.linalg.det(H)) > 1e-12
        d = np.full_like(g, 1e9)
        d[ok] = -np.linalg.solve(H[ok], g[ok][..., None])[..., 0]
        seeds = Q[np.linalg.norm(d, axis=1) < 0.35]
        res.setdefault("n_seeds_plane", []).append(int(len(seeds)))
        if len(seeds):
            found += list(newton2(l, n, seeds, (i, j)))
    # 4. general position
    if not (edge_s or edge_t):
        rg = np.sin(np.pi*np.arange(1, 13)/26.0)
        an = (np.arange(7) + 0.5)*(np.pi/2)/7
        R, TH, PH = np.meshgrid(rg, an, an, indexing="ij")
        Q = np.stack([R*np.sin(TH)*np.cos(PH), R*np.sin(TH)*np.sin(PH), R*np.cos(TH)], -1).reshape(-1, 3)
        o = evs(Q)
        g = o[:, 1:4]; H = hsub(o, (0, 1, 2))
        ok = np.abs(np.linalg.det(H)) > 1e-12
        d = np.full_like(g, 1e9)
        d[ok] = -np.linalg.solve(H[ok], g[ok][..., None])[..., 0]
        seeds = Q[np.linalg.norm(d, axis=1) < 0.35]
        res["n_seeds_general"] = int(len(seeds))
        if len(seeds):
            found += list(newton2(l, n, seeds, (0, 1, 2)))
    for p in dedupe(found):
        kind = classify(p)
        if kind == "center" or kind.startswith("axis"):
            # axis points come from the axis scan; note any that the scan missed
            if kind.startswith("axis"):
                i = int(kind[-1]) - 1
                if not any(abs(p[i] - rr) < 1e-5 for rr in axis_roots[i]):
                    res.setdefault("axis_missed_by_scan", []).append([float(x) for x in p])
                    axis_roots[i].append(float(p[i])); record(p, kind)
            continue
        if np.linalg.norm(p) >= 1 - 1e-9:
            continue
        record(p, kind)
    res["points"] = pts
    # 5. boundary: critical points of E|S^2 and the normal component N = grad E . q
    bpts = []
    hfd = 1e-3

    def tang(p, tvec):
        return float(ev1(p)[1:4] @ tvec)

    polesH = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            if j == i:
                continue
            p = np.cos(hfd)*EYE[i] + np.sin(hfd)*EYE[j]
            tv = -np.sin(hfd)*EYE[i] + np.cos(hfd)*EYE[j]
            polesH[i, j] = tang(p, tv)/hfd
        e2 = np.array([polesH[i, j] for j in range(3) if j != i])
        ind, nul = index_of(e2, 1e-6)
        bpts.append(dict(kind="pole%d" % (i + 1), q=EYE[i].tolist(), N=res["pole_trace"][i],
                         teig=e2.tolist(), tindex=ind, tnull=nul))
    psi = np.linspace(0, np.pi/2, 33)
    for (i, j) in ((0, 1), (0, 2), (1, 2)):
        if (edge_s and (i, j) == (0, 1)) or (edge_t and (i, j) == (1, 2)):
            continue
        k = 3 - i - j
        P = np.cos(psi)[:, None]*EYE[i] + np.sin(psi)[:, None]*EYE[j]
        TV = -np.sin(psi)[:, None]*EYE[i] + np.cos(psi)[:, None]*EYE[j]
        o = ev1(P)
        T = np.einsum("ab,ab->a", o[:, 1:4], TV)
        fT = lambda x: tang(np.cos(x)*EYE[i] + np.sin(x)*EYE[j], -np.sin(x)*EYE[i] + np.cos(x)*EYE[j])
        br = []
        if polesH[i, j]*T[1] < 0:
            br.append((hfd, psi[1]))
        for m in range(1, 31):
            if T[m]*T[m + 1] < 0:
                br.append((psi[m], psi[m + 1]))
        # near the other end: tangent derivative at e_j towards e_i has sign -polesH[j,i] in psi
        if -polesH[j, i]*T[31] > 0:
            # T(psi) near pi/2 behaves like -polesH[j,i]*(pi/2-psi)*(-1) ... check sign by direct evaluation
            pass
        Tend = fT(np.pi/2 - hfd)
        if Tend*T[31] < 0:
            br.append((psi[31], np.pi/2 - hfd))
        for a, b in br:
            if fT(a)*fT(b) >= 0:
                continue
            x = brentq(fT, a, b, xtol=1e-12)
            p = np.cos(x)*EYE[i] + np.sin(x)*EYE[j]
            ob = ev1(p)
            N = float(ob[1:4] @ p)
            d_arc = (fT(x + 1e-4) - fT(x - 1e-4))/2e-4
            pk = p + 1e-4*EYE[k]; pk /= np.linalg.norm(pk)
            d_nor = float(ev1(pk)[1:4] @ EYE[k])/1e-4
            e2 = np.array([d_arc, d_nor]); ind, nul = index_of(e2, 1e-5)
            bpts.append(dict(kind="arc%d%d" % (i + 1, j + 1), q=p.tolist(), psi=float(x), N=N,
                             teig=e2.tolist(), tindex=ind, tnull=nul))
    if not (edge_s or edge_t):
        an = (np.arange(13) + 0.5)*(np.pi/2)/13

        def tg(x):
            th, ph = x
            p = np.array([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)])
            eth = np.array([np.cos(th)*np.cos(ph), np.cos(th)*np.sin(ph), -np.sin(th)])
            eph = np.array([-np.sin(ph), np.cos(ph), 0.0])
            g = ev1(p)[1:4]
            return np.array([g @ eth, g @ eph])
        TH, PH = np.meshgrid(an, an, indexing="ij")
        P = np.stack([np.sin(TH)*np.cos(PH), np.sin(TH)*np.sin(PH), np.cos(TH)], -1)
        ETH = np.stack([np.cos(TH)*np.cos(PH), np.cos(TH)*np.sin(PH), -np.sin(TH)], -1)
        EPH = np.stack([-np.sin(PH), np.cos(PH), 0*PH], -1)
        g = ev1(P)[..., 1:4]
        G1 = np.einsum("abc,abc->ab", g, ETH); G2 = np.einsum("abc,abc->ab", g, EPH)
        cand = []
        for a in range(12):
            for b in range(12):
                c1 = G1[a:a + 2, b:b + 2]; c2 = G2[a:a + 2, b:b + 2]
                if c1.min() < 0 < c1.max() and c2.min() < 0 < c2.max():
                    cand.append((0.5*(an[a] + an[a + 1]), 0.5*(an[b] + an[b + 1])))
        res["n_seeds_boundary_octant"] = len(cand)
        sols = []
        for x0 in cand:
            sol = root(tg, x0, method="hybr", tol=1e-13)
            x = sol.x
            if sol.success and 1e-5 < x[0] < np.pi/2 - 1e-5 and 1e-5 < x[1] < np.pi/2 - 1e-5 \
                    and np.linalg.norm(tg(x)) < 1e-9 and not any(np.linalg.norm(x - y) < 1e-6 for y in sols):
                sols.append(x)
        for x in sols:
            th, ph = x
            p = np.array([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)])
            N = float(ev1(p)[1:4] @ p)
            hh = 1e-4
            Jm = np.column_stack([(tg(x + hh*np.eye(2)[m]) - tg(x - hh*np.eye(2)[m]))/(2*hh) for m in range(2)])
            Jm[:, 1] /= np.sin(th)          # metric: d/dphi -> (1/sin th) d/dphi
            Hs = 0.5*(Jm + Jm.T)
            e2 = np.linalg.eigvalsh(Hs); ind, nul = index_of(e2, 1e-5)
            bpts.append(dict(kind="octant", q=p.tolist(), N=N, teig=e2.tolist(), tindex=ind, tnull=nul))
    res["boundary"] = bpts
    # 6. Morse boundary index formula
    cind, cnul = index_of(h)
    tot = (-1)**cind
    mult = {"axis": 2, "plane": 4, "general": 8, "pole": 2, "arc": 4, "octant": 8}
    degenerate = cnul > 0
    for p in pts:
        kind = p["kind"]
        if res["edge"]:
            # rotational symmetry: only points on the symmetry axis are isolated; circles have chi = 0
            sym_axis = "axis3" if edge_s else "axis1"
            if res["edge"] == "sphere" or kind != sym_axis:
                continue
            m = 2
        else:
            m = mult["axis" if kind.startswith("axis") else "plane" if kind.startswith("plane") else "general"]
        tot += m*(-1)**p["index"]; degenerate |= p["nullity"] > 0
    for b in bpts:
        kind = b["kind"]
        if res["edge"]:
            sym_pole = "pole3" if edge_s else "pole1"
            if res["edge"] == "sphere" or kind != sym_pole:
                continue
            m = 2
        else:
            m = mult["pole" if kind.startswith("pole") else "arc" if kind.startswith("arc") else "octant"]
        degenerate |= b["tnull"] > 0
        if b["N"] < 0:
            tot += m*(-1)**b["tindex"]
    if res["edge"] == "sphere":
        tot = 1
    res["morse_sum"] = int(tot); res["degenerate_flag"] = bool(degenerate)
    res["center_index"] = cind
    return res


if __name__ == "__main__":
    import sys, json, time
    t0 = time.time()
    r = census(float(sys.argv[1]), float(sys.argv[2]))
    print(json.dumps(r, indent=1)); print("time", time.time() - t0, file=sys.stderr)
