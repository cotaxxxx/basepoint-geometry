#!/usr/bin/env python3
"""Diagnostic-only B-LOCAL v2.2 regular hat-route probe.

Not certificate evidence and not a production source.  It monkeypatches the
readiness-draft finite route in memory to test R-6/R-8 plus priority/incremental
aggregation before any native source change.
"""
from __future__ import annotations

import collections
import heapq
import json
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import blocal_v22_model as model
import blocal_v22_policy as policy
import blocal_v22_readiness_test as readiness

CONFIG_PATH = HERE / "config.blocal-v2.2-readiness-ephemeral.json"
PI_LO = Fraction(333, 106)
PI_HI = Fraction(355, 113)


def load_runtime():
    config = model.parse_canonical_json(CONFIG_PATH.read_bytes())
    model.validate_config(config)
    from flint import acb, arb, ctx, fmpq
    ctx.prec = config["precision"]["bits"]
    route, adapter, kernel = readiness.load(config)
    return config, route, adapter, kernel, acb, arb, fmpq


def install_probe(config, route, adapter, kernel, acb, arb, fmpq):
    def factor_at(q: Fraction, power: int, where: str):
        qa = route._arb_exact(arb, fmpq, q)
        invq = arb(1) / qa
        invs = arb(1) / qa.sqrt()
        if power == 1:
            out = invs
        elif power == 3:
            out = invq * invs
        elif power == 5:
            out = invq * invq * invs
        else:
            raise ValueError(power)
        route._canonical(adapter, out, where)
        return out

    def q_factor_pair(q_ball: Any, q_lo: Fraction, power: int, where: str):
        qiv = route._canonical(adapter, q_ball, where + ".q")
        _, q_hi = model.interval_fractions(qiv, where + ".q")
        model.need(q_lo > 0 and q_hi >= q_lo, where + ": q endpoints")
        return factor_at(q_hi, power, where + ".lo"), factor_at(q_lo, power, where + ".hi"), q_hi

    def rational_factor_pair(lo: Fraction, hi: Fraction, where: str):
        model.need(Fraction(0) < lo <= hi, where)
        return route._arb_exact(arb, fmpq, lo), route._arb_exact(arb, fmpq, hi)

    def scale_pair(value: Any, pair, where: str):
        a = value * pair[0]
        b = value * pair[1]
        route._canonical(adapter, a, where + ".at_lo")
        route._canonical(adapter, b, where + ".at_hi")
        out = a.union(b)
        route._canonical(adapter, out, where + ".hull")
        return out

    def clipped(value: Any, lo: Fraction, hi: Fraction, where: str):
        iv = route._canonical(adapter, value, where)
        a, b = model.interval_fractions(iv, where)
        a = max(a, lo)
        b = min(b, hi)
        if a > b:
            raise route.SplitRequired(where + ":EMPTY_CLIP")
        return route._arb_interval(arb, fmpq, a, b)

    def regular_exact_bounds(cell, eps: Fraction):
        if cell.region == "R1":
            c0 = eps + (1-eps)*cell.a0
            c1 = eps + (1-eps)*cell.a1
            p0 = PI_LO * cell.b0
            p1 = PI_HI * cell.b1
        elif cell.region == "R2":
            c0 = eps * cell.a0
            c1 = eps * cell.a1
            p0 = eps + (PI_LO-eps)*cell.b0
            p1 = eps + (PI_HI-eps)*cell.b1
        else:
            raise ValueError(cell.region)
        rho2_lo = c0*c0 + p0*p0
        rho2_hi = c1*c1 + p1*p1
        model.need(rho2_lo > 0 and rho2_lo <= rho2_hi, "regular rho bounds")
        return c0, c1, p0, p1, rho2_lo, rho2_hi

    def square_lower(ball: Any, where: str) -> Fraction:
        iv = route._canonical(adapter, ball*ball, where)
        lo, _ = model.interval_fractions(iv, where)
        return max(Fraction(0), lo)

    def regular_hat_data(cell, r, lam_b, c, phi, g, u0, s0, eps):
        c0,c1,p0,p1,rho2_lo,rho2_hi = regular_exact_bounds(cell, eps)
        # sin(t) >= t - t^3/6 for t>=0.  With sin(t)>=0 on [0,pi],
        # sinc(t)^2 >= max(0,1-p1^2/6)^2.  Diagnostic helper only.
        sinc = max(Fraction(0), Fraction(1) - p1*p1/Fraction(6))
        k_sinc = sinc*sinc
        model.need(model.LAMBDA_PLUS*model.LAMBDA_PLUS-Fraction(1) > Fraction(1), "lambda coefficient")

        uiv = route._canonical(adapter, g["U"], "regular U")
        ulo, uhi = model.interval_fractions(uiv, "regular U")
        rlo, rhi = Fraction(1)-u0 if False else None, None
        # r = [1-u1,1-u0]; recover exact endpoints from the Arb r enclosure.
        riv = route._canonical(adapter, r, "regular r")
        rlo, rhi = model.interval_fractions(riv, "regular r")
        dlo, dhi = rlo-uhi, rhi-ulo
        if dlo <= 0 <= dhi:
            d2_lo = Fraction(0)
        else:
            d2_lo = min(abs(dlo), abs(dhi))**2
        zden = k_sinc + d2_lo/rho2_hi
        if zden <= 0:
            raise route.SplitRequired("REGULAR_Z_DEN_LO_NONPOSITIVE")

        # Stable B = sin^2(phi) + c^2 cos^2(phi).
        sp = phi.sin(); cp = phi.cos()
        Bstable = sp*sp + c*c*cp*cp
        A = (lam_b*lam_b-arb(1))*c*c
        rho2 = c*c + phi*phi
        rho = route._safe_positive_sqrt(adapter, arb, fmpq, rho2, rho2_lo, "regular.rho")

        invrho2 = rational_factor_pair(Fraction(1,1)/rho2_hi, Fraction(1,1)/rho2_lo, "invrho2")
        Ahat = clipped(scale_pair(A, invrho2, "Ahat"), Fraction(0), (model.LAMBDA_PLUS+s0)**2+Fraction(1), "Ahat.clip")
        Bhat = clipped(scale_pair(Bstable, invrho2, "Bhat"), Fraction(0), Fraction(1), "Bhat.clip")
        M = g["U"]*Ahat + r*Bhat

        # q/rho^2 >= zden, hence z <= 1/sqrt(zden).  Strengthen q_lo too.
        zhi_ball = arb(1) / route._arb_exact(arb, fmpq, zden).sqrt()
        zhi_iv = route._canonical(adapter, zhi_ball, "z_hi")
        _, zhi = model.interval_fractions(zhi_iv, "z_hi")
        qlo_base = route._regular_q_lo(cell.region, cell, model.LAMBDA_PLUS+s0, eps, None)
        qlo = max(qlo_base, zden*rho2_lo)
        p1q_lo, p1q_hi, qhi = q_factor_pair(g["q"], qlo, 1, "regular.qhalf")

        yh = clipped(scale_pair(g["W"], (p1q_lo,p1q_hi), "y_h"), Fraction(0), Fraction(1), "y_h.clip")
        v = clipped(scale_pair(r-g["U"], (p1q_lo,p1q_hi), "v"), Fraction(-1), Fraction(1), "v.clip")
        z_direct = scale_pair(rho, (p1q_lo,p1q_hi), "z.direct")
        z = clipped(z_direct, Fraction(0), zhi, "z.clip")
        gamma = clipped(g["L"]*yh, Fraction(0), Fraction(1), "gamma.clip")

        invrho_lo_ball = arb(1) / route._arb_exact(arb, fmpq, rho2_hi).sqrt()
        invrho_hi_ball = arb(1) / route._arb_exact(arb, fmpq, rho2_lo).sqrt()
        route._canonical(adapter, invrho_lo_ball, "invrho.lo")
        route._canonical(adapter, invrho_hi_ball, "invrho.hi")
        return {
            "rho":rho,"Ahat":Ahat,"Bhat":Bhat,"M":M,"y":yh,"v":v,"z":z,"gamma":gamma,
            "invrho_pair":(invrho_lo_ball,invrho_hi_ball),"zden":zden,"qlo":qlo,"qhi":qhi,
            "rho2_lo":rho2_lo,"rho2_hi":rho2_hi,"k_sinc":k_sinc,"d2_lo":d2_lo,
        }

    def regular_eval(quantity, kernel_, adapter_, acb_type, arb_type, fmpq_type,
                     cell, u0, u1, s0, s1, eps):
        r=route._r_ball(arb_type,fmpq_type,u0,u1)
        lam_b=route._lambda_ball(arb_type,fmpq_type,s0,s1)
        pi=arb_type.pi();one=arb_type(1);eps_a=route._arb_exact(arb_type,fmpq_type,eps)
        a=route._arb_interval(arb_type,fmpq_type,cell.a0,cell.a1)
        b=route._arb_interval(arb_type,fmpq_type,cell.b0,cell.b1)
        if cell.region=="R1":
            c=eps_a+(one-eps_a)*a;phi=pi*b;measure=(one-eps_a)*pi
        elif cell.region=="R2":
            c=eps_a*a;phi=eps_a+(pi-eps_a)*b;measure=eps_a*(pi-eps_a)
        else:
            raise ValueError(cell.region)
        g=route._geometry(adapter_,arb_type,fmpq_type,r,lam_b,c,phi)
        d=regular_hat_data(cell,r,lam_b,c,phi,g,u0,s0,eps)
        h,h1,h2,gsplits=route._angle_union(kernel_,adapter_,acb_type,arb_type,d["gamma"],False,quantity=="H_U")
        if quantity=="F":
            # Normative F-4 cancellation-free regular bracket.
            value=-g["U"]*h - g["L"]*h1*d["M"]*d["y"]*d["z"]*d["z"]
        else:
            # Exact J=rho*K expression already certified by symbolic audit.
            z=d["z"]; y=d["y"]; v=d["v"]; M=d["M"]; Bhat=d["Bhat"]; rho=d["rho"]
            J=g["L"]*(arb_type(2)*g["U"]*h1*M*z**3
                +g["L"]*h2*M*M*y*z**5
                +h1*(-Bhat*y*rho*z**2+arb_type(3)*M*y*v*z**3))
            K=scale_pair(J,d["invrho_pair"],"regular.K_from_J")
            value=-K
        area=route._arb_exact(arb_type,fmpq_type,(cell.a1-cell.a0)*(cell.b1-cell.b0))
        contribution=value*measure*area
        route._canonical(adapter_,contribution,"regular hat contribution")
        return contribution,{
            "regular_hat_route":True,"zden":model.rational_json(d["zden"]),
            "q_lo":model.rational_json(d["qlo"]),"q_hi":model.rational_json(d["qhi"]),
            "rho2_lo":model.rational_json(d["rho2_lo"]),"rho2_hi":model.rational_json(d["rho2_hi"]),
            "sinc2_lo":model.rational_json(d["k_sinc"]),"d2_lo":model.rational_json(d["d2_lo"]),
            "gamma_subdivisions":gsplits,"gamma_fallback_used":bool(gsplits),
        }

    # R-6 on noncorner Duffy children; corner bounded extension stays unchanged.
    def duffy_eval(quantity, kernel_, adapter_, acb_type, arb_type, fmpq_type,
                   cell, u0, u1, s0, s1, eps):
        r=route._r_ball(arb_type,fmpq_type,u0,u1);lam_b=route._lambda_ball(arb_type,fmpq_type,s0,s1)
        x=route._arb_interval(arb_type,fmpq_type,cell.a0,cell.a1);yd=route._arb_interval(arb_type,fmpq_type,cell.b0,cell.b1)
        eps_a=route._arb_exact(arb_type,fmpq_type,eps);one=arb_type(1)
        if cell.region=="T1": c=eps_a*x;phi=eps_a*x*yd;Ahat=(lam_b*lam_b-one)/(one+yd*yd)
        elif cell.region=="T2": phi=eps_a*x;c=eps_a*x*yd;Ahat=(lam_b*lam_b-one)*yd*yd/(one+yd*yd)
        else: raise ValueError(cell.region)
        S2=one-c*c;S=route._safe_nonnegative_sqrt(adapter_,arb_type,fmpq_type,S2,"Duffy.S");U=S*phi.cos()
        w2=lam_b*lam_b*S2+c*c;w=route._safe_positive_sqrt(adapter_,arb_type,fmpq_type,w2,Fraction(1),"Duffy.w");L=lam_b/w
        bh_lo=route._bhat_lower(eps);Bhat=route._arb_interval(arb_type,fmpq_type,bh_lo,Fraction(1));M=U*Ahat+r*Bhat
        zden=route._z_den_lo(cell.region,cell,u1,s0,eps);z_hi=arb_type(1)/route._arb_exact(arb_type,fmpq_type,zden).sqrt()
        corner=(cell.a0==0);gy=route._safe_positive_sqrt(adapter_,arb_type,fmpq_type,one+yd*yd,Fraction(1),"Duffy.g");rho=eps_a*x*gy
        if corner:
            yh=arb_type(0).union(arb_type(1));v=arb_type(-1).union(arb_type(1));z=arb_type(0).union(z_hi);gamma=arb_type(0).union(arb_type(1))
        else:
            g=route._geometry(adapter_,arb_type,fmpq_type,r,lam_b,c,phi)
            rho2_lo=eps*eps*cell.a0*cell.a0*(1+cell.b0*cell.b0);qlo=rho2_lo*zden
            p1lo,p1hi,_=q_factor_pair(g["q"],qlo,1,"Duffy.qhalf")
            yh=clipped(scale_pair(g["W"],(p1lo,p1hi),"Duffy.y"),Fraction(0),Fraction(1),"Duffy.y.clip")
            v=clipped(scale_pair(r-U,(p1lo,p1hi),"Duffy.v"),Fraction(-1),Fraction(1),"Duffy.v.clip")
            ziv=route._canonical(adapter_,z_hi,"Duffy.zhi");_,zhi=model.interval_fractions(ziv,"Duffy.zhi")
            z=clipped(scale_pair(rho,(p1lo,p1hi),"Duffy.z"),Fraction(0),zhi,"Duffy.z.clip")
            gamma=clipped(L*yh,Fraction(0),Fraction(1),"Duffy.gamma")
        h,h1,h2,gsplits=route._angle_union(kernel_,adapter_,acb_type,arb_type,gamma,corner,quantity=="H_U")
        if quantity=="F":
            JF=rho*(-U*h-L*h1*M*yh*z*z);transformed=eps_a*JF/gy
        else:
            J=L*(arb_type(2)*U*h1*M*z**3+L*h2*M*M*yh*z**5+h1*(-Bhat*yh*rho*z**2+arb_type(3)*M*yh*v*z**3))
            transformed=-eps_a*J/gy
        area=route._arb_exact(arb_type,fmpq_type,(cell.a1-cell.a0)*(cell.b1-cell.b0));contribution=transformed*area
        route._canonical(adapter_,contribution,"Duffy contribution")
        return contribution,{"duffy_r6":True,"gamma_subdivisions":gsplits,"gamma_fallback_used":bool(gsplits)}

    route._regular_eval = regular_eval
    route._duffy_eval = duffy_eval

    def probe_enclose_route(quantity, kernel_, adapter_, acb_type, arb_type, fmpq_type,
                            cfg, u0, u1, s0, s1, required_sign=None):
        model.need(required_sign in {None,"POS","NEG","NONZERO"},"probe sign mode")
        pcfg=cfg["route_policies"]["F_ROUTE" if quantity=="F" else "K_ROUTE"]
        eps=model.fraction_from_dyadic(cfg["geometry"]["eps"])
        active={};heap=[];total_lo=Fraction(0);total_hi=Fraction(0);evaluations=0

        def diagnostic(reason):
            counts=collections.Counter(x[0].region for x in active.values())
            depths=collections.Counter(x[0].depth for x in active.values())
            tops=[]
            for path,(cell,ball,detail,iv,lo,hi) in active.items():
                tops.append((hi-lo,cell.region,path,cell.depth,lo,hi,detail))
            tops=sorted(tops,reverse=True)[:10]
            norm=model.normalize_interval(model.outward_dyadic(total_lo,total_hi))
            return {"reason":reason,"evaluations":evaluations,"active_leaves":len(active),"region_counts":dict(counts),"depth_counts":dict(depths),"normalized":norm,
                    "top_widths":[{"width":model.rational_json(w),"region":r,"path":p,"depth":d,"lo":model.rational_json(lo),"hi":model.rational_json(hi),
                                   "gamma_fallback":detail.get("gamma_fallback_used"),"zden":detail.get("zden")} for w,r,p,d,lo,hi,detail in tops]}

        def add(cell):
            nonlocal total_lo,total_hi,evaluations
            if cell.depth < pcfg["min_depth"]:
                for ch in route._split(cell): add(ch)
                return
            if evaluations >= pcfg["max_evaluations"]:
                raise RuntimeError("PROBE_BUDGET "+json.dumps(diagnostic("MAX_EVALUATIONS"),sort_keys=True,separators=(",",":")))
            try:
                ball,detail=route._cell_eval(quantity,kernel_,adapter_,acb_type,arb_type,fmpq_type,cell,u0,u1,s0,s1,eps)
            except route.SplitRequired as exc:
                if cell.depth >= pcfg["max_depth"]:
                    raise RuntimeError("PROBE_DEPTH "+json.dumps(diagnostic(exc.reason),sort_keys=True,separators=(",",":"))) from exc
                for ch in route._split(cell): add(ch)
                return
            evaluations+=1
            iv=route._canonical(adapter_,ball,"probe child");lo,hi=model.interval_fractions(iv,"probe child")
            model.need(len(active)<pcfg["max_children"],"probe child budget")
            active[cell.path]=(cell,ball,detail,iv,lo,hi);total_lo+=lo;total_hi+=hi
            if cell.depth<pcfg["max_depth"]:
                heapq.heappush(heap,(-(hi-lo),policy.REGION_ORDER[cell.region],cell.path))

        for cell in route._root_initial(): add(cell)

        def state():
            un=model.outward_dyadic(total_lo,total_hi);norm=model.normalize_interval(un);lo,hi=model.interval_fractions(norm,"root")
            ok=True if required_sign is None else lo>0 if required_sign=="POS" else hi<0 if required_sign=="NEG" else (lo>0 or hi<0)
            return ok,norm

        while True:
            ok,norm=state()
            if ok: break
            item=None
            while heap:
                _,_,path=heapq.heappop(heap);cand=active.get(path)
                if cand is not None and cand[0].depth<pcfg["max_depth"]:
                    item=cand;break
            if item is None:
                raise RuntimeError("PROBE_NO_SPLIT "+json.dumps(diagnostic("NO_SPLITTABLE"),sort_keys=True,separators=(",",":")))
            cell,ball,detail,iv,lo,hi=item
            del active[cell.path];total_lo-=lo;total_hi-=hi
            model.need(len(active)+2<=pcfg["max_children"],"probe child budget")
            for ch in route._split(cell): add(ch)
        return norm,{"proof_id":"DIAGNOSTIC","evaluation_count":evaluations,"active_leaves":len(active),"required_sign_mode":required_sign}

    route.enclose_route = probe_enclose_route


