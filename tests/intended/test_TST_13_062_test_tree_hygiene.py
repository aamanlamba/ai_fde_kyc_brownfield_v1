from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]


def test_TST_13_062_test_tree_hygiene():
    bad_literals = []
    bad_skip = []
    xfail_issues = []
    self_comparison_issues = []
    literal_true = 'assert ' + 'True'
    literal_one = 'assert ' + '1'
    skip_marker = '@pytest.mark.' + 'skip'
    skipif_marker = '@pytest.mark.' + 'skipif'
    skip_call = 'skip' + '('
    skipif_call = 'skipif' + '('

    root_hook_tree = ast.parse((ROOT.parent / 'conftest.py').read_text(encoding='utf-8'))
    registry_node = next(
        (
            node.value
            for node in root_hook_tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == 'LEGACY_KNOWN_DEFECTS' for target in node.targets)
        ),
        None,
    )
    try:
        registry = ast.literal_eval(registry_node) if registry_node is not None else {}
    except (ValueError, TypeError):
        registry = {}
    if not registry or any('F-07-' not in reason for reason in registry.values()):
        xfail_issues.append('root conftest.py registry entries must include F-07- reasons')
    hook = next(
        (node for node in root_hook_tree.body if isinstance(node, ast.FunctionDef) and node.name == 'pytest_collection_modifyitems'),
        None,
    )
    strict_hook = hook is not None and any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == 'xfail'
        and any(
            keyword.arg == 'strict'
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value is True
            for keyword in node.keywords
        )
        for node in ast.walk(hook)
    )
    if not strict_hook:
        xfail_issues.append('root conftest.py hook must use pytest.mark.xfail(strict=True)')

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
                if node.name.startswith('test_'):
                    constructed = {
                        target.id
                        for statement in node.body
                        if isinstance(statement, ast.Assign)
                        and isinstance(statement.value, ast.Call)
                        and isinstance(statement.value.func, ast.Name)
                        and statement.value.func.id[:1].isupper()
                        for target in statement.targets
                        if isinstance(target, ast.Name)
                    }
                    assertions = [statement.test for statement in ast.walk(node) if isinstance(statement, ast.Assert)]
                    if constructed and assertions and all(
                        isinstance(assertion, ast.Compare)
                        and any(
                            isinstance(child, ast.Attribute)
                            and isinstance(child.value, ast.Name)
                            and child.value.id in constructed
                            for child in ast.walk(assertion)
                        )
                        and all(isinstance(value, ast.Constant) for value in assertion.comparators)
                        for assertion in assertions
                    ):
                        self_comparison_issues.append(f'{path.relative_to(ROOT)}::{node.name}')

    assert not bad_literals, bad_literals
    assert not bad_skip, bad_skip
    assert not xfail_issues, xfail_issues
    assert not self_comparison_issues, self_comparison_issues
