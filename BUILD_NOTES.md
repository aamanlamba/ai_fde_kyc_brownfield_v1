# Build Notes

## Python test command

One command runs everything:

- `python -m pytest -q`

Pytest summary line:

- `56 passed, 2 xfailed, 1 warning in 1.12s`

## BS-14-02

| SPEC / carry-over | Files | Tests |
| --- | --- | --- |
| SPEC-12-003 extraction port and tolerant sidecar adapter | `src/ports.py`, `src/adapters/sidecar_text.py`, `src/adapters/mock_extraction.py`, `src/orchestrator/wiring.py`, `src/service.py` | `test_TST_13_006_sidecar_extraction_matches_baseline`, `test_TST_13_007_label_variation_tolerated`, `test_TST_13_008_missing_field_listed_not_inferred`, `test_TST_13_009_unparsed_line_reaches_rules`, `test_TST_13_010_extraction_unavailable_reviews_offline` |
| SPEC-12-004 document type normalization and allow-list | `src/validation/doctype.py`, `src/service.py`, `src/rules.py`, `config/policy_v1.json` | `test_TST_13_011_doctype_normalisation_matches_ground_truth`, `test_TST_13_012_unsupported_type_reviews`, `test_TST_13_032_allow_list_from_policy`, `test_bs02_unsupported_type_keeps_tamper` |
| SPEC-12-008 policy version, aliases, and cached policy | `src/models.py`, `src/adapters/file_policy_source.py`, `src/orchestrator/wiring.py`, `config/policy_v1.json` | `test_TST_13_031_policy_version_on_every_result`, `test_bs02_policy_loaded_once`, `test_bs02_alias_labels_end_to_end` |
| CF-1/CF-2/CF-3/CF-4 and response consistency | `src/obs/import_graph.py`, `src/orchestrator/wiring.py`, `src/rules.py`, `src/service.py`, `tests/intended/` | `test_TST_13_001_import_graph_boundaries`, `test_TST_13_002_import_graph_detects_violation`, `test_TST_13_033_invalid_policy_rejected`, `test_TST_13_062_test_tree_hygiene`, `test_bs02_no_passed_code_on_review` |
| D-66 legacy snapshot projection | Root `conftest.py`; `scripts/sanity_check.py` legacy projection comparison | `test_expected_case_outputs_are_current_regression_snapshots` remains the registered strict xfail; `test_bs02_legacy_projection_unchanged` verifies all six cases |

D-66 changes: root `conftest.py` registers the exact-output legacy snapshot defect with `strict=True`; `scripts/sanity_check.py` recursively compares the keys present in each expected baseline output, including nested document entries.

SIMULATED items: none.

Pytest summary line: `42 passed, 1 xfailed, 1 warning in 0.21s`.

## BS-14-03

| SPEC / carry-over | Files | Tests |
| --- | --- | --- |
| SPEC-12-005 pure mandatory-field, number-format, expiry, and outcome rules | `src/validation/rules.py`, `src/rules.py`, `src/service.py` | `test_TST_13_013_expired_with_fixed_clock`, `test_TST_13_014_expiry_boundary`, `test_TST_13_015_decision_date_from_clock`, `test_TST_13_016_invalid_expiry_reviews`, `test_TST_13_017_missing_name_reviews`, `test_TST_13_018_malformed_number_reviews` |
| Tamper signal port and adapter | `src/ports.py`, `src/adapters/tamper_marker.py`, `src/orchestrator/wiring.py`, `src/service.py` | `test_bs03_tamper_via_provider` |
| Validation purity and clock injection | `src/validation/rules.py`, `src/orchestrator/wiring.py`, `src/rules.py` | `test_bs03_validation_layer_is_pure`, `test_TST_13_015_decision_date_from_clock` |
| CF-5/CF-6/CF-7 | Root `conftest.py`, `src/obs/import_graph.py`, `tests/intended/test_TST_13_002_import_graph_detects_violation.py`, `tests/intended/test_bs01_policy_values_drive_rules.py` | `test_bs03_registry_matches_from_parent_dir`, `test_TST_13_002_import_graph_detects_violation` |

