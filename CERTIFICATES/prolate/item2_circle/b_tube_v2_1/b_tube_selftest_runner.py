#!/usr/bin/env python3
"""Build deterministic B-TUBE v2.1 mock artifacts; no production calculation."""
from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
from pathlib import Path
from typing import Any

from affine_geometry import (
    Q_RULE,
    AffinePredictor,
    exact_join_intersection,
    krawczyk_image,
    physical_tube,
    shifted,
)
from mock_kernel import F_interval, MOCK_KERNEL_SHA256, ROOT, dFdr_interval
from numeric_schema import (
    D_NEG_ONE,
    D_ZERO,
    Dyadic,
    DyadicInterval,
    Rational,
    canonical_json_bytes,
    canonical_jsonl,
    chain_genesis,
    sha256_hex,
)

GENESIS_DOMAIN = "B-TUBE-RECORD-CHAIN-GENESIS-v1"
CG_ARTIFACT_SHA256 = "c0f624a955657f906c09c45b016a92f7bcdfa70d26c2508efeb3f06dd7d27381"
CG_CONFIG_SHA256 = "bb6a3655d335240549cbe1f6eec2a9e68e00219eb9c1a2be65796e2e342a0d17"
CG_SOURCE_HEAD = "1e0f671c91798b9c044c04c7a4224a21e1e67830"
FG_LEMMA = "F_G_FIXED_SLICE_IDENTITY_V1"
BLOCAL_MOCK_SHA256 = "1111111111111111111111111111111111111111111111111111111111111111"


@dataclass(frozen=True)
class Bundle:
    config_bytes: bytes
    dependencies_bytes: bytes
    records_jsonl: bytes
    summary_bytes: bytes

    def write(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "config.json").write_bytes(self.config_bytes)
        (directory / "DEPENDENCIES.json").write_bytes(self.dependencies_bytes)
        (directory / "B_TUBE_RECORDS.jsonl").write_bytes(self.records_jsonl)
        (directory / "B_TUBE_CERTIFICATE.json").write_bytes(self.summary_bytes)


def default_config(*, checker_dps: int = 60) -> dict[str, Any]:
    return {
        "schema": "btube-selftest-config-v2.1",
        "mode": "SELFTEST_ONLY",
        "dps": 60,
        "checker_dps": checker_dps,
        "q_evaluation_rule": Q_RULE,
        "lambda_start": Rational(2, 1).to_json(),
        "lambda_match": Rational(118, 25).to_json(),
        "chain_genesis_domain": GENESIS_DOMAIN,
        "chain_genesis_sha256": chain_genesis(GENESIS_DOMAIN),
        "boundary_dependency_sha256": BLOCAL_MOCK_SHA256,
        "cg_match_dependency": {
            "artifact_zip_sha256": CG_ARTIFACT_SHA256,
            "config_sha256": CG_CONFIG_SHA256,
            "source_head": CG_SOURCE_HEAD,
            "run_id": 30334858060,
            "artifact_id": 8680673043,
            "artifact_name": "item3-cgtube-pilot-certified-30334858060",
            "lambda": Rational(118, 25).to_json(),
            "root_interval": {
                "lo": Rational(1, 64).to_json(),
                "hi": Rational(11, 256).to_json(),
            },
            "b_kernel_sha256": MOCK_KERNEL_SHA256,
            "cg_kernel_sha256": MOCK_KERNEL_SHA256,
            "paper_lemma_id": FG_LEMMA,
        },
    }


def logical_dependencies(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "btube-logical-dependencies-v2.1",
        "cg_match_dependency": config["cg_match_dependency"],
        "logical_lemmas": [
            {"id": "PARAMETRIC_KRAWCZYK_EXISTENCE_V1", "machine_conclusion": True},
            {"id": "STRICT_MONOTONE_ZERO_UNIQUENESS_V1", "machine_conclusion": True},
            {"id": "CONTINUOUS_UNIQUE_ZERO_BRANCH_V1", "machine_conclusion": True},
            {"id": FG_LEMMA, "machine_conclusion": True},
            {"id": "ANALYTIC_IMPLICIT_BRANCH_V1", "machine_conclusion": False},
        ],
        "cross_item_note": "item2 B-TUBE intentionally matches the canonical item3 C-G-TUBE slice",
    }


