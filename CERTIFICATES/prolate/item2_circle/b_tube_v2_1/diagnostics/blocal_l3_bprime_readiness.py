#!/usr/bin/env python3
import argparse
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import tempfile
import time
import zipfile

from flint import acb, arb, ctx
import flint
import sympy as sp

ROUTE_ID = "BLOCAL_L3_STAGE1_ENDPOINT_PLUS_BPRIME_MONOTONICITY_V1"
POLICY_ID = "BLOCAL_L3_BPRIME_STAGE1_POLICY_V1"
DOMAIN_AUDIT_ID = "BLOCAL_L3_BPRIME_EXTENSION_DOMAIN_AUDIT_V1"
BRANCH_GUARD_AUDIT_ID = "INHERITED_STAGE1_ANALYTIC_BRANCH_GUARDS_V1"
IDENTITY_ID = "BLOCAL_L3_BOUNDARY_IDENTITY_B_EQ_F_R1_V1"

ROOT = Path(__file__).resolve().parents[5]
BTUBE = ROOT / "CERTIFICATES/prolate/item2_circle/b_tube_v2_1"
RUN_CONFIG = BTUBE / "config.blocal-v2.2-run.json"
STAGE1_CONFIG = BTUBE / "config.blocal-stage1.json"
STAGE1_ZIP = BTUBE / "dependencies/blocal-stage1-boundary-entry.zip"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def fail(msg: str):
    raise RuntimeError(msg)


def exact_symbolic_domain_audit(lambda_lo_num: int, lambda_lo_den: int, lambda_hi_num: int, lambda_hi_den: int):
    # Exact algebraic identities in contact-centred variables.
    t, q, lam = sp.symbols("t q lam", nonnegative=True)
    T = t**2
    d = lam**2 - 1
    c2 = 4*T*(1-T)*q
    m = 2*T
    u = 1 - 2*T
    A = 1 + d*(1-T)*q
    J = 1 + d*(1-2*T)*q
    N = d*c2 + 2*m
    K = d*c2*u + m*(2-m)
    W = lam**2 - d*c2

    checks = {
        "N_EQ_4T_A": sp.expand(N - 4*T*A),
        "K_EQ_4T1MT_J": sp.expand(K - 4*T*(1-T)*J),
        "W_EQ_LAM2_1MC2_PLUS_C2": sp.expand(W - (lam**2*(1-c2) + c2)),
    }
    if any(v != 0 for v in checks.values()):
        fail(f"symbolic identity failure: {checks}")

    # Prove x^2 <= 1 for x = lam*t/(sqrt(W)*sqrt(A)).
    # W*A-lam^2*T = (1-T)*R(T,q,d), and R is concave in q.
    D = sp.symbols("D", nonnegative=True)
    TT, QQ = sp.symbols("TT QQ", nonnegative=True)
    R = (
        4*QQ**2*TT**2*D**2
        - 4*QQ**2*TT*D**2
        - 4*QQ*TT*D
        + QQ*D**2
        + QQ*D
        + D
        + 1
    )
    factor_check = sp.expand(
        (1-TT) * R
        - ((1 + D - D*(4*TT*(1-TT)*QQ)) * (1 + D*(1-TT)*QQ) - (1+D)*TT)
    )
    if factor_check != 0:
        fail("x-range factor identity failed")
    r_q0 = sp.factor(R.subs(QQ, 0))
    r_q1 = sp.factor(R.subs(QQ, 1))
    q2_coeff = sp.Poly(R, QQ).coeff_monomial(QQ**2)
    if sp.expand(r_q0 - (D+1)) != 0:
        fail("R(q=0) identity failed")
    if sp.expand(r_q1 - (2*TT*D-D-1)**2) != 0:
        fail("R(q=1) square identity failed")
    if sp.expand(q2_coeff - 4*TT*(TT-1)*D**2) != 0:
        fail("R q^2 coefficient identity failed")

    # Exact rational check that the whole admitted lambda interval is > 1.
    if lambda_lo_num <= lambda_lo_den:
        fail("lambda lower endpoint is not > 1")
    if lambda_hi_num * lambda_lo_den <= lambda_lo_num * lambda_hi_den:
        fail("lambda interval is not strictly increasing")

    return {
        "audit_id": DOMAIN_AUDIT_ID,
        "status": "PASS",
        "lambda_gt_1_exact": True,
        "A_lower_bound": "A=1+(lambda^2-1)(1-T)q >= 1",
        "W_lower_bound": "W=lambda^2(1-c2)+c2 >= 1",
        "c2_range": "c2=4T(1-T)q in [0,1]",
        "x_range_proof": {
            "claim": "0 <= x <= 1",
            "factor": "W*A-lambda^2*T=(1-T)R",
            "R_q_concavity": "coeff(q^2)=4*T*(T-1)*D^2 <= 0",
            "R_q0": "D+1 > 0",
            "R_q1": "(2*T*D-D-1)^2 >= 0",
            "conclusion": "W*A-lambda^2*T >= 0",
        },
        "angle_data_domain": "x in [0,1], z=1-x^2 in [0,1]; x=1 endpoint handled by hypergeometric branch",
        "symbolic_checks": {k: str(v) for k, v in checks.items()},
        "sympy_version": sp.__version__,
    }


