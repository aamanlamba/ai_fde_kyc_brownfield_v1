# Build Notes

## Python test command

One command runs everything:

- `python -m pytest -q`

Pytest summary line:

- `42 passed, 1 xfailed, 1 warning in 0.21s`

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

## SPEC coverage

| SPEC ID | Files / functions | Test names |
| --- | --- | --- |
| SPEC-12-001 | `src/ports.py`, `src/adapters/*.py`, `src/repository.py`, `src/ocr.py`, `src/obs/import_graph.py` | `test_TST_13_001_import_graph_boundaries`, `test_TST_13_002_import_graph_detects_violation` |
| SPEC-12-008 | `src/adapters/file_policy_source.py`, `src/rules.py`, `config/policy_v1.json` | `test_TST_13_033_invalid_policy_rejected`, `test_bs01_policy_values_drive_rules` |
| SPEC-12-018 | `OWNERS.md`, `src/adapters/file_policy_source.py` | `test_TST_13_064_unlisted_approver_rejected` |
| SPEC-12-017 | `tests/intended/`, `tests/legacy_known_defects/README.md` | `test_TST_13_062_test_tree_hygiene` |
| Clock port | `src/adapters/clocks.py`, `src/rules.py` | `test_bs01_fixed_clock_expiry_boundary` |

## SIMULATED items

Expected: none.

## Known limitations

- `MANIFEST.sha256` is now stale for the modified files in this slice.
- `SystemClock` makes expiry outcomes date-dependent; sample outcomes remain unchanged until 2030-07-04, the earliest non-expired expiry in the sample dataset.
- The repository intentionally keeps the baseline API contracts and output snapshots unchanged while adding the module skeleton and policy loader.
