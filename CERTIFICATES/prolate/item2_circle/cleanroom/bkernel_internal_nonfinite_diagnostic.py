#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

from flint import acb, arb, ctx

HERE = Path(__file__).resolve().parent
VENDOR = HERE.parent / "vendor"
sys.path.insert(0, str(VENDOR))
import prolate_circle_F_cleanroom as kernel

EXPECTED_KERNEL_SHA256 = "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac"
LAM = Fraction(3307749, 1600000)
TOL = "1e-20"
DEPTH = 12
LIMIT = 200000
ctx.dps = 60

POINTS = [
    ("A_A0_LO", Fraction(2047, 2048)),
    ("B_FR_SPLIT", Fraction(32331, 32768)),
    ("C_FINITE_CONTROL", Fraction(16165, 16384)),
]

HYPOTHESIS = (
    "Near the singular corner theta->pi/2, phi->0, the real-domain quantity "
    "q has the strict exact floor q >= (1-r)^2 > 0, but analytic integration "
    "balls may widen the direct q enclosure across zero. The derivative route "
    "contains the strongest q^{-5/2}-scale amplification through gamma_rr, so "
    "dFdr is expected to become nonfinite before F at point B."
)


def exact_arb(x: Fraction) -> arb:
    return arb(str(x.numerator)) / arb(str(x.denominator))


def _is_finite_text(x: Any) -> bool:
    s = str(x).lower()
    return "nan" not in s and "inf" not in s


def _man_exp(x: arb) -> list[str] | None:
    try:
        a, b = x.man_exp()
        return [str(a), str(b)]
    except Exception:
        return None


def arb_record(x: arb) -> dict[str, Any]:
    out: dict[str, Any] = {"text": str(x), "finite": _is_finite_text(x)}
    if not out["finite"]:
        return out
    try:
        mid = x.mid()
        rad = x.rad()
        out.update({
            "midpoint": str(mid),
            "radius": str(rad),
            "lower": str(x.lower()),
            "upper": str(x.upper()),
            "midpoint_man_exp": _man_exp(mid),
            "radius_man_exp": _man_exp(rad),
            "contains_zero": bool(0 in x),
        })
    except Exception as exc:
        out["metadata_error"] = f"{type(exc).__name__}: {exc}"
    return out


def acb_record(x: acb) -> dict[str, Any]:
    out: dict[str, Any] = {"text": str(x), "finite": _is_finite_text(x)}
    try:
        out["real"] = arb_record(x.real)
        out["imag"] = arb_record(x.imag)
        out["radius_magnitude"] = arb_record(x.rad())
        out["imag_contains_zero"] = bool(0 in x.imag)
    except Exception as exc:
        out["metadata_error"] = f"{type(exc).__name__}: {exc}"
    return out


def value_record(x: Any) -> dict[str, Any]:
    if isinstance(x, acb):
        return acb_record(x)
    if isinstance(x, arb):
        return arb_record(x)
    return {"text": repr(x), "finite": True}


