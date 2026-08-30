#!/usr/bin/env python3
import argparse, json, hashlib, subprocess
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def frac(x):
    if isinstance(x,dict):
        for a,b in (("p","q"),("num","den"),("numerator","denominator")):
            if a in x and b in x: return str(x[a]),str(x[b])
    if isinstance(x,str) and "/" in x:
        a,b=x.split("/",1); return a.strip(),b.strip()
def walk(o,p="$"):
    h=[]
    if isinstance(o,dict):
        if "q_left" in o and "q_right" in o:
            ql,qr=frac(o["q_left"]),frac(o["q_right"])
            idx=o.get("cell_index",o.get("cell",o.get("index")))
            if ql and qr and idx in (0,"0",None): h.append((p,ql,qr))
        for k,v in o.items(): h+=walk(v,p+"."+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): h+=walk(v,f"{p}[{i}]")
    return h

ap=argparse.ArgumentParser(); ap.add_argument("--repo",default=".")
ap.add_argument("--anchors",default=None)
ap.add_argument("--component1",default="CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/CELL0_COMPONENT1_TUBE_GEOMETRY_V1.json")
ap.add_argument("--out",default="CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/A0B_CELL0_PREDICTOR_INPUT_PIN_V1.json")
a=ap.parse_args(); repo=Path(a.repo).resolve()
if a.anchors: anchors=Path(a.anchors).resolve()
else:
    c=list(repo.rglob("A0B_START_ANCHORS.json"))
    if len(c)!=1: raise SystemExit(f"FAIL_A0B_START_ANCHORS_RESOLUTION count={len(c)}")
    anchors=c[0]
component=(repo/a.component1).resolve()
ao=json.loads(anchors.read_text()); co=json.loads(component.read_text())
ci=co["candidate_inputs"]; target=(frac(ci["q_left"]),frac(ci["q_right"]))
hits=[h for h in walk(ao) if (h[1],h[2])==target]
if len(hits)!=1: raise SystemExit(f"FAIL_A0B_COMPONENT1_Q_MATCH count={len(hits)} hits={hits}")
path,ql,qr=hits[0]
if subprocess.check_output(["git","-C",str(repo),"status","--porcelain"],text=True).strip(): raise SystemExit("FAIL_DIRTY_SOURCE_TREE")
head=subprocess.check_output(["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip()
r={"schema":"a0b-cell0-predictor-input-pin-v1","status":"PINNED_NOT_YET_USED_FOR_NC04B","binding_use_authorized":False,
"source":{"artifact":str(anchors.relative_to(repo)) if anchors.is_relative_to(repo) else str(anchors),"sha256":sha(anchors),"declared_run":"33010418300","declared_historical_head":"891a7ff","resolved_json_path":path},
"component1":{"artifact":str(component.relative_to(repo)),"sha256":sha(component)},
"cell_index":0,"q_left":{"p":ql[0],"q":ql[1]},"q_right":{"p":qr[0],"q":qr[1]},"component1_exact_match":True,"creation_head":head,"nc04b_contract_code":"FAIL_PREDICTOR_INPUT_PIN"}
op=(repo/a.out).resolve(); op.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
print("A0B_PIN="+str(op)); print("A0B_PIN_SHA256="+sha(op)); print("Q_LEFT="+ql[0]+"/"+ql[1]); print("Q_RIGHT="+qr[0]+"/"+qr[1]); print("COMPONENT1_EXACT_MATCH=TRUE")
