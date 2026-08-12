#!/usr/bin/env python3
"""B-LOCAL v2.2 Taylor2 method-selection diagnostic, revision 3.

Record-only wrapper around the byte-pinned V2 prototype. Gamma partition tables
are interned once at the record root, snapshots retain a state hash and counts,
and enclosure sequences are bounded to first/last N entries. Full JSON is
written to BLOCAL_V22_FULL_RECORD; stdout contains a short summary only.
Design evidence only; never certificate evidence.
"""
from __future__ import annotations
import contextlib,hashlib,io,json,os
from pathlib import Path
from typing import Any
import blocal_v22_method_taylor2_probe_v2 as v2

PROTOTYPE_ID="BLOCAL_V22_TAYLOR2_CHARTED_METHOD_SELECTION_V3_BOUNDED_RECORD"
V2_SHA256="e84a549818a3678dc17cfd034c50a6a367ad029a6815c52359e03bfc55f19353"
SEQUENCE_EDGE_COUNT=8
DEFAULT_RECORD="/tmp/blocal-v22-method-selection-taylor2-full-v3.json"
_REGISTRY:dict[str,dict[str,Any]]={}
_ORIG_GAMMA_RECORDS=v2.gamma_records

def canonical(x:Any)->bytes:
 return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def intern_gamma_records(trace:dict[str,Any])->dict[str,Any]:
 rows=_ORIG_GAMMA_RECORDS(trace);ids=[]
 for row in rows:
  digest=hashlib.sha256(canonical(row)).hexdigest()
  prior=_REGISTRY.get(digest)
  if prior is not None and prior!=row:raise RuntimeError("GAMMA_PARTITION_HASH_COLLISION")
  _REGISTRY[digest]=row;ids.append(digest)
 state=hashlib.sha256(canonical(ids)).hexdigest()
 return {"partition_state_sha256":state,"partition_count":len(ids)}

def bounded(seq:list[Any])->dict[str,Any]:
 n=len(seq)
 if n<=2*SEQUENCE_EDGE_COUNT:return {"total_count":n,"truncated":False,"entries":seq}
 return {"total_count":n,"truncated":True,"first":seq[:SEQUENCE_EDGE_COUNT],"last":seq[-SEQUENCE_EDGE_COUNT:]}

def compact(x:Any)->Any:
 if isinstance(x,list):return [compact(y) for y in x]
 if not isinstance(x,dict):return x
 out={}
 for k,val in x.items():
  if k=="enclosure_sequence" and isinstance(val,list):out[k]=compact(bounded(val))
  else:out[k]=compact(val)
 return out

def phase_summary(row:dict[str,Any])->dict[str,Any]:
 c=row.get("evaluation_subdivision_counts")
 if not isinstance(c,dict):c={}
 return {
  "phase":row.get("phase"),
  "predicate_result":row.get("predicate_result"),
  "failure_reason":row.get("failure_reason"),
  "elapsed_seconds":row.get("elapsed_seconds"),
  "counters":{k:c.get(k) for k in (
   "cell_evaluation_attempts","cell_evaluations","active_leaves",
   "max_spatial_depth_used","spatial_split_count","gamma_angle_calls",
   "gamma_bin_evaluations","gamma_bin_split_count","gamma_adaptive_calls",
   "gamma_max_bin_depth_used","gamma_terminal_failures") if k in c},
 }

def main()->int:
 v2_bytes=Path(v2.__file__).read_bytes()
 if hashlib.sha256(v2_bytes).hexdigest()!=V2_SHA256:raise RuntimeError("V2_PROTOTYPE_SHA256_MISMATCH")
 v2.gamma_records=intern_gamma_records
 capture=io.StringIO()
 with contextlib.redirect_stdout(capture):rc=v2.main()
 lines=[x for x in capture.getvalue().splitlines() if x.strip()]
 if not lines:raise RuntimeError("V2_RECORD_MISSING")
 record=compact(json.loads(lines[-1]))
 record["record_normalization"]={
  "schema":"BLOCAL_V22_SECTION_6_5_BOUNDED_RECORD_V3",
  "prototype_id":PROTOTYPE_ID,
  "v2_sha256":V2_SHA256,
  "gamma_partition_registry":{k:_REGISTRY[k] for k in sorted(_REGISTRY)},
  "gamma_partition_registry_count":len(_REGISTRY),
  "enclosure_sequence_policy":{"edge_count":SEQUENCE_EDGE_COUNT,"counters_preserved":True},
  "certificate_evidence":False,
 }
 path=Path(os.environ.get("BLOCAL_V22_FULL_RECORD",DEFAULT_RECORD))
 payload=canonical(record)+b"\n";path.write_bytes(payload)
 results=record.get("results",[])
 summary={
  "schema":"BLOCAL_V22_SECTION_6_5_SUMMARY_V3",
  "full_record_path":str(path),
  "full_record_bytes":len(payload),
  "full_record_sha256":hashlib.sha256(payload).hexdigest(),
  "prototype_id":PROTOTYPE_ID,
  "prototype_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  "git_source_head":record.get("git_source_head"),
  "declared_budgets":record.get("declared_budgets"),
  "gamma_partition_registry_count":len(_REGISTRY),
  "all_six_conditions_pass":record.get("all_six_conditions_pass"),
  "method_selection_gate":record.get("method_selection_gate"),
  "total_elapsed_seconds":record.get("total_elapsed_seconds"),
  "phases":[phase_summary(x) for x in results],
  "certificate_evidence":False,
 }
 print(json.dumps(summary,sort_keys=True,separators=(",",":")),flush=True)
 return rc

if __name__=="__main__":raise SystemExit(main())
