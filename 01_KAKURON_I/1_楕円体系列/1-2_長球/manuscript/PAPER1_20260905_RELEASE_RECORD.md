# Paper 1 — 2026-09-05 evidence-complete manuscript record

## Paper

**基点分岐：扁長回転楕円体上で停留円が中心へ収縮する臨界軸比**
— 錐体積重み付き動径–法線角に対する区間認証 —

古田 勝士 / Katsushi Furuta — Independent Researcher
Manuscript date: **2026-09-05**

This record binds the 2026-09-05 evidence-complete manuscript state to the public certificate archive. The earlier `Paper1_Japanese_Revised_20260823.*` files remain historical manuscript artifacts and are not the evidence-complete 2026-09-05 rendering.

## Certified local result

The equatorial quadratic coefficient has a unique simple zero in `(4.72438, 4.72439)`, with `Q'(a_c)<0` and `H4(a_c)<0`. The 20-digit endpoint certificate gives:

- `Q(4.72438340452113340672) > 0`
- `Q(4.72438340452113340673) < 0`

The axial coefficient certificate gives `Qz(a)>0` on every certified subinterval of `[4.70,4.75]`; the rounded manuscript lower bound is **0.0885587746621582**.

## Qz interval table used by the 2026-09-05 manuscript

| a interval | certified Qz enclosure |
|---|---|
| [4.70,4.71] | [0.0902528418054467, 0.0999373544299639] |
| [4.71,4.72] | [0.0898252211752637, 0.0994655331139743] |
| [4.72,4.73] | [0.0894003622655778, 0.0989967593326489] |
| [4.73,4.74] | [0.0889782093794167, 0.0985310412573711] |
| [4.74,4.75] | [0.0885587746621582, 0.0980683196709266] |

## 20-digit endpoint enclosures

- `Q(...672) = [4.45950117779900917098986772e-22, 4.45950117779900917098986968e-22]`
- `Q(...673) = [-5.00431892402172225190109006e-22, -5.00431892402172225190108810e-22]`

## Public evidence

All eleven certificate/audit objects are under `CERTIFICATES/prolate/local_bifurcation/` and are SHA-256 pinned by `SHA256SUMS.txt`. The five ac/Qz objects belong to the **2026-09 new certification chain**; their JSON `certificate_id` fields identify that chain.

Evidence-completion commit: `68bc9828c3476e9db2d73d338e731c48c0931f54`.

## Reproduction metadata

Use the metadata recorded by each certificate JSON. For the 2026-09 chain:

- ac certificate: Python 3.13.14, dps 100, tolerance `1e-40`.
- Qz certificate: Python 3.13.14, dps 70, tolerance `1e-28`, subdivisions 5.
- Common recorded components: python-flint 0.9.0, FLINT 3.6.0, SymPy 1.14.0, mpmath 1.3.0.
- cap-chain environment remains the environment recorded by the pre-existing repository certificate chain.

The local bifurcation theorem does not use the global B-TUBE classification as a premise. `bg-prolate-spheroid` remains `NOT_BINDING / DIAGNOSTIC_ONLY` for this record.

## Evidence boundary

The 2026-09-05 evidence audit closed the previous public-evidence gap: the equatorial `Q/Q'/H4` chain, the 20-digit `a_c` endpoint chain, and the axial `Qz` chain are now all public and SHA-pinned in the canonical repository. This file is a provenance/release record; mathematical authority remains the manuscript together with the pinned certificate bytes and their fail-closed outputs.
