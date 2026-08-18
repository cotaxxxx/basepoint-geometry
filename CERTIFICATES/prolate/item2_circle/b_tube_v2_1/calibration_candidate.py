"""Deterministic evaluation of one calibration candidate."""
from calibration_context import *
from calibration_numeric import *


def _evaluate_krawczyk(*, kernel, arb_type, domain, lam_lo, lam_hi, tol, depth, limit):
    lam_box = _fraction_box(lam_lo, lam_hi, arb_type)
    domain_box = _dyadic_box(domain, arb_type)
    midpoint = domain.midpoint()
    midpoint_lam = (lam_lo + lam_hi) / 2
    residual = arb_ball_to_exact_interval(kernel.F_arb(
        _dyadic_arb(midpoint, arb_type), lam_box,
        tol=tol, depth=depth, limit=limit,
    ))
    slope = arb_ball_to_exact_interval(kernel.dFdr_arb(
        domain_box, lam_box, tol=tol, depth=depth, limit=limit,
    ))
    center_slope = arb_ball_to_exact_interval(kernel.dFdr_arb(
        _dyadic_arb(midpoint, arb_type), _rational_arb(midpoint_lam, arb_type),
        tol=tol, depth=depth, limit=limit,
    ))
    slope_mid = center_slope.midpoint()
    preconditioner = D_ZERO
    if slope_mid != D_ZERO:
        preconditioner = _nearest_dyadic(
            Fraction(1, 1) / slope_mid.as_fraction(), bits=96
        )
    image = DyadicInterval.point(midpoint)
    left_margin = D_ZERO
    right_margin = D_ZERO
    reason = None
    passed = False
    if preconditioner == D_ZERO:
        reason = "preconditioner_zero"
    else:
        image = krawczyk_image(
            m=midpoint, residual=residual, slope=slope,
            preconditioner=preconditioner, domain=domain,
        )
        left_margin = image.lo - domain.lo
        right_margin = domain.hi - image.hi
        if not domain.strictly_contains(image):
            reason = "krawczyk_not_strict"
        elif not slope.hi < D_ZERO:
            reason = "slope_not_strictly_negative"
        else:
            passed = True
    return {
        "image": image,
        "left_margin": left_margin,
        "passed": passed,
        "preconditioner": preconditioner,
        "reason": reason,
        "residual": residual,
        "right_margin": right_margin,
        "slope": slope,
    }


