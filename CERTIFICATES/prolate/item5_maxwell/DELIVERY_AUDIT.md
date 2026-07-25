# Item 5 certified delivery audit

Status: **ARCHIVED / CERTIFIED**

## Delivered ZIP

- file: `item5_certified.zip`
- actual uploaded ZIP SHA-256: `832c61f659998188cd231032e6cbb0c7f9be7cf63fb7403a156fb78b99a9957f`
- ZIP integrity test: passed; seven members, no CRC errors

The combined certificate contains an earlier internal field

`package_zip_sha256 = 2c7ada4a12e3d0090be97de07650f87e033f65071fcdaa4fdbf1cb3cd3f3ca4c`.

That value does **not** equal the SHA-256 of the uploaded delivery ZIP above. The machine certificate has been preserved without alteration, and this audit records the distinction explicitly rather than rewriting certified output.

## Delivered members and SHA-256

| Original member | Repository path | SHA-256 |
|---|---|---|
| `certificate_item5_combined.json` | `certificate_item5_combined.json` | `ac208bcdaa73f613fa307076e2c30ba9e9e26502d19aef953f1cbe5deff4afd9` |
| `stage5a_state.json` | `stage5a_state.json` | `443757d08f078bbe43f8f441a4837371f6689208081a38098cf0afedb8c9c880` |
| `stage5a.py` | `certified_delivery/stage5a.py` | `8ad0b5dc57534a696021baa3e9b9be581a93417e7738c3c92e56578a570c23cf` |
| `phi_split_driver.py` | `certified_delivery/phi_split_driver.py` | `da97812554547603a23bebf7b8e9e022fdd6a083f27e1e05c6e7cc3c6c680428` |
| `prolate_maxwell_arb_certificate.py` | `certified_delivery/prolate_maxwell_arb_certificate.py` | `62cdc0de93df1393aa956078b5469da5cef9f6e80c4833dc051f574bb1e53c21` |
| `prolate_maxwell_reference.json` | `prolate_maxwell_reference.json` | `32b06ef5a5e0290563d9fa3ea651a01800acfdc101c5dca5f2aeb81f86770e20` |
| `prolate_maxwell_symbolic_audit.json` | `prolate_maxwell_symbolic_audit.json` | `5c595e2e0f731f028708244c97ce33f7e53c2d1a975e45661fcbecc1d48e5f69` |

The delivery copy of `prolate_maxwell_arb_certificate.py` is isolated under `certified_delivery/` because the PR already contains a newer serial implementation under the same original filename. The delivered `stage5a.py` imports the isolated module when run from that directory. The older `phi_split_driver.py` retains its exploratory narrow-bracket constants and is archived as provenance; it is not the source of the final wide-bracket theorem.

## Independent ingestion checks

- all three Python files pass `python -m py_compile`;
- combined JSON status is `CERTIFIED`;
- all four conditions in the combined certificate are marked certified;
- `stage5a_state.json` records strict positive lower endpoint, strict negative upper endpoint, and strict negative derivative interval;
- the interval-Newton enclosure lies strictly inside `[1717/500,1718/500]`;
- the certified root enclosure contains the non-certified reference `3.434868442866843`.

## Certified theorem

For

\[
D(\lambda)=E_\lambda(1,0)-E_\lambda(0,0),
\qquad
I_5=[1717/500,1718/500],
\]

one has

\[
D(1717/500)>0,
\qquad
D(1718/500)<0,
\qquad
D'(I_5)<0.
\]

Hence `D` has exactly one simple zero in `I_5`, and the boundary/center value crossing is transverse. One interval-Newton step gives

\[
\boxed{
3.4347589497567105
<\lambda_{\rm cross}<
3.4349743513998283
}.
\]
