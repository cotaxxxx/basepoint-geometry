#!/usr/bin/env python3
"""Finite cancellation-free F/K angular routes for all B-LOCAL v2.2 consumers.

READINESS DRAFT v2.  Direct pinned F_arb/dFdr_arb are formula provenance only
and are never called by this module.  All proof evaluation uses exact domain
partitions, Duffy corner regularization, per-child gamma/denominator data,
endpoint-safe square roots, exact-endpoint reciprocal denominator factors, and
a deterministic adaptive ball sum.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

import blocal_v22_model as model
import blocal_v22_policy as policy

F_ROUTE_ID = policy.F_ROUTE_ID
K_ROUTE_ID = policy.K_ROUTE_ID
HELPER_VALIDATION_ID = policy.HELPER_VALIDATION_ID


class SplitRequired(RuntimeError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class Cell:
    region: str
    path: str
    depth: int
    a0: Fraction
    a1: Fraction
    b0: Fraction
    b1: Fraction


def _arb_exact(arb_type: Any, fmpq_type: Any, q: Fraction) -> Any:
    return arb_type(fmpq_type(q.numerator, q.denominator))


def _arb_interval(arb_type: Any, fmpq_type: Any,
                  lo: Fraction, hi: Fraction) -> Any:
    model.need(lo <= hi, "Arb interval order")
    return _arb_exact(arb_type, fmpq_type, lo).union(
        _arb_exact(arb_type, fmpq_type, hi))


def _as_real(value: Any, where: str) -> Any:
    if not bool(0 in value.imag):
        raise SplitRequired(f"{where}:IMAGINARY_PART_EXCLUDES_ZERO")
    return value.real


def _canonical(adapter: Any, ball: Any, where: str) -> dict[str, Any]:
    """Canonicalization is also the mandatory explicit Arb finiteness gate."""
    try:
        return adapter.arb_ball_to_canonical_dyadic_interval(ball)
    except adapter.AdapterError as exc:
        raise SplitRequired(f"{where}:NONFINITE") from exc


def _finite_real(adapter: Any, ball: Any, where: str) -> Any:
    _canonical(adapter, ball, where)
    return ball


def _safe_nonnegative_sqrt(adapter: Any, arb_type: Any, fmpq_type: Any,
                           radicand: Any, where: str) -> Any:
    """Enclose sqrt(x) when mathematics proves x>=0.

    Arb midpoint-radius storage can give a ball touching zero a tiny negative
    lower endpoint.  Never call sqrt on that ball.  Canonicalize it, take only
    the rigorous upper endpoint, sqrt that positive exact endpoint, and hull it
    with 0.  The resulting ball may itself extend microscopically below zero,
    but no square root is applied to that hull.
    """
    iv = _canonical(adapter, radicand, f"{where}.radicand")
    _, hi = model.interval_fractions(iv, f"{where}.radicand")
    if hi < 0:
        raise SplitRequired(f"{where}:NEGATIVE_UPPER_ENDPOINT")
    if hi == 0:
        return arb_type(0)
    root_hi = _arb_exact(arb_type, fmpq_type, hi).sqrt()
    _canonical(adapter, root_hi, f"{where}.sqrt_upper")
    out = arb_type(0).union(root_hi)
    _canonical(adapter, out, f"{where}.sqrt_hull")
    return out


def _safe_positive_sqrt(adapter: Any, arb_type: Any, fmpq_type: Any,
                        radicand: Any, floor: Fraction, where: str) -> Any:
    """Enclose sqrt(x) from an independently proved exact floor x>=floor>0."""
    model.need(floor > 0, f"{where}: positive floor")
    iv = _canonical(adapter, radicand, f"{where}.radicand")
    _, hi = model.interval_fractions(iv, f"{where}.radicand")
    model.need(hi >= floor, f"{where}: upper endpoint below proved floor")
    lo_root = _arb_exact(arb_type, fmpq_type, floor).sqrt()
    hi_root = _arb_exact(arb_type, fmpq_type, hi).sqrt()
    out = lo_root.union(hi_root)
    lo_check, _ = model.interval_fractions(
        _canonical(adapter, out, f"{where}.sqrt_positive_hull"), where)
    if lo_check <= 0:
        raise SplitRequired(f"{where}:POSITIVE_SQRT_HULL_LOST_SIGN")
    return out


def _positive_inverse_factors(adapter: Any, arb_type: Any, fmpq_type: Any,
                              q_ball: Any, q_lo: Fraction,
                              where: str) -> tuple[Any, Any, Fraction]:
    """Build 1/q and 1/sqrt(q) from rigorous endpoint bounds, never q*sqrt(q).

    q_lo is independently proved for the current child.  q_hi is taken from a
    canonical outward enclosure of the actual q expression.  Reciprocal
    factors are then built from the exact rational endpoints.
    """
    model.need(q_lo > 0, f"{where}: q_lo positive")
    q_iv = _canonical(adapter, q_ball, f"{where}.q")
    _, q_hi = model.interval_fractions(q_iv, f"{where}.q")
    model.need(q_hi >= q_lo, f"{where}: q_hi >= q_lo")

    inv_q = _arb_interval(arb_type, fmpq_type, Fraction(1, 1) / q_hi,
                          Fraction(1, 1) / q_lo)
    invq_lo, _ = model.interval_fractions(
        _canonical(adapter, inv_q, f"{where}.inv_q"), f"{where}.inv_q")
    if invq_lo <= 0:
        raise SplitRequired(f"{where}:INV_Q_HULL_LOST_POSITIVITY")

    sqrt_hi = _arb_exact(arb_type, fmpq_type, q_hi).sqrt()
    sqrt_lo = _arb_exact(arb_type, fmpq_type, q_lo).sqrt()
    inv_sqrt_q = (arb_type(1) / sqrt_hi).union(arb_type(1) / sqrt_lo)
    invsqrt_lo, _ = model.interval_fractions(
        _canonical(adapter, inv_sqrt_q, f"{where}.inv_sqrt_q"),
        f"{where}.inv_sqrt_q")
    if invsqrt_lo <= 0:
        raise SplitRequired(f"{where}:INV_SQRT_Q_HULL_LOST_POSITIVITY")
    return inv_q, inv_sqrt_q, q_hi


def _r_ball(arb_type: Any, fmpq_type: Any,
            u0: Fraction, u1: Fraction) -> Any:
    return _arb_interval(arb_type, fmpq_type, 1-u1, 1-u0)


def _lambda_ball(arb_type: Any, fmpq_type: Any,
                 s0: Fraction, s1: Fraction) -> Any:
    return (_arb_exact(arb_type, fmpq_type, model.LAMBDA_PLUS)
            + _arb_interval(arb_type, fmpq_type, s0, s1))


def _bhat_lower(eps: Fraction) -> Fraction:
    # sin(t)/t >= cos(eps) >= 1-eps^2/2 on 0<=t<=eps.
    c = 1 - eps*eps/Fraction(2)
    model.need(c > 0, "Bhat cosine lower positive")
    return c*c


def _r2_global_q_lower(eps: Fraction) -> Fraction:
    # W >= 1-cos(eps), and 1-cos(eps)>=eps^2/2-eps^4/24.
    d = eps*eps/Fraction(2) - eps**4/Fraction(24)
    model.need(d > 0, "R2 q lower positive")
    return d*d


def validate_helper_lemmas(arb_type: Any, fmpq_type: Any,
                            config: dict[str, Any]) -> list[dict[str, Any]]:
    """Run-start strict validation of analytic helper inequalities."""
    eps = model.fraction_from_dyadic(config["geometry"]["eps"])
    eps_a = _arb_exact(arb_type, fmpq_type, eps)
    pi = arb_type.pi()
    pi_lo = _arb_exact(arb_type, fmpq_type, Fraction(333,106))
    pi_hi = _arb_exact(arb_type, fmpq_type, Fraction(355,113))
    model.need(bool(pi > pi_lo), "pi lower validation")
    model.need(bool(pi < pi_hi), "pi upper validation")
    cos_residual = eps_a.cos() - _arb_exact(
        arb_type, fmpq_type, 1-eps*eps/Fraction(2))
    model.need(bool(cos_residual >= arb_type(0)), "cos Taylor lower validation")
    bh = _bhat_lower(eps)
    q2 = _r2_global_q_lower(eps)
    return [
        {"lemma_id":"PI_ARCHIMEDEAN_BRACKET_V1",
         "domain":{"constant":"pi"},"precision":config["precision"]["bits"],
         "required_relation":"333/106 < pi < 355/113","status":"PASS"},
        {"lemma_id":"COS_EPS_TAYLOR_LOWER_V1",
         "domain":{"eps":model.dyadic_json(eps)},"precision":config["precision"]["bits"],
         "required_relation":"cos(eps)>=1-eps^2/2","status":"PASS"},
        {"lemma_id":"BHAT_LOWER_V2","domain":{"eps":model.dyadic_json(eps)},
         "precision":config["precision"]["bits"],"bound":model.rational_json(bh),
         "required_relation":"B_hat>=bound","status":"PASS"},
        {"lemma_id":"R2_GLOBAL_Q_LO_V2","domain":{"eps":model.dyadic_json(eps)},
         "precision":config["precision"]["bits"],"bound":model.rational_json(q2),
         "required_relation":"q>=bound on R2","status":"PASS"},
    ]


def _geometry(adapter: Any, arb_type: Any, fmpq_type: Any,
              r: Any, lam: Any, c: Any, phi: Any) -> dict[str, Any]:
    one = arb_type(1)
    # R-1: S^2 is mathematically nonnegative, but its Arb hull may extend a
    # few ulps below zero.  Use upper-endpoint sqrt, never sqrt(S2_ball).
    S2 = one-c*c
    S = _safe_nonnegative_sqrt(adapter, arb_type, fmpq_type, S2, "geometry.S")
    U = S*phi.cos()
    A = (lam*lam-one)*c*c
    B = one-U*U
    W = one-r*U
    q = W*W + A + r*r*B
    w2 = lam*lam*S2+c*c
    # lambda>1 and c in [0,1] imply w^2 >= 1 exactly.
    w = _safe_positive_sqrt(adapter, arb_type, fmpq_type, w2,
                            Fraction(1), "geometry.w")
    L = lam/w
    N = -U*A-r*B
    Nr = U*U-one
    return {"S2":S2,"S":S,"U":U,"A":A,"B":B,"W":W,"q":q,"w":w,
            "L":L,"N":N,"Nr":Nr}


def _fixed_gamma_bins(arb_type: Any) -> tuple[list[Any], list[dict[str, Any]]]:
    half = arb_type(1)/2
    return (
        [arb_type(0).union(half), half.union(arb_type(1))],
        [{"lo":model.dyadic_json(Fraction(0)),"hi":model.dyadic_json(Fraction(1,2))},
         {"lo":model.dyadic_json(Fraction(1,2)),"hi":model.dyadic_json(Fraction(1))}],
    )


def _angle_eval_balls(kernel: Any, adapter: Any, acb_type: Any,
                      balls: list[Any], need_h2: bool,
                      where: str) -> tuple[Any, Any, Any | None]:
    hout=h1out=h2out=None
    for i, gb in enumerate(balls):
        try:
            h,h1,h2=kernel.angle_data(acb_type(gb))
            hr=_finite_real(adapter,_as_real(h,f"{where}.h"),f"{where}.h[{i}]")
            h1r=_finite_real(adapter,_as_real(h1,f"{where}.h1"),f"{where}.h1[{i}]")
            h2r=None
            if need_h2:
                h2r=_finite_real(adapter,_as_real(h2,f"{where}.h2"),f"{where}.h2[{i}]")
        except (ValueError, ArithmeticError) as exc:
            raise SplitRequired("ANGLE_DATA_NONFINITE") from exc
        hout=hr if hout is None else hout.union(hr)
        h1out=h1r if h1out is None else h1out.union(h1r)
        if need_h2:
            assert h2r is not None
            h2out=h2r if h2out is None else h2out.union(h2r)
    assert hout is not None and h1out is not None
    _canonical(adapter,hout,f"{where}.h_hull")
    _canonical(adapter,h1out,f"{where}.h1_hull")
    if need_h2:
        assert h2out is not None
        _canonical(adapter,h2out,f"{where}.h2_hull")
    return hout,h1out,h2out


def _angle_union(kernel: Any, adapter: Any, acb_type: Any, arb_type: Any,
                 gamma: Any, force_bins: bool, need_h2: bool
                 ) -> tuple[Any, Any, Any | None, list[dict[str, Any]]]:
    """Child gamma first; on any nonfinite angle datum, use two exact bins.

    R-4 makes the two-bin fallback available to every angular cell, not only
    Duffy corner children.  A global [0,1] call is still forbidden: fallback
    evaluates the two proper subintervals separately and hulls their outputs.
    """
    bins, split_records = _fixed_gamma_bins(arb_type)
    if force_bins:
        h,h1,h2=_angle_eval_balls(kernel,adapter,acb_type,bins,need_h2,"gamma_bins")
        return h,h1,h2,split_records
    try:
        clipped=gamma.max(arb_type(0)).min(arb_type(1))
        _canonical(adapter,clipped,"child gamma")
        h,h1,h2=_angle_eval_balls(kernel,adapter,acb_type,[clipped],need_h2,"child_gamma")
        return h,h1,h2,[]
    except (SplitRequired, ValueError, ArithmeticError):
        h,h1,h2=_angle_eval_balls(kernel,adapter,acb_type,bins,need_h2,"gamma_bins")
        return h,h1,h2,split_records


def _r2_w_lower(adapter: Any, arb_type: Any, fmpq_type: Any,
                cell: Cell, u0: Fraction, eps: Fraction) -> tuple[Fraction,Fraction]:
    """Certified R2 child W lower bound from r_hi and cos(phi_lo)."""
    pi=arb_type.pi();eps_a=_arb_exact(arb_type,fmpq_type,eps)
    b0=_arb_exact(arb_type,fmpq_type,cell.b0)
    phi_lo=eps_a+(pi-eps_a)*b0
    cos_phi_lo=phi_lo.cos()
    cos_iv=_canonical(adapter,cos_phi_lo,"R2 cos(phi_lo)")
    _,cos_hi=model.interval_fractions(cos_iv,"R2 cos(phi_lo)")
    # U=S*cos(phi), 0<=S<=1.  For negative cosine the maximum U is 0.
    u_hi=max(Fraction(0),min(Fraction(1),cos_hi))
    r_hi=1-u0
    w_lo=1-r_hi*u_hi
    model.need(w_lo>=0,"R2 W lower nonnegative")
    return w_lo,cos_hi


def _regular_q_lo(region: str, cell: Cell, lam_lo: Fraction,
                  eps: Fraction, r2_w_lo: Fraction | None=None) -> Fraction:
    if region == "R1":
        # c = eps + (1-eps)*a. q>=A=(lambda^2-1)c^2.
        c0 = eps+(1-eps)*cell.a0
        return (lam_lo*lam_lo-1)*c0*c0
    # R-3: retain analytic phi>=eps floor and A, and add the child-specific
    # W^2 floor W>=1-r_hi*cos(phi_lo).
    global_lo = _r2_global_q_lower(eps)
    c0 = eps*cell.a0
    a_lo = (lam_lo*lam_lo-1)*c0*c0
    w2_lo = Fraction(0) if r2_w_lo is None else r2_w_lo*r2_w_lo
    return max(global_lo, a_lo, w2_lo)


def _regular_eval(quantity: str, kernel: Any, adapter: Any, acb_type: Any,
                  arb_type: Any, fmpq_type: Any, cell: Cell,
                  u0: Fraction,u1: Fraction,s0: Fraction,s1: Fraction,
                  eps: Fraction) -> tuple[Any,dict[str,Any]]:
    r=_r_ball(arb_type,fmpq_type,u0,u1)
    lam=_lambda_ball(arb_type,fmpq_type,s0,s1)
    lam_lo=model.LAMBDA_PLUS+s0
    pi=arb_type.pi();one=arb_type(1);eps_a=_arb_exact(arb_type,fmpq_type,eps)
    a=_arb_interval(arb_type,fmpq_type,cell.a0,cell.a1)
    b=_arb_interval(arb_type,fmpq_type,cell.b0,cell.b1)
    r2_w_lo=None; r2_cos_hi=None
    if cell.region=="R1":
        c=eps_a+(one-eps_a)*a;phi=pi*b
        measure=(one-eps_a)*pi
    elif cell.region=="R2":
        c=eps_a*a;phi=eps_a+(pi-eps_a)*b
        measure=eps_a*(pi-eps_a)
        r2_w_lo,r2_cos_hi=_r2_w_lower(adapter,arb_type,fmpq_type,cell,u0,eps)
    else:
        raise ValueError("regular region")
    g=_geometry(adapter,arb_type,fmpq_type,r,lam,c,phi)
    qlo=_regular_q_lo(cell.region,cell,lam_lo,eps,r2_w_lo)
    model.need(qlo>0,"per-child q_lo")
    # R-2: never floor an Arb q ball and then divide by that midpoint-radius
    # ball.  Construct reciprocal factors from exact q_hi/q_lo endpoints.
    invq,invsqrtq,qhi=_positive_inverse_factors(
        adapter,arb_type,fmpq_type,g["q"],qlo,f"{cell.region}:{cell.path}")
    gamma=g["L"]*g["W"]*invsqrtq
    h,h1,h2,gsplits=_angle_union(
        kernel,adapter,acb_type,arb_type,gamma,False,quantity=="H_U")
    gamma_r=g["L"]*g["N"]*invq*invsqrtq
    if quantity=="F":
        value=-g["U"]*h + g["W"]*h1*gamma_r
    else:
        # Numerator uses the original q enclosure; only negative powers use
        # endpoint reciprocal factors.
        num=g["Nr"]*g["q"]-arb_type(3)*g["N"]*(r-g["U"])
        gamma_rr=g["L"]*num*invq*invq*invsqrtq
        assert h2 is not None
        K=-arb_type(2)*g["U"]*h1*gamma_r + g["W"]*(h2*gamma_r*gamma_r+h1*gamma_rr)
        value=-K
    area=_arb_exact(arb_type,fmpq_type,(cell.a1-cell.a0)*(cell.b1-cell.b0))
    contribution=value*measure*area
    _canonical(adapter,contribution,"regular contribution")
    detail={
        "q_lo":model.rational_json(qlo),"q_hi":model.rational_json(qhi),
        "q_lo_policy":policy.Q_LO_POLICY_ID,
        "denominator_policy":policy.DENOMINATOR_POLICY_ID,
        "sqrt_policy":policy.SQRT_POLICY_ID,
        "gamma_policy":policy.GAMMA_POLICY_ID,"gamma_subdivisions":gsplits,
        "gamma_fallback_used":bool(gsplits),"measure_identity":policy.MEASURE_ID,
    }
    if cell.region=="R2":
        assert r2_w_lo is not None and r2_cos_hi is not None
        detail["R2_W_LO"]=model.rational_json(r2_w_lo)
        detail["R2_COS_PHI_LO_HI"]=model.rational_json(r2_cos_hi)
    return contribution,detail


def _z_den_lo(triangle: str, cell: Cell, u1: Fraction, s0: Fraction,
              eps: Fraction) -> Fraction:
    lam_lo=model.LAMBDA_PLUS+s0;r_lo=1-u1;bh=_bhat_lower(eps)
    model.need(lam_lo>1 and r_lo>0,"strip parameters")
    if triangle=="T1":
        ah=(lam_lo*lam_lo-1)/(1+cell.b1*cell.b1)
    elif triangle=="T2":
        ah=(lam_lo*lam_lo-1)*cell.b0*cell.b0/(1+cell.b0*cell.b0)
    else:
        raise ValueError("triangle")
    out=ah+r_lo*r_lo*bh
    model.need(out>0,"Z_DEN_LO")
    return out


def _duffy_eval(quantity: str, kernel: Any, adapter: Any, acb_type: Any,
                arb_type: Any, fmpq_type: Any, cell: Cell,
                u0: Fraction,u1: Fraction,s0: Fraction,s1: Fraction,
                eps: Fraction) -> tuple[Any,dict[str,Any]]:
    r=_r_ball(arb_type,fmpq_type,u0,u1);lam=_lambda_ball(arb_type,fmpq_type,s0,s1)
    x=_arb_interval(arb_type,fmpq_type,cell.a0,cell.a1)
    yd=_arb_interval(arb_type,fmpq_type,cell.b0,cell.b1)
    eps_a=_arb_exact(arb_type,fmpq_type,eps);one=arb_type(1)
    if cell.region=="T1":
        c=eps_a*x;phi=eps_a*x*yd;Ahat=(lam*lam-one)/(one+yd*yd)
    elif cell.region=="T2":
        phi=eps_a*x;c=eps_a*x*yd;Ahat=(lam*lam-one)*yd*yd/(one+yd*yd)
    else:
        raise ValueError("Duffy region")
    S2=one-c*c
    S=_safe_nonnegative_sqrt(adapter,arb_type,fmpq_type,S2,"Duffy.S")
    U=S*phi.cos()
    w2=lam*lam*S2+c*c
    w=_safe_positive_sqrt(adapter,arb_type,fmpq_type,w2,Fraction(1),"Duffy.w")
    L=lam/w
    bh_lo=_bhat_lower(eps);Bhat=_arb_interval(arb_type,fmpq_type,bh_lo,Fraction(1))
    M=U*Ahat+r*Bhat
    zden=_z_den_lo(cell.region,cell,u1,s0,eps)
    z_hi=arb_type(1)/_arb_exact(arb_type,fmpq_type,zden).sqrt()
    _canonical(adapter,z_hi,"Duffy z_hi")
    corner=(cell.a0==0)
    gy=_safe_positive_sqrt(adapter,arb_type,fmpq_type,one+yd*yd,Fraction(1),"Duffy.g")
    rho=eps_a*x*gy
    q_hi_record=None
    if corner:
        yh=arb_type(0).union(arb_type(1));v=arb_type(-1).union(arb_type(1));z=arb_type(0).union(z_hi)
        gamma=arb_type(0).union(arb_type(1))
    else:
        g=_geometry(adapter,arb_type,fmpq_type,r,lam,c,phi)
        # q >= rho^2 * Z_DEN_LO.  On a non-corner child x>=a0>0,
        # rho^2 >= eps^2*a0^2*(1+b0^2), an exact rational child floor.
        rho2_lo=eps*eps*cell.a0*cell.a0*(1+cell.b0*cell.b0)
        qlo=rho2_lo*zden
        invq,invsqrtq,qhi=_positive_inverse_factors(
            adapter,arb_type,fmpq_type,g["q"],qlo,f"{cell.region}:{cell.path}:Duffy")
        del invq
        q_hi_record=model.rational_json(qhi)
        yh=(g["W"]*invsqrtq).max(arb_type(0)).min(arb_type(1))
        v=(r-U)*invsqrtq
        z=(rho*invsqrtq).max(arb_type(0)).min(z_hi)
        gamma=(L*yh).max(arb_type(0)).min(arb_type(1))
    h,h1,h2,gsplits=_angle_union(
        kernel,adapter,acb_type,arb_type,gamma,corner,quantity=="H_U")
    if quantity=="F":
        JF=rho*(-U*h-L*h1*M*yh*z*z)
        transformed=eps_a*JF/gy
    else:
        assert h2 is not None
        J=L*(arb_type(2)*U*h1*M*z**3
             +L*h2*M*M*yh*z**5
             +h1*(-Bhat*yh*rho*z**2+arb_type(3)*M*yh*v*z**3))
        transformed=-eps_a*J/gy
    area=_arb_exact(arb_type,fmpq_type,(cell.a1-cell.a0)*(cell.b1-cell.b0))
    contribution=transformed*area
    _canonical(adapter,contribution,"Duffy contribution")
    detail={
        "Z_DEN_LO":model.rational_json(zden),"helper_lemma_id":"BHAT_LOWER_V2",
        "gamma_policy":policy.GAMMA_POLICY_ID,"gamma_subdivisions":gsplits,
        "gamma_fallback_used":bool(gsplits),"sqrt_policy":policy.SQRT_POLICY_ID,
        "bounded_extensions":{"y_h":"[0,1]" if corner else "CHILD_DIRECT",
                              "v":"[-1,1]" if corner else "CHILD_DIRECT",
                              "z":"[0,1/sqrt(Z_DEN_LO)]" if corner else "CHILD_DIRECT"},
        "duffy_id":policy.DUFFY_ID,"measure_identity":policy.MEASURE_ID,
        "triangle_substitution":cell.region,
    }
    if not corner:
        detail["denominator_policy"]=policy.DENOMINATOR_POLICY_ID
        detail["q_hi"]=q_hi_record
    return contribution,detail


def _cell_eval(quantity: str, kernel: Any, adapter: Any, acb_type: Any,
               arb_type: Any, fmpq_type: Any, cell: Cell,
               u0: Fraction,u1: Fraction,s0: Fraction,s1: Fraction,
               eps: Fraction) -> tuple[Any,dict[str,Any]]:
    if cell.region in ("T1","T2"):
        return _duffy_eval(quantity,kernel,adapter,acb_type,arb_type,fmpq_type,
                           cell,u0,u1,s0,s1,eps)
    return _regular_eval(quantity,kernel,adapter,acb_type,arb_type,fmpq_type,
                         cell,u0,u1,s0,s1,eps)


def _split(cell: Cell) -> list[Cell]:
    boxes=policy.split_box(cell.a0,cell.a1,cell.b0,cell.b1,cell.depth)
    return [Cell(cell.region,cell.path+str(i),cell.depth+1,*box)
            for i,box in enumerate(boxes)]


def _cover_ok(leaves: list[Cell], region: str) -> bool:
    selected=[c for c in leaves if c.region==region]
    area=sum((c.a1-c.a0)*(c.b1-c.b0) for c in selected)
    if area!=1:
        return False
    for i,c in enumerate(selected):
        for d in selected[:i]:
            if max(c.a0,d.a0)<min(c.a1,d.a1) and max(c.b0,d.b0)<min(c.b1,d.b1):
                return False
    return True


def _root_initial() -> list[Cell]:
    return [Cell(r,r,0,Fraction(0),Fraction(1),Fraction(0),Fraction(1))
            for r in ("T1","T2","R1","R2")]


def _proof_id(obj: dict[str,Any]) -> str:
    return model.sha256_bytes(model.canonical_json_bytes(obj))


def enclose_route(quantity: str, kernel: Any, adapter: Any, acb_type: Any,
                  arb_type: Any, fmpq_type: Any, config: dict[str,Any],
                  u0: Fraction,u1: Fraction,s0: Fraction,s1: Fraction,
                  required_sign: str | None = None) -> tuple[dict[str,Any],dict[str,Any]]:
    """Return canonical normalized enclosure and a reconstructible adaptive proof."""
    model.need(quantity in {"F","H_U"},"route quantity")
    model.need(Fraction(0)<=u0<=u1<=Fraction(1,4),"route u")
    model.need(-model.S_NEG<=s0<=s1,"route s")
    pkey="F_ROUTE" if quantity=="F" else "K_ROUTE";pcfg=config["route_policies"][pkey]
    eps=model.fraction_from_dyadic(config["geometry"]["eps"])
    leaves=_root_initial();evaluations=0
    values:dict[str,Any]={};meta:dict[str,dict[str,Any]]={};split_reasons:dict[str,str]={}

    def eval_one(cell: Cell) -> None:
        nonlocal evaluations
        model.need(evaluations < pcfg["max_evaluations"], "angular evaluation budget")
        value,detail=_cell_eval(quantity,kernel,adapter,acb_type,arb_type,fmpq_type,
                                cell,u0,u1,s0,s1,eps)
        evaluations+=1;values[cell.path]=value;meta[cell.path]=detail

    while True:
        forced=None
        for cell in sorted(leaves,key=lambda c:(policy.REGION_ORDER[c.region],c.path)):
            if cell.path not in values:
                try:
                    eval_one(cell)
                except SplitRequired as exc:
                    forced=(cell,exc.reason);break
        if forced is not None:
            cell,reason=forced
            model.need(cell.depth<pcfg["max_depth"], f"angular depth: {reason}")
            model.need(len(leaves)+1<=pcfg["max_children"], "angular child budget")
            leaves.remove(cell);values.pop(cell.path,None);meta.pop(cell.path,None)
            leaves.extend(_split(cell));split_reasons[cell.path]=reason
            continue
        shallow=next((c for c in sorted(leaves,key=lambda c:(policy.REGION_ORDER[c.region],c.path))
                      if c.depth<pcfg["min_depth"]),None)
        if shallow is not None:
            model.need(len(leaves)+1<=pcfg["max_children"],"angular child budget min depth")
            leaves.remove(shallow);values.pop(shallow.path,None);meta.pop(shallow.path,None)
            leaves.extend(_split(shallow));split_reasons[shallow.path]="MIN_DEPTH"
            continue
        child_intervals=[_canonical(adapter,values[c.path],"accepted child")
                         for c in sorted(leaves,key=lambda c:(policy.REGION_ORDER[c.region],c.path))]
        ulo,uhi=model.interval_add_exact(child_intervals)
        unnorm=model.outward_dyadic(ulo,uhi);normalized=model.normalize_interval(unnorm)
        lo,hi=model.interval_fractions(normalized,"root normalized")
        resolved=(required_sign is None or (required_sign=="POS" and lo>0)
                  or (required_sign=="NEG" and hi<0))
        if resolved:
            break
        candidates=[c for c in leaves if c.depth<pcfg["max_depth"]]
        model.need(candidates,"angular sign unresolved at depth limit")
        model.need(len(leaves)+1<=pcfg["max_children"],"angular sign child budget")
        def width_key(c:Cell)->tuple[Fraction,int,str]:
            iv=_canonical(adapter,values[c.path],"width")
            a,b=model.interval_fractions(iv,"width")
            return (b-a,-policy.REGION_ORDER[c.region],c.path)
        chosen=max(candidates,key=width_key)
        leaves.remove(chosen);values.pop(chosen.path,None);meta.pop(chosen.path,None)
        leaves.extend(_split(chosen));split_reasons[chosen.path]="ROOT_SIGN_UNRESOLVED"

    model.need(all(_cover_ok(leaves,r) for r in ("T1","T2","R1","R2")),"exact angular cover")
    ordered=sorted(leaves,key=lambda c:(policy.REGION_ORDER[c.region],c.path))
    child_records=[]
    for c in ordered:
        iv=_canonical(adapter,values[c.path],"final child")
        child_records.append({
            "child_id":c.path,"parent_id":c.path[:-1] if len(c.path)>2 else None,
            "region":c.region,"depth":c.depth,"box":{
                "a":model.interval_json(c.a0,c.a1),"b":model.interval_json(c.b0,c.b1)},
            "source_coordinates":"(x,y_D)" if c.region in ("T1","T2") else "NORMALIZED_SOURCE_BOX",
            "detail":meta[c.path],"contribution_enclosure":iv,"status":"ACCEPTED",
        })
    ulo,uhi=model.interval_add_exact([r["contribution_enclosure"] for r in child_records])
    unnormalized=model.outward_dyadic(ulo,uhi);normalized=model.normalize_interval(unnormalized)
    route_id=F_ROUTE_ID if quantity=="F" else K_ROUTE_ID
    body={
        "route_id":route_id,"quantity":quantity,"angular_policy_id":policy.ANGULAR_POLICY_ID,
        "policy":pcfg,"denominator_policy_id":policy.DENOMINATOR_POLICY_ID,
        "sqrt_policy_id":policy.SQRT_POLICY_ID,
        "gamma_policy_id":policy.GAMMA_POLICY_ID,"q_lo_policy_id":policy.Q_LO_POLICY_ID,
        "normalization_policy_id":policy.NORMALIZATION_POLICY_ID,
        "one_over_pi_enclosure":{"lo":model.rational_json(model.ONE_OVER_PI_LO),
                                 "hi":model.rational_json(model.ONE_OVER_PI_HI)},
        "normalization_bits":model.NORMALIZATION_BITS,
        "u_interval":model.interval_json(u0,u1),"s_interval":model.interval_json(s0,s1),
        "eps":config["geometry"]["eps"],"patch_type":model.PATCH_TYPE,
        "ordered_children":child_records,"split_reasons":split_reasons,
        "evaluation_count":evaluations,"unnormalized_sum":unnormalized,
        "normalized_enclosure":normalized,"complete_closed_cover":True,
        "direct_pinned_integrator_called":False,
    }
    body["proof_id"]=_proof_id(body)
    return normalized,body


def enclose_hu(kernel: Any,adapter: Any,acb_type:Any,arb_type:Any,fmpq_type:Any,
               config:dict[str,Any],u0:Fraction,u1:Fraction,s0:Fraction,s1:Fraction,
               required_sign: str | None="POS") -> tuple[dict[str,Any],dict[str,Any]]:
    return enclose_route("H_U",kernel,adapter,acb_type,arb_type,fmpq_type,
                         config,u0,u1,s0,s1,required_sign)


def enclose_f(kernel: Any,adapter: Any,acb_type:Any,arb_type:Any,fmpq_type:Any,
              config:dict[str,Any],r0:Fraction,r1:Fraction,lam0:Fraction,lam1:Fraction,
              required_sign: str | None=None) -> tuple[dict[str,Any],dict[str,Any]]:
    model.need(r0<=r1,"F r order");model.need(lam0<=lam1,"F lambda order")
    u0,u1=1-r1,1-r0;s0,s1=lam0-model.LAMBDA_PLUS,lam1-model.LAMBDA_PLUS
    return enclose_route("F",kernel,adapter,acb_type,arb_type,fmpq_type,
                         config,u0,u1,s0,s1,required_sign)
