#!/usr/bin/env python3
"""Finite cancellation-free F/K angular routes for all B-LOCAL v2.2 consumers.

READINESS DRAFT v2.  Direct pinned F_arb/dFdr_arb are formula provenance only
and are never called by this module.  All proof evaluation uses exact domain
partitions, Duffy corner regularization, per-child gamma/denominator data,
endpoint-safe square roots, exact-endpoint reciprocal denominator factors, and
a deterministic adaptive ball sum.
"""
from __future__ import annotations

import hashlib
import heapq
import json
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Callable

import blocal_v22_model as model
import blocal_v22_policy as policy

F_ROUTE_ID = policy.F_ROUTE_ID
K_ROUTE_ID = policy.K_ROUTE_ID
HELPER_VALIDATION_ID = policy.HELPER_VALIDATION_ID
METHOD_SELECTION_ADDENDUM_SHA256 = "7fafe5f465f9f38e61831b804a4bc95090af41b8fe31347897e7b2f40bf3d316"
C1_FLOOR_SPEC_SHA256 = "8492755d298ace4c09f5118993eb2f2fa968d55ae5d04b81ff20c2c856fc90d3"
HALF = Fraction(1, 2)
PI_LO = Fraction(333, 106)
PI_HI = Fraction(355, 113)


@dataclass(frozen=True)
class J2:
    v: Any
    ga: Any
    gb: Any
    haa: Any
    hab: Any
    hbb: Any

    def __add__(self, other: Any) -> "J2":
        o = _as_jet(other, self.v)
        return J2(self.v+o.v, self.ga+o.ga, self.gb+o.gb,
                  self.haa+o.haa, self.hab+o.hab, self.hbb+o.hbb)
    __radd__ = __add__
    def __neg__(self) -> "J2":
        return J2(-self.v, -self.ga, -self.gb, -self.haa, -self.hab, -self.hbb)
    def __sub__(self, other: Any) -> "J2": return self+(-_as_jet(other, self.v))
    def __rsub__(self, other: Any) -> "J2": return _as_jet(other, self.v)-self
    def __mul__(self, other: Any) -> "J2":
        o = _as_jet(other, self.v)
        return J2(self.v*o.v,
                  self.ga*o.v+self.v*o.ga,
                  self.gb*o.v+self.v*o.gb,
                  self.haa*o.v+2*self.ga*o.ga+self.v*o.haa,
                  self.hab*o.v+self.ga*o.gb+self.gb*o.ga+self.v*o.hab,
                  self.hbb*o.v+2*self.gb*o.gb+self.v*o.hbb)
    __rmul__ = __mul__
    def __truediv__(self, other: Any) -> "J2": return self*_jinv(_as_jet(other, self.v))
    def __rtruediv__(self, other: Any) -> "J2": return _as_jet(other, self.v)*_jinv(self)
    def __pow__(self, n: int) -> "J2":
        if n == 0: return _as_jet(1, self.v)
        if n < 0: return _jinv(self**(-n))
        out=None;base=self;k=n
        while k:
            if k & 1: out=base if out is None else out*base
            base=base*base;k >>= 1
        assert out is not None
        return out


