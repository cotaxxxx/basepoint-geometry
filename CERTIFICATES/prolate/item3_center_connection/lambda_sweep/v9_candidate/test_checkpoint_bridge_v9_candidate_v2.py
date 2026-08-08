#!/usr/bin/env python3
"""Integration controls for config-bound checkpoint bridge v2."""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

import checkpoint_bridge_v9_candidate_v2 as b
import checkpoint_v9_candidate as cp
import runner_v9_candidate_v2 as r


class SignInterval:
    def __init__(self, sign): self.sign=sign
    def strictly_positive(self): return self.sign=="POS"
    def strictly_negative(self): return self.sign=="NEG"
class MVInterval:
    finite=True
    def __init__(self, hi): self.hi=hi
class FakeAdapter:
    def __init__(self): self.kernel_call_counts={"FAKE":0}
    def evaluate_g(self, *, r_cell, lambda_box, dps):
        self.kernel_call_counts["FAKE"]+=1
        return SignInterval("POS" if r_cell[0]==Fraction(1,64) else "NEG")
    def evaluate_mean_value(self, *, r_cell, lambda_box, dps):
        self.kernel_call_counts["FAKE"]+=1
        root=(Fraction(1,64),Fraction(11,256))
        if r_cell==root:
            return SimpleNamespace(strict_negative=False,mean_value=MVInterval(Fraction(1)),r_score=Fraction(10),lambda_score=Fraction(1))
        return SimpleNamespace(strict_negative=True,mean_value=MVInterval(Fraction(-1)),r_score=Fraction(1),lambda_score=Fraction(1))

ROOT_R=(Fraction(1,64),Fraction(11,256))
ROOT_L=(Fraction(123731943,26214400),Fraction(118,25))
CONTEXT={
    "config_sha256":"1"*64,
    "aggregate_plan_sha256":"2"*64,
    "shard_id":"S00000000",
    "shard_index":0,
}

class BridgeV2Controls(unittest.TestCase):
    def test_context_is_bound_into_committed_payloads(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            store=cp.CheckpointStore(root)
            cadence=cp.CheckpointCadence(seconds=10000,attempts=32)
            hook=b.ProgressCheckpointHook(store=store,cadence=cadence,run_context=CONTEXT)
            result=r.run_rehearsal_partition(adapter=FakeAdapter(),root_r=ROOT_R,root_lambda=ROOT_L,progress_hook=hook)
            self.assertEqual(result.terminal_class,"COMPLETE_CANDIDATE")
            records=cp.recover_committed(root)
            self.assertEqual(len(records),1)
            progress_path=root/"checkpoint_payloads"/"progress"/f"{records[0].progress_payload_sha256}.json"
            import json
            obj=json.loads(progress_path.read_text(encoding="utf-8"))
            self.assertEqual(obj["run_context"],CONTEXT)

    def test_empty_context_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(b.BridgeContractError):
                b.ProgressCheckpointHook(
                    store=cp.CheckpointStore(Path(td)),
                    cadence=cp.CheckpointCadence(seconds=10000,attempts=32),
                    run_context={},
                )

    def test_context_appears_in_both_payload_types(self):
        snapshots=[]
        r.run_rehearsal_partition(adapter=FakeAdapter(),root_r=ROOT_R,root_lambda=ROOT_L,progress_hook=snapshots.append)
        self.assertEqual(b.progress_payload(snapshots[0],CONTEXT)["run_context"],CONTEXT)
        self.assertEqual(b.partial_payload(snapshots[0],CONTEXT)["run_context"],CONTEXT)

if __name__=="__main__":
    unittest.main(verbosity=2)