def _candidate_run_diagnostic(*, config, kernel, arb_type, start, width, radius,
                              candidate_index, records, previous):
    start_fraction = start.as_fraction()
    end = Rational.from_json(config["lambda_end"]).as_fraction()
    cells = _cell_partition(start_fraction, end, width.as_fraction(), config["max_cells"])
    tol = "1e-20"
    depth = config["max_subdivisions"]
    limit = config["evaluation_budget"]
    y_box = DyadicInterval(-radius, radius)
    anchor = _nearest_dyadic((CG_ROOT[0].as_fraction() + CG_ROOT[1].as_fraction()) / 2)
    predictors_reversed = []
    seed = anchor
    refresh = config["predictor_refresh"]
    for reverse_index, (left, right) in enumerate(reversed(cells)):
        right_iterations = 4 if reverse_index % refresh == 0 else 1
        q_right = _newton_predictor(
            kernel, arb_type, right, seed, iterations=right_iterations,
            tol=tol, depth=depth, limit=limit,
        )
        q_left = _newton_predictor(
            kernel, arb_type, left, q_right, iterations=1,
            tol=tol, depth=depth, limit=limit,
        )
        predictor = AffinePredictor(
            Rational.from_fraction(left), Rational.from_fraction(right), q_left, q_right,
        )
        predictors_reversed.append((left, right, predictor))
        seed = q_left
    predictors = list(reversed(predictors_reversed))

    previous = _append_record(records, previous, {
        "candidate_index": candidate_index, "lambda_width": width.to_json(),
        "record_type": "candidate_start", "tube_radius": radius.to_json(),
    })
    cell_passes = []
    joins_pass = True
    evaluation_count = 0
    sections = []
    for cell_index, (left, right, predictor) in enumerate(predictors):
        domain = physical_tube(predictor.range_hull(), y_box)
        reason = None
        result = {
            "image": DyadicInterval.point(domain.midpoint()),
            "left_margin": D_ZERO, "passed": False, "preconditioner": D_ZERO,
            "reason": None, "residual": DyadicInterval.point(D_ZERO),
            "right_margin": D_ZERO, "slope": DyadicInterval.point(D_ZERO),
        }
        if domain.lo <= D_ZERO or not domain.hi < D_ONE:
            reason = "physical_tube_outside_open_unit_interval"
        else:
            result = _evaluate_krawczyk(
                kernel=kernel, arb_type=arb_type, domain=domain, lam_lo=left, lam_hi=right,
                tol=tol, depth=depth, limit=limit,
            )
            evaluation_count += 3
            reason = result["reason"]
        cell_passes.append(result["passed"])
        sections.append((predictor, y_box))
        previous = _append_record(records, previous, {
            "candidate_index": candidate_index,
            "cell_index": cell_index,
            "evaluation_count": evaluation_count,
            "failure_reason": reason,
            "krawczyk_image": result["image"].to_json(),
            "lambda_interval": {
                "lo": Rational.from_fraction(left).to_json(),
                "hi": Rational.from_fraction(right).to_json(),
            },
            "left_margin": result["left_margin"].to_json(),
            "passed": result["passed"],
            "predictor": {
                "q_left": predictor.q_left.to_json(),
                "q_right": predictor.q_right.to_json(),
                "rule": Q_RULE,
            },
            "preconditioner": result["preconditioner"].to_json(),
            "record_type": "cell",
            "residual": result["residual"].to_json(),
            "right_margin": result["right_margin"].to_json(),
            "slope": result["slope"].to_json(),
            "subdivision_count": 0,
            "tube_interval": domain.to_json(),
        })

    for join_index in range(len(sections) - 1):
        left_predictor, left_y = sections[join_index]
        right_predictor, right_y = sections[join_index + 1]
        failure = None
        width_value = D_ZERO
        try:
            intersection = exact_join_intersection(
                left_predictor.q_right, left_y, right_predictor.q_left, right_y,
            )
            width_value = intersection.hi - intersection.lo
        except SchemaError:
            intersection = DyadicInterval.point(D_ZERO)
            failure = "join_empty_or_zero_width"
            joins_pass = False
        previous = _append_record(records, previous, {
            "candidate_index": candidate_index,
            "failure_reason": failure,
            "intersection": intersection.to_json(),
            "join_index": join_index,
            "record_type": "join",
            "width": width_value.to_json(),
        })

    passed = all(cell_passes) and joins_pass and evaluation_count <= limit
    previous = _append_record(records, previous, {
        "candidate_index": candidate_index,
        "cells_attempted": len(cells),
        "cells_passed": sum(cell_passes),
        "evaluation_count": evaluation_count,
        "joins_passed": joins_pass,
        "passed": passed,
        "record_type": "candidate_end",
    })
    return passed, previous, {
        "candidate_index": candidate_index,
        "lambda_width": width.to_json(),
        "tube_radius": radius.to_json(),
    }


