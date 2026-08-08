#!/usr/bin/env python3
"""Checkpoint-aware source-bound end-to-end driver candidate v2 for Item 3 sweep v9.

STATUS: IMPLEMENTATION CANDIDATE / FULL REHEARSAL NOT AUTHORIZED.

V2 binds the validated kernel and adapter candidates, runner-v2, checker-v2, immutable
checkpoint transaction source, and checkpoint bridge.  Mathematical result bytes exclude
wall-clock/checkpoint timing; timing is written to a separate diagnostic record.
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
import time
from types import ModuleType
from typing import Any


DRIVER_ID = "ITEM3_SWEEP_V9_REHEARSAL_DRIVER_CANDIDATE_V2"
BASE = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/v9_candidate/"

KERNEL_PATH = BASE + "prolate_F_derivatives_cleanroom_v9_candidate.py"
KERNEL_SHA256 = "abac1ce574097df32491aba187694b9800a3f76de9a85df9be0b7995923dab76"
ADAPTER_PATH = BASE + "adapter_v9_candidate_v2.py"
ADAPTER_SHA256 = "8a52b7bfa9491976df2ece4f3858a8bc4b4350222c60840c82fff92e0a05913b"
RUNNER_PATH = BASE + "runner_v9_candidate_v2.py"
RUNNER_SHA256 = "f8f7df69e2693d35879cc7021ca61d21acdfc27aa52cd45635d4d871a6af34e7"
CHECKER_PATH = BASE + "checker_v9_candidate_v2.py"
CHECKER_SHA256 = "b52fe84cf8084ecd55aa43322fb7577861dfde4d76689b587e1863b532c1aa50"
CHECKPOINT_PATH = BASE + "checkpoint_v9_candidate.py"
CHECKPOINT_SHA256 = "253ace8c28c9c5f2d4cb8a9c42b951f759c8f2be619da6845992dca0da10574c"
BRIDGE_PATH = BASE + "checkpoint_bridge_v9_candidate.py"
BRIDGE_SHA256 = "12cd66aeca19d4f7bfaa300ab8ee9fa1f4bbb2f6029a64bd0abb9214770ba797"

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
    try:
        path = (root / relative_path).resolve(strict=True)
    except FileNotFoundError as exc:
        raise DriverContractError("bound source path missing") from exc
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise DriverContractError("source path escapes checkout root") from exc
    if not path.is_file():
        raise DriverContractError("bound source is not regular file")
    return path


def load_bound_module(
    *, checkout_root: Path, relative_path: str, expected_sha256: str, module_name: str
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
    return module, BoundSource(relative_path, expected_sha256, str(path), str(origin), before, after)


def fraction_object(value: Fraction) -> dict[str, str]:
    return {"p": str(value.numerator), "q": str(value.denominator)}


def encode_value(value: Any) -> Any:
    if isinstance(value, Fraction):
        return fraction_object(value)
    if is_dataclass(value):
        return encode_value(asdict(value))
    if isinstance(value, tuple):
        return [encode_value(v) for v in value]
    if isinstance(value, list):
        return [encode_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): encode_value(v) for k, v in value.items()}
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise DriverContractError(f"unsupported mathematical evidence type: {type(value)!r}")


def canonical_json_bytes(value: Any) -> bytes:
    encoded = encode_value(value)
    return (
        json.dumps(encoded, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _bind_all(checkout_root: Path) -> tuple[dict[str, ModuleType], dict[str, BoundSource]]:
    specs = {
        "adapter": (ADAPTER_PATH, ADAPTER_SHA256),
        "runner": (RUNNER_PATH, RUNNER_SHA256),
        "checker": (CHECKER_PATH, CHECKER_SHA256),
        "checkpoint": (CHECKPOINT_PATH, CHECKPOINT_SHA256),
        "bridge": (BRIDGE_PATH, BRIDGE_SHA256),
    }
    modules: dict[str, ModuleType] = {}
    bindings: dict[str, BoundSource] = {}
    for key, (path, digest) in specs.items():
        module, binding = load_bound_module(
            checkout_root=checkout_root,
            relative_path=path,
            expected_sha256=digest,
            module_name=f"item3_v9_driver_v2_{key}",
        )
        modules[key] = module
        bindings[key] = binding
    return modules, bindings


def _fresh_adapters(adapter_mod: ModuleType, checkout_root: Path) -> tuple[Any, Any, Any]:
    kwargs = dict(
        checkout_root=checkout_root,
        kernel_source_path=KERNEL_PATH,
        kernel_source_sha256=KERNEL_SHA256,
        tol="1e-8",
        integration_depth=12,
        integration_limit=200000,
    )
    runner = adapter_mod.V9MeanValueAdapter(
        **kwargs, module_name="item3_v9_driver2_runner_kernel"
    )
    checker50 = adapter_mod.V9MeanValueAdapter(
        **kwargs, module_name="item3_v9_driver2_checker50_kernel"
    )
    checker70 = adapter_mod.V9MeanValueAdapter(
        **kwargs, module_name="item3_v9_driver2_checker70_kernel"
    )
    if len({id(runner), id(checker50), id(checker70)}) != 3:
        raise DriverContractError("runner/checker adapters are not distinct")
    return runner, checker50, checker70


def _require_fresh_output_dir(path: Path) -> None:
    if path.exists():
        if not path.is_dir():
            raise DriverContractError("output path exists and is not directory")
        if any(path.iterdir()):
            raise DriverContractError("rehearsal output directory must be empty")
    else:
        path.mkdir(parents=True)


def execute_rehearsal(
    *, checkout_root: Path, output_dir: Path, max_activations: int = 65536
) -> dict[str, Any]:
    _require_fresh_output_dir(output_dir)
    modules, bindings = _bind_all(checkout_root)
    adapter_mod = modules["adapter"]
    runner_mod = modules["runner"]
    checker_mod = modules["checker"]
    checkpoint_mod = modules["checkpoint"]
    bridge_mod = modules["bridge"]
    runner_adapter, checker50_adapter, checker70_adapter = _fresh_adapters(
        adapter_mod, checkout_root
    )

    checkpoint_root = output_dir / "checkpoint"
    store = checkpoint_mod.CheckpointStore(checkpoint_root)
    cadence = checkpoint_mod.CheckpointCadence(seconds=120.0, attempts=32)
    hook = bridge_mod.ProgressCheckpointHook(store=store, cadence=cadence)

    total_start = time.monotonic()
    runner_start = time.monotonic()
    runner_result = None
    runner_error = None
    try:
        runner_result = runner_mod.run_rehearsal_partition(
            adapter=runner_adapter,
            root_r=ROOT_R,
            root_lambda=ROOT_LAMBDA,
            dps=50,
            max_activations=max_activations,
            progress_hook=hook,
        )
    except Exception as exc:
        runner_error = f"{type(exc).__name__}:{exc}"
        try:
            hook.force_shutdown_checkpoint()
        except Exception as checkpoint_exc:
            runner_error += f";shutdown_checkpoint={type(checkpoint_exc).__name__}:{checkpoint_exc}"
    runner_seconds = time.monotonic() - runner_start

    checker_report = None
    checker_error = None
    checker_seconds = 0.0
    if runner_result is not None and runner_result.terminal_class == "COMPLETE_CANDIDATE":
        checker_start = time.monotonic()
        try:
            checker_report = checker_mod.verify_runner_result(
                runner_result=runner_result,
                control_adapter=checker50_adapter,
                verification_adapter=checker70_adapter,
                dps_control=50,
                dps_verify=70,
            )
        except Exception as exc:
            checker_error = f"{type(exc).__name__}:{exc}"
        checker_seconds = time.monotonic() - checker_start
    elif runner_result is not None:
        try:
            hook.force_shutdown_checkpoint()
        except Exception as checkpoint_exc:
            checker_error = f"shutdown_checkpoint={type(checkpoint_exc).__name__}:{checkpoint_exc}"

    total_seconds = time.monotonic() - total_start
    mathematical_pass = bool(
        runner_result is not None
        and runner_result.terminal_class == "COMPLETE_CANDIDATE"
        and checker_report is not None
        and checker_report.status == "PASS_CANDIDATE"
        and runner_error is None
        and checker_error is None
    )

    source_bindings = {key: encode_value(value) for key, value in bindings.items()}
    source_bindings["kernel"] = {
        "repo_relative_path": KERNEL_PATH,
        "sha256": KERNEL_SHA256,
        "runner_pre": runner_adapter.kernel_identity.pre_import_sha256,
        "runner_post": runner_adapter.kernel_identity.post_import_sha256,
        "checker50_pre": checker50_adapter.kernel_identity.pre_import_sha256,
        "checker50_post": checker50_adapter.kernel_identity.post_import_sha256,
        "checker70_pre": checker70_adapter.kernel_identity.pre_import_sha256,
        "checker70_post": checker70_adapter.kernel_identity.post_import_sha256,
    }

    result = {
        "schema": "ITEM3_SWEEP_V9_REHEARSAL_DRIVER_CANDIDATE_RESULT_V2",
        "driver_id": DRIVER_ID,
        "status": "PASS_CANDIDATE" if mathematical_pass else "NOT_CERTIFIED",
        "root_r": encode_value(ROOT_R),
        "root_lambda": encode_value(ROOT_LAMBDA),
        "source_bindings": source_bindings,
        "runner_result": encode_value(runner_result) if runner_result is not None else None,
        "runner_error": runner_error,
        "checker_report": encode_value(checker_report) if checker_report is not None else None,
        "checker_error": checker_error,
        "checkpoint_commit_count": len(hook.commit_records),
        "checkpoint_last_sha256": (
            hook.commit_records[-1].checkpoint_sha256 if hook.commit_records else None
        ),
        "nonclaim": (
            "PASS_CANDIDATE is not CERTIFIED_LAMBDA_RANGE and is invalid for production "
            "unless the exact source/config/dependency set is approved by the external "
            "V9 freeze receipt."
        ),
    }
    result_bytes = canonical_json_bytes(result)
    result_path = output_dir / "REHEARSAL_DRIVER_CANDIDATE_RESULT.json"
    result_path.write_bytes(result_bytes)
    (output_dir / "REHEARSAL_DRIVER_CANDIDATE_RESULT.json.sha256").write_text(
        hashlib.sha256(result_bytes).hexdigest() + "\n", encoding="ascii"
    )

    timing = {
        "schema": "ITEM3_SWEEP_V9_REHEARSAL_TIMING_DIAGNOSTIC_V1",
        "proof_status": "DIAGNOSTIC_TIMING_ONLY",
        "total_wall_seconds": total_seconds,
        "runner_wall_seconds": runner_seconds,
        "checker_wall_seconds": checker_seconds,
        "checkpoint_wall_seconds": hook.checkpoint_wall_seconds,
        "checkpoint_overhead_ratio": (
            hook.checkpoint_wall_seconds / total_seconds if total_seconds > 0 else None
        ),
    }
    (output_dir / "REHEARSAL_TIMING_DIAGNOSTIC.json").write_text(
        json.dumps(timing, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("CERTIFICATES/prolate/item3_center_connection/lambda_sweep/v9_candidate/rehearsal_v2_output"),
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
