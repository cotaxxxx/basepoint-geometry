#!/usr/bin/env python3
"""Pinned Stage-1 endpoint + B'(lambda) monotonicity proof route for B-LOCAL L3."""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
import tempfile
import zipfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import blocal_phase4_provenance as provenance
import blocal_v22_model as model

ROUTE_ID = model.L3_BPRIME_ROUTE_ID
POLICY_ID = model.L3_BPRIME_POLICY_ID
DOMAIN_AUDIT_ID = model.L3_BPRIME_DOMAIN_AUDIT_ID
BRANCH_GUARD_AUDIT_ID = model.L3_BPRIME_BRANCH_GUARD_AUDIT_ID
IDENTITY_ID = model.L3_BOUNDARY_IDENTITY_ID
INFERENCE_ID = model.L3_MONOTONICITY_INFERENCE_ID


def _audit_float_guards(source_text: str) -> dict[str, Any]:
    tree = ast.parse(source_text)
    locations: list[dict[str, Any]] = []
    stack: list[str] = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Name) and node.func.id == "float":
                locations.append({"function": stack[-1] if stack else None,
                                  "lineno": node.lineno})
            self.generic_visit(node)

    Visitor().visit(tree)
    allowed = {"_abs_upper", "_h_data"}
    model.need(len(locations) == 3, "exact inherited float guard count")
    model.need(all(x["function"] in allowed for x in locations),
               "inherited float guards only")
    return {
        "audit_id": BRANCH_GUARD_AUDIT_ID,
        "status": "PASS",
        "float_call_count": 3,
        "locations": locations,
        "allowed_functions": sorted(allowed),
        "proof_decision_use": False,
    }


def _poly_clean(p: dict[tuple[int, int, int], int]) -> dict[tuple[int, int, int], int]:
    return {m: c for m, c in p.items() if c}


def _poly_add(a: dict[tuple[int, int, int], int],
              b: dict[tuple[int, int, int], int]) -> dict[tuple[int, int, int], int]:
    out = dict(a)
    for monomial, coeff in b.items():
        out[monomial] = out.get(monomial, 0) + coeff
    return _poly_clean(out)


def _poly_scale(a: dict[tuple[int, int, int], int], k: int) -> dict[tuple[int, int, int], int]:
    return _poly_clean({m: k*c for m, c in a.items()})


def _poly_sub(a: dict[tuple[int, int, int], int],
              b: dict[tuple[int, int, int], int]) -> dict[tuple[int, int, int], int]:
    return _poly_add(a, _poly_scale(b, -1))


def _poly_mul(a: dict[tuple[int, int, int], int],
              b: dict[tuple[int, int, int], int]) -> dict[tuple[int, int, int], int]:
    out: dict[tuple[int, int, int], int] = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            monomial = tuple(x+y for x, y in zip(ma, mb))
            out[monomial] = out.get(monomial, 0) + ca*cb
    return _poly_clean(out)


def _poly_pow(a: dict[tuple[int, int, int], int], n: int) -> dict[tuple[int, int, int], int]:
    out = {(0, 0, 0): 1}
    for _ in range(n):
        out = _poly_mul(out, a)
    return out


def _poly_substitute_q(a: dict[tuple[int, int, int], int], value: int) -> dict[tuple[int, int, int], int]:
    out: dict[tuple[int, int, int], int] = {}
    for (et, eq, ed), coeff in a.items():
        monomial = (et, 0, ed)
        out[monomial] = out.get(monomial, 0) + coeff*(value**eq)
    return _poly_clean(out)


def _poly_q_coefficient(a: dict[tuple[int, int, int], int], degree: int) -> dict[tuple[int, int, int], int]:
    return _poly_clean({(et, 0, ed): coeff
                        for (et, eq, ed), coeff in a.items() if eq == degree})


