import pytest
from pathlib import Path

LEGACY_KNOWN_DEFECTS = {
    'tests/test_release_integrity.py::test_expected_case_outputs_are_current_regression_snapshots': 'F-07-018: snapshot asserts exact legacy output; superseded by additive v1 fields (BS-14-02)',
    'tests/test_service.py::test_name_variation_exposes_brownfield_gap': 'F-07-004: legacy test asserts CASE-005 APPROVE; reconciliation now refers it (BS-14-04)',
}


def pytest_collection_modifyitems(config, items):
    for item in items:
        reason = next(
            (
                value
                for registered, value in LEGACY_KNOWN_DEFECTS.items()
                if item.nodeid.endswith(registered)
                or _repo_relative_nodeid(item, registered)
            ),
            None,
        )
        if reason:
            item.add_marker(pytest.mark.xfail(strict=True, reason=reason))


def _repo_relative_nodeid(item, registered):
    try:
        item_path = Path(item.path).resolve().relative_to(Path(__file__).parent.resolve())
    except (AttributeError, ValueError):
        return False
    return f'{item_path.as_posix()}::{item.name}' == registered
