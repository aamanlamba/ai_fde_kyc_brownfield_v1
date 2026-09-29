from pathlib import Path
import textwrap

from src.obs.import_graph import check_import_boundaries


def test_TST_13_002_import_graph_detects_violation(tmp_path):
    root = tmp_path / 'src'
    (root / 'decision').mkdir(parents=True)
    (root / 'api').mkdir()
    (root / 'adapters').mkdir()
    for path in (root / '__init__.py', root / 'api' / '__init__.py', root / 'decision' / '__init__.py', root / 'adapters' / '__init__.py'):
        path.write_text('"""stub"""\n', encoding='utf-8')
    (root / 'decision' / 'bad_module.py').write_text(
        textwrap.dedent(
            '''
            from src.api import service
            
            def done():
                return service
            '''
        ),
        encoding='utf-8',
    )

    violations = check_import_boundaries(root)
    assert any('bad_module.py' in v for v in violations)
