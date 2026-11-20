"""analyze.py -- tables and figures from the run outputs.  DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import json, os, sys, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

OUT = sys.argv[1] if len(sys.argv) > 1 else "../out"
FIG = sys.argv[2] if len(sys.argv) > 2 else "../fig"
for f in ("/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf", "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"):
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name()
        break
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e4e3df", "grid.linewidth": 0.6, "axes.edgecolor": "#8a8984",
                     "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "text.color": "#0b0b0b", "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
                     "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.unicode_minus": False})
C_NONE, C_E1, C_E2, C_BOTH = "#c9c8c2", "#2a78d6", "#eb6834", "#1baf7a"
INK = "#0b0b0b"

rows = [json.loads(l) for l in open(os.path.join(OUT, "runA_census.jsonl"))]
rows.sort(key=lambda r: (r["i"], r["j"]))
B = json.load(open(os.path.join(OUT, "runB_curves.json")))
md = []
S = {}

# ---------------------------------------------------------------- Run A summary
err = [r for r in rows if "error" in r]
ok = [r for r in rows if "error" not in r]
inner = [r for r in ok if not r["edge"]]
S["n_shapes"] = len(rows); S["n_errors"] = len(err); S["n_interior_shapes"] = len(inner)
kinds = collections.Counter()
cls = collections.Counter()
offaxis = []; multi = []; idx1 = collections.Counter(); idx2 = collections.Counter(); idx3 = collections.Counter()
incons = []; morse_bad = []; degen = []; missed = []
for r in ok:
    na = [len(a) for a in r["axis_roots"]]
    for p in r["points"]:
        kinds[p["kind"]] += 1
        if p["kind"] == "axis1": idx1[p["index"]] += 1
        if p["kind"] == "axis2": idx2[p["index"]] += 1
        if p["kind"] == "axis3": idx3[p["index"]] += 1
    off = [p for p in r["points"] if not p["kind"].startswith("axis")]
    if off: offaxis.append((r["s"], r["t"], [(p["kind"], p["q"]) for p in off]))
    if max(na) > 1: multi.append((r["s"], r["t"], na))
    # internal consistency: a root on axis i exists iff h_i and the pole trace have opposite signs
    for i in range(3):
        expect = 1 if r["h"][i]*r["pole_trace"][i] < 0 else 0
        if na[i] != expect: incons.append((r["s"], r["t"], i + 1, na[i], r["h"][i], r["pole_trace"][i]))
    if r["morse_sum"] != 1: morse_bad.append((r["s"], r["t"], r["morse_sum"], r["degenerate_flag"]))
    if r["degenerate_flag"]: degen.append((r["s"], r["t"]))
    if r.get("axis_missed_by_scan"): missed.append((r["s"], r["t"]))
    if not r["edge"]:
        cls[(r["center_index"], na[0], na[1], na[2])] += 1
S.update(point_kinds=dict(kinds), index_axis1=dict(idx1), index_axis2=dict(idx2), index_axis3=dict(idx3),
         n_offaxis_shapes=len(offaxis), offaxis=offaxis[:20], n_multi_root=len(multi), multi=multi[:20],
         n_inconsistent=len(incons), inconsistent=incons[:20], n_morse_not_1=len(morse_bad), morse_not_1=morse_bad[:40],
         n_degenerate_flag=len(degen), n_axis_missed_by_scan=len(missed),
         classes={"center_index=%d, pairs(e1,e2,e3)=(%d,%d,%d)" % k: v for k, v in sorted(cls.items())})
# strict order of centre eigenvalues, sign of h3 and pole3
S["min_h3"] = min(r["h"][2] for r in ok); S["min_pole3"] = min(r["pole_trace"][2] for r in ok)
S["min_h2_minus_h1_interior"] = min(r["h"][1] - r["h"][0] for r in inner)
S["min_h3_minus_h2_interior"] = min(r["h"][2] - r["h"][1] for r in inner)
# transverse Hessian at axis points (interior shapes)
t1 = [p["hdiag"] for r in inner for p in r["points"] if p["kind"] == "axis1"]
t2 = [p["hdiag"] for r in inner for p in r["points"] if p["kind"] == "axis2"]
if t1:
    t1 = np.array(t1); S["axis1_points"] = dict(n=len(t1), E11_max=float(t1[:, 0].max()), E22_min=float(t1[:, 1].min()), E33_min=float(t1[:, 2].min()))
if t2:
    t2 = np.array(t2); S["axis2_points"] = dict(n=len(t2), E11_max=float(t2[:, 0].max()), E22_max=float(t2[:, 1].max()), E33_min=float(t2[:, 2].min()))
# boundary: critical points of E|S^2 and the normal component there
bk = collections.Counter(); bN = collections.defaultdict(list)
for r in inner:
    for b in r["boundary"]:
        bk[b["kind"]] += 1; bN[b["kind"]].append(abs(b["N"]))
S["boundary_critical_kinds"] = dict(bk)
S["boundary_min_absN"] = {k: float(min(v)) for k, v in bN.items()}
# edges against the spheroid ruling
lam = dict(c_ob=0.40796, d_ob=0.643545, b_pro=2.065382, c_pro=4.724383)
edge_bad = []
for r in ok:
    na = [len(a) for a in r["axis_roots"]]
    if r["edge"] == "prolate":
        exp = 1 if lam["b_pro"] < r["t"] < lam["c_pro"] else 0
        if not (na[0] == exp and na[1] == exp and na[2] == 0): edge_bad.append((r["s"], r["t"], na))
    if r["edge"] == "oblate":
        exp = 1 if 1/lam["d_ob"] < r["s"] < 1/lam["c_ob"] else 0
        if not (na[0] == exp and na[1] == 0 and na[2] == 0): edge_bad.append((r["s"], r["t"], na))
S["edge_rows"] = sum(1 for r in ok if r["edge"]); S["edge_disagree_with_ruling"] = edge_bad
S["seconds_total"] = sum(r.get("seconds", 0) for r in rows)
S["algo_counts"] = dict(collections.Counter(r.get("algo", 1) for r in ok))
json.dump(S, open(os.path.join(OUT, "summary_runA.json"), "w"), indent=1, default=str)

md.append("## Run A：主格子の census の要約\n")
md.append("| 項目 | 値 |\n|---|---|")
md.append("| 形の数（辺を含む） | %d（内部 %d、辺 %d） |" % (len(rows), len(inner), S["edge_rows"]))
md.append("| 実行時の例外 | %d |" % len(err))
md.append("| 停留点の種類ごとの個数（中心を除く、第一八分円の代表） | %s |" % ", ".join("%s: %d" % kv for kv in sorted(kinds.items())))
md.append("| 軸の外に停留点が見つかった形 | %d |" % len(offaxis))
md.append("| 1 本の軸に 2 個以上の根がある形 | %d |" % len(multi))
md.append("| 「根がある ⇔ h_i と極点トレースが異符号」に合わない (形, 軸) | %d |" % len(incons))
md.append("| Morse の指数和が 1 でない形 | %d |" % len(morse_bad))
md.append("| 退化の印（零固有値の許容幅内）が付いた形 | %d |" % len(degen))
md.append("| e₁ 軸の点の指数の分布 | %s |" % dict(idx1))
md.append("| e₂ 軸の点の指数の分布 | %s |" % dict(idx2))
md.append("| e₃ 軸の点の個数 | %d |" % sum(idx3.values()))
md.append("| min h₃、min E₃(e₃) | %.4f、%.4f |" % (S["min_h3"], S["min_pole3"]))
md.append("| 内部の形での min(h₂−h₁)、min(h₃−h₂) | %.4f、%.4f |" % (S["min_h2_minus_h1_interior"], S["min_h3_minus_h2_interior"]))
md.append("| 境界：E\\|S² の臨界点の種類ごとの個数（内部の形） | %s |" % ", ".join("%s: %d" % kv for kv in sorted(bk.items())))
md.append("| 境界：種類ごとの min\\|N\\| | %s |" % ", ".join("%s: %.2e" % kv for kv in sorted(S["boundary_min_absN"].items())))
md.append("| 辺の行が回転楕円体の裁定と合わない数 | %d / %d |" % (len(edge_bad), S["edge_rows"]))
md.append("")
md.append("### 領域の型ごとの形の数（内部の形）\n")
md.append("| 中心の指数 | e₁ の対 | e₂ の対 | e₃ の対 | 形の数 |\n|---|---|---|---|---|")
for k, v in sorted(cls.items()):
    md.append("| %d | %d | %d | %d | %d |" % (k + (v,)))
md.append("")

# ---------------------------------------------------------------- curves (Run B)
def tab(key, title):
    md.append("### %s\n" % title)
    md.append("| s | t | 求積による根のずれの見積もり |\n|---|---|---|")
    for r in B[key]:
        if r: md.append("| %.6f | %.8f | %.1e |" % (r["s"], r["t"], r["quad_shift"]))
    md.append("")
md.append("## Run B：分岐曲線（格子と独立に追跡）\n")
tab("Z1_t_of_s", "Z₁：h₁ = 0（s を固定して t を解く）"); tab("Z1_s_of_t", "Z₁：h₁ = 0（t を固定して s を解く）")
tab("D1_t_of_s", "∂₁：E₁(e₁) = 0（s を固定）"); tab("D1_s_of_t", "∂₁：E₁(e₁) = 0（t を固定）")
tab("Z2_t_of_s", "Z₂：h₂ = 0"); tab("D2_t_of_s", "∂₂：E₂(e₂) = 0")

# ---------------------------------------------------------------- figures
def curve(key):
    return np.array([(r["s"], r["t"]) for r in B[key] if r])
Z1 = np.vstack([curve("Z1_t_of_s"), curve("Z1_s_of_t")]); Z1 = Z1[np.argsort(Z1[:, 0])]
D1 = np.vstack([curve("D1_t_of_s"), curve("D1_s_of_t")]); D1 = D1[np.argsort(D1[:, 0])]
Z2 = curve("Z2_t_of_s"); D2 = curve("D2_t_of_s")

fig, ax = plt.subplots(figsize=(8.6, 6.4))
for r in inner:
    na = [len(a) for a in r["axis_roots"]]
    c = C_BOTH if na[0] and na[1] else C_E1 if na[0] else C_E2 if na[1] else C_NONE
    ax.plot(r["s"], r["t"], "o", ms=3.2, color=c, mec="none")
for r in ok:
    if r["edge"]:
        na = [len(a) for a in r["axis_roots"]]
        c = C_BOTH if na[0] and na[1] else C_E1 if na[0] else C_E2 if na[1] else C_NONE
        ax.plot(r["s"], r["t"], "s", ms=3.2, color=c, mec="none")
for arr, ls, lab in ((Z1, "-", "$Z_1$: $h_1=0$"), (Z2, "-", "$Z_2$: $h_2=0$"), (D1, "--", "$\\partial_1$: $E_1(e_1)=0$"), (D2, "--", "$\\partial_2$: $E_2(e_2)=0$")):
    m = arr[:, 0] <= 4.0
    ax.plot(arr[m, 0], arr[m, 1], ls, color=INK, lw=1.6)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xticks([1, 1.5, 2, 2.5, 3, 4]); ax.set_xticklabels(["1", "1.5", "2", "2.5", "3", "4"])
ax.set_yticks([1, 1.5, 2, 3, 4, 5, 6, 8]); ax.set_yticklabels(["1", "1.5", "2", "3", "4", "5", "6", "8"])
ax.minorticks_off()
ax.set_xlabel("$s = a_2/a_1$"); ax.set_ylabel("$t = a_3/a_2$")
bb = dict(boxstyle="round,pad=0.25", fc="#fcfcfb", ec="none", alpha=1.0)
ax.text(1.03, 1.13, "$R_A$\n中心だけ\n（極小）", fontsize=8.5, bbox=bb)
ax.text(1.42, 1.42, "$R_B$：$e_1$ の対（指数 1）\n中心は極小", fontsize=8.5, bbox=bb)
ax.text(1.05, 2.85, "$R_C$：$e_1$ と $e_2$ の対\n中心は極小", fontsize=8.5, bbox=bb)
ax.text(2.55, 1.45, "$R_D$：中心だけ\n（中心の指数 1）", fontsize=8.5, bbox=bb)
ax.text(2.2, 3.5, "$R_E$：$e_2$ の対（指数 2）\n中心の指数 1", fontsize=8.5, bbox=bb)
ax.text(1.9, 7.0, "$R_F$：中心だけ（中心の指数 2）", fontsize=8.5, bbox=bb)
ax.text(1.93, 1.62, "$Z_1$", fontsize=11, bbox=bb); ax.text(1.27, 1.52, r"$\partial_1$", fontsize=11, bbox=bb)
ax.text(3.4, 6.25, "$Z_2$", fontsize=11, bbox=bb); ax.text(3.4, 2.42, r"$\partial_2$", fontsize=11, bbox=bb)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([], [], marker="o", ls="", color=C_NONE, label="軸の対なし"),
                   Line2D([], [], marker="o", ls="", color=C_E1, label="$e_1$ の対だけ"),
                   Line2D([], [], marker="o", ls="", color=C_E2, label="$e_2$ の対だけ"),
                   Line2D([], [], marker="o", ls="", color=C_BOTH, label="$e_1$ と $e_2$ の対"),
                   Line2D([], [], color=INK, lw=1.6, label="中心の固有値の零曲線"),
                   Line2D([], [], color=INK, lw=1.6, ls="--", label="極点トレースの零曲線")],
          loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False, fontsize=9)
ax.set_title("停留点の地図（非区間の数値）：点は主格子の census、線は独立に追跡した曲線", fontsize=10, loc="left")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig1_map_st.png"), dpi=170); plt.close(fig)

# master plane (X, Y) = (ln sigma, ln v): axis i of shape (s,t) sits at
#   axis1: (ln s, ln s + ln t), axis2: (-ln s, ln t), axis3: (-ln s - ln t, -ln t)
fig, ax = plt.subplots(figsize=(7.6, 6.6))
def to_master(arr, axis):
    ls, lt = np.log(arr[:, 0]), np.log(arr[:, 1])
    return (ls, ls + lt) if axis == 1 else (-ls, lt)
zx = np.concatenate([to_master(Z2[::-1], 2)[0], to_master(Z1, 1)[0]]); zy = np.concatenate([to_master(Z2[::-1], 2)[1], to_master(Z1, 1)[1]])
dx = np.concatenate([to_master(D2[::-1], 2)[0], to_master(D1, 1)[0]]); dy = np.concatenate([to_master(D2[::-1], 2)[1], to_master(D1, 1)[1]])
ax.fill(np.concatenate([zx, dx[::-1]]), np.concatenate([zy, dy[::-1]]), color=C_E1, alpha=0.22, lw=0)
ax.plot(zx, zy, "-", color=INK, lw=1.6); ax.plot(dx, dy, "--", color=INK, lw=1.6)
ax.plot(zy, zx, "-", color=INK, lw=0.8, alpha=0.45); ax.plot(dy, dx, "--", color=INK, lw=0.8, alpha=0.45)
lim = 3.6
ax.plot([-lim, lim], [-lim, lim], color="#8a8984", lw=0.9); ax.plot([0, 0], [0, lim], color="#8a8984", lw=0.9)
ax.plot([-lim, 0], [0, 0], color="#8a8984", lw=0.9)
ax.plot([0], [0], "o", color=INK, ms=4)
ax.text(0.9, 2.9, "扇形 1\n（軸が最短）", fontsize=9, ha="center"); ax.text(-2.0, 2.9, "扇形 2\n（軸が中間）", fontsize=9, ha="center")
ax.text(-2.6, -0.9, "扇形 3\n（軸が最長）", fontsize=9, ha="center")
ax.text(1.05, 0.75, "扁平辺 (t=1)", fontsize=8, rotation=45, color="#52514e")
ax.text(0.05, 3.2, "扁長辺 (s=1)", fontsize=8, color="#52514e"); ax.text(-3.4, 0.07, "扁平辺 (t=1)", fontsize=8, color="#52514e")
ax.text(-2.2, 1.95, "Z: G=0", fontsize=10); ax.text(-2.2, 0.38, "D: b=0", fontsize=10)
ax.text(-1.3, 1.15, "帯 $\\mathcal{B}=\\{b<0<G\\}$：\nこの軸に対がある", fontsize=9, bbox=bb)
ax.set_xlim(-lim, lim); ax.set_ylim(-1.6, lim); ax.set_aspect("equal")
ax.set_xlabel("$X=\\ln\\sigma=\\ln(\\ell_j/\\ell_i)$"); ax.set_ylabel("$Y=\\ln v=\\ln(\\ell_k/\\ell_i)$")
ax.set_title("主平面：軸 i の主関数 $G(\\sigma,v)$、$b(\\sigma,v)$ の零曲線（薄い線は $\\sigma\\leftrightarrow v$ の鏡像）", fontsize=10, loc="left")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig2_master_plane.png"), dpi=170); plt.close(fig)

# far behaviour of Z2 and D2
fl = json.load(open(os.path.join(OUT, "flat_limit.json"))) if os.path.exists(os.path.join(OUT, "flat_limit.json")) else None
fig, ax = plt.subplots(figsize=(7.2, 4.6))
m = Z2[:, 0] >= 2
ax.plot(1/np.log(Z2[m, 0]), Z2[m, 1], "o-", color=C_E1, lw=2, ms=5, label="$Z_2$: $h_2=0$")
ax.plot(1/np.log(D2[m, 0]), D2[m, 1], "s-", color=C_E2, lw=2, ms=5, label="$\\partial_2$: $E_2(e_2)=0$")
if fl:
    ax.plot([0], [fl["t_c_inf"][0]], "o", mfc="none", mec=C_E1, ms=9); ax.plot([0], [1.0], "s", mfc="none", mec=C_E2, ms=9)
    ax.text(0.02, fl["t_c_inf"][0] + 0.12, "対数主要項の予想 t ≈ %.3f" % fl["t_c_inf"][0], fontsize=9)
    ax.text(0.02, 1.12, "対数主要項の予想 t = 1", fontsize=9)
ax.text(1/np.log(Z2[m, 0][0]) - 0.02, Z2[m, 1][0] + 0.15, "$Z_2$", fontsize=10, ha="right")
ax.text(1/np.log(D2[m, 0][0]) - 0.02, D2[m, 1][0] + 0.15, "$\\partial_2$", fontsize=10, ha="right")
ax.set_xlim(-0.03, 1.5); ax.set_ylim(0.8, 6.4)
ax.set_xlabel("1 / ln s"); ax.set_ylabel("曲線上の t")
ax.legend(frameon=False, fontsize=9, loc="center right")
ax.set_title("扁平な極限 $s\\to\\infty$ に向かう $Z_2$ と $\\partial_2$（s = 2 … 32）", fontsize=10, loc="left")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig3_far.png"), dpi=170); plt.close(fig)

# axis-root positions along grid columns (bifurcation diagrams in t at fixed s)
fig, axs = plt.subplots(1, 3, figsize=(11, 3.6), sharey=True)
for a, i_s in zip(axs, (2, 8, 16)):
    col = [r for r in ok if r["i"] == i_s]
    col.sort(key=lambda r: r["t"])
    for ax_i, c, lab in ((0, C_E1, "$e_1$ 軸"), (1, C_E2, "$e_2$ 軸")):
        tt = [r["t"] for r in col for _ in r["axis_roots"][ax_i]]; rr = [x for r in col for x in r["axis_roots"][ax_i]]
        a.plot(tt, rr, "o-" if ax_i == 0 else "s-", color=c, lw=2, ms=4, label=lab)
    a.set_xscale("log"); a.set_xticks([1, 2, 3, 4, 6, 8]); a.set_xticklabels(["1", "2", "3", "4", "6", "8"]); a.minorticks_off()
    a.set_title("s = %.3f" % col[0]["s"], fontsize=10, loc="left"); a.set_xlabel("t"); a.set_ylim(0, 1.02)
axs[0].set_ylabel("軸の上の停留点の位置 r"); axs[0].legend(frameon=False, fontsize=9)
fig.suptitle("軸の上の対の位置：$r\\to1$ で境界へ抜け、$r\\to0$ で中心に吸収される", fontsize=10, x=0.01, ha="left")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig4_axis_branches.png"), dpi=170); plt.close(fig)

# ---------------------------------------------------------------- ledger (CSV) of the grid
import csv
REG = {(0, 0, 0): "R_A", (0, 1, 0): "R_B", (0, 1, 1): "R_C", (1, 0, 0): "R_D", (1, 0, 1): "R_E", (2, 0, 0): "R_F"}
with open(os.path.join(OUT, "runA_ledger.csv"), "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["i", "j", "s", "t", "mode", "n_nodes", "algo", "h1", "h2", "h3", "pole1", "pole2", "pole3",
                 "n_e1", "n_e2", "n_e3", "r_e1", "r_e2", "index_e1", "index_e2", "n_plane", "n_general",
                 "n_boundary_nonpole", "center_index", "morse_sum", "result"])
    for r in rows:
        if "error" in r:
            wr.writerow([r["i"], r["j"], r["s"], r["t"], "error"] + [""]*20 + [r["error"]]); continue
        na = [len(a) for a in r["axis_roots"]]
        p1 = [p for p in r["points"] if p["kind"] == "axis1"]; p2 = [p for p in r["points"] if p["kind"] == "axis2"]
        npl = sum(1 for p in r["points"] if p["kind"].startswith("plane")); ng = sum(1 for p in r["points"] if p["kind"] == "general")
        nb = sum(1 for b in r["boundary"] if not b["kind"].startswith("pole"))
        key = (r["center_index"], na[0], na[1])
        res = REG.get(key, "OTHER") if (na[2] == 0 and npl == 0 and ng == 0) else "OTHER"
        wr.writerow([r["i"], r["j"], "%.15g" % r["s"], "%.15g" % r["t"], r["edge"] or "interior", r["n"], r.get("algo", 1)]
                    + ["%.12g" % v for v in r["h"]] + ["%.12g" % v for v in r["pole_trace"]] + na
                    + ["%.12g" % r["axis_roots"][0][0] if na[0] else "", "%.12g" % r["axis_roots"][1][0] if na[1] else "",
                       p1[0]["index"] if p1 else "", p2[0]["index"] if p2 else "", npl, ng, nb, r["center_index"], r["morse_sum"], res])
frag = {"regions": dict(collections.Counter(REG.get((r["center_index"], len(r["axis_roots"][0]), len(r["axis_roots"][1])), "OTHER") for r in inner))}

# ---------------------------------------------------------------- Run C / D / E tables
def load(name):
    p = os.path.join(OUT, name)
    return json.load(open(p)) if os.path.exists(p) else None
C = load("runC_edges.json")
if C:
    md.append("## Run C：辺の近くの分裂\n")
    md.append("### 扁長辺 s = 1 + δ\n")
    md.append("| t | r₀ | E_rr | E_33 | B | δ | E_22（e₁ の点） | 予想 | E_11（e₂ の点） | 予想 | E(e₁)−E(e₂) | 予想 2Bδ | 指数 e₁/e₂ |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    rc = []
    for r in C["prolate"]:
        if "split" not in r: continue
        for e in r["split"]:
            if "E22_at_e1" not in e: continue
            md.append("| %.2f | %.6f | %.4f | %.4f | %.6f | %g | %.4e | %.4e | %.4e | %.4e | %.4e | %.4e | %d/%d |" % (
                r["t"], r["r0"], r["E_rr"], r["E_33"], r["B"], e["delta"], e["E22_at_e1"], e["pred_E22"], e["E11_at_e2"], e["pred_E11"],
                e["dE"], e["pred_dE"], e["index_e1"], e["index_e2"]))
        e = r["split"][0]
        rc.append("| %.2f | %.6f | %.4f | %.4f | %.6f | %.4e | %.4e | %s/%s |" % (r["t"], r["r0"], r["E_rr"], r["E_33"], r["B"],
                  e.get("E22_at_e1", float("nan")), e.get("pred_E22", float("nan")), e.get("index_e1"), e.get("index_e2")))
    frag["runC_rows"] = "\n".join(rc)
    md.append("\n### 扁平辺 t = 1 + δ（e₁ 軸の対）\n")
    md.append("| s | δ | r₁ | E_11 | E_22 | E_33 | e₂ 軸の根 | e₃ 軸の根 |\n|---|---|---|---|---|---|---|---|")
    for r in C["oblate"]:
        for e in r["split"]:
            if e["r1"] and "hdiag" in e:
                md.append("| %.2f | %g | %.6f | %.5f | %.5f | %.5f | %d | %d |" % (r["s"], e["delta"], e["r1"][0], *e["hdiag"], len(e["r2"]), len(e["r3"])))
    md.append("")
D = load("runD_sphere.json")
if D:
    md.append("## Run D：球の近く\n")
    md.append("| r | 数値の E′(r) | 閉じた式 | 差 |\n|---|---|---|---|")
    for p in D["sphere_profile"]:
        md.append("| %g | %.12f | %.12f | %.1e |" % (p["r"], p["numeric"], p["closed"], p["diff"]))
    bt = D["sphere_boundary_trace"]
    md.append("\n境界のトレース：数値 %.12f、π²/32 = %.12f\n" % (bt["numeric"], bt["closed"]))
    md.append("| s | t | 中心以外の停留点 | min q·∇E/\\|q\\|² | h₁ | h₂ | h₃ | Morse の和 |\n|---|---|---|---|---|---|---|---|")
    for r in D["grid"]:
        md.append("| %.5f | %.5f | %d | %.4f | %.4f | %.4f | %.4f | %d |" % (r["s"], r["t"], r["n_noncentral"], r["min_radial"], *r["h"], r["morse_sum"]))
    md.append("")
    frag["runD"] = dict(max_profile_diff=max(abs(p["diff"]) for p in D["sphere_profile"]), trace_num=bt["numeric"], trace_closed=bt["closed"],
                        n_grid=len(D["grid"]), n_with_noncentral=sum(1 for r in D["grid"] if r["n_noncentral"]),
                        min_radial=min(r["min_radial"] for r in D["grid"]), morse_all_1=all(r["morse_sum"] == 1 for r in D["grid"]))
Ef = load("runE_far.json")
if Ef:
    md.append("## Run E：遠方の格子（節点数を倍々にして収束を確認）\n")
    md.append("| s | t | h₁ | h₂ | h₃ | E₁(e₁) | E₂(e₂) | E₃(e₃) | 節点数 n | 最後の 2 段の差 | 収束 |\n|---|---|---|---|---|---|---|---|---|---|---|")
    for r in Ef:
        md.append("| %g | %g | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f | %d | %.0e | %s |" % (r["s"], r["t"], *r["h"], *r["pole"], r["n"], r["last_diff"],
                  "収束" if r["last_diff"] < 1e-8 else "**未収束**"))
    md.append("")
    conv = [r for r in Ef if r["last_diff"] < 1e-8]
    frag["runE"] = dict(n=len(Ef), n_conv=len(conv), unconverged=[(r["s"], r["t"]) for r in Ef if r["last_diff"] >= 1e-8],
                        min_h3_conv=min(r["h"][2] for r in conv), min_pole3_conv=min(r["pole"][2] for r in conv),
                        h2_lt_h1=[(r["s"], r["t"]) for r in conv if r["h"][1] < r["h"][0]])
P = load("probe_shear_sign.json")
if P:
    frag["shear"] = dict(c12=[min(r["c12_min"] for r in P), max(r["c12_max"] for r in P)], c13=[min(r["c13_min"] for r in P), max(r["c13_max"] for r in P)],
                         c23=[min(r["c23_min"] for r in P), max(r["c23_max"] for r in P)], n=len(P))
json.dump(frag, open(os.path.join(OUT, "report_fragments.json"), "w"), indent=1, default=str)

open(os.path.join(OUT, "tables.md"), "w").write("\n".join(md) + "\n")
print(json.dumps({k: v for k, v in S.items() if k not in ("offaxis", "multi", "inconsistent")}, indent=1, default=str)[:6000])
