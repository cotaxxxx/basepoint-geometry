from __future__ import annotations

import base64
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTS = [
    ROOT / "item0d_certified.zip.parts" / "offset00000.b64",
    ROOT / "item0d_certified.zip.parts" / "offset06000.b64",
    ROOT / "item0d_certified.zip.parts" / "offset12000.b64",
    ROOT / "item0d_certified.zip.parts" / "offset18000.b64",
    ROOT / "item0d_certified.zip.parts" / "offset24000.b64",
    ROOT / "item0d_certified.zip.parts" / "offset25000.b64",
    ROOT / "item0d_certified.zip.parts" / "offset26000.b64",
    ROOT / "item0d_certified.zip.parts" / "offset27000.b64",
    ROOT / "item0d_certified.zip.parts" / "offset28000.b64",
    ROOT / "item0d_certified.zip.parts" / "offset29000.b64",
]
OUT = ROOT / "item0d_certified.zip"
EXPECTED_SIZE = 29502
EXPECTED_SHA256 = (
    "db1c68e4bbf43fcb49bd5f27de5d45a36b44f1f8e77141477832ce16ae68df2a"
)


def main() -> None:
    payload = b"".join(
        base64.b64decode(path.read_text(encoding="ascii").strip(), validate=True)
        for path in PARTS
    )
    actual_sha256 = hashlib.sha256(payload).hexdigest()

    if len(payload) != EXPECTED_SIZE:
        raise SystemExit(
            f"size mismatch: expected {EXPECTED_SIZE}, got {len(payload)}"
        )
    if actual_sha256 != EXPECTED_SHA256:
        raise SystemExit(
            "SHA-256 mismatch: "
            f"expected {EXPECTED_SHA256}, got {actual_sha256}"
        )

    OUT.write_bytes(payload)
    print(
        f"wrote {OUT} ({len(payload)} bytes), "
        f"sha256={actual_sha256}"
    )


if __name__ == "__main__":
    main()