class Tracker:
    def __init__(self, point_id: str, r: Fraction, function_id: str):
        self.point_id = point_id
        self.r = r
        self.function_id = function_id
        self.callback_count = 0
        self.analytic_true = 0
        self.analytic_false = 0
        self.first_nonfinite: dict[str, Any] | None = None
        self.nonfinite_events: list[dict[str, Any]] = []
        self._local: dict[str, Any] | None = None
        self.structural_q_floor = (Fraction(1, 1) - r) ** 2

    def begin(self, theta: acb, phi: acb, analytic: bool) -> None:
        self.callback_count += 1
        self.analytic_true += int(bool(analytic))
        self.analytic_false += int(not bool(analytic))
        self._local = {
            "callback_index": self.callback_count,
            "analytic": bool(analytic),
            "theta": acb_record(theta),
            "phi": acb_record(phi),
            "last_finite_variable": None,
            "last_finite_ball": None,
            "q_direct": None,
            "q_identity": None,
            "W": None,
            "A": None,
            "B": None,
            "intermediates": [],
        }

    def note(self, name: str, value: Any) -> Any:
        assert self._local is not None
        rec = value_record(value)
        self._local["intermediates"].append(
            {"name": name, "diagnostic_only": False, "ball": rec}
        )
        if name in {"q_direct", "W"}:
            self._local[name] = rec
        if name == "q_direct" and isinstance(value, acb):
            try:
                self._local["q_direct_real_lower_negative"] = bool(value.real.lower() < 0)
                self._local["q_direct_real_contains_zero"] = bool(0 in value.real)
            except Exception:
                self._local["q_direct_real_lower_negative"] = None
                self._local["q_direct_real_contains_zero"] = None
        if rec.get("finite", False):
            self._local["last_finite_variable"] = name
            self._local["last_finite_ball"] = rec
            return value

        event = {
            "point_id": self.point_id,
            "function": self.function_id,
            "variable": name,
            "value": rec,
            "callback_index": self._local["callback_index"],
            "analytic": self._local["analytic"],
            "theta": self._local["theta"],
            "phi": self._local["phi"],
            "last_finite_variable": self._local["last_finite_variable"],
            "last_finite_ball": self._local["last_finite_ball"],
            "q_direct": self._local["q_direct"],
            "q_identity": self._local["q_identity"],
            "W": self._local["W"],
            "A": self._local["A"],
            "B": self._local["B"],
            "real_domain_structural_q_floor": {
                "exact": f"{self.structural_q_floor.numerator}/{self.structural_q_floor.denominator}",
                "decimal": float(self.structural_q_floor),
                "basis": "q = W^2 + A + r^2 B with W=1-rU >= 1-r on the real angular domain",
            },
            "intermediates_up_to_failure": list(self._local["intermediates"]),
            "q_direct_real_lower_negative": self._local.get("q_direct_real_lower_negative"),
            "q_direct_real_contains_zero": self._local.get("q_direct_real_contains_zero"),
        }
        if self.first_nonfinite is None:
            self.first_nonfinite = event
        if len(self.nonfinite_events) < 12:
            self.nonfinite_events.append(event)
        return value

    def observe_diagnostic(self, name: str, value: Any) -> Any:
        assert self._local is not None
        rec = value_record(value)
        self._local["intermediates"].append(
            {"name": name, "diagnostic_only": True, "ball": rec}
        )
        if name in {"q_identity", "A", "B"}:
            self._local[name] = rec
        return value

    def summary(self) -> dict[str, Any]:
        return {
            "callback_count": self.callback_count,
            "analytic_true_count": self.analytic_true,
            "analytic_false_count": self.analytic_false,
            "first_nonfinite": self.first_nonfinite,
            "nonfinite_events_retained": self.nonfinite_events,
            "real_domain_structural_q_floor": {
                "exact": f"{self.structural_q_floor.numerator}/{self.structural_q_floor.denominator}",
                "decimal": float(self.structural_q_floor),
            },
        }


def geometry_probe(
    theta: acb, phi: acb, r: acb, lam: acb, analytic: bool, t: Tracker,
    *, need_second_derivative: bool,
) -> dict[str, Any]:
    s = t.note("s", theta.sin())
    c = t.note("c", theta.cos())
    cos_phi = t.note("cos_phi", phi.cos())
    u = t.note("u", s * cos_phi)
    ell = t.note("ell", s * s + lam * lam * c * c)
    w2 = t.note("w2", lam * lam * s * s + c * c)
    w = t.note("w", w2.sqrt(analytic=analytic))
    q_direct = t.note("q_direct", ell - 2 * r * u + r * r)
    W = t.note("W", 1 - r * u)
    A = t.observe_diagnostic("A", (lam * lam - 1) * c * c)
    B = t.observe_diagnostic("B", 1 - u * u)
    q_identity = t.observe_diagnostic("q_identity", W * W + A + r * r * B)
    sqrt_q = t.note("sqrt_q", q_direct.sqrt(analytic=analytic))
    gamma = t.note("gamma", lam * W / (w * sqrt_q))
    N = t.note("N", u * (1 - ell) + r * (u * u - 1))
    gamma_r = t.note("gamma_r", (lam / w) * N / (q_direct * sqrt_q))
    N_r = None
    gamma_rr = None
    if need_second_derivative:
        N_r = t.note("N_r", u * u - 1)
        gamma_rr = t.note(
            "gamma_rr",
            (lam / w) * (N_r * q_direct - 3 * N * (r - u))
            / (q_direct * q_direct * sqrt_q),
        )
    return {
        "s": s, "u": u, "W": W, "gamma": gamma,
        "gamma_r": gamma_r, "gamma_rr": gamma_rr,
        "q": q_direct, "q_identity": q_identity,
    }