class SplitRequired(RuntimeError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class EnclosureFailure(RuntimeError):
    def __init__(self, reason:str, evaluations:int):
        super().__init__(reason);self.reason=reason;self.evaluations=evaluations


@dataclass(frozen=True)
class _WidthEntry:
    width: Fraction
    neg_region_order: int
    path: str

    def __lt__(self, other: "_WidthEntry") -> bool:
        # heapq is a min-heap; reverse the complete historical max() key.
        return (self.width,self.neg_region_order,self.path) > (
            other.width,other.neg_region_order,other.path)


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


def _as_jet(x: Any, like: Any) -> J2:
    if isinstance(x, J2): return x
    z=like*0
    return J2(x,z,z,z,z,z)


def _jvar(v: Any, axis: int) -> J2:
    z=v*0;one=z+1
    return J2(v,one if axis==0 else z,one if axis==1 else z,z,z,z)


def _junary(x: J2, f0: Any, f1: Any, f2: Any) -> J2:
    return J2(f0,f1*x.ga,f1*x.gb,
              f2*x.ga*x.ga+f1*x.haa,
              f2*x.ga*x.gb+f1*x.hab,
              f2*x.gb*x.gb+f1*x.hbb)


def _jet_fracs(adapter: Any, x: Any, where: str) -> tuple[Fraction,Fraction]:
    return model.interval_fractions(_canonical(adapter,x,where),where)


def _jinv(x: J2) -> J2:
    # Adapter-independent finiteness is checked by Arb arithmetic here and at
    # every enclosing call site; zero-containing denominators fail closed.
    if bool(0 in x.v): raise SplitRequired("JINV_DENOM_CONTAINS_ZERO")
    f0=1/x.v;f1=-1/(x.v*x.v);f2=2/(x.v*x.v*x.v)
    return _junary(x,f0,f1,f2)


def _jsin(x: J2) -> J2:
    s=x.v.sin();c=x.v.cos();return _junary(x,s,c,-s)


def _jcos(x: J2) -> J2:
    s=x.v.sin();c=x.v.cos();return _junary(x,c,-s,-c)


def _half_power_at(arb_type: Any, fmpq_type: Any, q: Fraction, odd: int) -> Any:
    model.need(q>0 and odd>=1 and odd%2==1,"half power")
    qa=_arb_exact(arb_type,fmpq_type,q);inv=arb_type(1)/qa;out=arb_type(1)/qa.sqrt()
    for _ in range((odd-1)//2): out*=inv
    return out


def _qpow(adapter: Any, arb_type: Any, fmpq_type: Any,
          x: J2, floor: Fraction, odd: int, where: str) -> J2:
    model.need(floor>0,where+": floor")
    _,hi=_jet_fracs(adapter,x.v,where+".x");model.need(hi>=floor,where+": hi")
    a0=_half_power_at(arb_type,fmpq_type,hi,odd);b0=_half_power_at(arb_type,fmpq_type,floor,odd)
    f0=a0.union(b0);coef1=-arb_type(odd)/2
    f1=(coef1*_half_power_at(arb_type,fmpq_type,hi,odd+2)).union(
       coef1*_half_power_at(arb_type,fmpq_type,floor,odd+2))
    coef2=_arb_exact(arb_type,fmpq_type,Fraction(odd*(odd+2),4))
    f2=(coef2*_half_power_at(arb_type,fmpq_type,hi,odd+4)).union(
       coef2*_half_power_at(arb_type,fmpq_type,floor,odd+4))
    for i,v in enumerate((f0,f1,f2)): _canonical(adapter,v,f"{where}.f{i}")
    return _junary(x,f0,f1,f2)


def _jsqrt(adapter: Any, arb_type: Any, fmpq_type: Any,
           x: J2, floor: Fraction, where: str) -> J2:
    model.need(floor>0,where+": floor")
    _,hi=_jet_fracs(adapter,x.v,where+".x");model.need(hi>=floor,where+": hi")
    vlo=_arb_exact(arb_type,fmpq_type,floor).sqrt();vhi=_arb_exact(arb_type,fmpq_type,hi).sqrt()
    f0=vlo.union(vhi);inv=(arb_type(1)/vhi).union(arb_type(1)/vlo);f1=inv/2
    p3a=(arb_type(1)/_arb_exact(arb_type,fmpq_type,floor))*(arb_type(1)/vlo)
    p3b=(arb_type(1)/_arb_exact(arb_type,fmpq_type,hi))*(arb_type(1)/vhi)
    f2=-(p3a.union(p3b))/4
    for i,v in enumerate((f0,f1,f2)): _canonical(adapter,v,f"{where}.f{i}")
    return _junary(x,f0,f1,f2)


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


_FLOOR_REGISTRY:dict[str,dict[str,Any]]={}
_FLOOR_USE:dict[str,int]={}
_C1_STRUCTURAL_USES=0
_FLOOR_SITE_COUNTS={s:{"calls":0,"natural":0,"structural":0} for s in policy.EFFECTIVE_FLOOR_SITES}
_GAMMA_TRACE:dict[str,dict[str,Any]]={}


def _reset_floor_trace()->None:
    global _C1_STRUCTURAL_USES
    _FLOOR_REGISTRY.clear();_FLOOR_USE.clear();_C1_STRUCTURAL_USES=0
    for s in _FLOOR_SITE_COUNTS:_FLOOR_SITE_COUNTS[s]={"calls":0,"natural":0,"structural":0}


def _reset_gamma_trace()->None:_GAMMA_TRACE.clear()


def _record_gamma(rows:list[dict[str,Any]])->None:
    for row in rows:
        base={k:v for k,v in row.items() if k!="use_count"}
        dig=hashlib.sha256(model.canonical_json_bytes(base)).hexdigest()
        if dig not in _GAMMA_TRACE:_GAMMA_TRACE[dig]=base|{"use_count":row.get("use_count",1)}
        else:_GAMMA_TRACE[dig]["use_count"]+=row.get("use_count",1)


def _intern_floor(rec:dict[str,Any])->str:
    global _C1_STRUCTURAL_USES
    dig=hashlib.sha256(model.canonical_json_bytes(rec)).hexdigest()
    prior=_FLOOR_REGISTRY.get(dig)
    if prior is not None:model.need(prior==rec,"floor record hash collision")
    _FLOOR_REGISTRY[dig]=rec;_FLOOR_USE[dig]=_FLOOR_USE.get(dig,0)+1;_C1_STRUCTURAL_USES+=int(rec.get("site")=="C1_STRUCTURAL_Q")
    return dig


def _natural_lower(adapter:Any,x:Any,where:str)->tuple[Fraction|None,str|None]:
    try:
        lo,_=model.interval_fractions(_canonical(adapter,x,where),where)
        if lo<=0:return None,"NATURAL_LOWER_NONPOSITIVE"
        return lo,None
    except Exception as exc:return None,"NATURAL_LOWER_UNAVAILABLE:"+type(exc).__name__


def _effective_floor(adapter:Any,site:str,structural:Fraction,x:Any,where:str,
                     region:str,scope:str,cell:Cell)->tuple[Fraction,str]:
    model.need(site in policy.EFFECTIVE_FLOOR_SITES,"enumerated floor site")
    model.need(structural>=0,"structural floor nonnegative")
    natural,reason=_natural_lower(adapter,x,where+".natural")
    if natural is None:effective=structural;source="structural"
    else:effective=max(structural,natural);source="natural" if natural>structural else "structural"
    _FLOOR_SITE_COUNTS[site]["calls"]+=1;_FLOOR_SITE_COUNTS[site][source]+=1
    rec={"site":site,"chart":region,"scope":scope,"path":cell.path,
         "structural":model.rational_json(structural),
         "natural":None if natural is None else model.rational_json(natural),
         "effective":model.rational_json(effective),"selected_source":source,
         "fallback_reason":reason,"shared_by":["f0","f1","f2"]}
    return effective,_intern_floor(rec)


def _floor_summary()->dict[str,Any]:
    ordered={k:_FLOOR_REGISTRY[k] for k in sorted(_FLOOR_REGISTRY)};keys=sorted(ordered);limit=64
    return {"call_sites":list(policy.EFFECTIVE_FLOOR_SITES),"unique_count":len(keys),
            "total_use_count":sum(_FLOOR_USE.values()),
            "c1_structural_uses":_C1_STRUCTURAL_USES,
            "canonical_sha256":hashlib.sha256(model.canonical_json_bytes(ordered)).hexdigest(),
            "retained_limit":limit,"retained":{k:ordered[k] for k in keys[:limit]},
            "truncated":len(keys)>limit,"omitted_count":max(0,len(keys)-limit),
            "per_site":{k:dict(_FLOOR_SITE_COUNTS[k]) for k in policy.EFFECTIVE_FLOOR_SITES}}


def _endpoint_ball(arb_type:Any,b:Fraction)->Any:
    return (arb_type(PI_LO.numerator)/PI_LO.denominator*(arb_type(b.numerator)/b.denominator)).union(
        arb_type(PI_HI.numerator)/PI_HI.denominator*(arb_type(b.numerator)/b.denominator))


def _c1_floor(adapter:Any,arb_type:Any,fmpq_type:Any,cell:Cell,r:J2,s0:Fraction,
              eps:Fraction)->tuple[Fraction,Fraction,str,dict[str,Any]]:
    c0=eps+(HALF-eps)*cell.a0;c1=eps+(HALF-eps)*cell.a1
    lamlo=model.LAMBDA_PLUS+s0;A=(lamlo*lamlo-1)*c0*c0;model.need(A>0,"C1 A floor")
    rlo,rhi=_jet_fracs(adapter,r.v,"C1.r");dropped=[];W2=RB=Fraction(0);u_max=None;r_endpoint=None
    try:
        _,chi=model.interval_fractions(_canonical(adapter,_endpoint_ball(arb_type,cell.b0).cos(),"C1.cos"),"C1.cos")
        cmax=min(chi,Fraction(1));Slo=max(Fraction(0),1-c1*c1);u_max=cmax if cmax>=0 else Slo*cmax
        ruse=rhi if u_max>=0 else rlo;r_endpoint="r_hi" if u_max>=0 else "r_lo"
        Wlo=1-ruse*u_max;W2=max(Fraction(0),Wlo)**2
    except Exception as exc:dropped.append("W2_lo:"+type(exc).__name__)
    try:
        sl,_=model.interval_fractions(_canonical(adapter,_endpoint_ball(arb_type,cell.b0).sin(),"C1.sin0"),"C1.sin0")
        sr,_=model.interval_fractions(_canonical(adapter,_endpoint_ball(arb_type,cell.b1).sin(),"C1.sin1"),"C1.sin1")
        sinmin=max(Fraction(0),min(sl,sr))
        if cell.b0<HALF<cell.b1:cos2=Fraction(0)
        elif cell.b1<=HALF:
            m,_=model.interval_fractions(_canonical(adapter,_endpoint_ball(arb_type,cell.b1).cos(),"C1.cos1"),"C1.cos1");cos2=max(Fraction(0),m)**2
        else:
            _,m=model.interval_fractions(_canonical(adapter,_endpoint_ball(arb_type,cell.b0).cos(),"C1.cos0n"),"C1.cos0n");cos2=max(Fraction(0),-m)**2
        RB=rlo*rlo*max(Fraction(0),sinmin*sinmin+c0*c0*cos2)
    except Exception as exc:dropped.append("RB_lo:"+type(exc).__name__)
    qfloor=A+W2+RB;model.need(qfloor>0,"C1 q floor")
    S2=max(Fraction(3,4),1-c1*c1)
    rec={"region":"C1","path":cell.path,"depth":cell.depth,"A_lo":model.rational_json(A),
         "W2_lo":model.rational_json(W2),"RB_lo":model.rational_json(RB),
         "component_dropped":dropped,"U_max":None if u_max is None else model.rational_json(u_max),
         "r_endpoint":r_endpoint,"S2_floor":model.rational_json(S2),"q_floor":model.rational_json(qfloor)}
    return qfloor,S2,_intern_floor({"site":"C1_STRUCTURAL_Q","record":rec}),rec


def _angle4_one(adapter: Any, acb_type: Any, arb_type: Any,
                gamma: Any, where: str) -> tuple[Any,Any,Any,Any,Any]:
    c=acb_type(gamma);one=acb_type(1);z=(one-c)/2
    H=z.hypgeom_2f1(one/2,one/2,acb_type(3)/2);h=4*z*H*H;x=-h/4
    S=x.hypgeom_0f1(acb_type(3)/2);T=x.hypgeom_0f1(acb_type(5)/2)
    V=x.hypgeom_0f1(acb_type(7)/2);Q=x.hypgeom_0f1(acb_type(9)/2)
    h1=-2/S;h2=(acb_type(2)/3)*T/S**3
    B=(acb_type(4)/15)*V/S**3-(acb_type(4)/3)*T*T/S**4
    h3=(-h1/4)*B
    Bx=(acb_type(8)/105)*Q/S**3-(acb_type(8)/5)*T*V/S**4+(acb_type(32)/9)*T**3/S**5
    h4=(-h2/4)*B+(h1*h1/16)*Bx
    return tuple(_finite_real(adapter,_as_real(v,f"{where}.h{k}"),f"{where}.h{k}")
                 for k,v in enumerate((h,h1,h2,h3,h4)))  # type: ignore[return-value]


def _angle4_adaptive(adapter: Any, acb_type: Any, arb_type: Any,
                     gamma: Any, max_bin_depth: int, where: str
                     ) -> tuple[tuple[Any,Any,Any,Any,Any],list[dict[str,Any]]]:
    clipped=gamma.max(arb_type(0)).min(arb_type(1))
    lo,hi=model.interval_fractions(_canonical(adapter,clipped,where+".clamp"),where+".clamp")
    leaves:list[tuple[Fraction,Fraction,int,tuple[Any,Any,Any,Any,Any]]]=[]
    def ball(a:Fraction,b:Fraction)->Any:
        return (arb_type(a.numerator)/a.denominator).union(arb_type(b.numerator)/b.denominator)
    def rec2(a:Fraction,b:Fraction,depth:int)->None:
        try: leaves.append((a,b,depth,_angle4_one(adapter,acb_type,arb_type,ball(a,b),f"{where}.bin.{depth}")))
        except Exception as exc:
            if depth>=max_bin_depth or a==b: raise SplitRequired("ANGLE4_ADAPTIVE_BIN_DEPTH") from exc
            m=(a+b)/2;rec2(a,m,depth+1);rec2(m,b,depth+1)
    rec2(lo,hi,0)
    out=[None]*5
    for *_,vals in leaves:
        for i,v in enumerate(vals): out[i]=v if out[i] is None else out[i].union(v)
    cuts=[leaves[0][0]]+[x[1] for x in leaves]
    records=[{"initial_interval":model.interval_json(lo,hi),
        "cuts":[model.rational_json(x) for x in cuts],"bin_count":len(leaves),
        "max_bin_depth":max(x[2] for x in leaves),"use_count":1}]
    return (out[0],out[1],out[2],out[3],out[4]),records


def _angle_union(kernel: Any, adapter: Any, acb_type: Any, arb_type: Any,
                 gamma: Any, force_bins: bool, need_h2: bool,
                 max_bin_depth: int = 12
                 ) -> tuple[Any, Any, Any | None, list[dict[str, Any]]]:
    """Deterministic midpoint subdivision until h..h'''' are finite."""
    del kernel,force_bins,need_h2
    hs,records=_angle4_adaptive(adapter,acb_type,arb_type,gamma,max_bin_depth,"gamma")
    return hs[0],hs[1],hs[2],records


def _hcompose(kernel: Any, adapter: Any, acb_type: Any, arb_type: Any,
              gamma: J2, which: int, where: str, max_bin_depth: int) -> J2:
    hs,records=_angle4_adaptive(adapter,acb_type,arb_type,gamma.v,max_bin_depth,where)
    _record_gamma(records)
    if which==0:f0,f1,f2=hs[0],hs[1],hs[2]
    elif which==1:f0,f1,f2=hs[1],hs[2],hs[3]
    elif which==2:f0,f1,f2=hs[2],hs[3],hs[4]
    else:raise ValueError(which)
    del records
    return _junary(gamma,f0,f1,f2)


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


def _chart_q_floor(adapter:Any,arb_type:Any,fmpq_type:Any,region:str,cell:Cell,
                   u0:Fraction,s0:Fraction,eps:Fraction)->Fraction:
    lamlo=model.LAMBDA_PLUS+s0;coef=lamlo*lamlo-1;model.need(coef>0,"lambda coefficient")
    if region=="TH":return coef/Fraction(4)
    if region=="R2":
        wlo,_=_r2_w_lower(adapter,arb_type,fmpq_type,cell,u0,eps)
        return _regular_q_lo("R2",cell,lamlo,eps,wlo)
    raise ValueError(region)


def _geometry_jet(quantity:str,kernel:Any,adapter:Any,acb_type:Any,arb_type:Any,
                  fmpq_type:Any,region:str,a:J2,b:J2,r:J2,lam:J2,cell:Cell,
                  u0:Fraction,s0:Fraction,eps:Fraction,scope:str,max_gamma_depth:int
                  )->tuple[J2,dict[str,Any]]:
    pi=arb_type.pi();ea=_arb_exact(arb_type,fmpq_type,eps);ids=[];c1dig=None;c1rec=None
    if region=="C1":
        c=ea+_arb_exact(arb_type,fmpq_type,HALF-eps)*a;phi=pi*b
        qstruct,Sstruct,c1dig,c1rec=_c1_floor(adapter,arb_type,fmpq_type,cell,r,s0,eps)
        S2=1-c*c;Sfloor,Sdig=_effective_floor(adapter,"ORDINARY_S2",Sstruct,S2.v,
            "C1.S2",region,scope,cell);S=_jsqrt(adapter,arb_type,fmpq_type,S2,Sfloor,"C1.S")
        density=_as_jet(arb_type(1),a.v);ids.append(Sdig)
    elif region=="TH":
        theta=(pi/3)*a;phi=pi*b;S=_jsin(theta);c=_jcos(theta);density=S
        qstruct=_chart_q_floor(adapter,arb_type,fmpq_type,region,cell,u0,s0,eps)
    elif region=="R2":
        c=ea*a;phi=ea+(pi-ea)*b;S2=1-c*c
        Sfloor,Sdig=_effective_floor(adapter,"ORDINARY_S2",1-eps*eps,S2.v,
            "R2.S2",region,scope,cell);S=_jsqrt(adapter,arb_type,fmpq_type,S2,Sfloor,"R2.S")
        density=_as_jet(arb_type(1),a.v);ids.append(Sdig)
        qstruct=_chart_q_floor(adapter,arb_type,fmpq_type,region,cell,u0,s0,eps)
    else:raise ValueError(region)
    U=S*_jcos(phi);A=(lam*lam-1)*c*c;B=1-U*U;W=1-r*U;q=W*W+A+r*r*B
    w2=lam*lam*S*S+c*c
    wfloor,Wdig=_effective_floor(adapter,"ORDINARY_W2",Fraction(1),w2.v,
        region+".w2",region,scope,cell);L=lam*_qpow(adapter,arb_type,fmpq_type,w2,wfloor,1,region+".w2");ids.append(Wdig)
    qfloor,Qdig=_effective_floor(adapter,"ORDINARY_Q",qstruct,q.v,
        region+".q",region,scope,cell);ids.append(Qdig)
    N=-U*A-r*B;Nr=U*U-1
    qm1=_qpow(adapter,arb_type,fmpq_type,q,qfloor,1,region+".qm1")
    qm3=_qpow(adapter,arb_type,fmpq_type,q,qfloor,3,region+".qm3")
    qm5=_qpow(adapter,arb_type,fmpq_type,q,qfloor,5,region+".qm5")
    gamma=L*W*qm1;gr=L*N*qm3;grr=L*(Nr*q-3*N*(r-U))*qm5
    h=_hcompose(kernel,adapter,acb_type,arb_type,gamma,0,region+".h",max_gamma_depth)
    h1=_hcompose(kernel,adapter,acb_type,arb_type,gamma,1,region+".h1",max_gamma_depth)
    if quantity=="F":out=-U*h+W*h1*gr
    else:
        h2=_hcompose(kernel,adapter,acb_type,arb_type,gamma,2,region+".h2",max_gamma_depth)
        out=-(-2*U*h1*gr+W*(h2*gr*gr+h1*grr))
    detail={"chart":region,"q_floor":model.rational_json(qfloor),"q_lo":model.rational_json(qfloor),
            "q_hi":model.rational_json(_jet_fracs(adapter,q.v,region+".qhi")[1]),
            "q_lo_policy":policy.Q_LO_POLICY_ID,"denominator_policy":policy.DENOMINATOR_POLICY_ID,
            "sqrt_policy":policy.SQRT_POLICY_ID,"measure_identity":policy.MEASURE_ID,
            "gamma_policy":policy.GAMMA_POLICY_ID,"gamma_subdivisions":[],"gamma_fallback_used":False,
            "gamma_clamp":"[0,1]","gamma_clamp_fail_closed":True,
            "effective_floor_record_sha256":ids,"taylor_order":2,"gamma_lemma":"SOS_GAMMA_IN_0_1"}
    if c1dig is not None:detail.update({"c1_floor_record_sha256":c1dig,
        "c1_q_floor_source":"C1_A_W2_B" if not c1rec["component_dropped"] else "C1_COMPONENT_DROPPED"})
    return density*out,detail


def _taylor_cell(quantity:str,kernel:Any,adapter:Any,acb_type:Any,arb_type:Any,
                 fmpq_type:Any,cell:Cell,u0:Fraction,u1:Fraction,s0:Fraction,s1:Fraction,
                 eps:Fraction,max_gamma_depth:int)->tuple[Any,dict[str,Any]]:
    _reset_gamma_trace()
    rb=_r_ball(arb_type,fmpq_type,u0,u1);lb=_lambda_ball(arb_type,fmpq_type,s0,s1);z=arb_type(0)
    rj=J2(rb,z,z,z,z,z);lj=J2(lb,z,z,z,z,z)
    am=(cell.a0+cell.a1)/2;bm=(cell.b0+cell.b1)/2
    fc,detail=_geometry_jet(quantity,kernel,adapter,acb_type,arb_type,fmpq_type,cell.region,
        _jvar(_arb_exact(arb_type,fmpq_type,am),0),_jvar(_arb_exact(arb_type,fmpq_type,bm),1),
        rj,lj,cell,u0,s0,eps,"center",max_gamma_depth)
    fb,_=_geometry_jet(quantity,kernel,adapter,acb_type,arb_type,fmpq_type,cell.region,
        _jvar(_arb_interval(arb_type,fmpq_type,cell.a0,cell.a1),0),
        _jvar(_arb_interval(arb_type,fmpq_type,cell.b0,cell.b1),1),
        rj,lj,cell,u0,s0,eps,"box",max_gamma_depth)
    da=cell.a1-cell.a0;db=cell.b1-cell.b0;area=da*db
    caa=area*da*da/Fraction(24);cbb=area*db*db/Fraction(24);cab=area*da*db/Fraction(16)
    hlo,hhi=_jet_fracs(adapter,fb.hab,"Taylor Hab");cross=max(abs(hlo),abs(hhi))*cab
    src=fc.v*_arb_exact(arb_type,fmpq_type,area)+fb.haa*_arb_exact(arb_type,fmpq_type,caa)+fb.hbb*_arb_exact(arb_type,fmpq_type,cbb)+_arb_interval(arb_type,fmpq_type,-cross,cross)
    if cell.region=="C1":factor=_arb_exact(arb_type,fmpq_type,HALF-eps)*arb_type.pi()
    elif cell.region=="TH":factor=(arb_type.pi()/3)*arb_type.pi()
    else:factor=_arb_exact(arb_type,fmpq_type,eps)*(arb_type.pi()-_arb_exact(arb_type,fmpq_type,eps))
    out=src*factor;_canonical(adapter,out,"Taylor contribution")
    aa0,aa1=_jet_fracs(adapter,fb.haa,"Taylor Haa");bb0,bb1=_jet_fracs(adapter,fb.hbb,"Taylor Hbb")
    detail.update({"_score_a":max(abs(aa0),abs(aa1))*caa+cross/2,
                   "_score_b":max(abs(bb0),abs(bb1))*cbb+cross/2,
                   "remainder_rule":"diag area*w^2/24 + cross supabs*area*wa*wb/16",
                   "gamma_subdivisions":[_GAMMA_TRACE[k] for k in sorted(_GAMMA_TRACE)],
                   "gamma_fallback_used":any(x["bin_count"]>1 for x in _GAMMA_TRACE.values())})
    return out,detail


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


def _z_den_lo(triangle: str, cell: Cell, u0: Fraction, u1: Fraction,
              s0: Fraction, eps: Fraction) -> tuple[Fraction,Fraction,Fraction,Fraction]:
    lam_lo=model.LAMBDA_PLUS+s0;r_lo=1-u1;bh=_bhat_lower(eps)
    model.need(lam_lo>1 and r_lo>0,"strip parameters")
    if triangle=="T1":
        ah=(lam_lo*lam_lo-1)/(1+cell.b1*cell.b1)
    elif triangle=="T2":
        ah=(lam_lo*lam_lo-1)*cell.b0*cell.b0/(1+cell.b0*cell.b0)
    else:
        raise ValueError("triangle")
    rho2_hi=eps*eps*cell.a1*cell.a1*(1+cell.b1*cell.b1)
    model.need(rho2_hi>0,"Duffy rho2_hi")
    what=u0*u0/rho2_hi
    rb=r_lo*r_lo*bh
    out=max(Fraction(0),ah)+max(Fraction(0),rb)+max(Fraction(0),what)
    model.need(out>0,"Z_DEN_LO")
    return out,ah,rb,what


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
    Sfloor,Sdig=_effective_floor(adapter,"DUFFY_S2",Fraction(0),S2,"Duffy.S2",cell.region,"box",cell)
    if Sfloor>0:S=_safe_positive_sqrt(adapter,arb_type,fmpq_type,S2,Sfloor,"Duffy.S.effective")
    else:S=_safe_nonnegative_sqrt(adapter,arb_type,fmpq_type,S2,"Duffy.S.fallback")
    U=S*phi.cos();A=(lam*lam-one)*c*c;B=one-U*U;W=one-r*U;q=W*W+A+r*r*B
    w2=lam*lam*S2+c*c
    wfloor,Wdig=_effective_floor(adapter,"DUFFY_W2",Fraction(1),w2,"Duffy.w2",cell.region,"box",cell)
    w=_safe_positive_sqrt(adapter,arb_type,fmpq_type,w2,wfloor,"Duffy.w.effective");L=lam/w
    bh_lo=_bhat_lower(eps);Bhat=_arb_interval(arb_type,fmpq_type,bh_lo,Fraction(1))
    M=U*Ahat+r*Bhat
    zden,ahat_lo,rb_lo,what=_z_den_lo(cell.region,cell,u0,u1,s0,eps)
    z_hi=arb_type(1)/_arb_exact(arb_type,fmpq_type,zden).sqrt()
    _canonical(adapter,z_hi,"Duffy z_hi")
    corner=(cell.a0==0)
    g2=one+yd*yd
    gfloor,Gdig=_effective_floor(adapter,"DUFFY_G2",Fraction(1),g2,"Duffy.g2",cell.region,"box",cell)
    gy=_safe_positive_sqrt(adapter,arb_type,fmpq_type,g2,gfloor,"Duffy.g.effective")
    rho=eps_a*x*gy
    q_hi_record=None
    if corner:
        yh=arb_type(0).union(arb_type(1));v=arb_type(-1).union(arb_type(1));z=arb_type(0).union(z_hi)
        gamma=arb_type(0).union(arb_type(1))
    else:
        # q >= rho^2 * Z_DEN_LO.  On a non-corner child x>=a0>0,
        # rho^2 >= eps^2*a0^2*(1+b0^2), an exact rational child floor.
        rho2_lo=eps*eps*cell.a0*cell.a0*(1+cell.b0*cell.b0)
        qlo=rho2_lo*zden
        invq,invsqrtq,qhi=_positive_inverse_factors(
            adapter,arb_type,fmpq_type,q,qlo,f"{cell.region}:{cell.path}:Duffy")
        del invq
        q_hi_record=model.rational_json(qhi)
        yh=(W*invsqrtq).max(arb_type(0)).min(arb_type(1))
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
        "Duffy_Z_components":{"Ahat_lo":model.rational_json(ahat_lo),
            "r_lo2_Bhat_lo":model.rational_json(rb_lo),
            "u0_2_over_rho2_hi":model.rational_json(what),
            "rho2_hi":model.rational_json(eps*eps*cell.a1*cell.a1*(1+cell.b1*cell.b1))},
        "effective_floor_record_sha256":[Sdig,Wdig,Gdig],
        "local_geometry":["S","U","W","B","q"],
        "gamma_policy":policy.GAMMA_POLICY_ID,"gamma_subdivisions":gsplits,
        "gamma_fallback_used":any(x["bin_count"]>1 for x in gsplits),"gamma_fallback_class":"corner" if corner else "non_corner",
        "gamma_clamp":"[0,1]","gamma_clamp_fail_closed":True,
        "sqrt_policy":policy.SQRT_POLICY_ID,
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
               eps: Fraction,max_gamma_depth:int) -> tuple[Any,dict[str,Any]]:
    if cell.region in ("T1","T2"):
        return _duffy_eval(quantity,kernel,adapter,acb_type,arb_type,fmpq_type,
                           cell,u0,u1,s0,s1,eps)
    return _taylor_cell(quantity,kernel,adapter,acb_type,arb_type,fmpq_type,
                        cell,u0,u1,s0,s1,eps,max_gamma_depth)


def _split(cell: Cell, detail:dict[str,Any]|None=None) -> list[Cell]:
    if detail is not None and cell.region in ("R2","C1","TH"):
        axis="A" if detail.get("_score_a",0)>=detail.get("_score_b",0) else "B"
        if axis=="A":
            m=(cell.a0+cell.a1)/2;boxes=[(cell.a0,m,cell.b0,cell.b1),(m,cell.a1,cell.b0,cell.b1)]
        else:
            m=(cell.b0+cell.b1)/2;boxes=[(cell.a0,cell.a1,cell.b0,m),(cell.a0,cell.a1,m,cell.b1)]
    else:boxes=policy.split_box(cell.a0,cell.a1,cell.b0,cell.b1,cell.depth)
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
            for r in ("T1","T2","R2","C1","TH")]


