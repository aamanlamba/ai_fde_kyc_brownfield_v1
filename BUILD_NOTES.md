# Build Notes

## Python test command

One command runs everything:

- `python -m pytest -q`

Pytest summary line:

- `29 passed, 1 warning in 0.14s`

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