def angle_probe(gamma: acb, t: Tracker) -> tuple[acb, acb, acb]:
    one = acb(1)
    z = t.note("angle.z", (one - gamma) / 2)
    H = t.note("angle.H_2f1", z.hypgeom_2f1(one / 2, one / 2, acb(3) / 2))
    h = t.note("angle.h", 4 * z * H * H)
    x = t.note("angle.x", -h / 4)
    S = t.note("angle.S_0f1_3_2", x.hypgeom_0f1(acb(3) / 2))
    T = t.note("angle.T_0f1_5_2", x.hypgeom_0f1(acb(5) / 2))
    h1 = t.note("angle.h1", -2 / S)
    h2 = t.note("angle.h2", (acb(2) / 3) * T / S**3)
    return h, h1, h2


def make_F_probe(t: Tracker):
    def probe(theta: acb, phi: acb, r: acb, lam: acb, analytic: bool) -> acb:
        t.begin(theta, phi, analytic)
        g = geometry_probe(
            theta, phi, r, lam, analytic, t, need_second_derivative=False
        )
        h, h1, _ = angle_probe(g["gamma"], t)
        term1 = t.note("F.term1", -g["u"] * h)
        term2 = t.note("F.term2", g["W"] * h1 * g["gamma_r"])
        bracket = t.note("F.bracket", term1 + term2)
        return t.note("F.integrand", g["s"] * bracket)
    return probe


def make_dF_probe(t: Tracker):
    def probe(theta: acb, phi: acb, r: acb, lam: acb, analytic: bool) -> acb:
        t.begin(theta, phi, analytic)
        g = geometry_probe(
            theta, phi, r, lam, analytic, t, need_second_derivative=True
        )
        _, h1, h2 = angle_probe(g["gamma"], t)
        term1 = t.note("dF.term1", -2 * g["u"] * h1 * g["gamma_r"])
        term2a = t.note("dF.term2a_h2_gr2", h2 * g["gamma_r"] ** 2)
        term2b = t.note("dF.term2b_h1_grr", h1 * g["gamma_rr"])
        term2 = t.note("dF.term2", g["W"] * (term2a + term2b))
        bracket = t.note("dF.bracket", term1 + term2)
        return t.note("dF.integrand", g["s"] * bracket)
    return probe


def run_one(point_id: str, r_frac: Fraction, function_id: str) -> dict[str, Any]:
    tracker = Tracker(point_id, r_frac, function_id)
    r = acb(exact_arb(r_frac))
    lam = acb(exact_arb(LAM))
    probe = make_F_probe(tracker) if function_id == "F_arb" else make_dF_probe(tracker)
    started = time.time()
    try:
        value = kernel._rigorous_integral_2d(probe, r, lam, arb(TOL), DEPTH, LIMIT)
        real = kernel._as_real(value, f"instrumented_{function_id}")
        final = arb_record(real)
        status = "finite" if final.get("finite") else "nonfinite"
        exception = None
    except Exception as exc:
        status = "exception"
        final = None
        exception = {"type": type(exc).__name__, "message": str(exc)}
    result = {
        "point_id": point_id,
        "r": f"{r_frac.numerator}/{r_frac.denominator}",
        "r_decimal": float(r_frac),
        "function": function_id,
        "status": status,
        "final_value": final,
        "exception": exception,
        "elapsed_s": round(time.time() - started, 6),
        "tracker": tracker.summary(),
    }
    print("INTERNAL_DIAGNOSTIC_RESULT " + json.dumps(result, separators=(",", ":")), flush=True)
    return result