def _cell_record(
    *,
    cell_index: int,
    lam_lo: Rational,
    lam_hi: Rational,
    q_left: Dyadic,
    q_right: Dyadic,
    y_box: DyadicInterval,
    display_tag: str,
) -> dict[str, Any]:
    predictor = AffinePredictor(lam_lo, lam_hi, q_left, q_right)
    q_hull = predictor.range_hull()
    x_box = physical_tube(q_hull, y_box)
    residual = F_interval(q_hull, (lam_lo, lam_hi))
    slope = dFdr_interval(x_box, (lam_lo, lam_hi))
    k_image = krawczyk_image(
        m=D_ZERO,
        residual=residual,
        slope=slope,
        preconditioner=D_NEG_ONE,
        domain=y_box,
    )
    return {
        "schema": "btube-record-v2.1",
        "phase": "cell",
        "cell_index": cell_index,
        "lambda": {"lo": lam_lo.to_json(), "hi": lam_hi.to_json()},
        "q_endpoint": {"left": q_left.to_json(), "right": q_right.to_json()},
        "q_rule": Q_RULE,
        "y_interval": y_box.to_json(),
        "m_y": D_ZERO.to_json(),
        "preconditioner": D_NEG_ONE.to_json(),
        "saved": {
            "q_hull": q_hull.to_json(),
            "physical_x": x_box.to_json(),
            "residual_h": residual.to_json(),
            "slope": slope.to_json(),
            "krawczyk": k_image.to_json(),
        },
        "unresolved": False,
        "display": {"tag": display_tag, "kind": "cell"},
    }


def _join_record(left: dict[str, Any], right: dict[str, Any], display_tag: str) -> dict[str, Any]:
    left_y = DyadicInterval.from_json(left["y_interval"])
    right_y = DyadicInterval.from_json(right["y_interval"])
    left_q = Dyadic.from_json(left["q_endpoint"]["right"])
    right_q = Dyadic.from_json(right["q_endpoint"]["left"])
    lam = Rational.from_json(left["lambda"]["hi"])
    intersection = exact_join_intersection(left_q, left_y, right_q, right_y)
    midpoint = intersection.midpoint()
    residual = F_interval(DyadicInterval.point(midpoint), (lam, lam))
    slope = dFdr_interval(intersection, (lam, lam))
    k_image = krawczyk_image(
        m=midpoint,
        residual=residual,
        slope=slope,
        preconditioner=D_NEG_ONE,
        domain=intersection,
    )
    return {
        "schema": "btube-record-v2.1",
        "phase": "join",
        "between": [left["cell_index"], right["cell_index"]],
        "lambda": lam.to_json(),
        "left_section": shifted(left_y, left_q).to_json(),
        "right_section": shifted(right_y, right_q).to_json(),
        "intersection": intersection.to_json(),
        "midpoint": midpoint.to_json(),
        "preconditioner": D_NEG_ONE.to_json(),
        "saved": {
            "residual": residual.to_json(),
            "slope": slope.to_json(),
            "krawczyk": k_image.to_json(),
        },
        "unresolved": False,
        "display": {"tag": display_tag, "kind": "join"},
    }


def _boundary_record(first: dict[str, Any], *, full: bool, display_tag: str) -> dict[str, Any]:
    lam = Rational.from_json(first["lambda"]["lo"])
    base: dict[str, Any] = {
        "schema": "btube-record-v2.1",
        "phase": "boundary",
        "lambda_start": lam.to_json(),
        "status": "PASS" if full else "DEFERRED",
        "unresolved": False,
        "display": {"tag": display_tag, "kind": "boundary"},
    }
    if not full:
        return base
    terminal = DyadicInterval(ROOT - Dyadic(1, 6), ROOT + Dyadic(1, 6))
    first_y = DyadicInterval.from_json(first["y_interval"])
    first_q = Dyadic.from_json(first["q_endpoint"]["left"])
    first_section = shifted(first_y, first_q)
    intersection = terminal.intersection(first_section)
    if intersection is None or not intersection.positive_width():
        raise RuntimeError("mock boundary intersection unexpectedly failed")
    midpoint = intersection.midpoint()
    residual = F_interval(DyadicInterval.point(midpoint), (lam, lam))
    slope = dFdr_interval(intersection, (lam, lam))
    k_image = krawczyk_image(
        m=midpoint,
        residual=residual,
        slope=slope,
        preconditioner=D_NEG_ONE,
        domain=intersection,
    )
    base.update(
        {
            "dependency_artifact_sha256": BLOCAL_MOCK_SHA256,
            "terminal_root_interval": terminal.to_json(),
            "first_section": first_section.to_json(),
            "intersection": intersection.to_json(),
            "midpoint": midpoint.to_json(),
            "preconditioner": D_NEG_ONE.to_json(),
            "saved": {
                "residual": residual.to_json(),
                "slope": slope.to_json(),
                "krawczyk": k_image.to_json(),
            },
        }
    )
    return base


