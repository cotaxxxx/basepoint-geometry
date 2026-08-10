#!/usr/bin/env python3
"""B-LOCAL v2.2 finite boundary-strip enclosure route.

The singular square is evaluated only through the cancellation-free Duffy
expression J=rho*K. No direct 0/0 quotient is constructed on a box containing
the corner. The regular complement is evaluated from the same pinned full
F_r formula after an exact positive q lower bound is established.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any

import blocal_v22_model as model

BOUNDARY_ROUTE_ID = model.BOUNDARY_ROUTE_ID
LEMMA_ID = model.BOUNDARY_LEMMA_ID


def _arb_exact(arb_type: Any, fmpq_type: Any, value: Fraction) -> Any:
    return arb_type(fmpq_type(value.numerator, value.denominator))


def _arb_interval(arb_type: Any, fmpq_type: Any,
                  lower: Fraction, upper: Fraction) -> Any:
    model.need(lower <= upper, "interval order")
    lo = _arb_exact(arb_type, fmpq_type, lower)
    hi = _arb_exact(arb_type, fmpq_type, upper)
    return lo.union(hi)


def _unit_interval(arb_type: Any) -> Any:
    return arb_type(0).union(arb_type(1))


def _signed_unit_interval(arb_type: Any) -> Any:
    return arb_type(-1).union(arb_type(1))


def _as_real(value: Any, where: str) -> Any:
    if not bool(0 in value.imag):
        raise ValueError(f"{where}: imaginary part excludes zero")
    return value.real


def _h_derivatives(kernel: Any, acb_type: Any, gamma: Any) -> tuple[Any, Any]:
    _, h1, h2 = kernel.angle_data(acb_type(gamma))
    return _as_real(h1, "boundary h1"), _as_real(h2, "boundary h2")


def _lambda_ball(arb_type: Any, fmpq_type: Any,
                 s_lower: Fraction, s_upper: Fraction) -> Any:
    base = _arb_exact(arb_type, fmpq_type, model.LAMBDA_PLUS)
    return base + _arb_interval(arb_type, fmpq_type, s_lower, s_upper)


def _r_ball(arb_type: Any, fmpq_type: Any,
            u_lower: Fraction, u_upper: Fraction) -> Any:
    return _arb_interval(arb_type, fmpq_type, 1-u_upper, 1-u_lower)


def _regular_K(kernel: Any, acb_type: Any, arb_type: Any, fmpq_type: Any,
               u_lower: Fraction, u_upper: Fraction,
               s_lower: Fraction, s_upper: Fraction,
               c_ball: Any, phi_ball: Any, q_floor: Fraction) -> Any:
    r = _r_ball(arb_type, fmpq_type, u_lower, u_upper)
    lam = _lambda_ball(arb_type, fmpq_type, s_lower, s_upper)
    one = arb_type(1)
    # c is mathematically in [0,1]. Clamp only the dependency-rounding
    # overshoot before sqrt; this is the exact nonnegative quantity S^2.
    S2 = (one-c_ball*c_ball).max(arb_type(0))
    S = S2.sqrt()
    U = S * phi_ball.cos()
    A = (lam*lam-one) * c_ball*c_ball
    B = one-U*U
    W = one-r*U
    q = W*W + A + r*r*B
    # The region-specific q_floor was proved independently before this call.
    # max(q,q_floor) is an enclosure of the same mathematical q because q>=q_floor.
    q = q.max(_arb_exact(arb_type, fmpq_type, q_floor))
    sqrt_q = q.sqrt()
    w = (lam*lam*S2 + c_ball*c_ball).sqrt()
    L = lam/w
    # The exact sum-of-squares identity audited in blocal_v22_symbolic_audit.py
    # proves 0<=gamma<=1. Use that bounded extension instead of permitting
    # dependency overestimation to cross the angle-data branch boundary.
    gamma = _unit_interval(arb_type)
    h1, h2 = _h_derivatives(kernel, acb_type, gamma)
    N = -U*A-r*B
    gamma_r = L*N/(q*sqrt_q)
    gamma_rr = L*((U*U-one)*q - arb_type(3)*N*(r-U))/(q*q*sqrt_q)
    return -arb_type(2)*U*h1*gamma_r + W*(h2*gamma_r*gamma_r + h1*gamma_rr)


def _bhat_lower(eps: Fraction) -> Fraction:
    # sin(t)/t >= cos(eps) >= 1-eps^2/2 on [0,eps]. Therefore
    # B/rho^2 >= (1-eps^2/2)^2 on either Duffy triangle.
    lower_cos = 1 - eps*eps/Fraction(2)
    model.need(lower_cos > 0, "positive cosine lower bound")
    return lower_cos*lower_cos


def _r1_q_min(s_lower: Fraction, eps: Fraction) -> Fraction:
    lam_lower = model.LAMBDA_PLUS + s_lower
    model.need(lam_lower > 1, "lambda lower > 1")
    return (lam_lower*lam_lower-1)*eps*eps


def _r2_q_min(eps: Fraction) -> Fraction:
    # On phi>=eps, U<=cos(eps), r<=1, so W>=1-cos(eps).
    # Alternating Taylor: 1-cos(eps) >= eps^2/2-eps^4/24.
    d = eps*eps/Fraction(2) - eps**4/Fraction(24)
    model.need(d > 0, "positive R2 W lower bound")
    return d*d


def _z_den_lower(triangle: str, t_lower: Fraction, t_upper: Fraction,
                 u_upper: Fraction, s_lower: Fraction, eps: Fraction) -> Fraction:
    lam_lower = model.LAMBDA_PLUS+s_lower
    r_lower = 1-u_upper
    model.need(lam_lower > 1 and r_lower > 0, "positive strip parameters")
    bh = _bhat_lower(eps)
    if triangle == "T1":
        ah = (lam_lower*lam_lower-1)/(1+t_upper*t_upper)
    elif triangle == "T2":
        ah = (lam_lower*lam_lower-1)*t_lower*t_lower/(1+t_lower*t_lower)
    else:
        raise ValueError("triangle")
    zden = ah+r_lower*r_lower*bh
    model.need(zden > 0, "Z_DEN_LO > 0")
    return zden


def _duffy_J(kernel: Any, acb_type: Any, arb_type: Any, fmpq_type: Any,
             triangle: str,
             u_lower: Fraction, u_upper: Fraction,
             s_lower: Fraction, s_upper: Fraction,
             x_lower: Fraction, x_upper: Fraction,
             t_lower: Fraction, t_upper: Fraction,
             eps: Fraction) -> tuple[Any, Fraction]:
    r = _r_ball(arb_type, fmpq_type, u_lower, u_upper)
    lam = _lambda_ball(arb_type, fmpq_type, s_lower, s_upper)
    x = _arb_interval(arb_type, fmpq_type, x_lower, x_upper)
    t = _arb_interval(arb_type, fmpq_type, t_lower, t_upper)
    eps_a = _arb_exact(arb_type, fmpq_type, eps)
    one = arb_type(1)
    if triangle == "T1":
        c = eps_a*x
        phi = eps_a*x*t
        Ahat = (lam*lam-one)/(one+t*t)
    elif triangle == "T2":
        phi = eps_a*x
        c = eps_a*x*t
        Ahat = (lam*lam-one)*t*t/(one+t*t)
    else:
        raise ValueError("triangle")

    S = (one-c*c).sqrt()
    U = S*phi.cos()
    w = (lam*lam*(one-c*c)+c*c).sqrt()
    L = lam/w

    # The exact Bhat is finite but would require a sinc implementation at x=0.
    # The design permits certified interval bounds. We use the exact inequalities
    # bhat_lo <= Bhat <= 1, valid on the whole dyadic square.
    bh_lo = _bhat_lower(eps)
    Bhat = _arb_interval(arb_type, fmpq_type, bh_lo, Fraction(1))
    M = U*Ahat+r*Bhat

    zden = _z_den_lower(triangle, t_lower, t_upper, u_upper, s_lower, eps)
    z_upper = (_arb_exact(arb_type, fmpq_type, zden).sqrt())**-1
    z = arb_type(0).union(z_upper)
    yq = _unit_interval(arb_type)
    v = _signed_unit_interval(arb_type)
    gamma = _unit_interval(arb_type)  # exact geometric bound, symbolically audited
    h1, h2 = _h_derivatives(kernel, acb_type, gamma)
    rho = eps_a*x*(one+t*t).sqrt()

    J = L*(
        arb_type(2)*U*h1*M*z**3
        + L*h2*M*M*yq*z**5
        + h1*(-Bhat*yq*rho*z**2 + arb_type(3)*M*yq*v*z**3)
    )
    transformed = eps_a*J/(one+t*t).sqrt()
    return transformed, zden


def _grid(power: int) -> list[tuple[Fraction, Fraction]]:
    n = 1 << power
    return [(Fraction(i,n), Fraction(i+1,n)) for i in range(n)]


def _integrate_duffy(kernel: Any, acb_type: Any, arb_type: Any, fmpq_type: Any,
                     triangle: str,
                     u_lower: Fraction, u_upper: Fraction,
                     s_lower: Fraction, s_upper: Fraction,
                     eps: Fraction, power: int) -> tuple[Any, Fraction, int]:
    total = arb_type(0)
    minimum_zden: Fraction | None = None
    count = 0
    for x0,x1 in _grid(power):
        for t0,t1 in _grid(power):
            value,zden = _duffy_J(kernel,acb_type,arb_type,fmpq_type,triangle,
                                  u_lower,u_upper,s_lower,s_upper,x0,x1,t0,t1,eps)
            area = (x1-x0)*(t1-t0)
            total += value*_arb_exact(arb_type,fmpq_type,area)
            minimum_zden = zden if minimum_zden is None else min(minimum_zden,zden)
            count += 1
    assert minimum_zden is not None
    return total,minimum_zden,count


def _integrate_regular(kernel: Any, acb_type: Any, arb_type: Any, fmpq_type: Any,
                       region: str,
                       u_lower: Fraction, u_upper: Fraction,
                       s_lower: Fraction, s_upper: Fraction,
                       eps: Fraction, power: int) -> tuple[Any, Fraction, int]:
    total = arb_type(0)
    pi = arb_type.pi()
    eps_a = _arb_exact(arb_type,fmpq_type,eps)
    one = arb_type(1)
    if region == "R1":
        q_min = _r1_q_min(s_lower,eps)
        jac = (one-eps_a)*pi
    elif region == "R2":
        q_min = _r2_q_min(eps)
        jac = eps_a*(pi-eps_a)
    else:
        raise ValueError("region")
    # q_min is proved before direct evaluation. Its positivity is an invariant
    # checked by both route and checker.
    model.need(q_min > 0, f"{region} q_min")
    count=0
    for a0,a1 in _grid(power):
        for b0,b1 in _grid(power):
            a = _arb_interval(arb_type,fmpq_type,a0,a1)
            b = _arb_interval(arb_type,fmpq_type,b0,b1)
            if region == "R1":
                c = eps_a+(one-eps_a)*a
                phi = pi*b
            else:
                c = eps_a*a
                phi = eps_a+(pi-eps_a)*b
            value = _regular_K(kernel,acb_type,arb_type,fmpq_type,
                               u_lower,u_upper,s_lower,s_upper,c,phi,q_min)
            area = (a1-a0)*(b1-b0)
            total += value*jac*_arb_exact(arb_type,fmpq_type,area)
            count += 1
    return total,q_min,count


def enclose_boundary_hu(kernel: Any, acb_type: Any, arb_type: Any, fmpq_type: Any,
                        config: dict[str, Any],
                        u_lower: Fraction, u_upper: Fraction,
                        s_lower: Fraction, s_upper: Fraction) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    """Return H_u, machine-readable diagnostics, and four contribution balls."""
    b = config["boundary_strip"]
    eps = model.fraction_from_dyadic(b["eps"], "eps")
    u_cut = model.fraction_from_dyadic(b["u_cut"], "u_cut")
    model.need(Fraction(0) <= u_lower <= u_upper <= u_cut, "boundary strip u box")
    model.need(-model.S_NEG <= s_lower <= s_upper, "boundary strip s box lower")
    power = config["precision"]["angular_grid_power"]

    t1,z1,n1 = _integrate_duffy(kernel,acb_type,arb_type,fmpq_type,"T1",
                                u_lower,u_upper,s_lower,s_upper,eps,power)
    t2,z2,n2 = _integrate_duffy(kernel,acb_type,arb_type,fmpq_type,"T2",
                                u_lower,u_upper,s_lower,s_upper,eps,power)
    r1,q1,n3 = _integrate_regular(kernel,acb_type,arb_type,fmpq_type,"R1",
                                  u_lower,u_upper,s_lower,s_upper,eps,power)
    r2,q2,n4 = _integrate_regular(kernel,acb_type,arb_type,fmpq_type,"R2",
                                  u_lower,u_upper,s_lower,s_upper,eps,power)
    fr = (t1+t2+r1+r2)/arb_type.pi()
    hu = -fr
    diagnostics = {
        "lemma_id": LEMMA_ID,
        "route_id": BOUNDARY_ROUTE_ID,
        "patch_type": model.PATCH_TYPE,
        "regularization_method": model.REGULARIZATION_METHOD,
        "eps": model.dyadic_json(eps),
        "u_cut": model.dyadic_json(u_cut),
        "z_den_lo": {"T1": model.rational_json(z1), "T2": model.rational_json(z2)},
        "q_min": {"R1": model.rational_json(q1), "R2": model.rational_json(q2)},
        "algebraic_bounds": {"y": "[0,1]", "v": "[-1,1]", "gamma": "[0,1]"},
        "angular_subboxes": n1+n2+n3+n4,
        "duffy_triangles": ["T1","T2"],
        "regular_regions": ["R1","R2"],
        "sin_theta_dtheta_cancelled_symbolically": True,
        "independent_one_over_sqrt_one_minus_c2_evaluated": False,
    }
    contributions = {"T1": t1, "T2": t2, "R1": r1, "R2": r2}
    return hu,diagnostics,contributions
