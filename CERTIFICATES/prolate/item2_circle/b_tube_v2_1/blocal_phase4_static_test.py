#!/usr/bin/env python3
"""Calculation-free static audit for B-LOCAL v2.1 Phase 4.

The production kernel is parsed as source but is never imported or evaluated.
"""
from __future__ import annotations

import ast
import hashlib
import json
import py_compile
import sys
import zipfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve(strict=True).parent
REPOSITORY_ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import blocal_arb_adapter as adapter  # noqa: E402
import blocal_phase4_engine as engine  # noqa: E402
import blocal_phase4_model as model  # noqa: E402
import blocal_phase4_provenance as provenance  # noqa: E402
import blocal_phase4_runner as runner  # noqa: E402

CONFIG_PATH = HERE / "config.blocal-run.json"
ROUTE_DOC_PATH = HERE / "BLOCAL_R1_ENDPOINT_ROUTE.md"
REQUIREMENTS_PATH = HERE / "requirements.blocal-run.txt"
WORKFLOW_PATH = REPOSITORY_ROOT / ".github/workflows/prolate-item2-blocal-v2-1.yml"
EXPECTED_STAGE1_ARCHIVE = "ab7112ae7ae570555d1add5c48adb72100562c71aff6b74c94883f58da0f495b"
EXPECTED_STAGE1_CONFIG = "da7e1554ca29344cd4d781cb3cc48a3581d1e3d36ca3ac7cf837d42fb313e37e"
EXPECTED_KERNEL = "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac"
EXPECTED_WHEEL = "376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76"
IMPLEMENTATION_NAMES = (
    "blocal_phase4_runner.py", "blocal_phase4_model.py",
    "blocal_phase4_provenance.py", "blocal_phase4_engine.py",
)


class StaticAuditError(RuntimeError):
    pass


def need(value: Any, message: str) -> None:
    if not value:
        raise StaticAuditError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function(tree: ast.Module, name: str) -> ast.FunctionDef:
    matches = [node for node in tree.body
               if isinstance(node, ast.FunctionDef) and node.name == name]
    need(len(matches) == 1, f"function {name}")
    return matches[0]


