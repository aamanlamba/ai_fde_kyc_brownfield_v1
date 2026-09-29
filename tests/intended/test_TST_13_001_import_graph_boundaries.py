from pathlib import Path

from src.obs.import_graph import check_import_boundaries


ROOT = Path(__file__).resolve().parents[1]


def test_TST_13_001_import_graph_boundaries():
    assert not check_import_boundaries(ROOT.parent / 'src')
