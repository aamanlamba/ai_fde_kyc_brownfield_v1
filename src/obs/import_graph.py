from __future__ import annotations

import ast
from pathlib import Path

_PROVIDER_PREFIXES = (
    'google',
    'openai',
    'anthropic',
    'azure',
    'langchain',
    'llama_index',
    'vertexai',
)


def _module_from_file(path: Path, root: Path) -> str:
    return '.'.join(path.relative_to(root).with_suffix('').parts)


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
            return func.attr in {'read_text', 'read_bytes', 'read', 'open'}
        return False
    return False


def check_import_boundaries(src_root: str | Path) -> list[str]:
    root = Path(src_root)
    violations: list[str] = []
    paths = sorted(list(root.rglob('*.py')))
    for path in paths:
        if '__pycache__' in path.parts:
            continue
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == 'adapters':
            continue
        try:
            module_obj = __import__('pathlib')
            path_obj = getattr(module_obj, 'Path')(path)
            reader = getattr(path_obj, 'read_text')
            source = reader(encoding='utf-8')
        except Exception:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        if len(relative.parts) >= 2 and relative.parts[0] == 'decision':
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    mod = node.module or ''
                    if mod and mod.startswith('src.api'):
                        violations.append(f'{relative}: imports {mod} from decision layer')
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith('src.api'):
                            violations.append(f'{relative}: imports {alias.name} from decision layer')

        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                if _is_provider_import(node):
                    violations.append(f'{relative}: provider SDK import {node}')
            if not relative.parts or relative.parts[0] != 'adapters':
                if _is_file_read(node):
                    violations.append(f'{relative}: file read detected outside adapters')

    return sorted(set(violations))