def dotted(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def calls(node: ast.AST) -> list[str]:
    return [name for child in ast.walk(node) if isinstance(child, ast.Call)
            and (name := dotted(child.func))]


def constants(node: ast.AST) -> list[Any]:
    return [child.value for child in ast.walk(node)
            if isinstance(child, ast.Constant)]


def source_tree(path: Path) -> tuple[str, ast.Module]:
    source = path.read_text(encoding="utf-8")
    return source, ast.parse(source, filename=str(path))


def audit_config() -> dict[str, Any]:
    raw = CONFIG_PATH.read_bytes()
    config = model.parse_canonical_json(raw)
    model.validate_config(config)
    stage1 = config["stage1_dependency"]
    need(stage1["artifact_zip_sha256"] == EXPECTED_STAGE1_ARCHIVE,
         "Stage-1 archive anchor")
    need(stage1["config_sha256"] == EXPECTED_STAGE1_CONFIG,
         "Stage-1 descriptor anchor")
    need(stage1["source_head"] == "b0582728d3f8fd3508ba8574a898017212a28caa",
         "Stage-1 source head")
    need(stage1["certificate_sha256"] ==
         "d7a1d0764dd1138a59090e53f1e601c58c703f2d34c0c16eb4b2c4f3f4539188",
         "Stage-1 certificate hash")
    need(stage1["manifest_sha256"] ==
         "f15d01b410a53ad14dd86688cb7a8a86bf6ef85b108d1d3822840bb0a97bc069",
         "Stage-1 manifest hash")
    need(config["kernel"]["sha256"] == EXPECTED_KERNEL, "kernel anchor")
    need(config["endpoint_route"]["id"] == model.ROUTE_ID, "route A")
    need(config["authorization"] == {
        "execution": "TAG_ONLY_EXPLICIT_AUTHORIZATION_REQUIRED",
        "diagnostic_cli": False,
        "calibration_auto_start": False,
    }, "authorization boundary")
    pins = config["implementation"]["sources_sha256"]
    expected_paths = {
        f"CERTIFICATES/prolate/item2_circle/b_tube_v2_1/{name}"
        for name in IMPLEMENTATION_NAMES
    }
    need(set(pins) == expected_paths, "implementation source allowlist")
    for relative_path, expected in pins.items():
        need(digest(REPOSITORY_ROOT / relative_path) == expected,
             f"implementation source pin: {relative_path}")
    need(config["implementation"]["entrypoint_path"].endswith(
         "/blocal_phase4_runner.py"), "entrypoint")
    need(digest(HERE / "blocal_arb_adapter.py") ==
         config["adapter"]["source_sha256"], "adapter source pin")
    lemmas = model.logical_lemmas()
    need(isinstance(lemmas, list) and len(lemmas) == 1
         and lemmas[0]["machine_verified"] is False, "logical lemma boundary")
    return config


def audit_existing_pins(config: dict[str, Any]) -> None:
    stage1 = config["stage1_dependency"]
    descriptor = REPOSITORY_ROOT / stage1["config_path"]
    archive = REPOSITORY_ROOT / stage1["artifact_path"]
    kernel = REPOSITORY_ROOT / config["kernel"]["path"]
    for path in (descriptor, archive, kernel):
        need(path.is_file() and not path.is_symlink(), f"pinned regular file: {path}")
    need(digest(descriptor) == EXPECTED_STAGE1_CONFIG, "descriptor byte identity")
    need(digest(archive) == EXPECTED_STAGE1_ARCHIVE, "archive byte identity")
    need(digest(kernel) == EXPECTED_KERNEL, "kernel byte identity")
    provenance.verify_stage1_dependency(REPOSITORY_ROOT, stage1)
    descriptor_obj = model.parse_canonical_json(descriptor.read_bytes())
    with zipfile.ZipFile(archive) as bundle:
        need(bundle.testzip() is None, "archive CRC")
        need(bundle.namelist() == descriptor_obj["archive_members"], "archive members")


def audit_kernel_structure(config: dict[str, Any]) -> None:
    path = REPOSITORY_ROOT / config["kernel"]["path"]
    _, tree = source_tree(path)
    states: list[Any] = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "FORMULA_STATE"
            for target in node.targets
        ) and isinstance(node.value, ast.Constant):
            states.append(node.value.value)
    need(states == ["FILLED"], "kernel FORMULA_STATE")
    for name in ("F_arb", "dFdr_arb"):
        node = function(tree, name)
        args = node.args.args
        need([arg.arg for arg in args] == ["r", "lam", "tol", "depth", "limit"],
             f"kernel API {name}")
        need([dotted(arg.annotation) for arg in args[:2]] == ["arb", "arb"],
             f"kernel input types {name}")
        need(dotted(node.returns) == "arb", f"kernel return type {name}")


def audit_provenance_structure() -> None:
    path = HERE / "blocal_phase4_provenance.py"
    source, tree = source_tree(path)
    loader = function(tree, "load_pinned_module")
    text = ast.get_source_segment(source, loader) or ""
    loader_calls = calls(loader)
    need(loader_calls.count("path.read_bytes") >= 2, "pre/post source rehash")
    for token in ("module.__file__", "pre-import hash", "imported origin mismatch",
                  "post-import hash", "resolve(strict=True)"):
        need(token in text, f"module provenance gate: {token}")
    repository_gate = function(tree, "repo_file")
    gate_text = ast.get_source_segment(source, repository_gate) or ""
    for token in ("is_symlink", "relative_to(root)", "is_file"):
        need(token in gate_text, f"path containment gate: {token}")


