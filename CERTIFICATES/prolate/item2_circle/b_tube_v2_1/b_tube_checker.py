#!/usr/bin/env python3
"""Independent fail-closed checker for B-TUBE v2.1 self-test artifacts."""
from checker_common import *
from checker_records import *

def check_bundle(bundle: Bundle) -> CheckResult:
    try:
        config, dependencies, records_raw, summary = _parse_bundle(bundle)
        _check_config_and_dependencies(config, dependencies)
        records = _check_chain(config, records_raw, summary)
        if summary.get("unresolved_terminal") != 0:
            _fail("unresolved terminal is nonzero")
        conclusion = summary.get("machine_conclusion")
        if not isinstance(conclusion, dict) or conclusion.get("real_analytic") is not False:
            _fail("machine conclusion must exclude real analyticity")
        boundary_records = [record for record in records if record.get("phase") == "boundary"]
        cell_records = [record for record in records if record.get("phase") == "cell"]
        join_records = [record for record in records if record.get("phase") == "join"]
        match_records = [record for record in records if record.get("phase") == "match"]
        if len(boundary_records) != 1 or len(match_records) != 1 or not cell_records:
            _fail("required record phases missing or duplicated")
        if len(join_records) != len(cell_records) - 1:
            _fail("JOIN record count mismatch")
        cells = [_check_cell(record, index) for index, record in enumerate(cell_records)]
        lambda_start = Rational.from_json(config["lambda_start"])
        lambda_match = Rational.from_json(config["lambda_match"])
        if cells[0]["lambda_lo"] != lambda_start:
            _fail("cell coverage does not begin at lambda_start")
        if cells[-1]["lambda_hi"] != lambda_match:
            _fail("cell coverage does not end at 118/25")
        for left, right in zip(cells, cells[1:]):
            if left["lambda_hi"] != right["lambda_lo"]:
                if left["lambda_hi"] < right["lambda_lo"]:
                    _fail("lambda coverage gap")
                _fail("lambda coverage overlap")
        for record, left, right in zip(join_records, cells, cells[1:]):
            _check_join(record, left, right)
        verdict = _check_boundary(boundary_records[0], cells[0], config, summary)
        _check_match(match_records[0], cells[-1], config)
        if summary.get("expected_verdict") != verdict:
            _fail("summary verdict differs from reconstructed verdict")
        return CheckResult(
            verdict=verdict,
            cells=len(cells),
            joins=len(join_records),
            chain_tip_sha256=summary["chain_tip_sha256"],
        )
    except (SchemaError, KeyError, TypeError, ValueError) as exc:
        raise CheckError(f"schema/reconstruction failure: {exc}") from exc


def load_bundle(directory: Path) -> Bundle:
    return Bundle(
        config_bytes=(directory / "config.json").read_bytes(),
        dependencies_bytes=(directory / "DEPENDENCIES.json").read_bytes(),
        records_jsonl=(directory / "B_TUBE_RECORDS.jsonl").read_bytes(),
        summary_bytes=(directory / "B_TUBE_CERTIFICATE.json").read_bytes(),
    )


def exit_for_bundle(bundle: Bundle) -> int:
    try:
        check_bundle(bundle)
    except CheckError as exc:
        return exc.exit_code
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        result = check_bundle(load_bundle(args.directory))
    except CheckError as exc:
        print(exc)
        raise SystemExit(exc.exit_code)
    print(result.verdict, result.cells, result.joins, result.chain_tip_sha256)


if __name__ == "__main__":
    main()
