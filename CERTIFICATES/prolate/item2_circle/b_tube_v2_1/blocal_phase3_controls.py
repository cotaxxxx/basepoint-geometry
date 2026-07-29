#!/usr/bin/env python3
"""Frozen 45-to-46 control mapping for B-LOCAL Phase 3."""
from blocal_phase3_contract import need

DESIGN_CODES = ['STAGE1_SOURCE_HEAD', 'STAGE1_CERT_SHA', 'STAGE1_MANIFEST_SHA', 'STAGE1_PATH', 'STAGE1_STATUS', 'STAGE1_STATEMENT', 'STAGE1_CONCLUSION', 'STAGE1_SCOPE', 'STAGE1_CONTENT_AUDIT', 'DEPENDENCY_ARCHIVE', 'EXACT_RATIONAL', 'LAMBDA_ORDER', 'UMAX_ORDER', 'L1_NEGATIVE_STRIP', 'L2_NEGATIVE_STRIP', 'L1L2_GLOBAL_ENDPOINT', 'SNEG_VALUE', 'SNEG_INTEGER_PROOF', 'SECTION6_DIRECTION', 'BRACKET_WIDTH_PROOF', 'L3_NONNEGATIVE', 'L4_BOUNDARY_ZERO', 'L4_STRICT_DECREASE', 'ENCLOSURE_OBJECT', 'ADAPTER_PIN', 'DYADIC_CANONICAL', 'ADAPTER_NONFINITE', 'DISPLAY_NONNORMATIVE', 'GENESIS_CONFIG_HASH', 'CONFIG_HASH_NAMES', 'RECORD_ORDER', 'PREVIOUS_HASH', 'JSONL_BYTES', 'JSON_CANONICAL', 'COVERAGE_GAP', 'COVERAGE_OVERLAP', 'DOMAIN_OUTSIDE', 'UNRESOLVED', 'BUDGET', 'JSTART_MISSING', 'JSTART_DUPLICATE', 'JSTART_POSITION', 'JSTART_PROOF', 'MODE_STATE', 'INCOMPLETE_PROMOTION']

SELFTEST = ['stage1_source_head_tamper', 'stage1_certificate_sha_tamper', 'stage1_manifest_sha_tamper', 'stage1_path_mismatch', 'stage1_status_not_certified', 'stage1_statement_mismatch', 'stage1_machine_conclusion_mismatch', 'stage1_scope_mismatch', 'stage1_content_audit_missing', 'dependency_archive_mutated', 'display_fraction_without_object', 'lambda_candidate_order_changed', 'u_max_order_changed', 'l1_domain_starts_zero', 'l2_domain_starts_zero', 'l1_l2_old_global_endpoint', 's_neg_wrong', 's_neg_float_comparison', 'section6_relation_reversed', 'bracket_width_proof_missing', 'l3_extended_negative', 'l4_missing_boundary_zero', 'l4_missing_strict_decrease', 'enclosure_freeform_string', 'adapter_pin_mismatch', 'noncanonical_dyadic', 'adapter_accepts_nonfinite', 'display_enclosure_normative', 'genesis_uses_stage1_hash', 'config_hash_names_conflated', 'record_order_changed', 'previous_hash_tamper', 'jsonl_crlf', 'duplicate_key_or_float', 'coverage_gap', 'coverage_overlap', 'tile_outside_rectangle', 'unresolved_leaf_promoted', 'budget_exceeded_success', 'jstart_missing', 'jstart_duplicated', 'jstart_misplaced', 'jstart_self_containment_missing', 'invalid_mode_state', 'incomplete_promoted']

CONTROL_MAP = tuple(({'design_id': i, 'design_code': a, 'selftest_control': b} for i, (a, b) in enumerate(zip(DESIGN_CODES, SELFTEST), 1)))

EXTRA = {'selftest_id': 46, 'selftest_control': 'jstart_lambda_mismatch', 'relationship': 'D3 extra equality control'}

def mapping_test(source=None):
    need(len(CONTROL_MAP) == 45 and [x['design_id'] for x in CONTROL_MAP] == list(range(1, 46)) and (len(set(SELFTEST)) == 45) and (EXTRA['selftest_control'] not in SELFTEST), 'control map')
    if source:
        t = source.decode()
        for n in [*SELFTEST, EXTRA['selftest_control']]:
            need(n in t, f'control absent {n}')
