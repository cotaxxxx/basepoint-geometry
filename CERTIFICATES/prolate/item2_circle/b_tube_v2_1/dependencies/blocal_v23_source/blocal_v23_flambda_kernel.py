#!/usr/bin/env python3
"""Shared native F_lambda mathematical kernel for B-LOCAL v2.3.

DESIGN_DRAFT_ONLY / NOT_BINDING / NOT_PROMOTED.
No route orchestration or verdict logic lives here.
"""
from __future__ import annotations
from fractions import Fraction
from typing import Any
import blocal_v22_boundary as base
import blocal_v22_model as model
import blocal_v22_policy as policy

ORDINARY_FORMULA_ID = "BLOCAL_FLAMBDA_ORDINARY_V1"
DUFFY_FORMULA_ID = "BLOCAL_FLAMBDA_DUFFY_V1"


def geometry_jet_flambda(quantity: str, kernel: Any, adapter: Any, acb_type: Any,
                         arb_type: Any, fmpq_type: Any, region: str,
                         a: base.J2, b: base.J2, r: base.J2, lam: base.J2,
                         cell: base.Cell, u0: Fraction, s0: Fraction,
                         eps: Fraction, scope: str, max_gamma_depth: int):
    model.need(quantity == "F_lambda", "F_lambda ordinary quantity")
    pi=arb_type.pi(); ea=base._arb_exact(arb_type,fmpq_type,eps)
    ids=[]; c1dig=c1rec=None
    if region=="C1":
        c=ea+base._arb_exact(arb_type,fmpq_type,base.HALF-eps)*a; phi=pi*b
        qstruct,Sstruct,c1dig,c1rec=base._c1_floor(adapter,arb_type,fmpq_type,cell,r,s0,eps)
        S2=1-c*c; Sfloor,Sdig=base._effective_floor(adapter,"ORDINARY_S2",Sstruct,S2.v,"C1.S2",region,scope,cell)
        S=base._jsqrt(adapter,arb_type,fmpq_type,S2,Sfloor,"C1.S"); density=base._as_jet(arb_type(1),a.v); ids.append(Sdig)
    elif region=="TH":
        theta=(pi/3)*a; phi=pi*b; S=base._jsin(theta); c=base._jcos(theta); density=S
        qstruct=base._chart_q_floor(adapter,arb_type,fmpq_type,region,cell,u0,s0,eps)
    elif region=="R2":
        c=ea*a; phi=ea+(pi-ea)*b; S2=1-c*c
        Sfloor,Sdig=base._effective_floor(adapter,"ORDINARY_S2",1-eps*eps,S2.v,"R2.S2",region,scope,cell)
        S=base._jsqrt(adapter,arb_type,fmpq_type,S2,Sfloor,"R2.S"); density=base._as_jet(arb_type(1),a.v); ids.append(Sdig)
        qstruct=base._chart_q_floor(adapter,arb_type,fmpq_type,region,cell,u0,s0,eps)
    else: raise ValueError(region)
    U=S*base._jcos(phi); A=(lam*lam-1)*c*c; B=1-U*U; W=1-r*U; q=W*W+A+r*r*B
    w2=lam*lam*S*S+c*c
    wfloor,Wdig=base._effective_floor(adapter,"ORDINARY_W2",Fraction(1),w2.v,region+".w2",region,scope,cell)
    wm1=base._qpow(adapter,arb_type,fmpq_type,w2,wfloor,1,region+".wm1")
    wm3=base._qpow(adapter,arb_type,fmpq_type,w2,wfloor,3,region+".wm3")
    L=lam*wm1; ids.append(Wdig)
    qfloor,Qdig=base._effective_floor(adapter,"ORDINARY_Q",qstruct,q.v,region+".q",region,scope,cell); ids.append(Qdig)
    N=-U*A-r*B
    qm1=base._qpow(adapter,arb_type,fmpq_type,q,qfloor,1,region+".qm1")
    qm3=base._qpow(adapter,arb_type,fmpq_type,q,qfloor,3,region+".qm3")
    qm5=base._qpow(adapter,arb_type,fmpq_type,q,qfloor,5,region+".qm5")
    gamma=L*W*qm1; gr=L*N*qm3
    h1=base._hcompose(kernel,adapter,acb_type,arb_type,gamma,1,region+".h1",max_gamma_depth)
    h2=base._hcompose(kernel,adapter,acb_type,arb_type,gamma,2,region+".h2",max_gamma_depth)
    half=base._arb_exact(arb_type,fmpq_type,Fraction(1,2)); three_half=base._arb_exact(arb_type,fmpq_type,Fraction(3,2))
    A_lam=lam*2*c*c; L_lam=c*c*wm3; N_lam=-U*A_lam
    gamma_lam=L_lam*W*qm1-half*L*W*A_lam*qm3
    gamma_r_lam=L_lam*N*qm3+L*N_lam*qm3-three_half*L*N*A_lam*qm5
    out=-U*h1*gamma_lam+W*(h2*gamma_lam*gr+h1*gamma_r_lam)
    detail={"formula_id":ORDINARY_FORMULA_ID,"chart":region,
            "q_floor":model.rational_json(qfloor),"q_lo":model.rational_json(qfloor),
            "q_hi":model.rational_json(base._jet_fracs(adapter,q.v,region+".qhi")[1]),
            "q_lo_policy":policy.Q_LO_POLICY_ID,"denominator_policy":policy.DENOMINATOR_POLICY_ID,
            "sqrt_policy":policy.SQRT_POLICY_ID,"measure_identity":policy.MEASURE_ID,
            "gamma_policy":policy.GAMMA_POLICY_ID,"gamma_subdivisions":[],"gamma_fallback_used":False,
            "gamma_clamp":"[0,1]","gamma_clamp_fail_closed":True,
            "gamma_bound_basis":base.GAMMA_BOUND_BASIS_ID,"effective_floor_record_sha256":ids,
            "taylor_order":2,"gamma_lemma":"SOS_GAMMA_IN_0_1"}
    if c1dig is not None:
        detail.update({"c1_floor_record_sha256":c1dig,
                       "c1_q_floor_source":"C1_A_W2_B" if not c1rec["component_dropped"] else "C1_COMPONENT_DROPPED"})
    return density*out,detail


