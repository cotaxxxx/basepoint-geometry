(* ::Package:: *)

(* diagnostics/wolfram_handoff_cap_crosscheck.wl

   Oblate endpoint-cap symbolic cross-check.

   Evidence class:   SYMBOLIC_CROSSCHECK / NOT_BINDING
   Derivation class: EXACT for every symbolic identity;
                     HIGH_PRECISION (60 working digits, 50 reported digits)
                     for the direct sample residuals.

   This script checks the endpoint-cap algebra through an independent
   computer-algebra path. It does not certify an interval, does not replace
   the Arb interval checker, and does not change any existing receipt or
   evidence classification.

   Run from the repository root:

       wolframscript -file diagnostics/wolfram_handoff_cap_crosscheck.wl

   The expected process exit status is zero and the expected final line is
   failure_count=0.

   Conventions
   -----------
   The oblate spheroid is parametrized by

       x = (Sqrt[1-mu^2] Cos[phi], Sqrt[1-mu^2] Sin[phi], lam mu),
       -1 <= mu <= 1,

   and the axial base point is p = (0, 0, lam t) with t < 1. Write

       A     = 1 - t mu
       q     = 1 - mu^2 + lam^2 (mu - t)^2
       w^2   = lam^2 (1 - mu^2) + mu^2
       R     = Sqrt[1 - mu^2]
       C     = (1 - lam^2) mu + lam^2 t
       N     = -mu q - A lam^2 (t - mu)
       gamma = lam A / (w Sqrt[q])
       alpha = ArcCos[gamma].

   Mathematica reserves the single-letter names C, D, E and N, so the script
   uses symA, symQ, symW2, symR, symC and symN for the quantities written
   A, q, w^2, R, C and N above. Printed labels use the mathematical names.

   Sign branches are kept deliberately separate. Because

       Sin[alpha] = R Abs[C] / (w Sqrt[q]),

   the first t-derivative of alpha carries a factor Sign[C]. Collapsing the
   two branches before Abs[C] is handled can hide an incorrect square-root
   simplification. PowerExpand is never used in this script, and every
   symbolic and numerical sample input is an exact rational.
*)

failureCount = 0;

report[label_String, ok_] := Module[{good},
  good = TrueQ[ok];
  If[good,
    Print["PASS ", label],
    Print["FAIL ", label]; failureCount = failureCount + 1];
  good];

zeroQ[expr_] := Module[{simplified},
  simplified = Simplify[expr];
  TrueQ[simplified === 0] || TrueQ[simplified == 0]
    || TrueQ[FullSimplify[simplified] === 0]
    || TrueQ[FullSimplify[simplified] == 0]];

Print["wolfram_version=", $Version];
Print["wolfram_release_number=", $ReleaseNumber];
Print["script_path=",
  If[StringQ[$InputFileName] && $InputFileName =!= "", $InputFileName,
    "unknown"]];

(* ------------------------------------------------------------------- *)
(* Exact symbolic setup.                                               *)
(* ------------------------------------------------------------------- *)

aFn[m_, tv_, l_]  := 1 - tv m;
qFn[m_, tv_, l_]  := 1 - m^2 + l^2 (m - tv)^2;
w2Fn[m_, tv_, l_] := l^2 (1 - m^2) + m^2;
cFn[m_, tv_, l_]  := (1 - l^2) m + l^2 tv;
nFn[m_, tv_, l_]  := -m qFn[m, tv, l] - aFn[m, tv, l] l^2 (tv - m);

gammaFn[m_, tv_, l_] :=
  l aFn[m, tv, l] / (Sqrt[w2Fn[m, tv, l]] Sqrt[qFn[m, tv, l]]);
alphaFn[m_, tv_, l_] := ArcCos[gammaFn[m, tv, l]];

symA  = aFn[mu, t, lam];
symQ  = qFn[mu, t, lam];
symW2 = w2Fn[mu, t, lam];
symC  = cFn[mu, t, lam];
symN  = nFn[mu, t, lam];

(* symR and symSign are free symbols constrained by
   symR^2 == 1 - mu^2 with symR >= 0, and symSign^2 == 1. *)
relations = {symR^2 - (1 - mu^2), symSign^2 - 1};

clearAndReduce[expr_] := Module[{num},
  num = Expand[Numerator[Together[expr]]];
  Expand[Last[PolynomialReduce[num, relations, {symR, symSign}]]]];

branchSubstitution[sgnValue_] := {symSign -> sgnValue,
  symR -> Sqrt[1 - mu^2]};

branchAssumptions = -1 < mu < 1 && -1 < t < 1 && 0 < lam < 1/Sqrt[2];

(* ------------------------------------------------------------------- *)
(* Check 1.   N = -(1 - mu^2) C.                                       *)
(* ------------------------------------------------------------------- *)

