from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]


def test_TST_13_062_test_tree_hygiene():
    bad_literals = []
    bad_skip = []
    xfail_issues = []
    literal_true = 'assert ' + 'True'
    literal_one = 'assert ' + '1'
    skip_marker = '@pytest.mark.' + 'skip'
    skipif_marker = '@pytest.mark.' + 'skipif'
    skip_call = 'skip' + '('
    skipif_call = 'skipif' + '('

    for path in sorted(ROOT.rglob('*.py')):
        text = path.read_text(encoding='utf-8')
        if literal_true in text or literal_one in text:
            bad_literals.append(str(path.relative_to(ROOT)))
        if skip_marker in text or skipif_marker in text or skip_call in text or skipif_call in text:
            bad_skip.append(str(path.relative_to(ROOT)))
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and getattr(dec.func, 'attr', None) in {'xfail', 'skip'}:
                        if getattr(dec.func, 'attr', None) == 'xfail':
                            if not any(
                                isinstance(k, ast.keyword) and k.arg == 'strict' and isinstance(k.value, ast.Constant) and k.value.value is True
                                for k in dec.keywords
                            ):
                                xfail_issues.append(f'{path.relative_to(ROOT)}:: {node.name} missing strict=True')
                            reasons = [
                                kw.value.value for kw in dec.keywords if isinstance(kw, ast.keyword) and kw.arg == 'reason' and isinstance(kw.value, ast.Constant)
                            ]
                            if not reasons or not any('F-07-' in str(r) for r in reasons):
                                xfail_issues.append(f'{path.relative_to(ROOT)}:: {node.name} missing F-07 reason')

    assert not bad_literals, bad_literals
    assert not bad_skip, bad_skip
    assert not xfail_issues, xfail_issues
