#!/usr/bin/env python3
"""SHA256SUMS.txt over all files in this directory except the manifest."""
import hashlib, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
lines = []
for p in sorted(HERE.iterdir()):
    if p.name in ("SHA256SUMS.txt", "__pycache__") or p.is_dir():
        continue
    lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
(HERE / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n")
print(f"manifest: {len(lines)} entries")