def audit_runner_and_engine_structure() -> None:
    runner_source, runner_tree = source_tree(HERE / "blocal_phase4_runner.py")
    engine_source, engine_tree = source_tree(HERE / "blocal_phase4_engine.py")
    combined = runner_source + engine_source
    need("--" + "diagnostic" not in combined, "diagnostic CLI absent")
    need("B_arb" not in combined, "alternate boundary kernel absent")
    run_node = function(runner_tree, "run")
    run_text = ast.get_source_segment(runner_source, run_node) or ""
    need(run_text.index("verify_stage1_dependency") < run_text.index("from flint import"),
         "Stage-1 gate before flint import")
    need(run_text.index("verify_implementation_sources") < run_text.index("from flint import"),
         "source gate before flint import")
    need(run_text.index("from flint import") < run_text.index(
         '"blocal_pinned_prolate_circle_F_cleanroom"'), "kernel import order")
    main = function(runner_tree, "main")
    options = [value for value in constants(main)
               if isinstance(value, str) and value.startswith("--")]
    need(options == ["--config", "--output-dir"], "CLI exact options")

    l1 = function(engine_tree, "evaluate_l1")
    l2 = function(engine_tree, "evaluate_l2")
    l3 = function(engine_tree, "evaluate_l3_route_a")
    need("kernel.dFdr_arb" in calls(l1), "L1 dFdr_arb")
    need("kernel.F_arb" in calls(l2), "L2 F_arb")
    need("kernel.F_arb" in calls(l3), "L3 F_arb")
    need("kernel.dFdr_arb" not in calls(l3), "L3 derivative substitution absent")
    l3_text = ast.get_source_segment(engine_source, l3) or ""
    need("exact_r_one = arb_type(1)" in l3_text, "L3 exact integer r=1")
    need(not any(isinstance(value, float) for value in constants(l3)), "L3 float absent")
    need(not any(isinstance(node, ast.Try) for node in ast.walk(l3)), "L3 fallback absent")
    options_node = function(engine_tree, "kernel_options")
    options_text = ast.get_source_segment(engine_source, options_node) or ""
    need("arb_exact_dyadic" in options_text and '"tol"' in options_text,
         "exact binary tolerance path")


def audit_adapter() -> None:
    source, tree = source_tree(HERE / "blocal_arb_adapter.py")
    for token in ("float(", "Decimal(", ".str(", "repr("):
        need(token not in source, f"adapter forbidden path: {token}")
    adapter_node = function(tree, "arb_ball_to_canonical_dyadic_interval")
    need(calls(adapter_node).count("exact_man_exp") == 2,
         "adapter midpoint/radius exact extraction")

    class ManExp:
        def __init__(self, m: Any, e: Any): self.value = (m, e)
        def man_exp(self) -> tuple[Any, Any]: return self.value

    class Ball:
        def __init__(self, mm: Any, me: Any, rm: Any, re: Any):
            self._mid, self._rad = ManExp(mm, me), ManExp(rm, re)
        def mid(self) -> ManExp: return self._mid
        def rad(self) -> ManExp: return self._rad

    cases = (
        (0, 0, 0, 0), (3, 0, 0, 0), (-3, 0, 0, 0),
        (3, -4, 0, 0), (-3, -4, 0, 0), (3, -4, 1, -7),
        (7, -3, 1, -3), (-7, -3, 1, -3), (1, -2, 1, -1),
        (2**200 + 1, -100, 3, -120),
    )
    for case in cases:
        interval = adapter.arb_ball_to_canonical_dyadic_interval(Ball(*case))
        model.interval_fractions(interval, f"adapter case {case}")
    try:
        adapter.arb_ball_to_canonical_dyadic_interval(Ball("nan", 0, 0, 0))
    except adapter.AdapterError:
        pass
    else:
        raise StaticAuditError("adapter nonfinite synthetic input accepted")