def _candidate_run_binding(*, config, kernel, arb_type, start, width, radius,
                           candidate_index, records, previous):
    start_fraction = start.as_fraction()
    end = Rational.from_json(config["lambda_end"]).as_fraction()
    cells = _cell_partition(start_fraction, end, width.as_fraction(), config["max_cells"])
    tol = "1e-20"
    depth = config["max_subdivisions"]
    limit = config["evaluation_budget"]
    refresh = config["predictor_refresh"]
    sigma = Dyadic.from_json(config["adaptive_safety_factor"], "adaptive_safety_factor")
    a0_interval, _ = _load_a0_start_interval()
    anchor = a0_interval.midpoint()

    previous = _append_record(records, previous, {
        "adaptive_safety_factor": sigma.to_json(),
        "anchor_mode": ANCHOR_MODE,
        "candidate_index": candidate_index,
        "lambda_width": width.to_json(),
        "record_type": "candidate_start",
        "start_root_interval": a0_interval.to_json(),
        "tube_radius": radius.to_json(),
    })

    cell_passes = []
    cell_sections = []
    join_results = []
    evaluation_count = 0
    continuation_valid = True
    seed = anchor

    for cell_index, (left, right) in enumerate(cells):
        q_left = anchor if cell_index == 0 else seed
        iterations = 4 if cell_index % refresh == 0 else 1
        q_right = q_left
        if continuation_valid:
            q_right = _newton_predictor(
                kernel, arb_type, right, q_left, iterations=iterations,
                tol=tol, depth=depth, limit=limit,
            )
        predictor = AffinePredictor(
            Rational.from_fraction(left), Rational.from_fraction(right), q_left, q_right,
        )

        failure = None
        rho = D_ZERO
        boundary_left = D_ZERO
        boundary_right = D_ZERO
        domain = DyadicInterval.point(q_left)
        y_box = DyadicInterval.point(D_ZERO)
        result = {
            "image": DyadicInterval.point(q_left),
            "left_margin": D_ZERO, "passed": False, "preconditioner": D_ZERO,
            "reason": None, "residual": DyadicInterval.point(D_ZERO),
            "right_margin": D_ZERO, "slope": DyadicInterval.point(D_ZERO),
        }
        try:
            rho, boundary_left, boundary_right, domain = _adaptive_radius(
                predictor.range_hull(), radius, sigma
            )
            y_box = DyadicInterval(-rho, rho)
        except CalibrationError:
            failure = "adaptive_radius_or_physical_domain_invalid"
        if failure is None and not continuation_valid:
            failure = "branch_anchor_lost"

        if failure is None and cell_index == 0:
            start_section = shifted(y_box, q_left)
            if not a0_interval.contains(start_section):
                failure = "start_anchor_section_outside_a0_bracket"

        if failure is None:
            result = _evaluate_krawczyk(
                kernel=kernel, arb_type=arb_type, domain=domain, lam_lo=left, lam_hi=right,
                tol=tol, depth=depth, limit=limit,
            )
            evaluation_count += 3
            failure = result["reason"]

        passed = failure is None and result["passed"]
        cell_passes.append(passed)
        cell_sections.append((predictor, y_box, rho, passed, left, right))
        previous = _append_record(records, previous, {
            "adaptive_radius": rho.to_json(),
            "boundary_margin_left": boundary_left.to_json(),
            "boundary_margin_right": boundary_right.to_json(),
            "candidate_index": candidate_index,
            "cell_index": cell_index,
            "evaluation_count": evaluation_count,
            "failure_reason": failure,
            "krawczyk_image": result["image"].to_json(),
            "lambda_interval": {
                "lo": Rational.from_fraction(left).to_json(),
                "hi": Rational.from_fraction(right).to_json(),
            },
            "left_margin": result["left_margin"].to_json(),
            "passed": passed,
            "predictor": {
                "q_left": predictor.q_left.to_json(),
                "q_right": predictor.q_right.to_json(),
                "rule": Q_RULE,
            },
            "preconditioner": result["preconditioner"].to_json(),
            "radius_rule": ADAPTIVE_RADIUS_RULE,
            "record_type": "cell",
            "residual": result["residual"].to_json(),
            "right_margin": result["right_margin"].to_json(),
            "slope": result["slope"].to_json(),
            "subdivision_count": 0,
            "tube_interval": domain.to_json(),
        })

        if cell_index > 0:
            left_predictor, left_y, left_rho, left_passed, _, _ = cell_sections[cell_index - 1]
            right_predictor, right_y, right_rho, right_passed, _, _ = cell_sections[cell_index]
            join_failure = None
            intersection = DyadicInterval.point(D_ZERO)
            width_value = D_ZERO
            join_eval = {
                "image": DyadicInterval.point(D_ZERO),
                "left_margin": D_ZERO, "passed": False, "preconditioner": D_ZERO,
                "reason": None, "residual": DyadicInterval.point(D_ZERO),
                "right_margin": D_ZERO, "slope": DyadicInterval.point(D_ZERO),
            }
            try:
                intersection = exact_join_intersection(
                    left_predictor.q_right, left_y,
                    right_predictor.q_left, right_y,
                )
                width_value = intersection.hi - intersection.lo
            except SchemaError:
                join_failure = "join_empty_or_zero_width"
            if join_failure is None and not (left_passed and right_passed):
                join_failure = "adjacent_cell_failed"
            if join_failure is None:
                boundary_lambda = left
                join_eval = _evaluate_krawczyk(
                    kernel=kernel, arb_type=arb_type, domain=intersection,
                    lam_lo=boundary_lambda, lam_hi=boundary_lambda,
                    tol=tol, depth=depth, limit=limit,
                )
                evaluation_count += 3
                join_failure = join_eval["reason"]
            join_passed = join_failure is None and join_eval["passed"]
            join_results.append({
                "candidate_index": candidate_index,
                "evaluation_count": evaluation_count,
                "failure_reason": join_failure,
                "intersection": intersection.to_json(),
                "join_index": cell_index - 1,
                "krawczyk_image": join_eval["image"].to_json(),
                "left_margin": join_eval["left_margin"].to_json(),
                "left_radius": left_rho.to_json(),
                "passed": join_passed,
                "preconditioner": join_eval["preconditioner"].to_json(),
                "record_type": "join",
                "residual": join_eval["residual"].to_json(),
                "right_margin": join_eval["right_margin"].to_json(),
                "right_radius": right_rho.to_json(),
                "slope": join_eval["slope"].to_json(),
                "width": width_value.to_json(),
            })
            if not join_passed:
                continuation_valid = False

        if not passed:
            continuation_valid = False
        seed = q_right

    for join_record in join_results:
        previous = _append_record(records, previous, join_record)

    terminal_intersection = DyadicInterval.point(D_ZERO)
    terminal_match = False
    terminal_failure = "terminal_cg_overlap_missing"
    terminal_eval = {
        "image": DyadicInterval.point(D_ZERO),
        "left_margin": D_ZERO, "passed": False, "preconditioner": D_ZERO,
        "reason": None, "residual": DyadicInterval.point(D_ZERO),
        "right_margin": D_ZERO, "slope": DyadicInterval.point(D_ZERO),
    }
    if cell_sections:
        predictor, y_box, _, last_passed, _, _ = cell_sections[-1]
        terminal_section = shifted(y_box, predictor.q_right)
        overlap = terminal_section.intersection(_cg_root_dyadic_interval())
        if overlap is not None and overlap.positive_width() and last_passed:
            terminal_intersection = overlap
            terminal_eval = _evaluate_krawczyk(
                kernel=kernel, arb_type=arb_type, domain=overlap,
                lam_lo=end, lam_hi=end, tol=tol, depth=depth, limit=limit,
            )
            evaluation_count += 3
            terminal_failure = terminal_eval["reason"]
            terminal_match = terminal_failure is None and terminal_eval["passed"]

    joins_pass = all(record["passed"] for record in join_results)
    passed = (
        all(cell_passes)
        and joins_pass
        and terminal_match
        and evaluation_count <= limit
    )
    previous = _append_record(records, previous, {
        "candidate_index": candidate_index,
        "cells_attempted": len(cells),
        "cells_passed": sum(cell_passes),
        "evaluation_count": evaluation_count,
        "joins_passed": joins_pass,
        "passed": passed,
        "record_type": "candidate_end",
        "terminal_cg_intersection": terminal_intersection.to_json(),
        "terminal_failure_reason": terminal_failure,
        "terminal_krawczyk_image": terminal_eval["image"].to_json(),
        "terminal_left_margin": terminal_eval["left_margin"].to_json(),
        "terminal_match_passed": terminal_match,
        "terminal_preconditioner": terminal_eval["preconditioner"].to_json(),
        "terminal_residual": terminal_eval["residual"].to_json(),
        "terminal_right_margin": terminal_eval["right_margin"].to_json(),
        "terminal_slope": terminal_eval["slope"].to_json(),
    })
    return passed, previous, {
        "candidate_index": candidate_index,
        "lambda_width": width.to_json(),
        "tube_radius": radius.to_json(),
    }


def _candidate_run(*, config, kernel, arb_type, start, width, radius, candidate_index,
                   records, previous):
    if config["mode"] == CALIBRATION_MODE:
        return _candidate_run_diagnostic(
            config=config, kernel=kernel, arb_type=arb_type, start=start,
            width=width, radius=radius, candidate_index=candidate_index,
            records=records, previous=previous,
        )
    require_blocal_dependency(config)
    return _candidate_run_binding(
        config=config, kernel=kernel, arb_type=arb_type, start=start,
        width=width, radius=radius, candidate_index=candidate_index,
        records=records, previous=previous,
    )


__all__ = [name for name in globals() if not name.startswith("__")]