residual1 = Expand[symN + (1 - mu^2) symC];
report["check1_N_equals_minus_one_minus_mu2_times_C", residual1 === 0];

(* ------------------------------------------------------------------- *)
(* Check 2.   w^2 q - lam^2 A^2 = (1 - mu^2) C^2.                      *)
(* ------------------------------------------------------------------- *)

residual2 = Expand[symW2 symQ - lam^2 symA^2 - (1 - mu^2) symC^2];
report["check2_complement_identity_w2q_minus_lam2A2", residual2 === 0];

(* ------------------------------------------------------------------- *)
(* Check 3.   Both C > 0 and C < 0 branches of alpha_t and alpha_tt.   *)
(*                                                                     *)
(*    alpha_t  =  lam R Sign[C] / q                                    *)
(*    alpha_tt = -2 lam^3 R Sign[C] (t - mu) / q^2                     *)
(*                                                                     *)
(* The defining relation is -Sin[alpha] alpha_t = gamma_t, with        *)
(*    Sin[alpha] = R Abs[C] / (w Sqrt[q]),                             *)
(*    gamma_t    = lam N / (w q^(3/2)).                                *)
(* Multiplying that relation by w q^(3/2) clears both square roots     *)
(* without PowerExpand and leaves a polynomial identity modulo         *)
(* symR^2 = 1 - mu^2 and symSign^2 = 1.                                *)
(* ------------------------------------------------------------------- *)

alphaTBranch  = lam symR symSign / symQ;
alphaTTBranch = -2 lam^3 symR symSign (t - mu) / symQ^2;

report["check3_gamma_t_equals_lam_N_over_w_q_three_halves",
  zeroQ[D[gammaFn[mu, t, lam], t] - lam symN / (Sqrt[symW2] symQ^(3/2))]];

clearedFirstDerivative = -(symR symSign symC) alphaTBranch symQ - lam symN;
report["check3_alpha_t_cleared_polynomial_identity",
  clearAndReduce[clearedFirstDerivative] === 0];

report["check3_alpha_tt_is_t_derivative_of_alpha_t",
  clearAndReduce[D[alphaTBranch, t] - alphaTTBranch] === 0];

Do[
  Module[{sgnValue, label, first, second},
    sgnValue = branchValue;
    label = If[sgnValue === 1, "C_positive", "C_negative"];
    first = Simplify[
      clearedFirstDerivative /. branchSubstitution[sgnValue],
      Assumptions -> branchAssumptions];
    second = Simplify[
      (D[alphaTBranch, t] - alphaTTBranch) /. branchSubstitution[sgnValue],
      Assumptions -> branchAssumptions];
    report["check3_branch_" <> label <> "_alpha_t", zeroQ[first]];
    report["check3_branch_" <> label <> "_alpha_tt", zeroQ[second]];
  ],
  {branchValue, {1, -1}}];

(* ------------------------------------------------------------------- *)
(* Check 4.   The coefficient -4 mu alpha alpha_t in                   *)
(*            d^2/dt^2 (A alpha^2).                                    *)
(* ------------------------------------------------------------------- *)

productExpansion = Expand[
  D[symA alphaSym[t]^2, {t, 2}] /.
    {Derivative[2][alphaSym][t] -> att,
     Derivative[1][alphaSym][t] -> at,
     alphaSym[t] -> ang}];

Print["second_product_derivative=", productExpansion];

report["check4_cross_coefficient_equals_minus_4_mu",
  Expand[Coefficient[Coefficient[productExpansion, ang, 1], at, 1] + 4 mu]
    === 0];
report["check4_alpha_t_squared_coefficient_equals_2A",
  Expand[Coefficient[Coefficient[productExpansion, ang, 0], at, 2] - 2 symA]
    === 0];
report["check4_alpha_alpha_tt_coefficient_equals_2A",
  Expand[Coefficient[Coefficient[productExpansion, ang, 1], att, 1] - 2 symA]
    === 0];

(* ------------------------------------------------------------------- *)
(* Check 5.   Compact formula                                          *)
(*                                                                     *)
(*   d^2/dt^2 (A alpha^2)                                              *)
(*     = 2 A lam^2 R^2 / q^2 (1 - 2 alpha Tan[alpha]).                 *)
(*                                                                     *)
(* Tan[alpha] = Sin[alpha]/Cos[alpha] = R Abs[C] / (lam A), so on each  *)
(* branch Tan[alpha] = R Sign[C] C / (lam A).                          *)
(* ------------------------------------------------------------------- *)

tanAlphaBranch = symR symSign symC / (lam symA);

compactLeft = -4 mu ang alphaTBranch + 2 symA alphaTBranch^2
  + 2 symA ang alphaTTBranch;
compactRight = 2 symA lam^2 symR^2 / symQ^2 (1 - 2 ang tanAlphaBranch);