def _proof_id(obj: dict[str,Any]) -> str:
    return model.sha256_bytes(model.canonical_json_bytes(obj))


def enclose_route(quantity: str, kernel: Any, adapter: Any, acb_type: Any,
                  arb_type: Any, fmpq_type: Any, config: dict[str,Any],
                  u0: Fraction,u1: Fraction,s0: Fraction,s1: Fraction,
                  required_sign: str | None = None,
                  accept:Callable[[dict[str,Any]],bool]|None=None,
                  evaluation_cap:int|None=None) -> tuple[dict[str,Any],dict[str,Any]]:
    """Return canonical normalized enclosure and a reconstructible adaptive proof."""
    model.need(quantity in {"F","H_U"},"route quantity")
    model.need(Fraction(0)<=u0<=u1<=Fraction(1,4),"route u")
    model.need(-model.S_NEG<=s0<=s1,"route s")
    pkey="F_ROUTE" if quantity=="F" else "K_ROUTE";pcfg=config["route_policies"][pkey]
    effective_evaluation_cap=pcfg["max_evaluations"] if evaluation_cap is None else evaluation_cap
    model.need(isinstance(effective_evaluation_cap,int) and 0<effective_evaluation_cap<=pcfg["max_evaluations"],"route evaluation cap")
    eps=model.fraction_from_dyadic(config["geometry"]["eps"])
    _reset_floor_trace();evaluations=0
    leaves:dict[str,Cell]={};values:dict[str,Any]={};canonical:dict[str,dict[str,Any]]={}
    meta:dict[str,dict[str,Any]]={};split_reasons:dict[str,str]={}
    unevaluated:list[tuple[int,str]]=[];shallow:list[tuple[int,str]]=[];widths:list[_WidthEntry]=[]
    sum_lo=sum_hi=Fraction(0)

    def add_leaf(cell:Cell)->None:
        leaves[cell.path]=cell
        key=(policy.REGION_ORDER[cell.region],cell.path)
        heapq.heappush(unevaluated,key)
        if cell.depth<pcfg["min_depth"]:heapq.heappush(shallow,key)

    def remove_leaf(cell:Cell)->dict[str,Any]|None:
        nonlocal sum_lo,sum_hi
        leaves.pop(cell.path)
        detail=meta.pop(cell.path,None);values.pop(cell.path,None)
        iv=canonical.pop(cell.path,None)
        if iv is not None:
            lo,hi=model.interval_fractions(iv,"remove cached child")
            sum_lo-=lo;sum_hi-=hi
        return detail

    def split_leaf(cell:Cell,reason:str)->None:
        model.need(cell.depth<pcfg["max_depth"],f"angular depth: {reason}")
        model.need(len(leaves)+1<=pcfg["max_children"],"angular child budget")
        detail=remove_leaf(cell)
        for child in _split(cell,detail):add_leaf(child)
        split_reasons[cell.path]=reason

    def eval_one(cell: Cell) -> None:
        nonlocal evaluations,sum_lo,sum_hi
        if evaluations>=effective_evaluation_cap:
            raise EnclosureFailure("ANGULAR_EVALUATION_BUDGET",evaluations)
        value,detail=_cell_eval(quantity,kernel,adapter,acb_type,arb_type,fmpq_type,
                                cell,u0,u1,s0,s1,eps,pcfg["max_depth"])
        iv=_canonical(adapter,value,"accepted child")
        lo,hi=model.interval_fractions(iv,"cached child")
        evaluations+=1;values[cell.path]=value;canonical[cell.path]=iv;meta[cell.path]=detail
        sum_lo+=lo;sum_hi+=hi
        if cell.depth<pcfg["max_depth"]:
            heapq.heappush(widths,_WidthEntry(hi-lo,-policy.REGION_ORDER[cell.region],cell.path))

    for root in _root_initial():add_leaf(root)

    while True:
        forced=None
        while unevaluated:
            _,path=heapq.heappop(unevaluated)
            cell=leaves.get(path)
            if cell is None or path in canonical:continue
            try:eval_one(cell)
            except SplitRequired as exc:
                forced=(cell,exc.reason);break
        if forced is not None:
            split_leaf(*forced)
            continue
        shallow_cell=None
        while shallow:
            _,path=heapq.heappop(shallow);cell=leaves.get(path)
            if cell is not None and cell.depth<pcfg["min_depth"]:
                shallow_cell=cell;break
        if shallow_cell is not None:
            split_leaf(shallow_cell,"MIN_DEPTH")
            continue
        unnorm=model.outward_dyadic(sum_lo,sum_hi);normalized=model.normalize_interval(unnorm)
        lo,hi=model.interval_fractions(normalized,"root normalized")
        resolved=((accept is not None and accept(normalized)) or
                  (accept is None and (required_sign is None or (required_sign=="POS" and lo>0)
                  or (required_sign=="NEG" and hi<0))))
        if resolved:
            break
        model.need(len(leaves)+1<=pcfg["max_children"],"angular sign child budget")
        chosen=None
        while widths:
            entry=heapq.heappop(widths);cell=leaves.get(entry.path)
            if cell is not None and cell.depth<pcfg["max_depth"] and entry.path in canonical:
                chosen=cell;break
        model.need(chosen is not None,"angular sign unresolved at depth limit")
        split_leaf(chosen,"ROOT_PREDICATE_UNRESOLVED")

    leaf_list=list(leaves.values())
    model.need(all(_cover_ok(leaf_list,r) for r in policy.REGION_ORDER),"exact angular cover")
    ordered=sorted(leaf_list,key=lambda c:(policy.REGION_ORDER[c.region],c.path))
    child_records=[]
    for c in ordered:
        iv=canonical[c.path]
        child_records.append({
            "child_id":c.path,"parent_id":c.path[:-1] if len(c.path)>2 else None,
            "region":c.region,"depth":c.depth,"box":{
                "a":model.interval_json(c.a0,c.a1),"b":model.interval_json(c.b0,c.b1)},
            "source_coordinates":"(x,y_D)" if c.region in ("T1","T2") else "NORMALIZED_SOURCE_BOX",
            "detail":{k:v for k,v in meta[c.path].items() if not k.startswith("_score_")},
            "contribution_enclosure":iv,"status":"ACCEPTED",
        })
    ulo,uhi=model.interval_add_exact([r["contribution_enclosure"] for r in child_records])
    model.need((ulo,uhi)==(sum_lo,sum_hi),"incremental sum reconstruction")
    unnormalized=model.outward_dyadic(ulo,uhi);normalized=model.normalize_interval(unnormalized)
    route_id=F_ROUTE_ID if quantity=="F" else K_ROUTE_ID
    body={
        "route_id":route_id,"quantity":quantity,"angular_policy_id":policy.ANGULAR_POLICY_ID,
        "policy":pcfg,"denominator_policy_id":policy.DENOMINATOR_POLICY_ID,
        "effective_evaluation_cap":effective_evaluation_cap,
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
        "effective_floor_registry":_floor_summary(),
        "method_selection_addendum_sha256":METHOD_SELECTION_ADDENDUM_SHA256,
        "c1_floor_spec_sha256":C1_FLOOR_SPEC_SHA256,
    }
    body["proof_id"]=_proof_id(body)
    return normalized,body


