from __future__ import annotations

import ast
from pathlib import Path

TOOLING_EXEMPT = {'src/obs/import_graph.py', 'obs/import_graph.py'}

_PROVIDER_PREFIXES = (
    'google',
    'openai',
    'anthropic',
    'azure',
    'langchain',
    'llama_index',
    'vertexai',
)


def _normalise_import(module: str | None) -> str:
    return (module or '').split('.')[0]


def _is_provider_import(node: ast.Import | ast.ImportFrom) -> bool:
    if isinstance(node, ast.Import):
        names = [alias.name for alias in node.names]
        return any(name.split('.')[0] in _PROVIDER_PREFIXES for name in names)
    if node.module:
        return node.module.split('.')[0] in _PROVIDER_PREFIXES
    return False


def _is_file_read(node: ast.AST) -> bool:
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute):
            return func.attr in {'read_text', 'read_bytes', 'read'}
        if isinstance(func, ast.Name):
            return func.id == 'open'
    return False


def check_import_boundaries(src_root: str | Path) -> list[str]:
    root = Path(src_root)
    violations: list[str] = []
    paths = sorted(list(root.rglob('*.py')))
    for path in paths:
        if '__pycache__' in path.parts:
            continue
        relative = path.relative_to(root)
        rel_string = str(relative).replace('\\', '/')
        if rel_string in TOOLING_EXEMPT:
            continue
        if relative.parts and relative.parts[0] == 'adapters':
            continue
        try:
            source = path.read_text(encoding='utf-8')
        except Exception:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        if relative.parts and relative.parts[0] in {'decision', 'validation', 'reconciliation'}:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith('src.adapters'):
                            violations.append(f'{rel_string}: imports {alias.name} from forbidden layer')
                        if alias.name.startswith('src.') and not alias.name.startswith('src.adapters'):
                            violations.append(f'{rel_string}: imports {alias.name} from forbidden layer')
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ''
                    if mod.startswith('src.adapters'):
                        violations.append(f'{rel_string}: imports {mod} from forbidden layer')
                    if mod.startswith('src.') and not mod.startswith('src.adapters'):
                        violations.append(f'{rel_string}: imports {mod} from forbidden layer')

        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                if _is_provider_import(node):
                    violations.append(f'{rel_string}: provider SDK import {node}')
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
                if not (relative.parts and relative.parts[0] == 'adapters'):
                    violations.append(f'{rel_string}: bare open() call outside adapters')
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute):
                    if func.attr in {'read_text', 'read_bytes', 'read'} and not (relative.parts and relative.parts[0] == 'adapters'):
                        violations.append(f'{rel_string}: file read detected outside adapters')

    return sorted(set(violations))
