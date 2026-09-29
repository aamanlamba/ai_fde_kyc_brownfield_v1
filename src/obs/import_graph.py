from __future__ import annotations

import ast
from pathlib import Path

# The checker necessarily reads and parses source files.
TOOLING_EXEMPT = {'src/obs/import_graph.py', 'obs/import_graph.py'}
COMPOSITION_ROOT = 'orchestrator/wiring.py'
RESTRICTED_LAYER_IMPORTS = ('src.adapters', 'src.api', 'src.orchestrator')

_PROVIDER_PREFIXES = (
    'google',
    'openai',
    'anthropic',
    'azure',
    'langchain',
    'llama_index',
    'vertexai',
)


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

        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                if _is_provider_import(node):
                    violations.append(f'{rel_string}: provider SDK import {node}')
                if isinstance(node, ast.Import):
                    imported_modules = [alias.name for alias in node.names]
                else:
                    imported_modules = [node.module or '']
                for module in imported_modules:
                    if relative.parts and relative.parts[0] in {'decision', 'validation', 'reconciliation'}:
                        if any(module == prefix or module.startswith(prefix + '.') for prefix in RESTRICTED_LAYER_IMPORTS):
                            violations.append(f'{rel_string}: imports {module} from forbidden layer')
                    if (module == 'src.adapters' or module.startswith('src.adapters.')) and rel_string != COMPOSITION_ROOT:
                        violations.append(f'{rel_string}: concrete adapter import {module} outside composition root')
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
                if not (relative.parts and relative.parts[0] == 'adapters'):
                    violations.append(f'{rel_string}: bare open() call outside adapters')
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'open':
                owner = node.func.value
                if isinstance(owner, ast.Name) and owner.id in {'builtins', 'io'}:
                    if not (relative.parts and relative.parts[0] == 'adapters'):
                        violations.append(f'{rel_string}: {owner.id}.open() call outside adapters')
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute):
                    if func.attr in {'read_text', 'read_bytes', 'read'} and not (relative.parts and relative.parts[0] == 'adapters'):
                        violations.append(f'{rel_string}: file read detected outside adapters')

    return sorted(set(violations))
