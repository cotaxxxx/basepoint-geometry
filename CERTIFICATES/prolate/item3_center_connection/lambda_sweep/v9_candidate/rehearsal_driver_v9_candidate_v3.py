#!/usr/bin/env python3
"""Canonical shard-config end-to-end driver candidate v3 for Item 3 sweep v9.

STATUS: IMPLEMENTATION CANDIDATE / NOT FROZEN.

The same source and shard config support:
- qualification mode before freeze (no certification claim);
- production mode only with a matching canonical V9 freeze receipt.

The mathematical runner/checker path is identical in both modes.  Checkpoint timing and
wall-clock diagnostics remain outside mathematical evidence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from fractions import Fraction
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import time
from types import ModuleType
from typing import Any


DRIVER_ID = "ITEM3_SWEEP_V9_REHEARSAL_DRIVER_CANDIDATE_V3"
CONFIG_SCHEMA = "ITEM3_SWEEP_V9_SHARD_RUN_CONFIG_V1"
FREEZE_SCHEMA = "ITEM3_SWEEP_V9_FREEZE_RECEIPT_V1"
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
BRIDGE_PATH = BASE + "checkpoint_bridge_v9_candidate_v2.py"
BRIDGE_SHA256 = "59edc8bb73a9e263e8b0b102086ff92dff3898580f92bfe10d6c7216bdfbdebc"
AGGREGATE_VERIFIER_PATH = BASE + "aggregate_verifier_v9_candidate_v2.py"
AGGREGATE_VERIFIER_SHA256 = "bdb0eaa12f241108fbdd03e38cde34d1f1ffe085cff8fef89b413fe4dd255001"

SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
INT_RE = re.compile(r"-?(0|[1-9][0-9]*)\Z")
POS_RE = re.compile(r"[1-9][0-9]*\Z")
SHARD_RE = re.compile(r"S[0-9]{8}\Z")


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


@dataclass(frozen=True)
class ShardConfig:
    shard_id: str
    shard_index: int
    root_r: tuple[Fraction, Fraction]
    lambda_box: tuple[Fraction, Fraction]
    r_floor: Fraction
    lambda_floor: Fraction
    dps_control: int
    dps_verify: int
    max_activations: int
    integration_tol: str
    integration_depth: int
    integration_limit: int
    checkpoint_seconds: int
    checkpoint_attempts: int
    checkpoint_max_payload_bytes: int
    source_sha256: dict[str, str]
    design_sha256: str
    dependency_snapshot_sha256: str
    aggregate_plan_sha256: str
    required_freeze_receipt_schema: str
    config_sha256: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA_RE.fullmatch(value) is None:
        raise DriverContractError(f"{label}: require 64 lowercase hex")
    return value


def parse_rat(value: Any, label: str) -> Fraction:
    if not isinstance(value, dict) or set(value) != {"p", "q"}:
        raise DriverContractError(f"{label}: require exact keys p,q")
    p, q = value["p"], value["q"]
    if not isinstance(p, str) or INT_RE.fullmatch(p) is None:
        raise DriverContractError(f"{label}.p noncanonical")
    if not isinstance(q, str) or POS_RE.fullmatch(q) is None:
        raise DriverContractError(f"{label}.q noncanonical")
    pi, qi = int(p), int(q)
    result = Fraction(pi, qi)
    if result.numerator != pi or result.denominator != qi:
        raise DriverContractError(f"{label}: rational not reduced")
    return result


def parse_interval(value: Any, label: str) -> tuple[Fraction, Fraction]:
    if not isinstance(value, dict) or set(value) != {"lo", "hi"}:
        raise DriverContractError(f"{label}: require exact keys lo,hi")
    lo = parse_rat(value["lo"], label + ".lo")
    hi = parse_rat(value["hi"], label + ".hi")
    if not lo < hi:
        raise DriverContractError(f"{label}: require positive width")
    return lo, hi


def _reject_float(value: Any, where: str = "root") -> None:
    if isinstance(value, float):
        raise DriverContractError(f"binary float prohibited in canonical config: {where}")
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value):
            raise DriverContractError(f"non-string key: {where}")
        for k, v in value.items():
            _reject_float(v, f"{where}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _reject_float(v, f"{where}[{i}]")
    elif value is None or isinstance(value, (str, int, bool)):
        return
    else:
        raise DriverContractError(f"unsupported canonical config type at {where}")


def canonical_json_bytes(value: Any) -> bytes:
    encoded = encode_value(value)
    _reject_float(encoded)
    return (
        json.dumps(encoded, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


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
    if value is None or isinstance(value, (str, int, bool, float)):
        return value
    raise DriverContractError(f"unsupported evidence type: {type(value)!r}")


def load_canonical_json(path: Path) -> tuple[dict[str, Any], bytes, str]:
    raw = path.read_bytes()
    if not raw.endswith(b"\n"):
        raise DriverContractError("canonical JSON file must end in exactly one LF")
    try:
        obj = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise DriverContractError("canonical JSON parse failure") from exc
    if not isinstance(obj, dict):
        raise DriverContractError("canonical JSON top level must be object")
    _reject_float(obj)
    if canonical_json_bytes(obj) != raw:
        raise DriverContractError("JSON file is not canonical byte encoding")
    return obj, raw, sha256_bytes(raw)


def parse_config(path: Path) -> ShardConfig:
    obj, _raw, config_sha = load_canonical_json(path)
    expected_keys = {
        "aggregate_plan_sha256", "checkpoint", "dependency_snapshot_sha256",
        "design_sha256", "dps_control", "dps_verify", "integration",
        "lambda_box", "lambda_floor", "max_activations", "r_floor",
        "required_freeze_receipt_schema", "root_r", "schema", "shard_id",
        "shard_index", "source_sha256",
    }
    if set(obj) != expected_keys:
        raise DriverContractError("config field set mismatch")
    if obj["schema"] != CONFIG_SCHEMA:
        raise DriverContractError("config schema mismatch")
    shard_index = obj["shard_index"]
    if not isinstance(shard_index, int) or isinstance(shard_index, bool) or shard_index < 0:
        raise DriverContractError("shard_index must be nonnegative integer")
    shard_id = obj["shard_id"]
    if not isinstance(shard_id, str) or SHARD_RE.fullmatch(shard_id) is None:
        raise DriverContractError("shard_id syntax mismatch")
    if shard_id != f"S{shard_index:08d}":
        raise DriverContractError("shard_id/index mismatch")

    root_r = parse_interval(obj["root_r"], "root_r")
    lambda_box = parse_interval(obj["lambda_box"], "lambda_box")
    if not (Fraction(0) < root_r[0] < root_r[1] < Fraction(1)):
        raise DriverContractError("root_r outside 0<r<1")
    if not (Fraction(1) <= lambda_box[0] < lambda_box[1]):
        raise DriverContractError("lambda_box outside lambda>=1")
    r_floor = parse_rat(obj["r_floor"], "r_floor")
    lambda_floor = parse_rat(obj["lambda_floor"], "lambda_floor")
    if r_floor != Fraction(1, 1 << 16) or lambda_floor != Fraction(1, 1 << 16):
        raise DriverContractError("v9 floor policy mismatch")

    if obj["dps_control"] != 50 or obj["dps_verify"] != 70:
        raise DriverContractError("dps policy mismatch")
    if obj["max_activations"] != 65536:
        raise DriverContractError("activation budget mismatch")

    integration = obj["integration"]
    if not isinstance(integration, dict) or set(integration) != {"tol", "depth", "limit"}:
        raise DriverContractError("integration field set mismatch")
    if integration != {"tol": "1e-8", "depth": 12, "limit": 200000}:
        raise DriverContractError("integration policy mismatch")

    checkpoint = obj["checkpoint"]
    if not isinstance(checkpoint, dict) or set(checkpoint) != {"seconds", "attempts", "max_payload_bytes"}:
        raise DriverContractError("checkpoint field set mismatch")
    if checkpoint != {"seconds": 120, "attempts": 32, "max_payload_bytes": 33554432}:
        raise DriverContractError("checkpoint policy mismatch")

    sources = obj["source_sha256"]
    source_keys = {"kernel", "adapter", "runner", "checker", "checkpoint", "bridge", "driver", "aggregate_verifier"}
    if not isinstance(sources, dict) or set(sources) != source_keys:
        raise DriverContractError("source_sha256 field set mismatch")
    sources = {k: require_sha(v, f"source_sha256.{k}") for k, v in sources.items()}
    compiled = {
        "kernel": KERNEL_SHA256,
        "adapter": ADAPTER_SHA256,
        "runner": RUNNER_SHA256,
        "checker": CHECKER_SHA256,
        "checkpoint": CHECKPOINT_SHA256,
        "bridge": BRIDGE_SHA256,
        "aggregate_verifier": AGGREGATE_VERIFIER_SHA256,
        "driver": sha256_file(Path(__file__).resolve()),
    }
    if sources != compiled:
        raise DriverContractError("config source hash set does not match compiled driver source set")

    required_schema = obj["required_freeze_receipt_schema"]
    if required_schema != FREEZE_SCHEMA:
        raise DriverContractError("required freeze receipt schema mismatch")

    return ShardConfig(
        shard_id=shard_id,
        shard_index=shard_index,
        root_r=root_r,
        lambda_box=lambda_box,
        r_floor=r_floor,
        lambda_floor=lambda_floor,
        dps_control=50,
        dps_verify=70,
        max_activations=65536,
        integration_tol="1e-8",
        integration_depth=12,
        integration_limit=200000,
        checkpoint_seconds=120,
        checkpoint_attempts=32,
        checkpoint_max_payload_bytes=33554432,
        source_sha256=sources,
        design_sha256=require_sha(obj["design_sha256"], "design_sha256"),
        dependency_snapshot_sha256=require_sha(obj["dependency_snapshot_sha256"], "dependency_snapshot_sha256"),
        aggregate_plan_sha256=require_sha(obj["aggregate_plan_sha256"], "aggregate_plan_sha256"),
        required_freeze_receipt_schema=required_schema,
        config_sha256=config_sha,
    )


def parse_freeze_receipt(path: Path, config: ShardConfig) -> tuple[dict[str, Any], str]:
    obj, _raw, receipt_sha = load_canonical_json(path)
    expected = {
        "aggregate_plan_sha256", "config_sha256", "dependency_snapshot_sha256",
        "design_sha256", "freeze_verdict", "nonclaims",
        "performance_gate_report_sha256", "qualification_manifest_sha256", "schema",
        "source_sha256", "validation_report_sha256",
    }
    if set(obj) != expected:
        raise DriverContractError("freeze receipt field set mismatch")
    if obj["schema"] != FREEZE_SCHEMA or obj["freeze_verdict"] != "V9_FROZEN_APPROVED":
        raise DriverContractError("freeze receipt schema/verdict mismatch")
    if obj["config_sha256"] != config.config_sha256:
        raise DriverContractError("freeze receipt config hash mismatch")
    if obj["design_sha256"] != config.design_sha256:
        raise DriverContractError("freeze receipt design hash mismatch")
    if obj["dependency_snapshot_sha256"] != config.dependency_snapshot_sha256:
        raise DriverContractError("freeze receipt dependency hash mismatch")
    if obj["aggregate_plan_sha256"] != config.aggregate_plan_sha256:
        raise DriverContractError("freeze receipt aggregate-plan hash mismatch")
    if obj["source_sha256"] != config.source_sha256:
        raise DriverContractError("freeze receipt source hash mismatch")
    for key in (
        "qualification_manifest_sha256", "validation_report_sha256",
        "performance_gate_report_sha256",
    ):
        require_sha(obj[key], key)
    if not isinstance(obj["nonclaims"], list) or not all(isinstance(x, str) for x in obj["nonclaims"]):
        raise DriverContractError("freeze receipt nonclaims must be string list")
    return obj, receipt_sha


def resolve_contained(root: Path, relative_path: str) -> Path:
    root = root.resolve(strict=True)
    path = (root / relative_path).resolve(strict=True)
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
    require_sha(expected_sha256, "expected source hash")
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
            checkout_root=checkout_root, relative_path=path,
            expected_sha256=digest, module_name=f"item3_v9_driver3_{key}",
        )
        modules[key] = module
        bindings[key] = binding
    return modules, bindings


def _fresh_adapters(adapter_mod: ModuleType, checkout_root: Path, config: ShardConfig) -> tuple[Any, Any, Any]:
    kwargs = dict(
        checkout_root=checkout_root,
        kernel_source_path=KERNEL_PATH,
        kernel_source_sha256=KERNEL_SHA256,
        tol=config.integration_tol,
        integration_depth=config.integration_depth,
        integration_limit=config.integration_limit,
    )
    return (
        adapter_mod.V9MeanValueAdapter(**kwargs, module_name="item3_v9_driver3_runner_kernel"),
        adapter_mod.V9MeanValueAdapter(**kwargs, module_name="item3_v9_driver3_checker50_kernel"),
        adapter_mod.V9MeanValueAdapter(**kwargs, module_name="item3_v9_driver3_checker70_kernel"),
    )


def _require_fresh_output_dir(path: Path) -> None:
    if path.exists():
        if not path.is_dir() or any(path.iterdir()):
            raise DriverContractError("output directory must be fresh and empty")
    else:
        path.mkdir(parents=True)


def execute_shard(
    *, checkout_root: Path, config_path: Path, output_dir: Path,
    qualification_mode: bool, freeze_receipt_path: Path | None,
) -> dict[str, Any]:
    config = parse_config(config_path)
    freeze_receipt = None
    freeze_receipt_sha = None
    if qualification_mode:
        if freeze_receipt_path is not None:
            raise DriverContractError("qualification mode must not consume freeze receipt")
        authorization = "QUALIFICATION_ONLY"
    else:
        if freeze_receipt_path is None:
            raise DriverContractError("production mode requires freeze receipt")
        freeze_receipt, freeze_receipt_sha = parse_freeze_receipt(freeze_receipt_path, config)
        authorization = "FROZEN_PRODUCTION"

    _require_fresh_output_dir(output_dir)
    modules, bindings = _bind_all(checkout_root)
    runner_adapter, checker50, checker70 = _fresh_adapters(modules["adapter"], checkout_root, config)
    if len({id(runner_adapter), id(checker50), id(checker70)}) != 3:
        raise DriverContractError("adapter instances are not distinct")

    run_context = {
        "aggregate_plan_sha256": config.aggregate_plan_sha256,
        "authorization": authorization,
        "config_sha256": config.config_sha256,
        "dependency_snapshot_sha256": config.dependency_snapshot_sha256,
        "design_sha256": config.design_sha256,
        "freeze_receipt_sha256": freeze_receipt_sha,
        "shard_id": config.shard_id,
        "shard_index": config.shard_index,
        "source_sha256": config.source_sha256,
    }
    store = modules["checkpoint"].CheckpointStore(
        output_dir / "checkpoint", max_payload_bytes=config.checkpoint_max_payload_bytes
    )
    cadence = modules["checkpoint"].CheckpointCadence(
        seconds=config.checkpoint_seconds, attempts=config.checkpoint_attempts
    )
    hook = modules["bridge"].ProgressCheckpointHook(
        store=store, cadence=cadence, run_context=run_context
    )

    total_start = time.monotonic()
    runner_start = time.monotonic()
    runner_result = None
    runner_error = None
    try:
        runner_result = modules["runner"].run_rehearsal_partition(
            adapter=runner_adapter,
            root_r=config.root_r,
            root_lambda=config.lambda_box,
            dps=config.dps_control,
            max_activations=config.max_activations,
            r_floor=config.r_floor,
            lambda_floor=config.lambda_floor,
            progress_hook=hook,
        )
    except Exception as exc:
        runner_error = f"{type(exc).__name__}:{exc}"
        try:
            hook.force_shutdown_checkpoint()
        except Exception as cp_exc:
            runner_error += f";shutdown_checkpoint={type(cp_exc).__name__}:{cp_exc}"
    runner_seconds = time.monotonic() - runner_start

    checker_report = None
    checker_error = None
    checker_seconds = 0.0
    if runner_result is not None and runner_result.terminal_class == "COMPLETE_CANDIDATE":
        checker_start = time.monotonic()
        try:
            checker_report = modules["checker"].verify_runner_result(
                runner_result=runner_result,
                control_adapter=checker50,
                verification_adapter=checker70,
                dps_control=config.dps_control,
                dps_verify=config.dps_verify,
                r_floor=config.r_floor,
                lambda_floor=config.lambda_floor,
            )
        except Exception as exc:
            checker_error = f"{type(exc).__name__}:{exc}"
        checker_seconds = time.monotonic() - checker_start
    elif runner_result is not None:
        try:
            hook.force_shutdown_checkpoint()
        except Exception as cp_exc:
            checker_error = f"shutdown_checkpoint={type(cp_exc).__name__}:{cp_exc}"

    total_seconds = time.monotonic() - total_start
    mathematical_pass = bool(
        runner_result is not None
        and runner_result.terminal_class == "COMPLETE_CANDIDATE"
        and checker_report is not None
        and checker_report.status == "PASS_CANDIDATE"
        and runner_error is None and checker_error is None
    )
    result_status = (
        "QUALIFICATION_PASS_CANDIDATE" if qualification_mode and mathematical_pass
        else "SHARD_PASS_CANDIDATE" if (not qualification_mode and mathematical_pass)
        else "NOT_CERTIFIED"
    )

    source_bindings = {key: encode_value(value) for key, value in bindings.items()}
    source_bindings["kernel"] = {
        "repo_relative_path": KERNEL_PATH,
        "sha256": KERNEL_SHA256,
        "runner_pre": runner_adapter.kernel_identity.pre_import_sha256,
        "runner_post": runner_adapter.kernel_identity.post_import_sha256,
        "checker50_pre": checker50.kernel_identity.pre_import_sha256,
        "checker50_post": checker50.kernel_identity.post_import_sha256,
        "checker70_pre": checker70.kernel_identity.pre_import_sha256,
        "checker70_post": checker70.kernel_identity.post_import_sha256,
    }

    result = {
        "schema": "ITEM3_SWEEP_V9_SHARD_EVIDENCE_CANDIDATE_V1",
        "driver_id": DRIVER_ID,
        "status": result_status,
        "authorization": authorization,
        "config_sha256": config.config_sha256,
        "aggregate_plan_sha256": config.aggregate_plan_sha256,
        "design_sha256": config.design_sha256,
        "dependency_snapshot_sha256": config.dependency_snapshot_sha256,
        "freeze_receipt_sha256": freeze_receipt_sha,
        "shard_id": config.shard_id,
        "shard_index": config.shard_index,
        "root_r": encode_value(config.root_r),
        "lambda_box": encode_value(config.lambda_box),
        "source_bindings": source_bindings,
        "runner_result": encode_value(runner_result) if runner_result is not None else None,
        "runner_error": runner_error,
        "checker_report": encode_value(checker_report) if checker_report is not None else None,
        "checker_error": checker_error,
        "checkpoint_commit_count": len(hook.commit_records),
        "checkpoint_last_sha256": hook.commit_records[-1].checkpoint_sha256 if hook.commit_records else None,
        "nonclaim": (
            "A shard evidence candidate is not CERTIFIED_LAMBDA_RANGE. Aggregate and freeze "
            "gates remain external to this driver."
        ),
    }
    result_bytes = canonical_json_bytes(result)
    result_path = output_dir / "SHARD_EVIDENCE_CANDIDATE.json"
    result_path.write_bytes(result_bytes)
    (output_dir / "SHARD_EVIDENCE_CANDIDATE.json.sha256").write_text(
        sha256_bytes(result_bytes) + "\n", encoding="ascii"
    )

    timing = {
        "schema": "ITEM3_SWEEP_V9_SHARD_TIMING_DIAGNOSTIC_V1",
        "proof_status": "DIAGNOSTIC_TIMING_ONLY",
        "total_wall_seconds": total_seconds,
        "runner_wall_seconds": runner_seconds,
        "checker_wall_seconds": checker_seconds,
        "checkpoint_wall_seconds": hook.checkpoint_wall_seconds,
        "checkpoint_overhead_ratio": hook.checkpoint_wall_seconds / total_seconds if total_seconds > 0 else None,
    }
    (output_dir / "SHARD_TIMING_DIAGNOSTIC.json").write_text(
        json.dumps(timing, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout-root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--qualification-mode", action="store_true")
    parser.add_argument("--freeze-receipt", type=Path)
    args = parser.parse_args()
    result = execute_shard(
        checkout_root=args.checkout_root,
        config_path=args.config,
        output_dir=args.output_dir,
        qualification_mode=args.qualification_mode,
        freeze_receipt_path=args.freeze_receipt,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["status"] in {"QUALIFICATION_PASS_CANDIDATE", "SHARD_PASS_CANDIDATE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
