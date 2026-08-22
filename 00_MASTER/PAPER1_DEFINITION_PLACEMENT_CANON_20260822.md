# Paper 1: Canonical Placement of Definitions (2026-08-22)

Status: **CANONICAL**

This document supersedes the earlier plan to translate the 2026-08-20
field-declaration mission statement directly into the Introduction.

## 1. Fixed opening of the Introduction

The Introduction begins without a field name, fingerprint language, or metaphor.
It states only the operations actually performed in the paper.

> 本稿では、基点を幾何学的変数として扱う。対象に付随する汎関数を固定したうえで基点を動かし、そこに現れる停留点構造を取り出す。そして対象を変形させたとき、その構造がどう組み変わるかを調べる。

> In this paper the basepoint is treated as a geometric variable. Fixing a functional attached to the body, we vary the basepoint to extract the resulting stationary structure, and study how that structure reorganizes as the body is deformed.

The four operative verbs correspond directly to the paper:

1. vary the basepoint: vary `p`;
2. extract the stationary structure: determine `Crit(E_lambda)`;
3. deform the body: vary `lambda`;
4. reorganize: change the labeled stationary structure.

Continuous motion of position alone is not a bifurcation.

## 2. Three-layer placement

### Section 1: Introduction

Use the fixed opening above. Do not use a field name, fingerprint language, or
the lens metaphor.

### Section 2: Definitions

Introduce only the minimum framework required to state the main theorem:

- the triple `(P, Lambda, E)`;
- `Crit(E_lambda) = {p : d_p E_lambda = 0}`;
- `S = {(lambda, p) : d_p E_lambda(p) = 0}`;
- the projection `pi: S -> Lambda`;
- basepoint bifurcation as failure of label-preserving local triviality of `pi`.

The labels are:

- component dimension;
- normal Morse index;
- nullity;
- isotropy type.

Keep this general framework smaller than the main theorem. The paper must not
present a general theory larger than the result it proves.

### Outlook

Include:

- the three-axis conjectural picture: stationary circle to four points,
  `O(2) -> D_2h`, and the corresponding label change;
- the field name exactly once, explicitly as the author's terminology:
  "The author calls this framework basepoint geometry.";
- one line welcoming contact.

## 3. Governing principle

**Paper 1 bears the burden of basepoint bifurcation, not basepoint geometry.**

Basepoint bifurcation is a phenomenon asserted by the theorem and therefore
must be defined precisely in the paper. Basepoint geometry is a claim of wider
scope. Because Paper 1 proves only one example, presenting the field name as
the paper's main banner would exceed the evidence.

The term `basepoint bifurcation` has no established prior usage and must be
defined at first occurrence. The same applies to `basepoint geometry`, but the
latter appears only once in the Outlook as the author's terminology.

## 4. Exclusions and unchanged decisions

- The two-sentence banner statement containing fingerprint language is for
  use outside the paper only: banners, serial exposition, and broader outlook
  material.
- Paper 1 must not use the terms or claims "fingerprint", "descriptor",
  "invariant", or "distinguishing shapes" in its Outlook.
- Fingerprint language becomes a principal theme only in Paper 3.
- Position is excluded from the definition of bifurcation and may appear only
  as descriptive information in a bifurcation diagram.
- The Morse-Bott framework must be retained for stationary circles.

## 5. Scope boundary between Papers 1 and 2

- Paper 1 proves existence: at least one basepoint bifurcation occurs.
- Paper 2 proves completeness: the stationary structure is exhausted over the
  full parameter range.

Accordingly, Paper 1's B-TUBE certification must prove the stated existence
result but does not bear the burden of global completeness.
