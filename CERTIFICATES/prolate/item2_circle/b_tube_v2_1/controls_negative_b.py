#!/usr/bin/env python3
"""Dependency, byte and precision B-TUBE v2.1 negative controls."""
from controls_common import *

def neg_match_interval_tamper() -> int:
    return exit_for_bundle(_mutate_record(build_bundle(), "match", lambda r: r["cg_root_interval"].__setitem__("lo", Dyadic(1, 4).to_json())))


def neg_cg_artifact_sha_tamper() -> int:
    return exit_for_bundle(_mutate_record(build_bundle(), "match", lambda r: r.__setitem__("cg_artifact_sha256", "3" * 64)))


def neg_cg_kernel_sha_mismatch() -> int:
    return exit_for_bundle(_mutate_record(build_bundle(), "match", lambda r: r.__setitem__("cg_kernel_sha256", "4" * 64)))


def neg_fg_identity_lemma_missing() -> int:
    bundle = build_bundle()
    config, deps, records, summary = _objects(bundle)
    deps["logical_lemmas"] = [entry for entry in deps["logical_lemmas"] if entry.get("id") != FG_LEMMA]
    return exit_for_bundle(_rebuild(bundle, config=config, deps=deps, records=records, summary=summary))


def neg_previous_record_sha() -> int:
    bundle = build_bundle()
    lines = bundle.records_jsonl.split(b"\n")
    obj = parse_canonical_json_bytes(lines[1])
    obj["previous_record_sha256"] = "5" * 64
    lines[1] = canonical_json_bytes(obj)
    return exit_for_bundle(replace(bundle, records_jsonl=b"\n".join(lines)))


def neg_chain_record_reorder() -> int:
    bundle = build_bundle()
    lines = bundle.records_jsonl.split(b"\n")
    lines[1], lines[2] = lines[2], lines[1]
    return exit_for_bundle(replace(bundle, records_jsonl=b"\n".join(lines)))


def neg_record_key_order_noncanonical() -> int:
    bundle = build_bundle()
    lines = bundle.records_jsonl.split(b"\n")
    obj = parse_canonical_json_bytes(lines[0])
    lines[0] = json.dumps(obj, ensure_ascii=True, sort_keys=False, separators=(",", ":")).encode("utf-8")
    if lines[0] == canonical_json_bytes(obj):
        lines[0] = json.dumps({"zz": 0, **obj}, ensure_ascii=True, sort_keys=False, separators=(",", ":")).encode("utf-8")
    return exit_for_bundle(replace(bundle, records_jsonl=b"\n".join(lines)))


def neg_record_whitespace_noncanonical() -> int:
    bundle = build_bundle()
    lines = bundle.records_jsonl.split(b"\n")
    obj = parse_canonical_json_bytes(lines[0])
    lines[0] = json.dumps(obj, ensure_ascii=True, sort_keys=True, indent=1).encode("utf-8").replace(b"\n", b" ")
    return exit_for_bundle(replace(bundle, records_jsonl=b"\n".join(lines)))


def neg_record_trailing_newline() -> int:
    bundle = build_bundle()
    return exit_for_bundle(replace(bundle, records_jsonl=bundle.records_jsonl + b"\n"))


def neg_record_crlf() -> int:
    bundle = build_bundle()
    return exit_for_bundle(replace(bundle, records_jsonl=bundle.records_jsonl.replace(b"\n", b"\r\n", 1)))


def neg_record_duplicate_key() -> int:
    bundle = build_bundle()
    lines = bundle.records_jsonl.split(b"\n")
    raw = lines[0]
    if not raw.startswith(b"{"):
        return 1
    lines[0] = b'{"phase":"duplicate",' + raw[1:]
    return exit_for_bundle(replace(bundle, records_jsonl=b"\n".join(lines)))


def neg_record_chain_hash_over_linefeed() -> int:
    bundle = build_bundle()
    lines = bundle.records_jsonl.split(b"\n")
    second = parse_canonical_json_bytes(lines[1])
    second["previous_record_sha256"] = sha256_hex(lines[0] + b"\n")
    lines[1] = canonical_json_bytes(second)
    return exit_for_bundle(replace(bundle, records_jsonl=b"\n".join(lines)))


def neg_checker_dps_below_generator_dps() -> int:
    return exit_for_bundle(build_bundle(checker_dps=59))


def neg_unresolved_leaf() -> int:
    return exit_for_bundle(_mutate_record(build_bundle(), "cell", lambda r: r.__setitem__("unresolved", True)))


def neg_adapter_string_path_detected() -> int:
    return _exit_custom(lambda: (_ for _ in ()).throw(AssertionError("forbidden path")) if canonical_source_forbidden("value = flo" + "at(x)") else None)





__all__ = [name for name in globals() if not name.startswith("__")]