def audit_route_and_requirements() -> None:
    route = ROUTE_DOC_PATH.read_text(encoding="utf-8")
    for token in ("Route A", "F_arb(r=1", EXPECTED_KERNEL, "No `1-epsilon`",
                  "No exception handler retries", "MATHEMATICAL RUN NOT AUTHORIZED"):
        need(token in route, f"route document: {token}")
    requirements = REQUIREMENTS_PATH.read_text(encoding="ascii")
    need("python-flint==0.9.0" in requirements, "python-flint version")
    need(f"--hash=sha256:{EXPECTED_WHEEL}" in requirements, "wheel hash")
    need(requirements.count("--hash=") == 1, "dependency allowlist")


def audit_workflow(config: dict[str, Any]) -> None:
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    lower = text.lower()
    for forbidden in ("workflow_dispatch", "pull_request", "schedule:",
                      "--" + "diagnostic", "calibration"):
        need(forbidden not in lower, f"workflow forbidden token: {forbidden}")
    for required in (
        "tags:", "blocal-v2.1-run-*", "permissions:", "contents: read",
        "persist-credentials: false",
        "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683",
        "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
        "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
        "--require-hashes", "--only-binary=:all:", "--no-deps",
        'test ! -e "$RUN_DIR"', 'mkdir -m 700 "$RUN_DIR"',
    ):
        need(required in text, f"workflow required token: {required}")
    gate = text.index("Independent byte and structure gate")
    setup = text.index("Set up pinned Python")
    install = text.index("Install hash-pinned runtime dependency")
    execute = text.index("Execute separately authorized B-LOCAL run")
    need(gate < setup < install < execute, "workflow gate/setup/install/run order")
    pinned_paths = dict(config["implementation"]["sources_sha256"])
    pinned_paths[config["adapter"]["path"]] = config["adapter"]["source_sha256"]
    pinned_paths["CERTIFICATES/prolate/item2_circle/b_tube_v2_1/config.blocal-run.json"] = digest(CONFIG_PATH)
    pinned_paths["CERTIFICATES/prolate/item2_circle/b_tube_v2_1/blocal_phase4_static_test.py"] = digest(Path(__file__).resolve(strict=True))
    pinned_paths["CERTIFICATES/prolate/item2_circle/b_tube_v2_1/requirements.blocal-run.txt"] = digest(REQUIREMENTS_PATH)
    for path, expected in pinned_paths.items():
        need(f"{expected}  {path}" in text, f"workflow file pin: {path}")
    need(f"{EXPECTED_STAGE1_ARCHIVE}  {config['stage1_dependency']['artifact_path']}" in text,
         "workflow Stage-1 archive pin")
    need(f"{EXPECTED_STAGE1_CONFIG}  {config['stage1_dependency']['config_path']}" in text,
         "workflow Stage-1 descriptor pin")
    need(f"{EXPECTED_KERNEL}  {config['kernel']['path']}" in text,
         "workflow kernel pin")


def main() -> int:
    for name in (*IMPLEMENTATION_NAMES, "blocal_arb_adapter.py",
                 "blocal_phase4_static_test.py"):
        py_compile.compile(str(HERE / name), doraise=True)
    config = audit_config()
    audit_existing_pins(config)
    audit_kernel_structure(config)
    audit_provenance_structure()
    audit_runner_and_engine_structure()
    audit_adapter()
    audit_route_and_requirements()
    audit_workflow(config)
    result = {
        "schema": "blocal-phase4-static-audit-v1",
        "calculation_free": True,
        "kernel_imported": False,
        "kernel_evaluated": False,
        "endpoint_route": model.ROUTE_ID,
        "stage1_archive_sha256": EXPECTED_STAGE1_ARCHIVE,
        "stage1_config_sha256": EXPECTED_STAGE1_CONFIG,
        "kernel_sha256": EXPECTED_KERNEL,
        "status": "CHAT_SIDE_AUDIT_WAITING",
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
