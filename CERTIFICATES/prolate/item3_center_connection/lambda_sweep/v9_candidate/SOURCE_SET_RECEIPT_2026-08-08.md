# Item 3 sweep v9 — bound candidate source-set receipt

**Date:** 2026-08-08  
**Status:** `BOUND_IMPLEMENTATION_CANDIDATE / NOT FROZEN`

The following source set is the current implementation candidate for the first exact
`2^-20` rehearsal.  Every listed source has passed its applicable short-form source,
structural, transaction, or binding audit.  This receipt is not production approval.

```text
kernel
  prolate_F_derivatives_cleanroom_v9_candidate.py
  abac1ce574097df32491aba187694b9800a3f76de9a85df9be0b7995923dab76

adapter v2
  adapter_v9_candidate_v2.py
  8a52b7bfa9491976df2ece4f3858a8bc4b4350222c60840c82fff92e0a05913b

runner v2
  runner_v9_candidate_v2.py
  f8f7df69e2693d35879cc7021ca61d21acdfc27aa52cd45635d4d871a6af34e7

checker v2
  checker_v9_candidate_v2.py
  b52fe84cf8084ecd55aa43322fb7577861dfde4d76689b587e1863b532c1aa50

checkpoint transaction
  checkpoint_v9_candidate.py
  253ace8c28c9c5f2d4cb8a9c42b951f759c8f2be619da6845992dca0da10574c

checkpoint bridge
  checkpoint_bridge_v9_candidate.py
  12cd66aeca19d4f7bfaa300ab8ee9fa1f4bbb2f6029a64bd0abb9214770ba797

source-bound driver v2
  rehearsal_driver_v9_candidate_v2.py
  ca6068f9f1e3a55dda1ebdaaeaba0250a0d58ecb644905e12d33b58e39a62d77
```

## Passed gates already attached to this set

- candidate-v2 kernel static audit: PASS;
- candidate-v2 pinned python-flint 0.9.0 runtime audit: PASS;
- independent analytic rederivation: PASS;
- aggregate exact-core controls: PASS;
- adapter V2 runtime/source-binding audit including exact rehearsal endpoint signs: PASS;
- runner V2 deterministic order/depth/hook controls: PASS;
- checker V2 replay/mutation/dps70 controls: PASS;
- checkpoint immutable-payload transaction/recovery controls: PASS;
- runner/checkpoint bridge fsync integration controls: PASS;
- driver V2 all-source pre/post-hash and module-origin binding audit: PASS.

## Deliberately not yet passed

This source set is not frozen because the following final gates are still outstanding:

1. one self-contained integrated v9 contract v2 matching these bytes;
2. canonical logical dependency entries and snapshot tied to the final contract/source;
3. final run config and shard-plan identities;
4. >=256-leaf independent validation corpus on the final byte set;
5. three full hosted performance qualification repetitions on the final byte set;
6. canonical qualification manifest;
7. canonical external `ITEM3_SWEEP_V9_FREEZE_RECEIPT_V1` with verdict
   `V9_FROZEN_APPROVED`.

No full rehearsal has been launched from this receipt.
