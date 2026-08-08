#!/usr/bin/env python3
"""Exact multi-run aggregate verifier candidate v2 for Item 3 sweep v9.

STATUS: IMPLEMENTATION CANDIDATE / NOT FROZEN.

The verifier is stdlib-only.  It validates a canonical shard plan, one canonical config,
freeze receipt and production shard-evidence object per shard, exact lambda coverage,
positive-width adjacent root-window overlap, selected evidence identities, fresh-checker
proof records, and a raw32/big-endian selected-shard hash chain.

The run-to-run connection rule is the multi-run analogue of v8.1 S6: at a shared closed
lambda endpoint, each adjacent shard proves a unique zero in its own root window and
G_r<0 on that window.  Positive-width overlap makes the union connected, so strict
decrease on the union permits at most one zero; the two shard zeros are therefore the
same zero.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import struct
from typing import Any, Sequence


VERIFIER_ID = "ITEM3_SWEEP_V9_AGGREGATE_VERIFIER_CANDIDATE_V2"
PLAN_SCHEMA = "ITEM3_SWEEP_V9_SHARD_PLAN_V2"
CONFIG_SCHEMA = "ITEM3_SWEEP_V9_SHARD_RUN_CONFIG_V1"
FREEZE_SCHEMA = "ITEM3_SWEEP_V9_FREEZE_RECEIPT_V1"
EVIDENCE_SCHEMA = "ITEM3_SWEEP_V9_SHARD_EVIDENCE_CANDIDATE_V2"
PROVENANCE_SCHEMA = "ITEM3_SWEEP_V9_SHARD_PROVENANCE_V1"
AGGREGATE_SCHEMA = "ITEM3_SWEEP_V9_AGGREGATE_VERDICT_V2"
CHAIN_DOMAIN = b"ITEM3_SWEEP_V9_SELECTED_SHARD_CHAIN_V2\0"
SOURCE_KEYS = {
    "kernel", "adapter", "runner", "checker", "checkpoint", "bridge", "driver",
    "aggregate_verifier",
}
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
INT_RE = re.compile(r"-?(0|[1-9][0-9]*)\Z")
POS_RE = re.compile(r"[1-9][0-9]*\Z")
SHARD_RE = re.compile(r"S[0-9]{8}\Z")
ZERO_SHA = "0" * 64


class AggregateReject(RuntimeError):
    pass


@dataclass(frozen=True)
class PlannedShard:
    shard_index: int
    shard_id: str
    lambda_box: tuple[Fraction, Fraction]
    root_r: tuple[Fraction, Fraction]
    raw_lambda_box: dict[str, Any]
    raw_root_r: dict[str, Any]


@dataclass(frozen=True)
class Plan:
    total_lambda_range: tuple[Fraction, Fraction]
    ordered_shards: tuple[PlannedShard, ...]
    source_sha256: dict[str, str]
    design_sha256: str
    dependency_snapshot_sha256: str
    policy: dict[str, Any]
    plan_sha256: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA_RE.fullmatch(value) is None:
        raise AggregateReject(f"{label}: require 64 lowercase hex")
    return value


def _reject_float(value: Any, where: str = "root") -> None:
    if isinstance(value, float):
        raise AggregateReject(f"binary float prohibited in canonical evidence: {where}")
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value):
            raise AggregateReject(f"non-string JSON key: {where}")
        for key, item in value.items():
            _reject_float(item, f"{where}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_float(item, f"{where}[{index}]")
    elif value is None or isinstance(value, (str, int, bool)):
        return
    else:
        raise AggregateReject(f"unsupported canonical JSON type at {where}: {type(value)!r}")


def canonical_json_bytes(value: Any) -> bytes:
    _reject_float(value)
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


def load_canonical(path: Path) -> tuple[dict[str, Any], bytes, str]:
    raw = path.read_bytes()
    if not raw.endswith(b"\n"):
        raise AggregateReject(f"canonical file lacks LF: {path.name}")
    try:
        obj = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise AggregateReject(f"JSON parse failure: {path.name}") from exc
    if not isinstance(obj, dict):
        raise AggregateReject(f"top-level object required: {path.name}")
    _reject_float(obj)
    if canonical_json_bytes(obj) != raw:
        raise AggregateReject(f"noncanonical JSON bytes: {path.name}")
    return obj, raw, sha256_bytes(raw)


def parse_rat(value: Any, label: str) -> Fraction:
    if not isinstance(value, dict) or set(value) != {"p", "q"}:
        raise AggregateReject(f"{label}: require exact p,q")
    p, q = value["p"], value["q"]
    if not isinstance(p, str) or INT_RE.fullmatch(p) is None:
        raise AggregateReject(f"{label}.p noncanonical")
    if not isinstance(q, str) or POS_RE.fullmatch(q) is None:
        raise AggregateReject(f"{label}.q noncanonical")
    pi, qi = int(p), int(q)
    if math.gcd(abs(pi), qi) != 1:
        raise AggregateReject(f"{label}: rational not reduced")
    result = Fraction(pi, qi)
    if result.numerator != pi or result.denominator != qi:
        raise AggregateReject(f"{label}: noncanonical rational")
    return result


def parse_interval_object(value: Any, label: str) -> tuple[Fraction, Fraction]:
    if not isinstance(value, dict) or set(value) != {"lo", "hi"}:
        raise AggregateReject(f"{label}: require lo,hi object")
    lo = parse_rat(value["lo"], label + ".lo")
    hi = parse_rat(value["hi"], label + ".hi")
    if not lo < hi:
        raise AggregateReject(f"{label}: require positive width")
    return lo, hi


def parse_interval_list(value: Any, label: str, *, allow_point: bool = False) -> tuple[Fraction, Fraction]:
    if not isinstance(value, list) or len(value) != 2:
        raise AggregateReject(f"{label}: require two rational endpoints")
    lo = parse_rat(value[0], label + "[0]")
    hi = parse_rat(value[1], label + "[1]")
    if allow_point:
        if lo > hi:
            raise AggregateReject(f"{label}: reversed interval")
    elif not lo < hi:
        raise AggregateReject(f"{label}: require positive width")
    return lo, hi


def require_source_map(value: Any, *, self_hash: str | None = None) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != SOURCE_KEYS:
        raise AggregateReject("source_sha256 field set mismatch")
    result = {key: require_sha(item, f"source_sha256.{key}") for key, item in value.items()}
    if self_hash is not None and result["aggregate_verifier"] != self_hash:
        raise AggregateReject("aggregate verifier self hash mismatch")
    return result


def parse_plan(path: Path) -> Plan:
    obj, _raw, plan_sha = load_canonical(path)
    expected = {
        "dependency_snapshot_sha256", "design_sha256", "ordered_shards", "policy",
        "schema", "shard_count", "source_sha256", "total_lambda_range",
    }
    if set(obj) != expected or obj["schema"] != PLAN_SCHEMA:
        raise AggregateReject("plan schema/field set mismatch")
    self_hash = sha256_bytes(Path(__file__).read_bytes())
    sources = require_source_map(obj["source_sha256"], self_hash=self_hash)
    design = require_sha(obj["design_sha256"], "design_sha256")
    dependency = require_sha(obj["dependency_snapshot_sha256"], "dependency_snapshot_sha256")
    total = parse_interval_object(obj["total_lambda_range"], "total_lambda_range")

    policy = obj["policy"]
    expected_policy = {
        "checkpoint", "dps_control", "dps_verify", "integration", "lambda_floor",
        "max_activations", "r_floor", "required_freeze_receipt_schema",
    }
    if not isinstance(policy, dict) or set(policy) != expected_policy:
        raise AggregateReject("plan policy field set mismatch")
    if policy["dps_control"] != 50 or policy["dps_verify"] != 70:
        raise AggregateReject("plan dps policy mismatch")
    if policy["max_activations"] != 65536:
        raise AggregateReject("plan activation policy mismatch")
    if policy["integration"] != {"depth": 12, "limit": 200000, "tol": "1e-8"}:
        raise AggregateReject("plan integration policy mismatch")
    if policy["checkpoint"] != {"attempts": 32, "max_payload_bytes": 33554432, "seconds": 120}:
        raise AggregateReject("plan checkpoint policy mismatch")
    if parse_rat(policy["r_floor"], "policy.r_floor") != Fraction(1, 1 << 16):
        raise AggregateReject("plan r floor mismatch")
    if parse_rat(policy["lambda_floor"], "policy.lambda_floor") != Fraction(1, 1 << 16):
        raise AggregateReject("plan lambda floor mismatch")
    if policy["required_freeze_receipt_schema"] != FREEZE_SCHEMA:
        raise AggregateReject("plan freeze schema mismatch")

    shards = obj["ordered_shards"]
    if not isinstance(shards, list) or not shards:
        raise AggregateReject("ordered_shards must be nonempty")
    if obj["shard_count"] != len(shards):
        raise AggregateReject("shard_count mismatch")
    parsed: list[PlannedShard] = []
    seen: set[str] = set()
    for index, raw in enumerate(shards):
        if not isinstance(raw, dict) or set(raw) != {"lambda_box", "root_r", "shard_id", "shard_index"}:
            raise AggregateReject(f"shard[{index}] field set mismatch")
        if raw["shard_index"] != index:
            raise AggregateReject(f"shard[{index}] index mismatch")
        shard_id = raw["shard_id"]
        if not isinstance(shard_id, str) or SHARD_RE.fullmatch(shard_id) is None:
            raise AggregateReject(f"shard[{index}] id syntax mismatch")
        if shard_id != f"S{index:08d}" or shard_id in seen:
            raise AggregateReject(f"shard[{index}] id/index mismatch or duplicate")
        seen.add(shard_id)
        lbox = parse_interval_object(raw["lambda_box"], f"shard[{index}].lambda_box")
        rbox = parse_interval_object(raw["root_r"], f"shard[{index}].root_r")
        if not (Fraction(1) <= lbox[0] < lbox[1]):
            raise AggregateReject("planned lambda outside lambda>=1")
        if not (Fraction(0) < rbox[0] < rbox[1] < Fraction(1)):
            raise AggregateReject("planned r window outside 0<r<1")
        parsed.append(PlannedShard(index, shard_id, lbox, rbox, raw["lambda_box"], raw["root_r"]))

    if parsed[0].lambda_box[1] != total[1] or parsed[-1].lambda_box[0] != total[0]:
        raise AggregateReject("outer plan endpoints do not match total range")
    for i in range(len(parsed) - 1):
        upper, lower = parsed[i], parsed[i + 1]
        if upper.raw_lambda_box["lo"] != lower.raw_lambda_box["hi"]:
            raise AggregateReject(f"adjacent lambda endpoint bytes mismatch at {i}/{i+1}")
        if upper.lambda_box[0] != lower.lambda_box[1]:
            raise AggregateReject(f"adjacent lambda values mismatch at {i}/{i+1}")
        overlap_lo = max(upper.root_r[0], lower.root_r[0])
        overlap_hi = min(upper.root_r[1], lower.root_r[1])
        if not overlap_lo < overlap_hi:
            raise AggregateReject(f"adjacent root windows lack positive overlap at {i}/{i+1}")
    width_sum = sum((s.lambda_box[1] - s.lambda_box[0] for s in parsed), Fraction(0))
    if width_sum != total[1] - total[0]:
        raise AggregateReject("exact shard width sum mismatch")
    return Plan(total, tuple(parsed), sources, design, dependency, policy, plan_sha)


def parse_config_for_plan(path: Path, plan: Plan, shard: PlannedShard) -> tuple[dict[str, Any], str]:
    obj, _raw, config_sha = load_canonical(path)
    expected = {
        "aggregate_plan_sha256", "checkpoint", "dependency_snapshot_sha256", "design_sha256",
        "dps_control", "dps_verify", "integration", "lambda_box", "lambda_floor",
        "max_activations", "r_floor", "required_freeze_receipt_schema", "root_r", "schema",
        "shard_id", "shard_index", "source_sha256",
    }
    if set(obj) != expected or obj["schema"] != CONFIG_SCHEMA:
        raise AggregateReject("config schema/field set mismatch")
    if obj["aggregate_plan_sha256"] != plan.plan_sha256:
        raise AggregateReject("config aggregate-plan hash mismatch")
    if obj["design_sha256"] != plan.design_sha256:
        raise AggregateReject("config design hash mismatch")
    if obj["dependency_snapshot_sha256"] != plan.dependency_snapshot_sha256:
        raise AggregateReject("config dependency hash mismatch")
    if require_source_map(obj["source_sha256"]) != plan.source_sha256:
        raise AggregateReject("config source map mismatch")
    if obj["shard_id"] != shard.shard_id or obj["shard_index"] != shard.shard_index:
        raise AggregateReject("config shard identity mismatch")
    if obj["lambda_box"] != shard.raw_lambda_box or obj["root_r"] != shard.raw_root_r:
        raise AggregateReject("config shard interval bytes mismatch")
    policy_projection = {
        "checkpoint": obj["checkpoint"], "dps_control": obj["dps_control"],
        "dps_verify": obj["dps_verify"], "integration": obj["integration"],
        "lambda_floor": obj["lambda_floor"], "max_activations": obj["max_activations"],
        "r_floor": obj["r_floor"],
        "required_freeze_receipt_schema": obj["required_freeze_receipt_schema"],
    }
    if policy_projection != plan.policy:
        raise AggregateReject("config policy mismatch")
    return obj, config_sha


def parse_freeze_for_config(
    path: Path, *, plan: Plan, config_obj: dict[str, Any], config_sha: str
) -> tuple[dict[str, Any], str]:
    obj, _raw, receipt_sha = load_canonical(path)
    expected = {
        "aggregate_plan_sha256", "config_sha256", "dependency_snapshot_sha256", "design_sha256",
        "freeze_verdict", "nonclaims", "performance_gate_report_sha256",
        "qualification_manifest_sha256", "schema", "source_sha256", "validation_report_sha256",
    }
    if set(obj) != expected or obj["schema"] != FREEZE_SCHEMA:
        raise AggregateReject("freeze receipt schema/field set mismatch")
    if obj["freeze_verdict"] != "V9_FROZEN_APPROVED":
        raise AggregateReject("freeze receipt not approved")
    if obj["config_sha256"] != config_sha:
        raise AggregateReject("freeze/config hash mismatch")
    if obj["aggregate_plan_sha256"] != plan.plan_sha256:
        raise AggregateReject("freeze/plan hash mismatch")
    if obj["design_sha256"] != plan.design_sha256:
        raise AggregateReject("freeze/design hash mismatch")
    if obj["dependency_snapshot_sha256"] != plan.dependency_snapshot_sha256:
        raise AggregateReject("freeze/dependency hash mismatch")
    if require_source_map(obj["source_sha256"]) != plan.source_sha256:
        raise AggregateReject("freeze/source map mismatch")
    for key in ("performance_gate_report_sha256", "qualification_manifest_sha256", "validation_report_sha256"):
        require_sha(obj[key], key)
    if not isinstance(obj["nonclaims"], list) or not all(isinstance(x, str) for x in obj["nonclaims"]):
        raise AggregateReject("freeze nonclaims malformed")
    return obj, receipt_sha


def _expect_interval_list(raw: Any, expected: tuple[Fraction, Fraction], label: str) -> None:
    parsed = parse_interval_list(raw, label, allow_point=True)
    if parsed != expected:
        raise AggregateReject(f"{label} value mismatch")


def validate_shard_evidence(
    path: Path,
    *, plan: Plan, shard: PlannedShard, config_sha: str, receipt_sha: str,
) -> tuple[dict[str, Any], str]:
    obj, _raw, evidence_sha = load_canonical(path)
    required = {
        "aggregate_plan_sha256", "authorization", "checker_error", "checker_report",
        "config_sha256", "dependency_snapshot_sha256", "design_sha256", "driver_id",
        "freeze_receipt_sha256",
        "lambda_box", "nonclaim", "root_r", "runner_error", "runner_result", "schema",
        "shard_id", "shard_index", "source_bindings", "status",
    }
    if set(obj) != required or obj["schema"] != EVIDENCE_SCHEMA:
        raise AggregateReject("shard evidence schema/field set mismatch")
    if obj["status"] != "SHARD_PASS_CANDIDATE" or obj["authorization"] != "FROZEN_PRODUCTION":
        raise AggregateReject("shard evidence is not frozen production PASS candidate")
    if obj["driver_id"] != "ITEM3_SWEEP_V9_REHEARSAL_DRIVER_CANDIDATE_V3":
        raise AggregateReject("shard evidence driver ID mismatch")
    if obj["config_sha256"] != config_sha or obj["aggregate_plan_sha256"] != plan.plan_sha256:
        raise AggregateReject("shard evidence config/plan hash mismatch")
    if obj["design_sha256"] != plan.design_sha256 or obj["dependency_snapshot_sha256"] != plan.dependency_snapshot_sha256:
        raise AggregateReject("shard evidence design/dependency mismatch")
    if obj["freeze_receipt_sha256"] != receipt_sha:
        raise AggregateReject("shard evidence freeze receipt hash mismatch")
    if obj["shard_id"] != shard.shard_id or obj["shard_index"] != shard.shard_index:
        raise AggregateReject("shard evidence identity mismatch")
    _expect_interval_list(obj["root_r"], shard.root_r, "evidence.root_r")
    _expect_interval_list(obj["lambda_box"], shard.lambda_box, "evidence.lambda_box")
    if obj["runner_error"] is not None or obj["checker_error"] is not None:
        raise AggregateReject("shard evidence contains runner/checker error")
    runner = obj["runner_result"]
    checker = obj["checker_report"]
    if not isinstance(runner, dict) or not isinstance(checker, dict):
        raise AggregateReject("runner/checker report missing")
    if runner.get("runner_id") != "ITEM3_SWEEP_V9_REHEARSAL_RUNNER_CANDIDATE_V2":
        raise AggregateReject("runner ID mismatch")
    if runner.get("terminal_class") != "COMPLETE_CANDIDATE":
        raise AggregateReject("runner not complete candidate")
    _expect_interval_list(runner.get("root_r"), shard.root_r, "runner.root_r")
    _expect_interval_list(runner.get("root_lambda"), shard.lambda_box, "runner.root_lambda")
    attempts = runner.get("attempts")
    leaves = runner.get("accepted_leaves")
    if not isinstance(attempts, list) or not attempts or not isinstance(leaves, list) or not leaves:
        raise AggregateReject("runner complete evidence has empty attempts/leaves")

    if checker.get("checker_id") != "ITEM3_SWEEP_V9_REHEARSAL_CHECKER_CANDIDATE_V2":
        raise AggregateReject("checker ID mismatch")
    if checker.get("status") != "PASS_CANDIDATE":
        raise AggregateReject("checker not PASS candidate")
    d50 = checker.get("dps50_leaf_count")
    d70 = checker.get("dps70_verified_leaf_count")
    verified = checker.get("verified_leaves_dps70")
    if not isinstance(d50, int) or not isinstance(d70, int) or d50 <= 0 or d70 != d50:
        raise AggregateReject("checker leaf counts invalid")
    if not isinstance(verified, list) or len(verified) != d70:
        raise AggregateReject("checker dps70 verified-leaf list mismatch")
    if len(leaves) != d50:
        raise AggregateReject("runner/checker accepted leaf count mismatch")
    for i, leaf in enumerate(verified):
        if not isinstance(leaf, dict) or set(leaf) != {"lambda_box", "mean_value_hi_dps70", "path_id", "r_cell"}:
            raise AggregateReject(f"verified leaf[{i}] field set mismatch")
        mv_hi = parse_rat(leaf["mean_value_hi_dps70"], f"verified[{i}].mean_value_hi_dps70")
        if not mv_hi < 0:
            raise AggregateReject(f"verified leaf[{i}] is not strict NEG")
        r_cell = parse_interval_list(leaf["r_cell"], f"verified[{i}].r_cell", allow_point=False)
        l_cell = parse_interval_list(leaf["lambda_box"], f"verified[{i}].lambda_box", allow_point=False)
        if not (shard.root_r[0] <= r_cell[0] < r_cell[1] <= shard.root_r[1]):
            raise AggregateReject("verified r leaf outside planned root window")
        if not (shard.lambda_box[0] <= l_cell[0] < l_cell[1] <= shard.lambda_box[1]):
            raise AggregateReject("verified lambda leaf outside planned shard")

    bindings = obj["source_bindings"]
    if not isinstance(bindings, dict) or set(bindings) != {"adapter", "runner", "checker", "checkpoint", "bridge", "kernel"}:
        raise AggregateReject("source binding field set mismatch")
    for key in ("adapter", "runner", "checker", "checkpoint", "bridge"):
        record = bindings[key]
        if not isinstance(record, dict):
            raise AggregateReject(f"source binding {key} malformed")
        expected_sha = plan.source_sha256[key]
        if record.get("sha256") != expected_sha or record.get("pre_import_sha256") != expected_sha or record.get("post_import_sha256") != expected_sha:
            raise AggregateReject(f"source binding hash mismatch: {key}")
        if record.get("resolved_path") != record.get("module_origin"):
            raise AggregateReject(f"source binding origin mismatch: {key}")
    kernel = bindings["kernel"]
    if not isinstance(kernel, dict) or kernel.get("sha256") != plan.source_sha256["kernel"]:
        raise AggregateReject("kernel binding malformed")
    for key in ("runner_pre", "runner_post", "checker50_pre", "checker50_post", "checker70_pre", "checker70_post"):
        if kernel.get(key) != plan.source_sha256["kernel"]:
            raise AggregateReject(f"kernel binding mismatch: {key}")
    return obj, evidence_sha



def validate_shard_provenance(
    path: Path,
    *,
    plan: Plan,
    shard: PlannedShard,
    config_sha: str,
    receipt_sha: str,
    evidence_sha: str,
) -> None:
    obj, _raw, _provenance_sha = load_canonical(path)
    expected = {
        "aggregate_plan_sha256", "authorization", "checkpoint_commit_count",
        "checkpoint_last_sha256", "checkpoint_ledger_sha256", "config_sha256",
        "dependency_snapshot_sha256", "design_sha256", "freeze_receipt_sha256",
        "proof_status", "schema", "shard_evidence_sha256", "shard_id", "shard_index",
        "source_sha256",
    }
    if set(obj) != expected or obj["schema"] != PROVENANCE_SCHEMA:
        raise AggregateReject("shard provenance schema/field set mismatch")
    if obj["proof_status"] != "PROVENANCE_ONLY" or obj["authorization"] != "FROZEN_PRODUCTION":
        raise AggregateReject("shard provenance authorization/status mismatch")
    if obj["shard_evidence_sha256"] != evidence_sha:
        raise AggregateReject("provenance/evidence hash mismatch")
    if obj["config_sha256"] != config_sha or obj["aggregate_plan_sha256"] != plan.plan_sha256:
        raise AggregateReject("provenance config/plan hash mismatch")
    if obj["design_sha256"] != plan.design_sha256 or obj["dependency_snapshot_sha256"] != plan.dependency_snapshot_sha256:
        raise AggregateReject("provenance design/dependency mismatch")
    if obj["freeze_receipt_sha256"] != receipt_sha:
        raise AggregateReject("provenance freeze receipt hash mismatch")
    if obj["shard_id"] != shard.shard_id or obj["shard_index"] != shard.shard_index:
        raise AggregateReject("provenance shard identity mismatch")
    if require_source_map(obj["source_sha256"]) != plan.source_sha256:
        raise AggregateReject("provenance source map mismatch")
    count = obj["checkpoint_commit_count"]
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise AggregateReject("complete shard lacks committed checkpoint provenance")
    last_expected = require_sha(obj["checkpoint_last_sha256"], "checkpoint_last_sha256")
    ledger_expected = require_sha(obj["checkpoint_ledger_sha256"], "checkpoint_ledger_sha256")

    checkpoint_root = path.parent / "checkpoint"
    ledger_path = checkpoint_root / "SWEEP_PROGRESS.jsonl"
    if not ledger_path.is_file():
        raise AggregateReject("checkpoint ledger missing")
    ledger_raw = ledger_path.read_bytes()
    if not ledger_raw or not ledger_raw.endswith(b"\n"):
        raise AggregateReject("complete shard checkpoint ledger must end in LF")
    if sha256_bytes(ledger_raw) != ledger_expected:
        raise AggregateReject("checkpoint ledger hash mismatch")

    lines = ledger_raw.splitlines(keepends=True)
    if len(lines) != count:
        raise AggregateReject("checkpoint provenance count mismatch")
    previous = ZERO_SHA
    last_sha = None
    expected_context = {
        "aggregate_plan_sha256": plan.plan_sha256,
        "authorization": "FROZEN_PRODUCTION",
        "config_sha256": config_sha,
        "dependency_snapshot_sha256": plan.dependency_snapshot_sha256,
        "design_sha256": plan.design_sha256,
        "freeze_receipt_sha256": receipt_sha,
        "shard_id": shard.shard_id,
        "shard_index": shard.shard_index,
        "source_sha256": plan.source_sha256,
    }
    line_fields = {
        "checkpoint_sequence", "frontier_digest_sha256", "last_complete_attempt_id",
        "partial_evidence_sha256", "previous_checkpoint_sha256",
        "progress_payload_sha256", "schema", "status",
    }
    for index, line in enumerate(lines):
        try:
            line_obj = json.loads(line.decode("utf-8"))
        except Exception as exc:
            raise AggregateReject("checkpoint ledger JSON parse failure") from exc
        if canonical_json_bytes(line_obj) != line:
            raise AggregateReject("checkpoint ledger line is not canonical")
        if not isinstance(line_obj, dict) or set(line_obj) != line_fields:
            raise AggregateReject("checkpoint ledger line field set mismatch")
        if line_obj["schema"] != "ITEM3_SWEEP_V9_PROGRESS_LINE_V1" or line_obj["status"] != "PARTIAL":
            raise AggregateReject("checkpoint ledger schema/status mismatch")
        if line_obj["checkpoint_sequence"] != index:
            raise AggregateReject("checkpoint sequence mismatch")
        if line_obj["previous_checkpoint_sha256"] != previous:
            raise AggregateReject("checkpoint previous-line hash mismatch")
        progress_sha = require_sha(line_obj["progress_payload_sha256"], "progress_payload_sha256")
        partial_sha = require_sha(line_obj["partial_evidence_sha256"], "partial_evidence_sha256")
        frontier_sha = require_sha(line_obj["frontier_digest_sha256"], "frontier_digest_sha256")
        progress_path = checkpoint_root / "checkpoint_payloads" / "progress" / f"{progress_sha}.json"
        partial_path = checkpoint_root / "checkpoint_payloads" / "partial" / f"{partial_sha}.json"
        if not progress_path.is_file() or not partial_path.is_file():
            raise AggregateReject("committed checkpoint payload missing")
        progress, _progress_raw, observed_progress_sha = load_canonical(progress_path)
        partial, _partial_raw, observed_partial_sha = load_canonical(partial_path)
        if observed_progress_sha != progress_sha or observed_partial_sha != partial_sha:
            raise AggregateReject("committed checkpoint payload digest mismatch")
        frontier = progress.get("frontier")
        if sha256_bytes(canonical_json_bytes(frontier)) != frontier_sha:
            raise AggregateReject("checkpoint frontier digest mismatch")
        for label, payload in (("progress", progress), ("partial", partial)):
            context = payload.get("run_context")
            if not isinstance(context, dict):
                raise AggregateReject(f"{label} checkpoint run_context missing")
            for key, value in expected_context.items():
                if context.get(key) != value:
                    raise AggregateReject(f"{label} checkpoint run_context mismatch: {key}")
        last_sha = sha256_bytes(line)
        previous = last_sha
    if last_sha != last_expected:
        raise AggregateReject("checkpoint last hash mismatch")

def selected_chain_tip(plan_sha256: str, evidence_hashes: Sequence[str]) -> str:
    plan_raw = bytes.fromhex(require_sha(plan_sha256, "plan_sha256"))
    previous: bytes | None = None
    for index, value in enumerate(evidence_hashes):
        if index >= 2**64:
            raise AggregateReject("shard index exceeds uint64")
        h = bytes.fromhex(require_sha(value, f"evidence_hash[{index}]"))
        idx = struct.pack(">Q", index)
        preimage = CHAIN_DOMAIN + plan_raw + idx + (b"" if previous is None else previous) + h
        previous = hashlib.sha256(preimage).digest()
    if previous is None:
        raise AggregateReject("zero evidence hashes")
    return previous.hex()


def verify_aggregate(
    *,
    plan_path: Path,
    config_paths: Sequence[Path],
    freeze_receipt_paths: Sequence[Path],
    evidence_paths: Sequence[Path],
    provenance_paths: Sequence[Path],
) -> dict[str, Any]:
    plan = parse_plan(plan_path)
    n = len(plan.ordered_shards)
    if (len(config_paths) != n or len(freeze_receipt_paths) != n or len(evidence_paths) != n or len(provenance_paths) != n):
        raise AggregateReject("config/receipt/evidence/provenance count must equal shard count")

    config_hashes: list[str] = []
    receipt_hashes: list[str] = []
    evidence_hashes: list[str] = []
    adjacency: list[dict[str, Any]] = []

    for shard, config_path, receipt_path, evidence_path, provenance_path in zip(
        plan.ordered_shards, config_paths, freeze_receipt_paths, evidence_paths,
        provenance_paths, strict=True
    ):
        config_obj, config_sha = parse_config_for_plan(config_path, plan, shard)
        _receipt, receipt_sha = parse_freeze_for_config(
            receipt_path, plan=plan, config_obj=config_obj, config_sha=config_sha
        )
        _evidence, evidence_sha = validate_shard_evidence(
            evidence_path, plan=plan, shard=shard, config_sha=config_sha, receipt_sha=receipt_sha
        )
        validate_shard_provenance(
            provenance_path, plan=plan, shard=shard, config_sha=config_sha,
            receipt_sha=receipt_sha, evidence_sha=evidence_sha,
        )
        config_hashes.append(config_sha)
        receipt_hashes.append(receipt_sha)
        evidence_hashes.append(evidence_sha)

    for i in range(n - 1):
        upper, lower = plan.ordered_shards[i], plan.ordered_shards[i + 1]
        overlap_lo = max(upper.root_r[0], lower.root_r[0])
        overlap_hi = min(upper.root_r[1], lower.root_r[1])
        adjacency.append({
            "lower_shard_id": lower.shard_id,
            "root_overlap": {
                "lo": {"p": str(overlap_lo.numerator), "q": str(overlap_lo.denominator)},
                "hi": {"p": str(overlap_hi.numerator), "q": str(overlap_hi.denominator)},
            },
            "shared_lambda": upper.raw_lambda_box["lo"],
            "upper_shard_id": upper.shard_id,
        })

    tip = selected_chain_tip(plan.plan_sha256, evidence_hashes)
    return {
        "schema": AGGREGATE_SCHEMA,
        "verifier_id": VERIFIER_ID,
        "status": "CERTIFIED_LAMBDA_RANGE",
        "aggregate_plan_sha256": plan.plan_sha256,
        "covered_lambda_range": {
            "lo": {"p": str(plan.total_lambda_range[0].numerator), "q": str(plan.total_lambda_range[0].denominator)},
            "hi": {"p": str(plan.total_lambda_range[1].numerator), "q": str(plan.total_lambda_range[1].denominator)},
        },
        "design_sha256": plan.design_sha256,
        "dependency_snapshot_sha256": plan.dependency_snapshot_sha256,
        "source_sha256": plan.source_sha256,
        "config_sha256": config_hashes,
        "freeze_receipt_sha256": receipt_hashes,
        "selected_shard_evidence_sha256": evidence_hashes,
        "selected_chain_tip_sha256": tip,
        "adjacency_connections": adjacency,
        "machine_conclusion": (
            "For every lambda in the covered closed range, the certified root window "
            "contains exactly one zero of G. Adjacent shard roots agree at shared lambda "
            "endpoints by positive-width root-window overlap and strict G_r<0 on the "
            "connected union of the two windows."
        ),
        "nonclaims": [
            "No comparison with a_c is made by this aggregate verdict.",
            "No local normal-form, analyticity, or limit claim is promoted by this verdict.",
            "The verdict covers only the exact aggregate-plan lambda range.",
        ],
    }


def write_aggregate_verdict(
    *, output_path: Path, plan_path: Path, config_paths: Sequence[Path],
    freeze_receipt_paths: Sequence[Path], evidence_paths: Sequence[Path],
    provenance_paths: Sequence[Path],
) -> dict[str, Any]:
    result = verify_aggregate(
        plan_path=plan_path, config_paths=config_paths,
        freeze_receipt_paths=freeze_receipt_paths, evidence_paths=evidence_paths,
        provenance_paths=provenance_paths,
    )
    data = canonical_json_bytes(result)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    output_path.with_suffix(output_path.suffix + ".sha256").write_text(
        sha256_bytes(data) + "\n", encoding="ascii"
    )
    return result
