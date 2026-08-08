#!/usr/bin/env python3
"""Source-bound end-to-end driver candidate for Item 3 sweep v9.

STATUS: IMPLEMENTATION CANDIDATE / FULL REHEARSAL NOT AUTHORIZED.

This driver binds exact candidate bytes for adapter, runner, checker and kernel.  It can
execute the exact first rehearsal only after an external workflow/config explicitly
invokes `main`.  Merely importing or auditing this source performs no mathematical work.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from fractions import Fraction
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Any


DRIVER_ID = "ITEM3_SWEEP_V9_REHEARSAL_DRIVER_CANDIDATE_V1"

KERNEL_PATH = (
    "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/v9_candidate/"
    "prolate_F_derivatives_cleanroom_v9_candidate.py"
)
KERNEL_SHA256 = "abac1ce574097df32491aba187694b9800a3f76de9a85df9be0b7995923dab76"

ADAPTER_PATH = (
    "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/v9_candidate/"
    "adapter_v9_candidate_v2.py"
)
ADAPTER_SHA256 = "8a52b7bfa9491976df2ece4f3858a8bc4b4350222c60840c82fff92e0a05913b"

RUNNER_PATH = (
    "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/v9_candidate/"
    "runner_v9_candidate.py"
)
RUNNER_SHA256 = "53c1565fcb6880232c136a18aeb782b32533b94701a7af03ecbb578db02fe693"

CHECKER_PATH = (
    "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/v9_candidate/"
    "checker_v9_candidate.py"
)
CHECKER_SHA256 = "aef72166fd16ae8bfa2b07e2d7e146ad24ba9767e0a14c78795de43f56e3a434"

ROOT_R = (Fraction(1, 64), Fraction(11, 256))
ROOT_LAMBDA = (Fraction(123731943, 26214400), Fraction(118, 25))


class DriverContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class BoundSource:
    repo_relative_path: str
    sha256: str
    resolved_path: str
    module_origin: str
    pre_import_sha256: str
    post_import_sha256: str


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_contained(root: Path, relative_path: str) -> Path:
    root = root.resolve(strict=True)
    path = (root / relative_path).resolve(strict=True)
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise DriverContractError("source path escapes checkout root") from exc
    if not path.is_file():
        raise DriverContractError("bound source is not a regular file")
    return path


def load_bound_module(
    *,
    checkout_root: Path,
    relative_path: str,
    expected_sha256: str,
    module_name: str,
) -> tuple[ModuleType, BoundSource]:
    if len(expected_sha256) != 64 or any(c not in "0123456789abcdef" for c in expected_sha256):
        raise DriverContractError("expected SHA-256 must be 64 lowercase hex")
    if module_name in sys.modules:
        raise DriverContractError("bound module name already exists")
    path = resolve_contained(checkout_root, relative_path)
    before = sha256_file(path)
    if before != expected_sha256:
        raise DriverContractError(f"pre-import hash mismatch: {relative_path}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise DriverContractError("unable to construct import spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    origin_text = module.__spec__.origin if module.__spec__ is not None else None
    if not origin_text:
        raise DriverContractError("bound module has no origin")
    origin = Path(origin_text).resolve(strict=True)
    if origin != path:
        raise DriverContractError("bound module origin mismatch")
    after = sha256_file(path)
    if after != before:
        raise DriverContractError("bound source changed during import")
    return module, BoundSource(
        relative_path,
        expected_sha256,
        str(path),
        str(origin),
        before,
        after,
    )


def fraction_object(value: Fraction) -> dict[str, str]:
    return {"p": str(value.numerator), "q": str(value.denominator)}


def encode_value(value: Any) -> Any:
    if isinstance(value, Fraction):
        return fraction_object(value)
    if isinstance(value, tuple):
        return [encode_value(v) for v in value]
    if isinstance(value, list):
        return [encode_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): encode_value(v) for k, v in value.items()}
    if is_dataclass(value):
        return encode_value(asdict(value))
    # Adapter CanonicalInterval is a dataclass from a dynamically loaded module and is
    # already covered by is_dataclass.  Primitive strings/ints/bools/None pass through.
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise DriverContractError(f"unsupported evidence type: {type(value)!r}")


def canonical_json_bytes(obj: Any) -> bytes:
    return (json.dumps(encode_value(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def execute_rehearsal(
    *,
    checkout_root: Path,
    output_dir: Path,
    tol: str = "1e-8",
    integration_depth: int = 12,
    integration_limit: int = 200000,
    max_activations: int = 65536,
) -> dict[str, Any]:
    adapter_mod, adapter_bound = load_bound_module(
        checkout_root=checkout_root,
        relative_path=ADAPTER_PATH,
        expected_sha256=ADAPTER_SHA256,
        module_name="item3_v9_bound_adapter_candidate_v2",
    )
    runner_mod, runner_bound = load_bound_module(
        checkout_root=checkout_root,
        relative_path=RUNNER_PATH,
        expected_sha256=RUNNER_SHA256,
        module_name="item3_v9_bound_runner_candidate",
    )
    checker_mod, checker_bound = load_bound_module(
        checkout_root=checkout_root,
        relative_path=CHECKER_PATH,
        expected_sha256=CHECKER_SHA256,
        module_name="item3_v9_bound_checker_candidate",
    )

    adapter_kwargs = dict(
        checkout_root=checkout_root,
        kernel_source_path=KERNEL_PATH,
        kernel_source_sha256=KERNEL_SHA256,
        tol=tol,
        integration_depth=integration_depth,
        integration_limit=integration_limit,
    )
    runner_adapter = adapter_mod.V9MeanValueAdapter(
        **adapter_kwargs, module_name="item3_v9_runner_kernel_candidate"
    )
    checker_control_adapter = adapter_mod.V9MeanValueAdapter(
        **adapter_kwargs, module_name="item3_v9_checker50_kernel_candidate"
    )
    checker_verify_adapter = adapter_mod.V9MeanValueAdapter(
        **adapter_kwargs, module_name="item3_v9_checker70_kernel_candidate"
    )
    if len({id(runner_adapter), id(checker_control_adapter), id(checker_verify_adapter)}) != 3:
        raise DriverContractError("runner/checker adapters are not distinct instances")

    runner_result = runner_mod.run_rehearsal_partition(
        adapter=runner_adapter,
        root_r=ROOT_R,
        root_lambda=ROOT_LAMBDA,
        dps=50,
        max_activations=max_activations,
    )

    checker_report = None
    checker_error = None
    if runner_result.terminal_class == "COMPLETE_CANDIDATE":
        try:
            checker_report = checker_mod.verify_runner_result(
                runner_result=runner_result,
                control_adapter=checker_control_adapter,
                verification_adapter=checker_verify_adapter,
                dps_control=50,
                dps_verify=70,
            )
        except Exception as exc:
            checker_error = f"{type(exc).__name__}:{exc}"

    source_bindings = {
        "adapter": encode_value(adapter_bound),
        "runner": encode_value(runner_bound),
        "checker": encode_value(checker_bound),
        "kernel": {
            "repo_relative_path": KERNEL_PATH,
            "sha256": KERNEL_SHA256,
            "runner_pre": runner_adapter.kernel_identity.pre_import_sha256,
            "runner_post": runner_adapter.kernel_identity.post_import_sha256,
            "checker50_pre": checker_control_adapter.kernel_identity.pre_import_sha256,
            "checker50_post": checker_control_adapter.kernel_identity.post_import_sha256,
            "checker70_pre": checker_verify_adapter.kernel_identity.pre_import_sha256,
            "checker70_post": checker_verify_adapter.kernel_identity.post_import_sha256,
        },
    }

    mathematical_pass = bool(
        runner_result.terminal_class == "COMPLETE_CANDIDATE"
        and checker_report is not None
        and checker_report.status == "PASS_CANDIDATE"
    )
    aggregate = {
        "schema": "ITEM3_SWEEP_V9_REHEARSAL_DRIVER_CANDIDATE_RESULT_V1",
        "driver_id": DRIVER_ID,
        "status": "PASS_CANDIDATE" if mathematical_pass else "NOT_CERTIFIED",
        "root_r": encode_value(ROOT_R),
        "root_lambda": encode_value(ROOT_LAMBDA),
        "source_bindings": source_bindings,
        "runner_result": encode_value(runner_result),
        "checker_report": encode_value(checker_report) if checker_report is not None else None,
        "checker_error": checker_error,
        "nonclaim": (
            "This candidate result is not CERTIFIED_LAMBDA_RANGE and cannot authorize "
            "publication or a production theorem claim before the final freeze receipt."
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / "REHEARSAL_DRIVER_CANDIDATE_RESULT.json"
    result_bytes = canonical_json_bytes(aggregate)
    result_path.write_bytes(result_bytes)
    (output_dir / "REHEARSAL_DRIVER_CANDIDATE_RESULT.json.sha256").write_text(
        hashlib.sha256(result_bytes).hexdigest() + "\n", encoding="ascii"
    )
    return aggregate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("CERTIFICATES/prolate/item3_center_connection/lambda_sweep/v9_candidate/rehearsal_candidate_output"),
    )
    parser.add_argument("--max-activations", type=int, default=65536)
    args = parser.parse_args()
    result = execute_rehearsal(
        checkout_root=args.checkout_root,
        output_dir=args.output_dir,
        max_activations=args.max_activations,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["status"] == "PASS_CANDIDATE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