report["check5_compact_second_derivative_polynomial_identity",
  clearAndReduce[compactLeft - compactRight] === 0];

Do[
  Module[{sgnValue, label, res},
    sgnValue = branchValue;
    label = If[sgnValue === 1, "C_positive", "C_negative"];
    res = Simplify[
      (compactLeft - compactRight) /. branchSubstitution[sgnValue],
      Assumptions -> branchAssumptions];
    report["check5_branch_" <> label, zeroQ[res]];
  ],
  {branchValue, {1, -1}}];

(* ------------------------------------------------------------------- *)
(* Check 6.   Direct 50-digit samples against the unsimplified second  *)
(*            derivative.                                              *)
(*                                                                     *)
(* Every sample point is an exact rational with -1 < mu < 1, t < 1 and *)
(* 0 < lam < 1/Sqrt[2]. Both sign branches of C are represented.       *)
(* ------------------------------------------------------------------- *)

samplePoints = {
  {1/2, 1/2, 3/5},
  {-1/2, 1/2, 3/5},
  {4/5, -3/4, 2/5},
  {-9/10, 9/10, 1/2},
  {-3/10, 1/3, 7/10},
  {1/10, -9/10, 1/4},
  {-7/10, -1/2, 33/50},
  {3/5, 7/10, 5/8}};

workingDigits = 60;
reportedDigits = 50;
residualTolerance = 10^-45;

directSecondDerivative = D[symA alphaFn[mu, t, lam]^2, {t, 2}];

sampleResiduals = {};

Do[
  Module[{m0, t0, l0, cVal, sgnValue, branchLabel, rVal, qVal, aVal,
          alphaVal, directValue, compactValue, alphaTValue, alphaTTValue,
          resFirst, resSecond, resProduct},
    {m0, t0, l0} = sample;
    cVal = cFn[m0, t0, l0];
    sgnValue = Sign[cVal];
    branchLabel = Which[sgnValue === 1, "C>0", sgnValue === -1, "C<0",
      True, "C=0"];
    rVal = Sqrt[1 - m0^2];
    qVal = qFn[m0, t0, l0];
    aVal = aFn[m0, t0, l0];
    alphaVal = alphaFn[m0, t0, l0];

    (* Unsimplified direct differentiation, then numerical evaluation. *)
    directValue = N[
      directSecondDerivative /. {mu -> m0, t -> t0, lam -> l0},
      workingDigits];
    compactValue = N[
      2 aVal l0^2 (1 - m0^2)/qVal^2 (1 - 2 alphaVal Tan[alphaVal]),
      workingDigits];

    alphaTValue = l0 rVal sgnValue / qVal;
    alphaTTValue = -2 l0^3 rVal sgnValue (t0 - m0) / qVal^2;

    resFirst = Abs[
      N[D[alphaFn[mu, t, lam], t] /. {mu -> m0, t -> t0, lam -> l0},
        workingDigits] - N[alphaTValue, workingDigits]];
    resSecond = Abs[
      N[D[alphaFn[mu, t, lam], {t, 2}] /. {mu -> m0, t -> t0, lam -> l0},
        workingDigits] - N[alphaTTValue, workingDigits]];
    resProduct = Abs[directValue - compactValue];

    AppendTo[sampleResiduals,
      {m0, t0, l0, branchLabel, resFirst, resSecond, resProduct}];

    report["check6_sample_mu_" <> ToString[m0, InputForm]
        <> "_t_" <> ToString[t0, InputForm]
        <> "_lam_" <> ToString[l0, InputForm] <> "_" <> branchLabel,
      TrueQ[resFirst < residualTolerance]
        && TrueQ[resSecond < residualTolerance]
        && TrueQ[resProduct < residualTolerance]];
  ],
  {sample, samplePoints}];

report["check6_both_sign_branches_sampled",
  MemberQ[sampleResiduals[[All, 4]], "C>0"]
    && MemberQ[sampleResiduals[[All, 4]], "C<0"]];

Print["direct_second_derivative_residuals="];
Print["  working_digits=", workingDigits,
  " reported_digits=", reportedDigits,
  " tolerance=", N[residualTolerance, 3]];
Do[
  Print["  mu=", row[[1]], " t=", row[[2]], " lam=", row[[3]],
    " branch=", row[[4]],
    " alpha_t_residual=", N[row[[5]], reportedDigits],
    " alpha_tt_residual=", N[row[[6]], reportedDigits],
    " second_derivative_residual=", N[row[[7]], reportedDigits]],
  {row, sampleResiduals}];
Print["  max_second_derivative_residual=",
  N[Max[sampleResiduals[[All, 7]]], reportedDigits]];