def phase_result(name, fn):
    started=time.perf_counter()
    try:
        value=fn()
        return {"phase":name,"status":"PASS","elapsed_seconds":f"{time.perf_counter()-started:.6f}",**value}
    except Exception as exc:
        return {"phase":name,"status":"FAIL","elapsed_seconds":f"{time.perf_counter()-started:.6f}","error_type":type(exc).__name__,"error":str(exc)}


def main()->int:
    config,route,adapter,kernel,acb,arb,fmpq=load_runtime()
    install_probe(config,route,adapter,kernel,acb,arb,fmpq)
    route.validate_helper_lemmas(arb,fmpq,config)
    s=model.fraction_from_dyadic(config["lambda_candidates"][0]);lam=model.LAMBDA_PLUS+s;umax=model.fraction_from_dyadic(config["u_max_candidates"][0])

    def enc(name, thunk):
        iv,p=thunk();return {"enclosure":iv,"evaluation_count":p["evaluation_count"]}

    results=[]
    results.append(phase_result("initial_pos",lambda:enc("initial",lambda:route.enclose_f(kernel,adapter,acb,arb,fmpq,config,1-umax,1-umax,lam,lam,"POS"))))
    results.append(phase_result("l3",lambda:enc("l3",lambda:route.enclose_f(kernel,adapter,acb,arb,fmpq,config,Fraction(1),Fraction(1),model.LAMBDA_PLUS,lam,"NEG"))))
    results.append(phase_result("l2",lambda:enc("l2",lambda:route.enclose_f(kernel,adapter,acb,arb,fmpq,config,1-umax,1-umax,model.LAMBDA_PLUS-model.S_NEG,lam,"POS"))))
    results.append(phase_result("l1",lambda:enc("l1",lambda:route.enclose_hu(kernel,adapter,acb,arb,fmpq,config,Fraction(1,1<<9),Fraction(1,1<<8),-model.S_NEG,s,"POS"))))

    def jstart():
        left,right=1-umax,Fraction(1);bis=[]
        def fat(r,mode):
            iv,p=route.enclose_f(kernel,adapter,acb,arb,fmpq,config,r,r,lam,lam,mode);lo,hi=model.interval_fractions(iv,"J")
            sign="POSITIVE" if lo>0 else "NEGATIVE" if hi<0 else "UNRESOLVED";bis.append({"r":model.rational_json(r),"mode":mode,"sign":sign,"evaluations":p["evaluation_count"]});return iv,sign
        _,sign=fat(left,"POS");model.need(sign=="POSITIVE","initial positive")
        found=False
        for _ in range(config["budgets"]["J_START"]["max_bisections"]):
            mid=(left+right)/2;_,sign=fat(mid,"NONZERO")
            if sign=="NEGATIVE":right=mid;found=True;break
            if sign=="POSITIVE":left=mid;continue
            raise RuntimeError("NONZERO unresolved")
        model.need(found and right<1,"negative endpoint")
        u0,u1=1-right,1-left;hu,hp=route.enclose_hu(kernel,adapter,acb,arb,fmpq,config,u0,u1,s,s,"POS");D=model.interval_negate(hu);_,dhi=model.interval_fractions(D,"D");model.need(dhi<0,"D negative")
        mid=(left+right)/2;Fm,mp=route.enclose_f(kernel,adapter,acb,arb,fmpq,config,mid,mid,lam,lam,None);qlo,qhi=model.interval_divide_negative_denominator(Fm,D);N=model.outward_dyadic(mid-qhi,mid-qlo);nlo,nhi=model.interval_fractions(N,"N");model.need(left<nlo<=nhi<right,"Newton")
        return {"bracket":model.interval_json(left,right),"bisection":bis,"H_u":hu,"F_r":D,"newton_image":N,"derivative_evaluations":hp["evaluation_count"],"midpoint_evaluations":mp["evaluation_count"]}
    results.append(phase_result("jstart",jstart))

    payload={"schema":"blocal-v22-hat-probe-v4","certificate_evidence":False,"results":results,"all_pass":all(r["status"]=="PASS" for r in results)}
    print(json.dumps(payload,sort_keys=True,separators=(",",":")),flush=True)
    return 0 if payload["all_pass"] else 1


if __name__=="__main__":
    raise SystemExit(main())