def _match_record(last: dict[str, Any], config: dict[str, Any], display_tag: str) -> dict[str, Any]:
    lam = Rational.from_json(last["lambda"]["hi"])
    last_y = DyadicInterval.from_json(last["y_interval"])
    last_q = Dyadic.from_json(last["q_endpoint"]["right"])
    section = shifted(last_y, last_q)
    midpoint = section.midpoint()
    residual = F_interval(DyadicInterval.point(midpoint), (lam, lam))
    slope = dFdr_interval(section, (lam, lam))
    k_image = krawczyk_image(
        m=midpoint,
        residual=residual,
        slope=slope,
        preconditioner=D_NEG_ONE,
        domain=section,
    )
    cg = config["cg_match_dependency"]
    return {
        "schema": "btube-record-v2.1",
        "phase": "match",
        "lambda": lam.to_json(),
        "last_section": section.to_json(),
        "midpoint": midpoint.to_json(),
        "preconditioner": D_NEG_ONE.to_json(),
        "cg_root_interval": {
            "lo": Dyadic.from_fraction(Rational.from_json(cg["root_interval"]["lo"]).as_fraction()).to_json(),
            "hi": Dyadic.from_fraction(Rational.from_json(cg["root_interval"]["hi"]).as_fraction()).to_json(),
        },
        "cg_artifact_sha256": cg["artifact_zip_sha256"],
        "b_kernel_sha256": cg["b_kernel_sha256"],
        "cg_kernel_sha256": cg["cg_kernel_sha256"],
        "fg_identity_lemma_id": cg["paper_lemma_id"],
        "saved": {
            "residual": residual.to_json(),
            "slope": slope.to_json(),
            "krawczyk": k_image.to_json(),
        },
        "unresolved": False,
        "display": {"tag": display_tag, "kind": "match"},
    }


def _chain_records(records: list[dict[str, Any]], config: dict[str, Any]) -> tuple[bytes, str]:
    previous = config["chain_genesis_sha256"]
    chained: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        item = dict(record)
        item["record_index"] = index
        item["previous_record_sha256"] = previous
        raw = canonical_json_bytes(item)
        previous = sha256_hex(raw)
        chained.append(item)
    return canonical_jsonl(chained), previous


def build_bundle(
    *,
    full: bool = True,
    tight: bool = False,
    display_tag: str = "A",
    checker_dps: int = 60,
) -> Bundle:
    config = default_config(checker_dps=checker_dps)
    lam0 = Rational(2, 1)
    lam1 = Rational(3, 1)
    lam2 = Rational(118, 25)
    if tight:
        offset = Dyadic(1, 10)
        y_box = DyadicInterval(Dyadic(-3, 11), Dyadic(3, 11))
    else:
        offset = Dyadic(1, 8)
        y_box = DyadicInterval(Dyadic(-1, 7), Dyadic(1, 7))
    cells = [
        _cell_record(
            cell_index=0,
            lam_lo=lam0,
            lam_hi=lam1,
            q_left=ROOT - offset,
            q_right=ROOT + offset,
            y_box=y_box,
            display_tag=display_tag,
        ),
        _cell_record(
            cell_index=1,
            lam_lo=lam1,
            lam_hi=lam2,
            q_left=ROOT - offset,
            q_right=ROOT + offset,
            y_box=y_box,
            display_tag=display_tag,
        ),
    ]
    records = [
        _boundary_record(cells[0], full=full, display_tag=display_tag),
        *cells,
        _join_record(cells[0], cells[1], display_tag),
        _match_record(cells[-1], config, display_tag),
    ]
    records_jsonl, chain_tip = _chain_records(records, config)
    summary = {
        "schema": "btube-certificate-v2.1",
        "mode": "SELFTEST_ONLY",
        "expected_verdict": "CERTIFIED_B_TUBE_FULL" if full else "CERTIFIED_CORE_INTERVAL",
        "boundary_connection": "PASS" if full else "DEFERRED",
        "record_count": len(records),
        "chain_tip_sha256": chain_tip,
        "unresolved_terminal": 0,
        "machine_conclusion": {
            "each_lambda_has_exactly_one_tube_root": True,
            "slope_strictly_negative": True,
            "cell_roots_form_one_continuous_branch": True,
            "real_analytic": False,
        },
    }
    return Bundle(
        config_bytes=canonical_json_bytes(config),
        dependencies_bytes=canonical_json_bytes(logical_dependencies(config)),
        records_jsonl=records_jsonl,
        summary_bytes=canonical_json_bytes(summary),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--core", action="store_true")
    parser.add_argument("--tight", action="store_true")
    args = parser.parse_args()
    bundle = build_bundle(full=not args.core, tight=args.tight)
    bundle.write(args.out)
    print(args.out)


if __name__ == "__main__":
    main()