def _verify_domain_algebra_exact() -> dict[str, bool]:
    one = {(0, 0, 0): 1}
    T = {(1, 0, 0): 1}
    Q = {(0, 1, 0): 1}
    D = {(0, 0, 1): 1}
    one_minus_T = _poly_sub(one, T)
    c2 = _poly_scale(_poly_mul(_poly_mul(T, one_minus_T), Q), 4)
    A = _poly_add(one, _poly_mul(_poly_mul(D, one_minus_T), Q))
    J = _poly_add(one, _poly_mul(_poly_mul(D, _poly_sub(one, _poly_scale(T, 2))), Q))
    N = _poly_add(_poly_mul(D, c2), _poly_scale(T, 4))
    K = _poly_add(
        _poly_mul(_poly_mul(D, c2), _poly_sub(one, _poly_scale(T, 2))),
        _poly_mul(_poly_scale(T, 2), _poly_sub(_poly_scale(one, 2), _poly_scale(T, 2))),
    )
    W = _poly_sub(_poly_add(one, D), _poly_mul(D, c2))
    R = {
        (2, 2, 2): 4, (1, 2, 2): -4, (1, 1, 1): -4,
        (0, 1, 2): 1, (0, 1, 1): 1, (0, 0, 1): 1, (0, 0, 0): 1,
    }
    two_TD_minus_D_minus_1 = _poly_sub(
        _poly_sub(_poly_mul(_poly_scale(T, 2), D), D), one)
    checks = {
        'N_EQ_4T_A': not _poly_sub(N, _poly_scale(_poly_mul(T, A), 4)),
        'K_EQ_4T1MT_J': not _poly_sub(K, _poly_scale(_poly_mul(_poly_mul(T, one_minus_T), J), 4)),
        'W_EQ_1_PLUS_D_1MC2': not _poly_sub(W, _poly_add(one, _poly_mul(D, _poly_sub(one, c2)))),
        'C2_BOUND_IDENTITY': not _poly_sub(
            _poly_sub(one, _poly_scale(_poly_mul(T, one_minus_T), 4)),
            _poly_pow(_poly_sub(_poly_scale(T, 2), one), 2)),
        'X_RANGE_FACTOR': not _poly_sub(
            _poly_sub(_poly_mul(W, A), _poly_mul(_poly_add(one, D), T)),
            _poly_mul(one_minus_T, R)),
        'R_Q0': not _poly_sub(_poly_substitute_q(R, 0), _poly_add(D, one)),
        'R_Q1': not _poly_sub(_poly_substitute_q(R, 1), _poly_pow(two_TD_minus_D_minus_1, 2)),
        'R_Q2_CONCAVITY_COEFF': not _poly_sub(
            _poly_q_coefficient(R, 2),
            _poly_scale(_poly_mul(_poly_mul(T, _poly_sub(T, one)), _poly_pow(D, 2)), 4)),
    }
    model.need(all(checks.values()), 'L3 exact domain algebra audit')
    return checks

def _domain_audit(lambda_start: Fraction, config: dict[str, Any]) -> dict[str, Any]:
    model.need(model.LAMBDA_PLUS > 1, "lambda_plus > 1")
    model.need(lambda_start > model.LAMBDA_PLUS, "extended lambda order")
    model.need(config["l3_bprime_route"]["stage1_verify_change_of_variables_sha256"]
               == model.STAGE1_VERIFY_CHANGE_SHA256, "identity provenance pin")
    checks = _verify_domain_algebra_exact()
    return {
        "audit_id": DOMAIN_AUDIT_ID,
        "status": "PASS",
        "lambda_domain": model.rational_interval_json(model.LAMBDA_PLUS, lambda_start),
        "lambda_gt_1_exact": True,
        "exact_algebra_checks": checks,
        "A_positive_lemma": "A=1+(lambda^2-1)(1-T)q >= 1",
        "W_positive_lemma": "W=lambda^2(1-c2)+c2 >= 1",
        "c2_range_lemma": "c2=4T(1-T)q in [0,1]",
        "x_range_lemma": "W*A-lambda^2*T=(1-T)R; R concave in q; R(0)=D+1; R(1)=(2TD-D-1)^2",
        "angle_data_domain": "0<=x<=1; x=1 handled by pinned hypergeometric branch",
        "identity_id": IDENTITY_ID,
        "identity_source_sha256": model.STAGE1_VERIFY_CHANGE_SHA256,
        "no_new_singularity_or_branch_crossing": True,
    }

