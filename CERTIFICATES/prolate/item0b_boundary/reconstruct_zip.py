#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
from pathlib import Path

EXPECTED_SIZE = 34025
EXPECTED_SHA256 = "7a07e9c687ed59bec40103daf6b55c348f9c2cac5dcecf61bc7de64655b8d9be"
PARTS_DIR = Path(__file__).with_name("item0b_certified.zip.parts")
OUTPUT = Path(__file__).with_name("item0b_certified.zip")


def main() -> None:
    parts = sorted(PARTS_DIR.glob("offset*.b64"))
    if not parts:
        raise SystemExit("no Base64 parts found")
    data = b"".join(base64.b64decode(p.read_text().strip(), validate=True) for p in parts)
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != EXPECTED_SIZE:
        raise SystemExit(f"size mismatch: {len(data)} != {EXPECTED_SIZE}")
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"SHA-256 mismatch: {digest} != {EXPECTED_SHA256}")
    OUTPUT.write_bytes(data)
    print(f"wrote {OUTPUT.name}: {len(data)} bytes, SHA-256 {digest}")


if __name__ == "__main__":
    main()