def classify(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_key = {(x["point_id"], x["function"]): x for x in results}
    A_F = by_key[("A_A0_LO", "F_arb")]
    A_D = by_key[("A_A0_LO", "dFdr_arb")]
    B_F = by_key[("B_FR_SPLIT", "F_arb")]
    B_D = by_key[("B_FR_SPLIT", "dFdr_arb")]
    C_F = by_key[("C_FINITE_CONTROL", "F_arb")]
    C_D = by_key[("C_FINITE_CONTROL", "dFdr_arb")]
    pattern = {
        "A_both_nonfinite": A_F["status"] == "nonfinite" and A_D["status"] == "nonfinite",
        "B_F_finite_dF_nonfinite": B_F["status"] == "finite" and B_D["status"] == "nonfinite",
        "C_both_finite": C_F["status"] == "finite" and C_D["status"] == "finite",
    }
    event = B_D["tracker"]["first_nonfinite"]
    first = None if event is None else event.get("variable")
    q_family = {
        "sqrt_q", "gamma_r", "gamma_rr", "dF.term2a_h2_gr2",
        "dF.term2b_h1_grr", "dF.term2", "dF.bracket", "dF.integrand",
    }
    if all(pattern.values()) and first in q_family:
        verdict = "SUPPORTED"
    elif all(pattern.values()):
        verdict = "PARTIALLY_SUPPORTED_FIRST_FAILURE_ELSEWHERE"
    else:
        verdict = "NOT_SUPPORTED_BY_OBSERVED_PATTERN"
    return {
        "hypothesis_id": "Q_DIRECT_BALL_ZERO_CROSSING_WITH_DERIVATIVE_QM5_AMPLIFICATION_V1",
        "statement": HYPOTHESIS,
        "verdict": verdict,
        "observed_pattern": pattern,
        "B_dF_first_nonfinite_variable": first,
        "B_dF_first_nonfinite_event": event,
        "interpretation_guard": (
            "The exact structural floor q>0 applies to the real angular domain. "
            "A complex analytic integration ball whose direct q enclosure crosses zero "
            "does not imply that mathematical q is nonpositive on the real domain."
        ),
    }


def main() -> int:
    kernel_path = VENDOR / "prolate_circle_F_cleanroom.py"
    kernel_sha = hashlib.sha256(kernel_path.read_bytes()).hexdigest()
    if kernel_sha != EXPECTED_KERNEL_SHA256:
        raise SystemExit(f"kernel SHA mismatch: {kernel_sha}")
    results: list[dict[str, Any]] = []
    for point_id, r_frac in POINTS:
        results.append(run_one(point_id, r_frac, "F_arb"))
        results.append(run_one(point_id, r_frac, "dFdr_arb"))
    report = {
        "schema": "btube-bkernel-internal-nonfinite-diagnostic-v1",
        "purpose": "Identify the first nonfinite intermediate variable and distinguish real-domain q positivity from direct analytic-ball q enclosure failure.",
        "kernel_sha256": kernel_sha,
        "kernel_bytes_unchanged": True,
        "lambda_start": f"{LAM.numerator}/{LAM.denominator}",
        "settings": {"dps": 60, "tol": TOL, "depth": DEPTH, "limit": LIMIT},
        "points": [
            {
                "id": p,
                "r": f"{r.numerator}/{r.denominator}",
                "r_decimal": float(r),
                "exact_real_domain_q_floor": f"{((1-r)**2).numerator}/{((1-r)**2).denominator}",
            }
            for p, r in POINTS
        ],
        "hypothesis": HYPOTHESIS,
        "results": results,
        "hypothesis_assessment": classify(results),
    }
    out = HERE / "internal_nonfinite_diagnostic.json"
    out.write_text(json.dumps(report, separators=(",", ":")), encoding="utf-8")
    print("INTERNAL_DIAGNOSTIC_FINAL " + json.dumps(report["hypothesis_assessment"], separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
