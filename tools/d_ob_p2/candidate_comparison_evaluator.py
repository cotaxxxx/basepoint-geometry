#!/home/daybreak/.pyenv/versions/3.11.16/bin/python
"""Blind evaluator for the frozen D-OB P2 candidate comparison.

DIAGNOSTIC / NOT_EVIDENCE.  This program aggregates only the frozen section-9
row schema and displays the frozen section-11 gate order.  It contains no
winner rule, ranking, scalar score, or post-hoc numerical threshold.
"""
from __future__ import annotations
import argparse, csv, json, math
from collections import Counter
from pathlib import Path

LABEL="DIAGNOSTIC / NOT_EVIDENCE"
SETS=("C1","C2","C3","C4","C5")
GATE_ORDER=("Soundness","Identity/reproducibility","Width","Certification utility","Cost","Independent checking")
REQUIRED=("candidate_id","candidate_status","code_config_identity","used_producer_sha256","set_id","initial_box_index","r","t","lambda","c5_box_bounds","accepted","unresolved","cut_cells","regular_cells","L","B_cut","independent_J","c5_center_J_flag","upper_sum","enclosure_width","J_minus_L","SumUpper_minus_J","cell_count","max_cell_depth","max_box_depth","runtime_cpu","resource_settings","failure_reason","missing_reason")
NUMERIC=("L","B_cut","independent_J","upper_sum","enclosure_width","J_minus_L","SumUpper_minus_J","cell_count","max_cell_depth","max_box_depth","runtime_cpu")
SUM_FIELDS=("accepted","unresolved","cut_cells","regular_cells","cell_count","runtime_cpu")
MEAN_FIELDS=("L","B_cut","independent_J","upper_sum","enclosure_width","J_minus_L","SumUpper_minus_J","max_cell_depth","max_box_depth")

def die(s): raise SystemExit(s)
def f(x):
 if x in ("",None): return None
 y=float(x)
 if not math.isfinite(y): die("NONFINITE_NUMERIC")
 return y
def b(x):
 if x=="True": return 1.0
 if x=="False": return 0.0
 die("BOOLEAN_PARSE")
def read(path):
 with Path(path).open(newline="") as h:
  first=h.readline()
  if first.rstrip("\r\n")!="# DIAGNOSTIC / NOT_EVIDENCE": die("LABEL_MISMATCH")
  r=csv.DictReader(h,delimiter="\t")
  if tuple(r.fieldnames or ())!=REQUIRED: die("SECTION9_SCHEMA_MISMATCH")
  rows=list(r)
 if not rows: die("EMPTY_INPUT")
 return rows

def aggregate(rows):
 out={"rows":len(rows),"failure_reason_counts":dict(sorted(Counter(x["failure_reason"] or "<empty>" for x in rows).items())),"missing_reason_counts":dict(sorted(Counter(x["missing_reason"] or "<empty>" for x in rows).items()))}
 for k in SUM_FIELDS:
  vals=[b(x[k]) if k in ("accepted","unresolved") else f(x[k]) for x in rows]; vals=[x for x in vals if x is not None]
  out[k+"__n"]=len(vals); out[k+"__sum"]=sum(vals) if vals else None
 for k in MEAN_FIELDS:
  vals=[f(x[k]) for x in rows]; vals=[x for x in vals if x is not None]
  out[k+"__n"]=len(vals); out[k+"__mean"]=sum(vals)/len(vals) if vals else None
 return out

def delta(x,y):
 z={"rows":x["rows"]-y["rows"]}
 for k in list(x):
  if k.endswith(("__sum","__mean","__n")) and isinstance(x[k],(int,float)) and isinstance(y.get(k),(int,float)): z[k]=x[k]-y[k]
 return z

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--input",action="append",required=True,help="candidate=set:path or candidate:path; repeat"); ap.add_argument("--out",required=True); a=ap.parse_args()
 groups={}
 for spec in a.input:
  parts=spec.split(":",2)
  if len(parts)==2: cid,path=parts; sid=None
  elif len(parts)==3: cid,sid,path=parts
  else: die("INPUT_SPEC")
  rows=read(path)
  if any(x["candidate_id"]!=cid for x in rows): die("CANDIDATE_ID_MISMATCH")
  seen={x["set_id"] for x in rows}
  if sid is not None and seen!={sid}: die("SET_ID_MISMATCH")
  for x in rows: groups.setdefault((cid,x["set_id"]),[]).append(x)
 candidates=sorted({c for c,_ in groups})
 if "C0" not in candidates: die("BASELINE_C0_REQUIRED")
 report={"label":LABEL,"mode":"blind_frozen_evaluator","gate_order":list(GATE_ORDER),"soundness_rule":"reject candidate on soundness failure; accepted count cannot revive it","winner_rule":None,"scalar_score":None,"new_numeric_thresholds":[],"candidate_set_aggregates":{},"candidate_minus_C0":{}}
 for cid in candidates:
  report["candidate_set_aggregates"][cid]={}
  report["candidate_minus_C0"][cid]={}
  for sid in SETS:
   if (cid,sid) not in groups: continue
   q=aggregate(groups[(cid,sid)]); report["candidate_set_aggregates"][cid][sid]=q
   if cid!="C0" and ("C0",sid) in groups: report["candidate_minus_C0"][cid][sid]=delta(q,aggregate(groups[("C0",sid)]))
 Path(a.out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print(f"EVALUATOR_COMPLETE candidates={len(candidates)} output={Path(a.out).resolve()}")
if __name__=="__main__": main()
