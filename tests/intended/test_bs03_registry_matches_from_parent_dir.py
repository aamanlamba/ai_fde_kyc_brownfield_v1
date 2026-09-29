from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_TEST = 'tests/test_release_integrity.py::test_expected_case_outputs_are_current_regression_snapshots'


def test_bs03_registry_matches_from_parent_dir(tmp_path):
    copied_repo = tmp_path / 'repo'
    ignored = shutil.ignore_patterns('.git', '.pytest_cache', '__pycache__', '..KYC01_BS02_userrun.txt')
    shutil.copytree(ROOT, copied_repo, ignore=ignored)
    test_path = copied_repo / 'tests' / 'test_release_integrity.py'
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'pytest',
            '-q',
            '--rootdir',
            str(tmp_path),
            f'{test_path}::{SNAPSHOT_TEST.rsplit("::", 1)[1]}',
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert '1 xfailed' in result.stdout
    assert '1 failed' not in result.stdout
