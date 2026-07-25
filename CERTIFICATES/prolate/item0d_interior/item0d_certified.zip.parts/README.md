# Exact multipart representation of `item0d_certified.zip`

The GitHub text-contents connector cannot write a binary ZIP directly. The original 29,502-byte archive is therefore stored losslessly as independently Base64-encoded byte ranges.

Run from the parent directory:

```bash
python3 reconstruct_zip.py
```

The script decodes the files in the exact order below, concatenates the raw byte ranges, and accepts the output only if both size and SHA-256 match.

| File | Original byte range | Raw bytes | Git blob SHA-1 |
|---|---:|---:|---|
| `offset00000.b64` | `[0,6000)` | 6000 | `b3f7c968ac3d66447ac244eb359a23681fd5bc24` |
| `offset06000.b64` | `[6000,12000)` | 6000 | `6069a7660ecef5c19cf55c550f14c4294f617f04` |
| `offset12000.b64` | `[12000,18000)` | 6000 | `6a8c981601775fd899b04835f0af3a2f71ce2908` |
| `offset18000.b64` | `[18000,24000)` | 6000 | `6664f92df4267a91750d194bd4e43eeb4fd1e094` |
| `offset24000.b64` | `[24000,25000)` | 1000 | `d2327773df60e62f1101c88473c3456a0d00f987` |
| `offset25000.b64` | `[25000,26000)` | 1000 | `790df179d628e5703f4211c60d302a7e3cbec213` |
| `offset26000.b64` | `[26000,27000)` | 1000 | `161865c505fb13729d2052e3d59d273f9b7dd79e` |
| `offset27000.b64` | `[27000,28000)` | 1000 | `02ec05216207cfa30dca940c563660473420f929` |
| `offset28000.b64` | `[28000,29000)` | 1000 | `10f427f29a4ef78233f5c5f5bab96bb34fbd9dfb` |
| `offset29000.b64` | `[29000,29502)` | 502 | `31aea67b497fc80eaff6a13d95bc39846d68574d` |

Every listed Git blob SHA was independently compared with the SHA computed from the corresponding local Base64 text generated from the uploaded ZIP.

Expected reconstructed archive:

- size: `29502` bytes
- SHA-256: `db1c68e4bbf43fcb49bd5f27de5d45a36b44f1f8e77141477832ce16ae68df2a`
