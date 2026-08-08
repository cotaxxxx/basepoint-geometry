#!/usr/bin/env python3
"""Exact stdlib-only controls for aggregate_chain_core_v9."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import struct
import unittest

from aggregate_chain_core_v9 import (
    AggregateValidationError,
    CHAIN_DOMAIN,
    selected_chain_tip,
    shard_plan_sha256,
    validate_shard_plan_structure,
    verify_aggregate_selection,
)


PLAN_HASH = "3efa83c7365355d1f16d574a12bf1912ab6b0d7f01cd27bce43532c1f4e60659"
SHARD0_HASH = "da2ae8ba219c91797613747ed7554a2677ac797bb9cbe9557a884bfa0da6ad48"
SHARD1_HASH = "5ac6747bd1c9737034e95923613f7204fa1f80fcf5f759b1263a5b7d71581939"
EXPECTED_C0 = "d26034155cb915ac511826f5aca4a211f92d28aad5c5565dd3ebf1bc118b075a"
EXPECTED_C1 = "83d5bd03c4410181e57dd375e79cefbbed484a07f7ef6e3a8ca8a659cb7e3ffe"
CHECKER0 = sha256(b"checker0").hexdigest()
CHECKER1 = sha256(b"checker1").hexdigest()


def rat(p: str, q: str) -> dict[str, str]:
    return {"p": p, "q": q}


def two_shard_plan() -> dict:
    return {
        "schema": "ITEM3_SWEEP_V9_SHARD_PLAN_V1",
        "rehearsal_range": {
            "lo": rat("123731943", "26214400"),
            "hi": rat("118", "25"),
        },
        "shard_count": 2,
        "ordered_shards": [
            {
                "shard_index": 0,
                "shard_id": "S00000000",
                "lambda_lo": rat("247463911", "52428800"),
                "lambda_hi": rat("118", "25"),
            },
            {
                "shard_index": 1,
                "shard_id": "S00000001",
                "lambda_lo": rat("123731943", "26214400"),
                "lambda_hi": rat("247463911", "52428800"),
            },
        ],
    }


def selected() -> list[dict]:
    return [
        {
            "shard_index": 0,
            "shard_id": "S00000000",
            "shard_evidence_sha256": SHARD0_HASH,
            "checker_report_sha256": CHECKER0,
        },
        {
            "shard_index": 1,
            "shard_id": "S00000001",
            "shard_evidence_sha256": SHARD1_HASH,
            "checker_report_sha256": CHECKER1,
        },
    ]


class AggregateCoreControls(unittest.TestCase):
    def test_exact_rehearsal_partition(self) -> None:
        plan = two_shard_plan()
        ranges = validate_shard_plan_structure(plan)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(ranges[0][0], ranges[1][1])
        self.assertEqual(shard_plan_sha256(plan), PLAN_HASH)

    def test_frozen_chain_vector(self) -> None:
        self.assertEqual(selected_chain_tip(PLAN_HASH, [SHARD0_HASH]), EXPECTED_C0)
        self.assertEqual(selected_chain_tip(PLAN_HASH, [SHARD0_HASH, SHARD1_HASH]), EXPECTED_C1)
        self.assertEqual(
            verify_aggregate_selection(two_shard_plan(), PLAN_HASH, selected(), EXPECTED_C1),
            EXPECTED_C1,
        )

    def test_vector_is_big_endian_not_little_endian(self) -> None:
        P = bytes.fromhex(PLAN_HASH)
        h0 = bytes.fromhex(SHARD0_HASH)
        h1 = bytes.fromhex(SHARD1_HASH)
        c0_le = sha256(CHAIN_DOMAIN + P + struct.pack("<Q", 0) + h0).digest()
        c1_le = sha256(CHAIN_DOMAIN + P + struct.pack("<Q", 1) + c0_le + h1).hexdigest()
        self.assertNotEqual(c1_le, EXPECTED_C1)

    def test_gap_rejected(self) -> None:
        plan = two_shard_plan()
        plan["ordered_shards"][1]["lambda_hi"] = rat("247463910", "52428800")
        with self.assertRaises(AggregateValidationError):
            validate_shard_plan_structure(plan)

    def test_overlap_rejected(self) -> None:
        plan = two_shard_plan()
        plan["ordered_shards"][1]["lambda_hi"] = rat("247463912", "52428800")
        with self.assertRaises(AggregateValidationError):
            validate_shard_plan_structure(plan)

    def test_nonreduced_rational_rejected(self) -> None:
        plan = two_shard_plan()
        plan["ordered_shards"][0]["lambda_hi"] = rat("236", "50")
        with self.assertRaises(AggregateValidationError):
            validate_shard_plan_structure(plan)

    def test_wrong_selected_order_rejected(self) -> None:
        chosen = list(reversed(selected()))
        with self.assertRaises(AggregateValidationError):
            verify_aggregate_selection(two_shard_plan(), PLAN_HASH, chosen, EXPECTED_C1)

    def test_missing_shard_rejected(self) -> None:
        with self.assertRaises(AggregateValidationError):
            verify_aggregate_selection(two_shard_plan(), PLAN_HASH, selected()[:1], EXPECTED_C1)

    def test_stale_plan_hash_rejected(self) -> None:
        stale = sha256(b"stale-plan").hexdigest()
        stale_tip = selected_chain_tip(stale, [SHARD0_HASH, SHARD1_HASH])
        with self.assertRaises(AggregateValidationError):
            verify_aggregate_selection(two_shard_plan(), stale, selected(), stale_tip)

    def test_stale_chain_tip_rejected(self) -> None:
        with self.assertRaises(AggregateValidationError):
            verify_aggregate_selection(two_shard_plan(), PLAN_HASH, selected(), EXPECTED_C0)

    def test_boolean_index_rejected(self) -> None:
        plan = two_shard_plan()
        plan["ordered_shards"][0]["shard_index"] = False
        with self.assertRaises(AggregateValidationError):
            validate_shard_plan_structure(plan)

    def test_one_shard_rerun_changes_only_aggregate_selection(self) -> None:
        chosen = selected()
        unchanged0 = deepcopy(chosen[0])
        new_hash = sha256(b"shard1-rerun").hexdigest()
        chosen[1]["shard_evidence_sha256"] = new_hash
        new_tip = selected_chain_tip(PLAN_HASH, [SHARD0_HASH, new_hash])
        self.assertEqual(chosen[0], unchanged0)
        self.assertNotEqual(new_tip, EXPECTED_C1)
        self.assertEqual(
            verify_aggregate_selection(two_shard_plan(), PLAN_HASH, chosen, new_tip),
            new_tip,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
