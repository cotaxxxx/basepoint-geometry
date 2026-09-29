import csv, hashlib, sys
p = sys.argv[1] if len(sys.argv) > 1 else "phase0_points.tsv"
rows=[r for r in csv.DictReader((l for l in open(p) if not l.startswith("#")), delimiter="\t")]
fp="\n".join(f'{r["key"]}\t{float(r["B_standard"]):.8e}' for r in sorted(rows,key=lambda r:r["key"]))
print(len(rows), hashlib.sha256(fp.encode()).hexdigest())
