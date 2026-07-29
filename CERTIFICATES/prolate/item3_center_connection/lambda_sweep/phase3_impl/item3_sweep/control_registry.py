from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping

@dataclass(frozen=True)
class ControlBinding:
    control_id: str
    design_group: str
    implementation_component: str
    implementation_assertion: str
    test_case: str
    expectation_source: str

_GROUPS: dict[tuple[str, str], tuple[str, ...]] = {
    ('15.10', 'schema.dependencies'): (
        'NEG_LOGICAL_ALLOWLIST_CONFIG_BOOLEAN',
        'NEG_LOGICAL_ALLOWLIST_ID_MISMATCH',
        'NEG_LOGICAL_HASH_MISMATCH',
        'NEG_LOGICAL_LEMMA_ID_MISMATCH',
        'NEG_LOGICAL_NONCANONICAL_OBJECT',
        'NEG_LOGICAL_PAPER_LEMMA_SUBSTITUTION',
        'NEG_LOGICAL_REQUIRED_KEY_MISSING',
        'NEG_LOGICAL_SUPPORTS_CONFIG_SELF_REPORT',
        'NEG_LOGICAL_SUPPORTS_FALSE',
        'NEG_LOGICAL_UNKNOWN_ENTRY_FIELD',
        'NEG_LOGICAL_UNKNOWN_KEY',
    ),
    ('15.11', 'schema.config'): (
        'NEG_CONFIG_ALIAS_RETAINED',
        'NEG_CONFIG_ALIAS_VALUE_MISMATCH',
        'NEG_CONFIG_CHECKER_DPS',
        'NEG_CONFIG_COMPLETE_HASH_MISMATCH',
        'NEG_CONFIG_DELTA_OVERLAP_NONPOSITIVE',
        'NEG_CONFIG_ENCODING_ID',
        'NEG_CONFIG_ID_EMPTY',
        'NEG_CONFIG_ID_INVALID_CHARACTER',
        'NEG_CONFIG_LAMBDA_TARGET_DOMAIN',
        'NEG_CONFIG_PATH_ABSOLUTE',
        'NEG_CONFIG_PATH_DOTDOT',
        'NEG_CONFIG_PATH_EMPTY_COMPONENT',
        'NEG_CONFIG_PATH_SYMLINK_ESCAPE',
        'NEG_CONFIG_REQUIRED_FIELD_MISSING',
        'NEG_CONFIG_R_TILE_ALGORITHM_ID',
        'NEG_CONFIG_SHA_LENGTH',
        'NEG_CONFIG_SHA_UPPERCASE',
        'NEG_CONFIG_UNKNOWN_TOP_LEVEL_FIELD',
    ),
    ('15.2', 'checker.coverage'): (
        'NEG_COVERAGE_FAILED_ATTEMPT_INCLUDED',
        'NEG_COVERAGE_FAILED_PARENT_INCLUDED',
        'NEG_OPEN_CELL_COVERAGE_NOT_ONE',
        'NEG_OUTER_ENDPOINT_DUPLICATE',
        'NEG_PARTITION_LEAF_COUNT',
        'NEG_R_TILE_ORDER',
        'NEG_S1_SIGN',
        'NEG_S2_SIGN',
        'NEG_S3_NONNEGATIVE_CELL',
        'NEG_SHARED_ENDPOINT_BYTES_LAMBDA',
        'NEG_SHARED_ENDPOINT_BYTES_R',
        'NEG_SHARED_ENDPOINT_INCIDENT_NOT_TWO',
    ),
    ('15.3', 'canonical.frontier'): (
        'NEG_INCOMPLETE_INDEX_TERMINATES_AT_TARGET',
        'NEG_LAMBDA_CHAIN_GAP',
        'NEG_LAMBDA_CHAIN_OVERLAP',
        'NEG_LAMBDA_DENOMINATOR_NONPOSITIVE',
        'NEG_LAMBDA_DYADIC_FORCED_MUTATION',
        'NEG_LAMBDA_NONREDUCED',
        'NEG_LAMBDA_REACHED_JUMP',
        'NEG_TARGET_CLIP_VIOLATION',
        'NEG_ZERO_PASS_B0_CREATED',
        'NEG_ZERO_PASS_DEGENERATE_INTERVAL_QUOTED',
    ),
    ('15.4', 'checker.identity'): (
        'NEG_A5A_A5B_MIXED',
        'NEG_ANCHOR_PREDICATE',
        'NEG_DESIGN_HASH_MISMATCH',
        'NEG_ICG_NOT_CONTAINED_FATAL',
        'NEG_INTERNAL_J_INCONSISTENCY_RETRYABLE',
        'NEG_J_NONPOSITIVE',
        'NEG_KERNEL_IDENTITY_MISMATCH_RETRYABLE',
        'NEG_PILOT_KERNEL_HASH_MISMATCH',
        'NEG_PILOT_RECEIPT_HASH_MISMATCH',
        'NEG_PILOT_RUN_ID_MISMATCH',
        'NEG_PILOT_SOURCE_HASH_MISMATCH',
        'NEG_REQUIRED_RECORD_MISSING_RETRYABLE',
        'NEG_S7_APPLIED_TO_NONANCHOR_CHILD',
        'NEG_S7_APPLIED_TO_SEED_NOT_FINAL_W0',
        'NEG_S7_INTERSECTION_ONLY',
        'NEG_SEED_USED_AS_S6_ADJACENT_BOX',
        'NEG_SHARED_ENDPOINT_MISMATCH_RETRYABLE',
        'NEG_SNAPSHOT_PILOT_RELATION_MISMATCH',
    ),
    ('15.5', 'windows.transitions'): (
        'NEG_CLAMP_LOSES_MIN_WIDTH_ACCEPTED',
        'NEG_CLAMP_LOSES_OVERLAP_ACCEPTED',
        'NEG_INHERITED_OVERLAP_WRONG_CLASS',
        'NEG_INVALID_CLAMPED_WINDOW_INHERITED',
        'NEG_NEEDED_STEPS_NEGATIVE',
        'NEG_OVERLAP_DIRECTION',
        'NEG_OVERLAP_IMPOSSIBLE_INFINITE_LOOP',
        'NEG_OVERLAP_MIDPOINT_USES_CLAMPED_VALUE',
        'NEG_OVERLAP_OUTSIDE_DOMAIN_STEP',
        'NEG_OVERLAP_TIE',
        'NEG_PENDING_LOWER_IGNORES_NEW_UPPER_PASS',
        'NEG_PER_BOX_BUDGET_REGENERATION',
        'NEG_PREDICTOR_BOOTSTRAP',
        'NEG_PREDICTOR_CONTEXT_RECAPTURE_SAME_BOX',
        'NEG_PREDICTOR_CONTEXT_SPLIT_TIME_FROZEN',
        'NEG_PREDICTOR_PRIMARY_REGENERATION',
        'NEG_PREDICTOR_Q_NOT_LAMBDA_HI',
        'NEG_PRIMARY_BUILD_FAIL_CHILD_INHERITED',
        'NEG_REGENERATED_WINDOW_INHERITED',
        'NEG_REGENERATION_SECOND_TIME',
        'NEG_RUN_FATAL_REGENERATION',
        'NEG_R_CELL_BUDGET_REGENERATION',
        'NEG_SATURATED_SIDE_EXPANSION',
        'NEG_SEED_DOMAIN_GATE',
        'NEG_SEED_ICG_GATE',
        'NEG_SEED_MIN_WIDTH_GATE',
        'NEG_SEED_OVERLAP_WIDTH_GATE',
        'NEG_UNFINISHED_WINDOW_INHERITED',
        'NEG_WINDOW_FAIL_REGENERATION',
        'NEG_WINDOW_REDERIVATION_MISMATCH',
        'NEG_WINDOW_STEP_HISTORY_MISMATCH',
        'NEG_ZERO_REMAINING_REGENERATION',
    ),
    ('15.6', 'frontier.records'): (
        'NEG_CHILD_DEPTH_NOT_INCREMENTED',
        'NEG_CHILD_PER_BOX_COUNTER_NOT_RESET',
        'NEG_COMPLETE_FOLLOWED_BY_FRONTIER_STOP',
        'NEG_COMPLETE_GRAMMAR',
        'NEG_COMPLETE_WITH_NONEMPTY_STACK',
        'NEG_FRONTIER_STOP_NONDEPTH_ZERO',
        'NEG_FRONTIER_STOP_WITH_ATTEMPT_FAIL',
        'NEG_FRONTIER_STOP_WITH_ATTEMPT_FIELDS',
        'NEG_FRONTIER_STOP_WITH_SLICE_FAIL',
        'NEG_LOWER_CHILD_FIRST',
        'NEG_MIN_WIDTH_BOX_ATTEMPT',
        'NEG_PENDING_CHILD_NEW_INITIAL_BOX',
        'NEG_SPLIT_DEPTH_CONDITION',
        'NEG_SPLIT_HALF_WIDTH_CONDITION',
        'NEG_SPLIT_RECORD_CHILD_MISMATCH',
        'NEG_STACK_TOP_MISMATCH_NOT_FATAL',
        'NEG_TARGET_ZERO_WIDTH_CANDIDATE',
    ),
    ('15.7', 'budget.runner'): (
        'NEG_BUDGET_POSTCHECK',
        'NEG_EVALUATION_COUNTERS_NOT_SEPARATED',
        'NEG_FAILED_CALL_NOT_COUNTED',
        'NEG_GLOBAL_LIMIT_AFTER_PER_BOX_CHECK',
        'NEG_GLOBAL_STOP_ENCLOSURE_RETAINED',
        'NEG_GLOBAL_STOP_REGENERATION',
        'NEG_GLOBAL_STOP_SPLIT',
        'NEG_GUARD_RETRY_NOT_COUNTED',
        'NEG_PER_BOX_LIMIT_GREATER_THAN_GLOBAL',
        'NEG_PER_BOX_LIMIT_PER_ATTEMPT',
        'NEG_R_CELL_OVERBUDGET_ENCLOSURE_RETAINED',
    ),
    ('15.8', 'records.checker'): (
        'NEG_BOX_ATTEMPT_FAIL_MISSING',
        'NEG_CHECKER_FAIL_CERTIFIED',
        'NEG_ENUM_UNKNOWN_FAILURE_REASON',
        'NEG_PRIMARY_FAIL_RECORD_MISSING',
        'NEG_RECORD_ORDER_FINAL_FRONTIER',
        'NEG_RECORD_ORDER_GLOBAL_STOP',
        'NEG_RECORD_ORDER_PRIMARY_REGEN',
        'NEG_RECORD_ORDER_SPLIT',
        'NEG_REGENERATED_FAIL_RECORD_MISSING',
        'NEG_RUN_FATAL_EMITS_COMPLETE',
        'NEG_RUN_FATAL_EMITS_INCOMPLETE',
        'NEG_RUN_FATAL_EMITS_MANIFEST',
        'NEG_RUN_FATAL_USES_REACHED_FOR_VERDICT',
        'NEG_SLICE_BOX_FAIL_PROMOTED_COMPLETE',
        'NEG_SLICE_BOX_PASS_USED_AS_VERIFIED',
    ),
    ('15.9', 'canonical.verifier'): (
        'NEG_CERTIFIED_WORD_OUTSIDE_ALLOWLIST',
        'NEG_CHAIN_GENESIS_WRONG_DOMAIN',
        'NEG_CHAIN_USES_DEPENDENCY_HASH',
        'NEG_CHECKER_DPS_LT_DPS',
        'NEG_CHECKER_FRESH_SIGN_FAIL',
        'NEG_CHECKER_PREDICTOR_CONTEXT_MISMATCH',
        'NEG_CHECKER_STACK_MISMATCH',
        'NEG_CHECKER_WINDOW_ORDER_MISMATCH',
        'NEG_ENCLOSURE_ROUNDTRIP',
        'NEG_JSONL_FINAL_LF',
        'NEG_JSON_CRLF',
        'NEG_JSON_DUPLICATE_KEY',
        'NEG_JSON_TRAILING_LF',
        'NEG_NONCANONICAL_JSON',
    ),
    ('pos', 'integration'): (
        'POS_CHECKER_VERIFY_PASS',
        'POS_COMPLETE_2BOX',
        'POS_FRONTIER_STOP',
        'POS_GLOBAL_STOP',
        'POS_LIFO_PENDING_CHILD',
        'POS_PRIMARY_FAIL_REGENERATED_PASS',
        'POS_PRIMARY_UNBUILT_CHILD_CONTEXT',
        'POS_RUN_FATAL',
        'POS_TARGET_COMPLETE',
        'POS_WINDOW_FAIL_SPLIT',
    ),
}