def enclose_hu(kernel: Any,adapter: Any,acb_type:Any,arb_type:Any,fmpq_type:Any,
               config:dict[str,Any],u0:Fraction,u1:Fraction,s0:Fraction,s1:Fraction,
               required_sign: str | None="POS",
               accept:Callable[[dict[str,Any]],bool]|None=None,
               evaluation_cap:int|None=None) -> tuple[dict[str,Any],dict[str,Any]]:
    return enclose_route("H_U",kernel,adapter,acb_type,arb_type,fmpq_type,
                         config,u0,u1,s0,s1,required_sign,accept,evaluation_cap)


def enclose_f(kernel: Any,adapter: Any,acb_type:Any,arb_type:Any,fmpq_type:Any,
              config:dict[str,Any],r0:Fraction,r1:Fraction,lam0:Fraction,lam1:Fraction,
              required_sign: str | None=None,
              accept:Callable[[dict[str,Any]],bool]|None=None,
              evaluation_cap:int|None=None) -> tuple[dict[str,Any],dict[str,Any]]:
    model.need(r0<=r1,"F r order");model.need(lam0<=lam1,"F lambda order")
    u0,u1=1-r1,1-r0;s0,s1=lam0-model.LAMBDA_PLUS,lam1-model.LAMBDA_PLUS
    return enclose_route("F",kernel,adapter,acb_type,arb_type,fmpq_type,
                         config,u0,u1,s0,s1,required_sign,accept,evaluation_cap)