def prepare(repository_root: Path, config: dict[str, Any]) -> dict[str, Any]:
    model.validate_config(config)
    provenance.verify_stage1_dependency(repository_root, config["stage1_dependency"])
    stage1 = config["stage1_dependency"]
    descriptor_path = provenance.repo_file(repository_root, stage1["config_path"])
    descriptor_raw = descriptor_path.read_bytes()
    descriptor = model.parse_canonical_json(descriptor_raw)
    archive_path = provenance.repo_file(repository_root, stage1["artifact_path"])

    with zipfile.ZipFile(archive_path, "r") as bundle:
        names = bundle.namelist()
        model.need(names == descriptor["archive_members"], "Stage-1 member list")
        payload = descriptor["payload_sha256"]
        member_hashes: dict[str, str] = {}
        for name in names:
            data = bundle.read(name)
            digest = model.sha256_bytes(data)
            if name in payload:
                model.need(digest == payload[name], f"Stage-1 member pin {name}")
            member_hashes[name] = digest
        bprime_bytes = bundle.read("bprime_independent.py")
        cert_bytes = bundle.read("certificate_item2_independent.json")
        manifest_bytes = bundle.read("SHA256SUMS.txt")
        model.need(model.sha256_bytes(bprime_bytes) == model.STAGE1_BPRIME_SOURCE_SHA256,
                   "Stage-1 Bprime source")
        model.need(model.sha256_bytes(cert_bytes) == stage1["certificate_sha256"],
                   "Stage-1 certificate")
        model.need(model.sha256_bytes(manifest_bytes) == stage1["manifest_sha256"],
                   "Stage-1 manifest")
        model.need(member_hashes["verify_change_of_variables.py"]
                   == model.STAGE1_VERIFY_CHANGE_SHA256, "Stage-1 identity source")

    branch_guard_audit = _audit_float_guards(bprime_bytes.decode("utf-8"))
    cert = json.loads(cert_bytes)
    evaluation = cert["evaluations"]["B(206539/100000)"]
    model.need(evaluation["sign"] == "NEGATIVE", "Stage-1 endpoint sign")
    elo = Fraction(evaluation["lower"])
    ehi = Fraction(evaluation["upper"])
    model.need((elo, ehi) == (model.STAGE1_BPLUS_LO, model.STAGE1_BPLUS_HI),
               "Stage-1 endpoint exact enclosure")
    model.need(ehi < 0, "Stage-1 endpoint strict negative")
    model.need(config["l3_bprime_route"]["endpoint_evidence"] == {
        "evaluation_key": "B(206539/100000)",
        "enclosure": model.rational_interval_json(elo, ehi),
    }, "configured Stage-1 endpoint evidence")

    temp = tempfile.TemporaryDirectory(prefix="blocal-stage1-bprime-")
    extracted = Path(temp.name) / "bprime_independent.py"
    extracted.write_bytes(bprime_bytes)
    model.need(model.sha256_bytes(extracted.read_bytes()) == model.STAGE1_BPRIME_SOURCE_SHA256,
               "extracted Stage-1 Bprime hash")
    module_name = "blocal_stage1_bprime_pinned_for_l3"
    model.need(module_name not in sys.modules, "unique Stage-1 Bprime import")
    spec = importlib.util.spec_from_file_location(module_name, extracted)
    model.need(spec is not None and spec.loader is not None, "Stage-1 Bprime import spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        temp.cleanup()
        raise
    model.need(Path(module.__file__).resolve(strict=True) == extracted.resolve(strict=True),
               "Stage-1 Bprime imported origin")
    model.need(model.sha256_bytes(extracted.read_bytes()) == model.STAGE1_BPRIME_SOURCE_SHA256,
               "Stage-1 Bprime post-import hash")
    model.need(callable(module.Bprime) and callable(module._init_consts),
               "Stage-1 Bprime callable API")

    import flint  # type: ignore[import-not-found]
    model.need(getattr(flint, "__version__", None) == config["l3_bprime_route"]["python_flint"],
               "python-flint version")
    return {
        "module": module,
        "tempdir": temp,
        "branch_guard_audit": branch_guard_audit,
        "member_sha256": member_hashes,
        "endpoint_enclosure": model.rational_interval_json(elo, ehi),
        "stage1_source_head": stage1["source_head"],
        "archive_sha256": stage1["artifact_zip_sha256"],
        "descriptor_sha256": stage1["config_sha256"],
        "certificate_sha256": stage1["certificate_sha256"],
        "manifest_sha256": stage1["manifest_sha256"],
    }


def _evaluate(prepared: dict[str, Any], adapter: Any, lo: Fraction, hi: Fraction,
              config: dict[str, Any]) -> dict[str, Any]:
    from flint import arb, ctx  # type: ignore[import-not-found]
    policy = config["l3_bprime_route"]
    old_prec = int(ctx.prec)
    try:
        ctx.dps = policy["dps"]
        module = prepared["module"]
        module._init_consts()
        lam_lo = arb(lo.numerator) / arb(lo.denominator)
        lam_hi = arb(hi.numerator) / arb(hi.denominator)
        lam_ball = lam_lo.union(lam_hi)
        result = module.Bprime(
            lam_ball,
            bands=policy["bands"],
            rel_tol=arb(2) ** -18,
            eval_limit=policy["eval_limit"],
            depth_limit=policy["depth_limit"],
        )
        enclosure = adapter.arb_ball_to_canonical_dyadic_interval(result.real)
    finally:
        ctx.prec = old_prec
    a, b = model.interval_fractions(enclosure, "Bprime enclosure")
    return {
        "call_index": 0,
        "lambda_interval": model.rational_interval_json(lo, hi),
        "Bprime_enclosure": enclosure,
        "strict_upper_lt_zero": b < 0,
        "status": "CERTIFIED" if b < 0 else "UNRESOLVED",
        "failure_reason": None if b < 0 else "BPRIME_STRICT_NEGATIVE_UNRESOLVED",
    }


def certify_l3(prepared: dict[str, Any], adapter: Any, candidate_index: int,
               lambda_start: Fraction, s_start: Fraction,
               config: dict[str, Any]) -> tuple[dict[str, Any], bool, str | None, int]:
    model.need(lambda_start == model.LAMBDA_PLUS + s_start and s_start > 0,
               "L3 candidate lambda relation")
    policy = config["l3_bprime_route"]
    model.need(policy["max_interval_calls"] == 1 and policy["subdivision_enabled"] is False,
               "L3 Bprime V1 whole-interval policy")
    domain_audit = _domain_audit(lambda_start, config)
    failure: str | None = None
    try:
        leaf = _evaluate(prepared, adapter, model.LAMBDA_PLUS, lambda_start, config)
        leaves = [leaf]
        calls = 1
        certified = bool(leaf["strict_upper_lt_zero"])
        if not certified:
            failure = leaf["failure_reason"]
    except Exception as exc:
        leaves = [{
            "call_index": 0,
            "lambda_interval": model.rational_interval_json(model.LAMBDA_PLUS, lambda_start),
            "Bprime_enclosure": None,
            "strict_upper_lt_zero": False,
            "status": "UNRESOLVED",
            "failure_reason": f"BPRIME_ROUTE_{type(exc).__name__}",
        }]
        calls = 1
        certified = False
        failure = leaves[0]["failure_reason"]

    final_iv = leaves[0]["Bprime_enclosure"] if leaves[0]["Bprime_enclosure"] is not None else None
    record = {
        "record_type": "L3_MONOTONICITY",
        "node": "L3",
        "candidate_index": candidate_index,
        "route_id": ROUTE_ID,
        "policy_id": POLICY_ID,
        "identity_lemma_id": IDENTITY_ID,
        "inference_id": INFERENCE_ID,
        "lambda_plus": model.rational_json(model.LAMBDA_PLUS),
        "s_start": model.rational_json(s_start),
        "lambda_start": model.rational_json(lambda_start),
        "s_domain": model.interval_json(Fraction(0), s_start),
        "stage1_dependency": {
            "source_head": prepared["stage1_source_head"],
            "artifact_zip_sha256": prepared["archive_sha256"],
            "descriptor_sha256": prepared["descriptor_sha256"],
            "certificate_sha256": prepared["certificate_sha256"],
            "manifest_sha256": prepared["manifest_sha256"],
            "bprime_source_sha256": prepared["member_sha256"]["bprime_independent.py"],
            "identity_source_sha256": prepared["member_sha256"]["verify_change_of_variables.py"],
        },
        "stage1_endpoint_evidence": {
            "evaluation_key": "B(206539/100000)",
            "enclosure": prepared["endpoint_enclosure"],
            "strict_upper_lt_zero": True,
        },
        "derivative_policy": {
            "python_flint": policy["python_flint"],
            "dps": policy["dps"],
            "bands": policy["bands"],
            "rel_tol": policy["rel_tol"],
            "eval_limit": policy["eval_limit"],
            "depth_limit": policy["depth_limit"],
            "max_interval_calls": policy["max_interval_calls"],
            "max_subdivision_depth": policy["max_subdivision_depth"],
            "subdivision_enabled": policy["subdivision_enabled"],
        },
        "extended_domain_audit": domain_audit,
        "inherited_branch_guard_audit": prepared["branch_guard_audit"],
        "derivative_proof_domain": model.rational_interval_json(model.LAMBDA_PLUS, lambda_start),
        "derivative_interval_records": leaves,
        "final_Bprime_enclosure": final_iv,
        "Bprime_upper_lt_zero": certified,
        "monotonicity_inference_applied": certified,
        "boundary_identity_applied": certified,
        "direct_F_route_used": False,
        "sampled_or_finite_difference_used": False,
        "float_proof_decision_used": False,
        "final_claim": "H(0,s)<0 on [0,s_start]" if certified else None,
        "certified": certified,
        "failure_reason": None if certified else failure,
    }
    return record, certified, failure, calls
