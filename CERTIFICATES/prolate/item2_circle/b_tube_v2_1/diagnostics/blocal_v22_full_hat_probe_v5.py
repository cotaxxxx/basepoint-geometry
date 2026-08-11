#!/usr/bin/env python3
"""Diagnostic-only full regular-hat probe for B-LOCAL v2.2.

No certificate evidence.  R1 uses t=phi/c; R2 uses t=c/phi.  The regular
route constructs rho, Ahat, Bhat, y_h, v and z from normalized variables and
never uses a raw q^{-1/2} factor.
"""
from __future__ import annotations
import collections, heapq, json, sys, time
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import blocal_v22_model as model
import blocal_v22_policy as policy
import blocal_v22_readiness_test as readiness

CONFIG=HERE/"config.blocal-v2.2-readiness-ephemeral.json"
PI_LO=Fraction(333,106); PI_HI=Fraction(355,113); HALF_PI_HI=PI_HI/Fraction(2)


def main()->int:
    cfg=model.parse_canonical_json(CONFIG.read_bytes());model.validate_config(cfg)
    from flint import acb,arb,ctx,fmpq
    ctx.prec=cfg["precision"]["bits"]
    route,adapter,kernel=readiness.load(cfg)
    route.validate_helper_lemmas(arb,fmpq,cfg)

    def can(ball,where):return route._canonical(adapter,ball,where)
    def exact(q):return route._arb_exact(arb,fmpq,q)
    def interval(lo,hi):return route._arb_interval(arb,fmpq,lo,hi)

    def endpoint_scale(value,lo_factor,hi_factor,where):
        a=value*lo_factor;b=value*hi_factor;can(a,where+".lo");can(b,where+".hi");out=a.union(b);can(out,where+".hull");return out

    def positive_inverse_pair(ball,floor,where,power=1):
        iv=can(ball,where+".base");_,hi=model.interval_fractions(iv,where+".base");model.need(Fraction(0)<floor<=hi,where+" floor")
        def f(q):
            qa=exact(q);sq=qa.sqrt();inv=arb(1)/sq
            if power==2:inv=arb(1)/qa
            elif power==3:inv=(arb(1)/qa)*(arb(1)/sq)
            can(inv,where+".factor");return inv
        return f(hi),f(floor),hi

    def clip(ball,lo,hi,where):
        iv=can(ball,where);a,b=model.interval_fractions(iv,where);a=max(a,lo);b=min(b,hi)
        if a>b:raise route.SplitRequired(where+":EMPTY")
        return interval(a,b)

    def exact_source_bounds(cell,eps):
        if cell.region=="R1":
            c0=eps+(1-eps)*cell.a0;c1=eps+(1-eps)*cell.a1
            p0=PI_LO*cell.b0;p1=PI_HI*cell.b1
        else:
            c0=eps*cell.a0;c1=eps*cell.a1
            p0=eps+(PI_LO-eps)*cell.b0;p1=eps+(PI_HI-eps)*cell.b1
        return c0,c1,p0,p1

    def ratio_pair(num,den_lo,den_hi,where):
        # denominator is strictly positive; retain endpoint inverse factors.
        ilo=arb(1)/exact(den_hi);ihi=arb(1)/exact(den_lo);can(ilo,where+".ilo");can(ihi,where+".ihi")
        return endpoint_scale(num,ilo,ihi,where)

    def regular_hat(cell,r,lam,c,phi,u0,u1,s0,eps):
        c0,c1,p0,p1=exact_source_bounds(cell,eps)
        one=arb(1)
        if cell.region=="R1":
            # t=phi/c; k=sin(phi)/c; all denominators c>=eps.
            t=ratio_pair(phi,c0,c1,"R1.t")
            k=ratio_pair(phi.sin(),c0,c1,"R1.k")
            d=one+t*t;can(d,"R1.d")
            invd_lo,invd_hi,_=positive_inverse_pair(d,Fraction(1),"R1.dinv",power=2)
            rho=c*route._safe_positive_sqrt(adapter,arb,fmpq,d,Fraction(1),"R1.g")
            Ahat=endpoint_scale(lam*lam-one,invd_lo,invd_hi,"R1.Ahat")
            Bnum=k*k+phi.cos()*phi.cos()
            Bhat=endpoint_scale(Bnum,invd_lo,invd_hi,"R1.Bhat")
        else:
            # t=c/phi; sinc=sin(phi)/phi; denominator phi>=eps.
            t=ratio_pair(c,p0,p1,"R2.t")
            sinc=ratio_pair(phi.sin(),p0,p1,"R2.sinc")
            d=one+t*t;can(d,"R2.d")
            invd_lo,invd_hi,_=positive_inverse_pair(d,Fraction(1),"R2.dinv",power=2)
            rho=phi*route._safe_positive_sqrt(adapter,arb,fmpq,d,Fraction(1),"R2.g")
            Ahat=endpoint_scale((lam*lam-one)*t*t,invd_lo,invd_hi,"R2.Ahat")
            Bnum=sinc*sinc+t*t*phi.cos()*phi.cos()
            Bhat=endpoint_scale(Bnum,invd_lo,invd_hi,"R2.Bhat")
        Ahat=clip(Ahat,Fraction(0),Fraction(8),"Ahat.clip");Bhat=clip(Bhat,Fraction(0),Fraction(1),"Bhat.clip")

        g=route._geometry(adapter,arb,fmpq,r,lam,c,phi)
        rho_iv=can(rho,"rho");rho_lo,rho_hi=model.interval_fractions(rho_iv,"rho");model.need(rho_lo>0,"rho positive")
        invrho_lo=arb(1)/exact(rho_hi);invrho_hi=arb(1)/exact(rho_lo)
        u=interval(u0,u1)
        # For phi entirely below pi/2 use W=u+r(1-U), 1-U=B/(1+U)=rho^2 Bhat/(1+U).
        if p1<=HALF_PI_HI:
            den=one+g["U"]
            deniv=can(den,"1+U");denlo,denhi=model.interval_fractions(deniv,"1+U");denlo=max(Fraction(1),denlo)
            invden_lo=arb(1)/exact(denhi);invden_hi=arb(1)/exact(denlo)
            term=endpoint_scale(rho*Bhat,invden_lo,invden_hi,"rhoB/(1+U)")
            u_over_rho=endpoint_scale(u,invrho_lo,invrho_hi,"u/rho")
            What=u_over_rho+r*term
            Vhat=-u_over_rho+term
        else:
            What=endpoint_scale(g["W"],invrho_lo,invrho_hi,"W/rho")
            Vhat=endpoint_scale(r-g["U"],invrho_lo,invrho_hi,"V/rho")

        What=clip(What,Fraction(0),Fraction(2048),"What.clip")
        Vhat=clip(Vhat,Fraction(-2048),Fraction(2048),"Vhat.clip")
        # normalized q/rho^2 exact identities.  Choose the narrower enclosure.
        D1=What*What+Ahat+r*r*Bhat
        D2=Vhat*Vhat+Bhat+Ahat
        i1=can(D1,"D1");i2=can(D2,"D2");a1,b1=model.interval_fractions(i1,"D1");a2,b2=model.interval_fractions(i2,"D2")
        D=D1 if b1-a1<=b2-a2 else D2
        # certified strict floor inherited from q_lo / rho_hi^2.
        r2w=None
        if cell.region=="R2":r2w,_=route._r2_w_lower(adapter,arb,fmpq,cell,u0,eps)
        qlo=route._regular_q_lo(cell.region,cell,model.LAMBDA_PLUS+s0,eps,r2w)
        Dfloor=qlo/(rho_hi*rho_hi);model.need(Dfloor>0,"D floor")
        zlo,zhi,Dhi=positive_inverse_pair(D,Dfloor,"z",power=1)
        z=zlo.union(zhi);can(z,"z.hull")
        y=clip(endpoint_scale(What,zlo,zhi,"y"),Fraction(0),Fraction(1),"y.clip")
        v=clip(endpoint_scale(Vhat,zlo,zhi,"v"),Fraction(-1),Fraction(1),"v.clip")
        gamma=clip(g["L"]*y,Fraction(0),Fraction(1),"gamma")
        M=g["U"]*Ahat+r*Bhat
        return g,rho,Ahat,Bhat,M,y,v,z,gamma,(invrho_lo,invrho_hi),{"D_floor":Dfloor,"D_hi":Dhi,"q_lo":qlo,"rho_lo":rho_lo,"rho_hi":rho_hi}

    def regular_eval(quantity,kernel_,adapter_,acb_type,arb_type,fmpq_type,cell,u0,u1,s0,s1,eps):
        r=route._r_ball(arb_type,fmpq_type,u0,u1);lam=route._lambda_ball(arb_type,fmpq_type,s0,s1)
        pi=arb_type.pi();one=arb_type(1);epsa=exact(eps);a=interval(cell.a0,cell.a1);b=interval(cell.b0,cell.b1)
        if cell.region=="R1":c=epsa+(one-epsa)*a;phi=pi*b;measure=(one-epsa)*pi
        else:c=epsa*a;phi=epsa+(pi-epsa)*b;measure=epsa*(pi-epsa)
        g,rho,Ahat,Bhat,M,y,v,z,gamma,invrho,meta=regular_hat(cell,r,lam,c,phi,u0,u1,s0,eps)
        h,h1,h2,gs=route._angle_union(kernel_,adapter_,acb_type,arb_type,gamma,False,quantity=="H_U")
        if quantity=="F":value=-g["U"]*h-g["L"]*h1*M*y*z*z
        else:
            J=g["L"]*(arb_type(2)*g["U"]*h1*M*z**3+g["L"]*h2*M*M*y*z**5+h1*(-Bhat*y*rho*z**2+arb_type(3)*M*y*v*z**3))
            K=endpoint_scale(J,invrho[0],invrho[1],"K=J/rho");value=-K
        area=exact((cell.a1-cell.a0)*(cell.b1-cell.b0));out=value*measure*area;can(out,"regular contribution")
        return out,{"full_regular_hat":True,"gamma_fallback_used":bool(gs),"gamma_subdivisions":gs,
                    "D_floor":model.rational_json(meta["D_floor"]),"D_hi":model.rational_json(meta["D_hi"]),
                    "rho_lo":model.rational_json(meta["rho_lo"]),"rho_hi":model.rational_json(meta["rho_hi"])}

    route._regular_eval=regular_eval

    # Keep v2 Duffy implementation for this probe; v4 showed the dominant residual is regular R1.
    def probe_route(quantity,kernel_,adapter_,acb_type,arb_type,fmpq_type,config,u0,u1,s0,s1,required_sign=None):
        pcfg=config["route_policies"]["F_ROUTE" if quantity=="F" else "K_ROUTE"];eps=model.fraction_from_dyadic(config["geometry"]["eps"])
        active={};heap=[];lo_sum=Fraction(0);hi_sum=Fraction(0);evals=0
        def diag(reason):
            cnt=collections.Counter(v[0].region for v in active.values());norm=model.normalize_interval(model.outward_dyadic(lo_sum,hi_sum))
            tops=sorted([(v[5]-v[4],v[0].region,k,v[0].depth,v[6].get("gamma_fallback_used"),v[6].get("D_floor")) for k,v in active.items()],reverse=True)[:8]
            return {"reason":reason,"evaluations":evals,"leaves":len(active),"regions":dict(cnt),"normalized":norm,
                    "tops":[{"width":model.rational_json(w),"region":r,"path":p,"depth":d,"gamma_fallback":gf,"D_floor":df} for w,r,p,d,gf,df in tops]}
        def add(cell):
            nonlocal lo_sum,hi_sum,evals
            if cell.depth<pcfg["min_depth"]:
                for ch in route._split(cell):add(ch)
                return
            if evals>=pcfg["max_evaluations"]:raise RuntimeError("BUDGET "+json.dumps(diag("MAX_EVALUATIONS"),sort_keys=True,separators=(",",":")))
            try:ball,detail=route._cell_eval(quantity,kernel_,adapter_,acb_type,arb_type,fmpq_type,cell,u0,u1,s0,s1,eps)
            except route.SplitRequired as exc:
                if cell.depth>=pcfg["max_depth"]:raise RuntimeError("DEPTH "+json.dumps(diag(exc.reason),sort_keys=True,separators=(",",":"))) from exc
                for ch in route._split(cell):add(ch)
                return
            evals+=1;iv=can(ball,"child");lo,hi=model.interval_fractions(iv,"child");active[cell.path]=(cell,ball,iv,None,lo,hi,detail);lo_sum+=lo;hi_sum+=hi
            if cell.depth<pcfg["max_depth"]:heapq.heappush(heap,(-(hi-lo),policy.REGION_ORDER[cell.region],cell.path))
        for c0 in route._root_initial():add(c0)
        def ok():
            norm=model.normalize_interval(model.outward_dyadic(lo_sum,hi_sum));lo,hi=model.interval_fractions(norm,"root")
            return (required_sign is None or required_sign=="POS" and lo>0 or required_sign=="NEG" and hi<0 or required_sign=="NONZERO" and (lo>0 or hi<0)),norm
        while True:
            good,norm=ok()
            if good:return norm,{"proof_id":"DIAG","evaluation_count":evals}
            item=None
            while heap:
                _,_,p=heapq.heappop(heap);v=active.get(p)
                if v is not None and v[0].depth<pcfg["max_depth"]:item=v;break
            if item is None:raise RuntimeError("NOSPLIT "+json.dumps(diag("NO_SPLITTABLE"),sort_keys=True,separators=(",",":")))
            cell,ball,iv,_,lo,hi,detail=item;del active[cell.path];lo_sum-=lo;hi_sum-=hi
            for ch in route._split(cell):add(ch)
    route.enclose_route=probe_route

    s=model.fraction_from_dyadic(cfg["lambda_candidates"][0]);lam=model.LAMBDA_PLUS+s;umax=model.fraction_from_dyadic(cfg["u_max_candidates"][0])
    def run(name,fn):
        t=time.perf_counter()
        try:iv,p=fn();return {"phase":name,"status":"PASS","elapsed":f"{time.perf_counter()-t:.6f}","enclosure":iv,"evaluations":p["evaluation_count"]}
        except Exception as e:return {"phase":name,"status":"FAIL","elapsed":f"{time.perf_counter()-t:.6f}","error_type":type(e).__name__,"error":str(e)}
    res=[
      run("initial_pos",lambda:route.enclose_f(kernel,adapter,acb,arb,fmpq,cfg,1-umax,1-umax,lam,lam,"POS")),
      run("l3",lambda:route.enclose_f(kernel,adapter,acb,arb,fmpq,cfg,Fraction(1),Fraction(1),model.LAMBDA_PLUS,lam,"NEG")),
      run("l2",lambda:route.enclose_f(kernel,adapter,acb,arb,fmpq,cfg,1-umax,1-umax,model.LAMBDA_PLUS-model.S_NEG,lam,"POS")),
      run("l1",lambda:route.enclose_hu(kernel,adapter,acb,arb,fmpq,cfg,Fraction(1,1<<9),Fraction(1,1<<8),-model.S_NEG,s,"POS")),
    ]
    print(json.dumps({"schema":"blocal-v22-full-hat-probe-v5","certificate_evidence":False,"results":res,"all_pass":all(x["status"]=="PASS" for x in res)},sort_keys=True,separators=(",",":")),flush=True)
    return 0 if all(x["status"]=="PASS" for x in res) else 1

if __name__=="__main__":raise SystemExit(main())
