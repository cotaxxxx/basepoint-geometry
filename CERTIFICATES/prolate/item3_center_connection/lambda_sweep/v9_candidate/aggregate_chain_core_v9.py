#!/usr/bin/env python3
"""Pure-Python exact aggregate-chain core for Item 3 sweep v9.

No GitHub, filesystem traversal, numerical kernel, or interval-library operations occur in
this module. It implements only canonical shard-plan hashing, exact rational shard checks,
and the selected-shard SHA-256 byte grammar frozen in
SCHEMA_AGGREGATE_FREEZE_CANDIDATE.md.

STATUS: IMPLEMENTATION CANDIDATE / NOT PRODUCTION AUTHORIZATION.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
import math
import re
import struct
from typing import Iterable, Mapping, Sequence


CHAIN_DOMAIN = b"ITEM3_SWEEP_V9_SELECTED_SHARD_CHAIN_V1\0"
SHA256_HEX_RE = re.compile(r"[0-9a-f]{64}\Z")
SIGNED_DECIMAL_RE = re.compile(r"-?(0|[1-9][0-9]*)\Z")
POSITIVE_DECIMAL_RE = re.compile(r"[1-9][0-9]*\Z")


class AggregateValidationError(ValueError):
    """Raised when exact shard/chain validation fails closed."""


def require_sha256_hex(value: object, label: str) -> str:
    if not isinstance(value, str) or SHA256_HEX_RE.fullmatch(value) is None:
        raise AggregateValidationError(f"{label}: require 64 lowercase hex")
    return value


def canonical_json_bytes(value: object) -> bytes:
    """Canonical JSON bytes for the v9 shard-plan hash envelope."""
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise AggregateValidationError(f"noncanonical JSON value: {exc}") from exc
    return text.encode("utf-8")


def shard_plan_sha256(plan: Mapping[str, object]) -> str:
    return sha256(canonical_json_bytes(plan)).hexdigest()


def parse_canonical_rational(value: object, label: str) -> Fraction:
    """Parse canonical reduced-rational encoding {"p":str,"q":str}."""
    if not isinstance(value, Mapping) or set(value) != {"p", "q"}:
        raise AggregateValidationError(f"{label}: require exact keys p,q")
    p = value["p"]
    q = value["q"]
    if not isinstance(p, str) or SIGNED_DECIMAL_RE.fullmatch(p) is None:
        raise AggregateValidationError(f"{label}.p: noncanonical integer string")
    if not isinstance(q, str) or POSITIVE_DECIMAL_RE.fullmatch(q) is None:
        raise AggregateValidationError(f"{label}.q: require positive canonical integer string")
    pi = int(p)
    qi = int(q)
    if math.gcd(abs(pi), qi) != 1:
        raise AggregateValidationError(f"{label}: rational is not reduced")
    if pi == 0 and p != "0":
        raise AggregateValidationError(f"{label}.p: noncanonical zero")
    return Fraction(pi, qi)


def validate_shard_plan_structure(plan: Mapping[str, object]) -> list[tuple[Fraction, Fraction]]:
    """Validate exact ordered-shard union and return [(lo,hi),...] in index order."""
    if plan.get("schema") != "ITEM3_SWEEP_V9_SHARD_PLAN_V1":
        raise AggregateValidationError("wrong shard-plan schema")

    rehearsal = plan.get("rehearsal_range")
    if not isinstance(rehearsal, Mapping) or set(rehearsal) != {"lo", "hi"}:
        raise AggregateValidationError("rehearsal_range: require exact keys lo,hi")
    target_lo = parse_canonical_rational(rehearsal["lo"], "rehearsal_range.lo")
    target_hi = parse_canonical_rational(rehearsal["hi"], "rehearsal_range.hi")
    if not target_lo < target_hi:
        raise AggregateValidationError("rehearsal range must have positive width")

    shards = plan.get("ordered_shards")
    if not isinstance(shards, list) or not shards:
        raise AggregateValidationError("ordered_shards must be a nonempty list")
    shard_count = plan.get("shard_count")
    if isinstance(shard_count, bool) or not isinstance(shard_count, int):
        raise AggregateValidationError("shard_count must be an integer")
    if shard_count != len(shards):
        raise AggregateValidationError("shard_count mismatch")

    result: list[tuple[Fraction, Fraction]] = []
    seen_ids: set[str] = set()
    for expected_index, item in enumerate(shards):
        if not isinstance(item, Mapping):
            raise AggregateValidationError(f"shard[{expected_index}] is not an object")
        actual_index = item.get("shard_index")
        if isinstance(actual_index, bool) or not isinstance(actual_index, int):
            raise AggregateValidationError(f"shard[{expected_index}] index is not an integer")
        if actual_index != expected_index:
            raise AggregateValidationError(f"shard[{expected_index}] index mismatch")
        shard_id = item.get("shard_id")
        if not isinstance(shard_id, str) or not shard_id:
            raise AggregateValidationError(f"shard[{expected_index}] invalid shard_id")
        if shard_id in seen_ids:
            raise AggregateValidationError(f"duplicate shard_id: {shard_id}")
        seen_ids.add(shard_id)

        lo = parse_canonical_rational(item.get("lambda_lo"), f"shard[{expected_index}].lambda_lo")
        hi = parse_canonical_rational(item.get("lambda_hi"), f"shard[{expected_index}].lambda_hi")
        if not lo < hi:
            raise AggregateValidationError(f"shard[{expected_index}] must have positive width")
        result.append((lo, hi))

    # Index zero is the uppermost shard. The exact union is checked downward.
    if result[0][1] != target_hi:
        raise AggregateValidationError("uppermost shard does not meet rehearsal high endpoint")
    if result[-1][0] != target_lo:
        raise AggregateValidationError("lowermost shard does not meet rehearsal low endpoint")
    for i in range(len(result) - 1):
        upper_lo, upper_hi = result[i]
        lower_lo, lower_hi = result[i + 1]
        if upper_lo != lower_hi:
            raise AggregateValidationError(f"shards {i} and {i+1} have a gap or overlap")
        if not lower_lo < lower_hi <= upper_hi:
            raise AggregateValidationError(f"shards {i} and {i+1} have invalid downward order")

    total_width = sum((hi - lo for lo, hi in result), Fraction(0))
    if total_width != target_hi - target_lo:
        raise AggregateValidationError("exact shard-width sum does not equal rehearsal width")
    return result


def selected_shard_hashes(
    plan: Mapping[str, object],
    selected: Sequence[Mapping[str, object]],
) -> list[str]:
    """Validate one selected passing evidence hash per planned shard."""
    shards = plan.get("ordered_shards")
    if not isinstance(shards, list):
        raise AggregateValidationError("plan ordered_shards missing")
    if len(selected) != len(shards):
        raise AggregateValidationError("selected shard count mismatch")

    hashes: list[str] = []
    for i, (planned, chosen) in enumerate(zip(shards, selected, strict=True)):
        if not isinstance(planned, Mapping) or not isinstance(chosen, Mapping):
            raise AggregateValidationError(f"selected[{i}] invalid object")
        chosen_index = chosen.get("shard_index")
        if isinstance(chosen_index, bool) or not isinstance(chosen_index, int):
            raise AggregateValidationError(f"selected[{i}] index is not an integer")
        if chosen_index != i:
            raise AggregateValidationError(f"selected[{i}] index mismatch")
        if chosen.get("shard_id") != planned.get("shard_id"):
            raise AggregateValidationError(f"selected[{i}] shard_id mismatch")
        hashes.append(require_sha256_hex(chosen.get("shard_evidence_sha256"), f"selected[{i}].shard_evidence_sha256"))
        require_sha256_hex(chosen.get("checker_report_sha256"), f"selected[{i}].checker_report_sha256")
    return hashes


def selected_chain_tip(aggregate_plan_sha256: str, shard_hashes: Iterable[str]) -> str:
    """Compute the exact selected-shard chain tip using the frozen byte grammar."""
    plan_digest = bytes.fromhex(require_sha256_hex(aggregate_plan_sha256, "aggregate_plan_sha256"))
    previous: bytes | None = None
    count = 0
    for index, value in enumerate(shard_hashes):
        if index >= 2**64:
            raise AggregateValidationError("shard index exceeds uint64")
        shard_digest = bytes.fromhex(require_sha256_hex(value, f"shard_hash[{index}]"))
        index_bytes = struct.pack(">Q", index)
        if previous is None:
            preimage = CHAIN_DOMAIN + plan_digest + index_bytes + shard_digest
        else:
            preimage = CHAIN_DOMAIN + plan_digest + index_bytes + previous + shard_digest
        previous = sha256(preimage).digest()
        count += 1
    if previous is None or count == 0:
        raise AggregateValidationError("cannot compute aggregate chain for zero shards")
    return previous.hex()


def verify_aggregate_selection(
    plan: Mapping[str, object],
    aggregate_plan_sha256: str,
    selected: Sequence[Mapping[str, object]],
    claimed_tip_sha256: str,
) -> str:
    """Validate exact shard structure/plan hash/selection and return the derived tip."""
    validate_shard_plan_structure(plan)
    claimed_plan_hash = require_sha256_hex(aggregate_plan_sha256, "aggregate_plan_sha256")
    derived_plan_hash = shard_plan_sha256(plan)
    if claimed_plan_hash != derived_plan_hash:
        raise AggregateValidationError("aggregate plan SHA-256 mismatch")
    hashes = selected_shard_hashes(plan, selected)
    derived = selected_chain_tip(claimed_plan_hash, hashes)
    claimed = require_sha256_hex(claimed_tip_sha256, "selected_chain_tip_sha256")
    if derived != claimed:
        raise AggregateValidationError("selected shard chain tip mismatch")
    return derived
