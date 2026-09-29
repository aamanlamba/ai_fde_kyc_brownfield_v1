from pathlib import Path
import textwrap

from src.obs.import_graph import check_import_boundaries


def test_TST_13_002_import_graph_detects_violation(tmp_path):
    root = tmp_path / 'src'
    (root / 'decision').mkdir(parents=True)
    (root / 'adapters').mkdir()
    for path in (root / '__init__.py', root / 'decision' / '__init__.py', root / 'adapters' / '__init__.py'):
        path.write_text('"""stub"""\n', encoding='utf-8')
    (root / 'decision' / 'bad_module.py').write_text(
        textwrap.dedent(
            '''
            from src.adapters.sample_repository import load_sidecar
            
            def done():
                return load_sidecar('CASE-001-PASSPORT')
            '''
        ),
        encoding='utf-8',
    )
    (root / 'decision' / 'bare_open.py').write_text(
        'def read(path):\n    return open(path, encoding="utf-8").read()\n',
        encoding='utf-8',
    )

    violations = check_import_boundaries(root)
    assert any('bad_module.py' in violation for violation in violations)
    assert any('bare_open.py' in violation and 'open()' in violation for violation in violations)