SIMULATED: `MarkerSignal` inspects the synthetic `ALTERED_TEXT_REGION_DETECTED` sidecar marker; it does not perform image forensics.

Pytest summary line: `50 passed, 1 xfailed, 1 warning in 0.82s`.

## BS-14-04

| SPEC / carry-over | Files | Tests |
| --- | --- | --- |
| SPEC-12-006 deterministic identity reconciliation | `src/reconciliation/identity.py`, `src/service.py`, `src/orchestrator/wiring.py`, `src/models.py` | `test_TST_13_019_case005_name_variation_reviews`, `test_TST_13_020_ocr_confusion_tolerated`, `test_TST_13_021_clean_cases_no_identity_reason`, `test_TST_13_022_harmless_variations_tolerated`, `test_TST_13_023_dob_mismatch_reviews`, `test_TST_13_024_unrelated_name_mismatch` |
| Policy-configured name tolerances | `config/policy_v1.json`, `src/adapters/file_policy_source.py` | `test_TST_13_033_invalid_policy_rejected`, `test_TST_13_022_harmless_variations_tolerated` |
| D-73 intended-change registry and projection | `config/intended_changes.json`, root `conftest.py`, `scripts/sanity_check.py`, `tests/intended/test_bs02_legacy_projection_unchanged.py` | `test_expected_case_outputs_are_current_regression_snapshots`, `test_name_variation_exposes_brownfield_gap`, `test_TST_13_021_clean_cases_no_identity_reason` |
| CF-10 aliases follow runtime policy source | `src/adapters/sidecar_text.py`, `src/orchestrator/wiring.py` | `test_bs04_aliases_follow_policy_source` |

D-73: `config/intended_changes.json` records only CASE-005 `decision` and `reason_codes` as intended case-level changes. The root xfail registry tracks the protected CASE-005 legacy assertion; the scoped `scripts/sanity_check.py` projection excludes only the registered keys for that case. Document-level projections remain compared.

SIMULATED: `MarkerSignal` (unchanged); it recognizes only the synthetic sidecar marker and is not image forensics.

Pytest summary line: `56 passed, 2 xfailed, 1 warning in 1.12s`.

## SPEC coverage

| SPEC ID | Files / functions | Test names |
| --- | --- | --- |
| SPEC-12-001 | `src/ports.py`, `src/adapters/*.py`, `src/repository.py`, `src/ocr.py`, `src/obs/import_graph.py` | `test_TST_13_001_import_graph_boundaries`, `test_TST_13_002_import_graph_detects_violation` |
| SPEC-12-008 | `src/adapters/file_policy_source.py`, `src/rules.py`, `config/policy_v1.json` | `test_TST_13_033_invalid_policy_rejected`, `test_bs01_policy_values_drive_rules` |
| SPEC-12-018 | `OWNERS.md`, `src/adapters/file_policy_source.py` | `test_TST_13_064_unlisted_approver_rejected` |
| SPEC-12-017 | `tests/intended/`, `tests/legacy_known_defects/README.md` | `test_TST_13_062_test_tree_hygiene` |
| Clock port | `src/adapters/clocks.py`, `src/rules.py` | `test_TST_13_014_expiry_boundary` |

## SIMULATED items

Expected: none.

## Known limitations

- `MarkerSignal` is SIMULATED and only recognizes the synthetic sidecar marker; image forensics is not implemented.
- OCR remains deterministic and sidecar-backed; this slice does not add an OCR provider or network dependency.
- Runtime expiry decisions use the injected system clock; tests use `FixedClock` for deterministic boundaries.
- `MANIFEST.sha256` remains unchanged and may not reflect files added by these development slices.