(* ------------------------------------------------------------------- *)
(* Check 7.   Analyticity of Phi(u) = ArcSin[Sqrt[u]]^2 at u = 0.      *)
(*                                                                     *)
(*   Phi(u) = Sum_{n >= 1} 4^n u^n / (2 n^2 Binomial[2 n, n]).         *)
(* ------------------------------------------------------------------- *)

phiOrder = 8;
phiSeries = Series[ArcSin[Sqrt[u]]^2, {u, 0, phiOrder}];
phiPolynomial = Normal[phiSeries];

report["check7_phi_series_is_polynomial_in_u",
  TrueQ[PolynomialQ[phiPolynomial, u]]];
report["check7_phi_series_vanishes_at_zero",
  TrueQ[Simplify[phiPolynomial /. u -> 0] === 0]];

phiCoefficients = Table[
  SeriesCoefficient[ArcSin[Sqrt[u]]^2, {u, 0, n}], {n, 0, phiOrder}];
phiExpected = Table[
  If[n === 0, 0, 4^n/(2 n^2 Binomial[2 n, n])], {n, 0, phiOrder}];

report["check7_phi_coefficients_match_closed_form",
  TrueQ[Simplify[phiCoefficients - phiExpected]
    === ConstantArray[0, phiOrder + 1]]];

phiTestPoint = 1/1000;
phiTruncationResidual = Abs[
  N[ArcSin[Sqrt[phiTestPoint]]^2, workingDigits]
    - N[phiPolynomial /. u -> phiTestPoint, workingDigits]];
report["check7_phi_truncation_residual_is_order_u_nine",
  TrueQ[phiTruncationResidual < 10^-26]];

Print["phi_series=", phiPolynomial];
Print["phi_series_coefficients=", phiCoefficients];
Print["phi_series_closed_form=4^n u^n/(2 n^2 Binomial[2n,n]) for n>=1"];
Print["phi_truncation_residual_at_u_", phiTestPoint, "=",
  N[phiTruncationResidual, reportedDigits]];

(* ------------------------------------------------------------------- *)
(* Check 8.   max_z z/(1 + z^2)^2 = 9/(16 Sqrt[3]) at z = 1/Sqrt[3].   *)
(*                                                                     *)
(* This is the uniform majorant used by the endpoint cap: with         *)
(* z = lam (t - mu)/R the branch formula for alpha_tt becomes          *)
(*                                                                     *)
(*   alpha_tt = -2 lam^2 Sign[C] z / (R^2 (1 + z^2)^2),                *)
(*                                                                     *)
(* so |alpha_tt| <= 9 lam^2 / (8 Sqrt[3] R^2).                         *)
(*                                                                     *)
(* The global bound is proved by the exact factorization               *)
(*                                                                     *)
(*   9 (1 + z^2)^2 - 16 Sqrt[3] z                                      *)
(*     = (z - 1/Sqrt[3])^2 (9 z^2 + 6 Sqrt[3] z + 27),                 *)
(*                                                                     *)
(* whose second factor has discriminant 108 - 972 = -864 < 0 and       *)
(* positive leading coefficient, hence is positive definite.           *)
(* ------------------------------------------------------------------- *)

majorantFunction = z/(1 + z^2)^2;
majorantArgMax = 1/Sqrt[3];
majorantMaximum = 9/(16 Sqrt[3]);

report["check8_argmax_is_critical_point",
  zeroQ[D[majorantFunction, z] /. z -> majorantArgMax]];
report["check8_value_at_argmax",
  zeroQ[(majorantFunction /. z -> majorantArgMax) - majorantMaximum]];

majorantFactorization = Simplify[
  Expand[9 (1 + z^2)^2 - 16 Sqrt[3] z
    - Expand[(z - majorantArgMax)^2 (9 z^2 + 6 Sqrt[3] z + 27)]]];
report["check8_global_bound_factorization", zeroQ[majorantFactorization]];
report["check8_cofactor_is_positive_definite",
  TrueQ[Simplify[(6 Sqrt[3])^2 - 4*9*27] === -864]];
report["check8_maxvalue_agrees",
  zeroQ[MaxValue[{majorantFunction, z >= 0}, z] - majorantMaximum]];

report["check8_alpha_tt_majorant_form",
  clearAndReduce[
    alphaTTBranch
      + 2 lam^2 symSign (lam (t - mu)/symR)
        / (symR^2 (1 + (lam (t - mu)/symR)^2)^2)] === 0];

Print["majorant_maximum=", majorantMaximum];
Print["majorant_maximum_numeric=", N[majorantMaximum, reportedDigits]];
Print["majorant_argmax=", majorantArgMax];
Print["majorant_alpha_tt_bound=9 lam^2/(8 Sqrt[3] R^2)"];

(* ------------------------------------------------------------------- *)
(* Summary.                                                            *)
(* ------------------------------------------------------------------- *)

Print["failure_count=", failureCount];

Exit[If[failureCount === 0, 0, 1]];