def duffy_eval_flambda(kernel: Any, adapter: Any, acb_type: Any, arb_type: Any,
                       fmpq_type: Any, cell: base.Cell, u0: Fraction,u1: Fraction,
                       s0: Fraction,s1: Fraction,eps: Fraction):
    r=base._r_ball(arb_type,fmpq_type,u0,u1); lam=base._lambda_ball(arb_type,fmpq_type,s0,s1)
    x=base._arb_interval(arb_type,fmpq_type,cell.a0,cell.a1); yd=base._arb_interval(arb_type,fmpq_type,cell.b0,cell.b1)
    eps_a=base._arb_exact(arb_type,fmpq_type,eps); one=arb_type(1); g2=one+yd*yd
    if cell.region=="T1":
        c=eps_a*x; phi=eps_a*x*yd; Ahat=(lam*lam-one)/g2; Ahat_lam=2*lam/g2
    elif cell.region=="T2":
        phi=eps_a*x; c=eps_a*x*yd; Ahat=(lam*lam-one)*yd*yd/g2; Ahat_lam=2*lam*yd*yd/g2
    else: raise ValueError("Duffy region")
    S2=one-c*c; Sfloor,Sdig=base._effective_floor(adapter,"DUFFY_S2",Fraction(0),S2,"Duffy.S2",cell.region,"box",cell)
    S=base._safe_positive_sqrt(adapter,arb_type,fmpq_type,S2,Sfloor,"Duffy.S.effective") if Sfloor>0 else base._safe_nonnegative_sqrt(adapter,arb_type,fmpq_type,S2,"Duffy.S.fallback")
    U=S*phi.cos(); A=(lam*lam-one)*c*c; B=one-U*U; W=one-r*U; q=W*W+A+r*r*B
    w2=lam*lam*S2+c*c; wfloor,Wdig=base._effective_floor(adapter,"DUFFY_W2",Fraction(1),w2,"Duffy.w2",cell.region,"box",cell)
    w=base._safe_positive_sqrt(adapter,arb_type,fmpq_type,w2,wfloor,"Duffy.w.effective"); L=lam/w; L_lam=c*c/(w*w*w)
    bh_lo=base._bhat_lower(eps); Bhat=base._arb_interval(arb_type,fmpq_type,bh_lo,Fraction(1)); M=U*Ahat+r*Bhat; M_lam=U*Ahat_lam
    zden,ahat_lo,rb_lo,what=base._z_den_lo(cell.region,cell,u0,u1,s0,eps)
    z_hi=arb_type(1)/base._arb_exact(arb_type,fmpq_type,zden).sqrt(); base._canonical(adapter,z_hi,"Duffy z_hi")
    corner=(cell.a0==0); gfloor,Gdig=base._effective_floor(adapter,"DUFFY_G2",Fraction(1),g2,"Duffy.g2",cell.region,"box",cell)
    gy=base._safe_positive_sqrt(adapter,arb_type,fmpq_type,g2,gfloor,"Duffy.g.effective"); rho=eps_a*x*gy; q_hi_record=None
    if corner:
        yh=arb_type(0).union(arb_type(1)); z=arb_type(0).union(z_hi); gamma=arb_type(0).union(arb_type(1))
    else:
        rho2_lo=eps*eps*cell.a0*cell.a0*(1+cell.b0*cell.b0); qlo=rho2_lo*zden
        _,invsqrtq,qhi=base._positive_inverse_factors(adapter,arb_type,fmpq_type,q,qlo,f"{cell.region}:{cell.path}:Duffy")
        q_hi_record=model.rational_json(qhi); yh=(W*invsqrtq).max(arb_type(0)).min(arb_type(1)); z=(rho*invsqrtq).max(arb_type(0)).min(z_hi); gamma=(L*yh).max(arb_type(0)).min(arb_type(1))
    _,h1,h2,gsplits=base._angle_union(kernel,adapter,acb_type,arb_type,gamma,corner,True); assert h2 is not None
    half=base._arb_exact(arb_type,fmpq_type,Fraction(1,2)); three_half=base._arb_exact(arb_type,fmpq_type,Fraction(3,2))
    gamma_lam=L_lam*yh-half*L*yh*Ahat_lam*z*z
    d_M_y_z2=M_lam*yh*z*z-three_half*M*yh*Ahat_lam*z**4
    z2=z*z
    d_core=-U*h1*gamma_lam-(L_lam*h1*M*yh*z2+L*h2*gamma_lam*M*yh*z2+L*h1*d_M_y_z2)
    transformed=eps_a*(rho*d_core)/gy
    area=base._arb_exact(arb_type,fmpq_type,(cell.a1-cell.a0)*(cell.b1-cell.b0)); contribution=transformed*area
    base._canonical(adapter,contribution,"F_lambda Duffy contribution")
    detail={"formula_id":DUFFY_FORMULA_ID,"Z_DEN_LO":model.rational_json(zden),"helper_lemma_id":"BHAT_LOWER_V2",
            "Duffy_Z_components":{"Ahat_lo":model.rational_json(ahat_lo),"r_lo2_Bhat_lo":model.rational_json(rb_lo),
                                  "u0_2_over_rho2_hi":model.rational_json(what),"rho2_hi":model.rational_json(eps*eps*cell.a1*cell.a1*(1+cell.b1*cell.b1))},
            "effective_floor_record_sha256":[Sdig,Wdig,Gdig],"local_geometry":["S","U","W","B","q"],
            "gamma_policy":policy.GAMMA_POLICY_ID,"gamma_subdivisions":gsplits,
            "gamma_fallback_used":any(x["bin_count"]>1 for x in gsplits),"gamma_fallback_class":"corner" if corner else "non_corner",
            "gamma_clamp":"[0,1]","gamma_clamp_fail_closed":True,"gamma_bound_basis":base.GAMMA_BOUND_BASIS_ID,
            "sqrt_policy":policy.SQRT_POLICY_ID,"bounded_extensions":{"y_h":"[0,1]" if corner else "CHILD_DIRECT","z":"[0,1/sqrt(Z_DEN_LO)]" if corner else "CHILD_DIRECT"},
            "duffy_id":policy.DUFFY_ID,"measure_identity":policy.MEASURE_ID,"triangle_substitution":cell.region}
    if not corner: detail.update({"denominator_policy":policy.DENOMINATOR_POLICY_ID,"q_hi":q_hi_record})
    return contribution,detail

__all__=["ORDINARY_FORMULA_ID","DUFFY_FORMULA_ID","geometry_jet_flambda","duffy_eval_flambda"]