def audit_float_guards(source_text: str):
    tree = ast.parse(source_text)
    locations = []
    stack = []

    class V(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == "float":
                locations.append({"function": stack[-1] if stack else None, "lineno": node.lineno})
            self.generic_visit(node)

    V().visit(tree)
    allowed = {"_abs_upper", "_h_data"}
    bad = [x for x in locations if x["function"] not in allowed]
    if bad:
        fail(f"unexpected float call(s) in pinned bprime source: {bad}")
    if len(locations) != 3:
        fail(f"expected exactly 3 inherited float guards, found {len(locations)}: {locations}")
    return {
        "audit_id": BRANCH_GUARD_AUDIT_ID,
        "status": "PASS",
        "float_call_count": len(locations),
        "locations": locations,
        "allowed_functions": sorted(allowed),
        "proof_decision_use": False,
    }


class Tee(io.TextIOBase):
    def __init__(self, *streams):
        self.streams = streams
    def write(self, s):
        for st in self.streams:
            st.write(s)
            st.flush()
        return len(s)
    def flush(self):
        for st in self.streams:
            st.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="readiness-out")
    args = ap.parse_args()
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    run_cfg_bytes = RUN_CONFIG.read_bytes()
    run_cfg = json.loads(run_cfg_bytes)
    s1 = run_cfg["stage1_dependency"]

    if sha256_file(STAGE1_ZIP) != s1["artifact_zip_sha256"]:
        fail("Stage-1 ZIP SHA-256 mismatch")
    if sha256_file(STAGE1_CONFIG) != s1["config_sha256"]:
        fail("Stage-1 descriptor SHA-256 mismatch")

    stage1_cfg = json.loads(STAGE1_CONFIG.read_text())
    if stage1_cfg["content_audit_status"] != "STAGE1_CONTENT_AUDITED":
        fail("Stage-1 content audit status mismatch")
    if stage1_cfg["source_head"] != s1["source_head"]:
        fail("Stage-1 source head mismatch")

    zip_sha = sha256_file(STAGE1_ZIP)
    member_hashes = {}
    with zipfile.ZipFile(STAGE1_ZIP, "r") as zf:
        names = sorted(zf.namelist())
        if names != sorted(stage1_cfg["archive_members"]):
            fail(f"Stage-1 ZIP member list mismatch: {names}")
        for name in names:
            data = zf.read(name)
            got = sha256_bytes(data)
            want = stage1_cfg.get("payload_sha256", {}).get(name)
            if want is not None and got != want:
                fail(f"Stage-1 member SHA mismatch for {name}: {got} != {want}")
            member_hashes[name] = got
        bprime_bytes = zf.read("bprime_independent.py")
        if sha256_bytes(bprime_bytes) != stage1_cfg["payload_sha256"]["bprime_independent.py"]:
            fail("bprime_independent.py payload mismatch")
        cert_bytes = zf.read("certificate_item2_independent.json")
        if sha256_bytes(cert_bytes) != s1["certificate_sha256"]:
            fail("Stage-1 certificate payload mismatch")
        manifest_bytes = zf.read("SHA256SUMS.txt")
        if sha256_bytes(manifest_bytes) != s1["manifest_sha256"]:
            fail("Stage-1 manifest payload mismatch")
        verify_bytes = zf.read("verify_change_of_variables.py")
        if sha256_bytes(verify_bytes) != stage1_cfg["payload_sha256"]["verify_change_of_variables.py"]:
            fail("verify_change_of_variables.py payload mismatch")

    branch_guard_audit = audit_float_guards(bprime_bytes.decode("utf-8"))

    # Exact candidate interval [lambda_plus, lambda_plus+2^-9].
    lo_num, lo_den = 206539, 100000
    # 206539/100000 + 1/512 = 3307749/1600000.
    hi_num, hi_den = 3307749, 1600000
    domain_audit = exact_symbolic_domain_audit(lo_num, lo_den, hi_num, hi_den)
    domain_audit["identity_provenance"] = {
        "identity_id": IDENTITY_ID,
        "pinned_verify_change_of_variables_sha256": member_hashes["verify_change_of_variables.py"],
        "replayed_exact_identities": ["N=4T*A", "K=4T(1-T)J", "W=lambda^2(1-c2)+c2"],
    }

    with tempfile.TemporaryDirectory(prefix="stage1-bprime-") as td:
        td = Path(td)
        with zipfile.ZipFile(STAGE1_ZIP, "r") as zf:
            zf.extract("bprime_independent.py", td)
        bprime_path = td / "bprime_independent.py"
        if sha256_file(bprime_path) != stage1_cfg["payload_sha256"]["bprime_independent.py"]:
            fail("extracted bprime source mismatch")

        spec = importlib.util.spec_from_file_location("stage1_bprime_pinned", bprime_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if sha256_file(Path(mod.__file__).resolve()) != stage1_cfg["payload_sha256"]["bprime_independent.py"]:
            fail("imported bprime origin/re-hash mismatch")

        ctx.dps = 18
        mod._init_consts()
        lam_lo = arb(lo_num) / arb(lo_den)
        lam_hi = arb(hi_num) / arb(hi_den)
        lam_ball = lam_lo.union(lam_hi)

        transcript_buf = io.StringIO()
        tee = Tee(sys.stdout, transcript_buf)
        t0 = time.time()
        with contextlib.redirect_stdout(tee):
            print(f"READINESS route={ROUTE_ID}")
            print(f"policy={POLICY_ID}")
            print(f"lambda_ball={lam_ball.str(30, radius=True)}")
            result = mod.Bprime(
                lam_ball,
                bands=4,
                rel_tol=arb(2) ** -18,
                eval_limit=8000,
                depth_limit=22,
            )
        elapsed = time.time() - t0

    re = result.real
    lo = arb(re.lower())
    up = arb(re.upper())
    strict_negative = bool(up < 0)
    if not strict_negative:
        fail(f"Bprime readiness did not separate negative: {re.str(30, radius=True)}")

    transcript = transcript_buf.getvalue()
    (outdir / "bprime-transcript.txt").write_text(transcript, encoding="utf-8")

    record = {
        "schema": "blocal-l3-bprime-readiness-v1",
        "certificate_evidence": False,
        "evidence_role": "READINESS_DESIGN_ONLY",
        "route_id": ROUTE_ID,
        "policy_id": POLICY_ID,
        "domain_audit": domain_audit,
        "branch_guard_audit": branch_guard_audit,
        "stage1": {
            "source_head": s1["source_head"],
            "artifact_zip_sha256": zip_sha,
            "descriptor_sha256": sha256_file(STAGE1_CONFIG),
            "certificate_sha256": s1["certificate_sha256"],
            "manifest_sha256": s1["manifest_sha256"],
            "bprime_source_sha256": member_hashes["bprime_independent.py"],
            "member_sha256": member_hashes,
        },
        "lambda_domain": {
            "lo": {"p": str(lo_num), "q": str(lo_den)},
            "hi": {"p": str(hi_num), "q": str(hi_den)},
            "display": "[lambda_plus, lambda_plus+2^-9]",
        },
        "runtime": {
            "python": platform.python_version(),
            "python_flint": getattr(flint, "__version__", "unknown"),
            "sympy": sp.__version__,
            "dps": 18,
            "bands": 4,
            "rel_tol": "2^-18",
            "eval_limit": 8000,
            "depth_limit": 22,
            "elapsed_seconds": f"{elapsed:.6f}",
            "pid": os.getpid(),
            "single_process": True,
        },
        "Bprime": {
            "ball": re.str(40, radius=True),
            "lower": lo.str(35),
            "upper": up.str(35),
            "strict_upper_lt_zero": strict_negative,
        },
        "transcript_sha256": sha256_bytes(transcript.encode("utf-8")),
        "status": "GREEN" if strict_negative else "RED",
    }
    record_path = outdir / "l3-bprime-readiness.json"
    record_path.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    hashes = []
    for p in sorted(outdir.iterdir()):
        if p.is_file() and p.name != "SHA256SUMS.txt":
            hashes.append(f"{sha256_file(p)}  {p.name}")
    (outdir / "SHA256SUMS.txt").write_text("\n".join(hashes) + "\n", encoding="utf-8")

    print(f"Bprime = {re.str(30, radius=True)}")
    print(f"upper   = {up.str(25)}")
    print(f"elapsed = {elapsed:.1f}s")
    print("L3 BPRIME READINESS GREEN")


if __name__ == "__main__":
    main()
