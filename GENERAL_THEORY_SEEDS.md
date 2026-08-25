# General-Theory Seeds

Updated: 2026-08-25

This file records structures encountered in the particular papers that may
later contribute to the general theory of Basepoint Geometry and, ultimately,
Basepoint Dynamics.

It is a research notebook, not a theorem ledger. Unless a statement is linked
to an independently audited proof or certificate, it remains
`NOT_BINDING`.

## Recording template

Each entry should identify:

- the particular cases from which it arose;
- the part that appears independent of the specific body `K`;
- the assumptions actually used;
- the candidate general statement;
- the evidence status and fixed repository references;
- unresolved analytic or computational obligations.

---

## Seed 1: Sign-selected orbit type in an axisymmetric deformation

### Particular cases

Consider the axisymmetric spheroid family

```text
x^2 + z^2 + y^2/lambda^2 <= 1,
```

with the sphere at `lambda = 1`.

- Pulling in both `y` directions gives the prolate family
  `lambda > 1`.
- Compressing in both `y` directions gives the oblate family
  `0 < lambda < 1`.

When the sphere is deformed away from `lambda=1`, the observed stationary
sets follow different orbit types:

- prolate: an equatorial stationary circle enters from the boundary and
  contracts to the center;
- oblate: two axial stationary points enter from the poles and move to the
  center.

If the deformation is traversed in the reverse direction, the time ordering is
reversed: the stationary set is born at the center and disappears at the
boundary.

### Common representation structure

At the center, axial `O(2)` symmetry splits the tangent representation as

```text
R^3 = R^2_perp + R_parallel.
```

The two summands have different multiplicities and orbit geometry:

- a nonzero vector in `R^2_perp` generates an `O(2)` circle;
- a nonzero vector in `R_parallel` gives the two reflection-related axial
  points.

The particular computations indicate that the sign of the axial deformation
selects which Hessian block reaches degeneracy:

- prolate deformation selects the transverse double eigenvalue and therefore a
  stationary circle;
- oblate deformation selects the axial simple eigenvalue and therefore two
  axial points.

### Candidate general principle

For an analytic one-parameter family of axisymmetric bodies passing through an
isotropic body, a simple crossing of one isotypic Hessian block may select the
orbit type of the bifurcating stationary set. The dimension and isotropy type
of that set should be governed by the corresponding group representation,
while the branch direction is determined by the first nonvanishing invariant
higher-order coefficient.

This is presently a structural interpretation, not a general theorem.

### Boundary-to-center lifecycle

The two cases suggest a common three-stage organization:

```text
boundary kernel changes sign
-> stationary orbit moves through the interior
-> a center Hessian block becomes degenerate.
```

The direction reverses when the shape parameter is traversed in reverse.

The boundary event and the center event are different mechanisms:

- boundary entry or exit is controlled by a one-sided boundary stationary
  kernel;
- center birth or absorption is controlled by a Hessian eigenvalue crossing
  and the relevant invariant higher-order term.

No numerical reciprocity between the prolate and oblate critical ratios is
expected. The functional is not invariant under the anisotropic map that
exchanges elongation with flattening.

### Current numerical landmarks

Prolate values are interval-certified in the existing prolate evidence:

```text
boundary event: lambda_partial in [2.06538, 2.06539]
center event:   lambda_star    in [4.72438, 4.72439]
```

Oblate values remain high-precision candidates:

```text
boundary event: lambda_entry_ob = 0.6435457703666799690435
center event:   lambda_axis_ob  = 0.40795886030094636425
```

The evidence classes must not be conflated merely because the four values are
displayed in one comparison.

### Fixed references

- Prolate project state:
  `cotaxxxx/basepoint-geometry@87d16e6d5f6ed63bd9f47b28e6f607851ca97f41`.
- Oblate endpoint prototype:
  `cotaxxxx/Oblate-Spheroid-Research@92e3ad5d2ab8a8b7b9a7cfee7ef5f84890af3e89`.
- Oblate review record: draft pull request #1.

### General-theory obligations

Before promotion into a general theorem, determine:

1. the precise analytic family and compactness assumptions;
2. whether the center critical set is isolated or Morse--Bott;
3. the normal nondegeneracy and transversality conditions;
4. the invariant normal form for each isotypic component;
5. conditions excluding additional local branches;
6. the relation, if any, between center bifurcation and boundary passage;
7. which parts belong to geometry and which require Basepoint Dynamics.

This seed does not enlarge P1 or P2.