def _binding(control_id: str, design_group: str, component: str) -> ControlBinding:
    return ControlBinding(
        control_id=control_id,
        design_group=design_group,
        implementation_component=component,
        implementation_assertion=f"{component}:{control_id}",
        test_case=f"test_control_{control_id.lower()}",
        expectation_source=f"phase2/CONTROL_EXPECT.json#{control_id}",
    )

CONTROL_BINDINGS: Mapping[str, ControlBinding] = {
    control_id: _binding(control_id, design_group, component)
    for (design_group, component), control_ids in _GROUPS.items()
    for control_id in control_ids
}

def validate_control_bindings(
    phase2_expect: Mapping[str, Mapping[str, Any]] | set[str] | None = None,
) -> None:
    if len(CONTROL_BINDINGS) != 168:
        raise RuntimeError(f"expected 168 controls, got {len(CONTROL_BINDINGS)}")
    if set(CONTROL_BINDINGS) != {binding.control_id for binding in CONTROL_BINDINGS.values()}:
        raise RuntimeError("control_id/key mismatch")
    if phase2_expect is None:
        return
    expected_ids = set(phase2_expect)
    if set(CONTROL_BINDINGS) != expected_ids:
        missing = sorted(expected_ids - set(CONTROL_BINDINGS))
        extra = sorted(set(CONTROL_BINDINGS) - expected_ids)
        raise RuntimeError(f"Phase-2/Phase-3 control key mismatch: missing={missing}, extra={extra}")
    if isinstance(phase2_expect, set):
        return
    required_fields = {"fixture_id", "mutation", "expected_failure_reason", "expected_terminal_class", "expected_checker_result"}
    for control_id, entry in phase2_expect.items():
        if set(entry) != required_fields or entry["fixture_id"] != control_id:
            raise RuntimeError(f"invalid Phase-2 expectation shape: {control_id}")
    mandatory = phase2_expect["NEG_PREDICTOR_PRIMARY_REGENERATION"]
    if mandatory["expected_checker_result"] != "VERIFY_FAIL" or mandatory["expected_failure_reason"] != "RECORD_GRAMMAR_VIOLATION":
        raise RuntimeError("predictor-primary regeneration expectation is not single-valued")
