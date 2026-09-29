from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from src.ports import PolicySource


class PolicyLoadError(ValueError):
    pass


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = ROOT / 'config' / 'policy_v1.json'
DEFAULT_OWNERS_PATH = ROOT / 'OWNERS.md'


def _read_owner_roles(path: Path | str = DEFAULT_OWNERS_PATH) -> set[str]:
    candidate = Path(path)
    if not candidate.exists():
        raise PolicyLoadError(f'missing ownership file: {candidate}')
    roles: set[str] = set()
    for line in candidate.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped or '=' not in stripped:
            continue
        role = stripped.split('=', 1)[1].strip()
        if role:
            roles.add(role)
    if not roles:
        raise PolicyLoadError('no roles found in OWNERS.md')
    return roles


class FilePolicySource(PolicySource):
    def __init__(self, path: str | Path = DEFAULT_POLICY_PATH, owners_path: str | Path = DEFAULT_OWNERS_PATH):
        self.path = Path(path)
        self.owners_path = Path(owners_path)
        self._policy = self.load_policy()

    def load_policy(self) -> dict[str, Any]:
        if not self.path.exists():
            raise PolicyLoadError(f'missing policy file: {self.path}')
        try:
            raw = json.loads(self.path.read_text(encoding='utf-8'))
        except Exception as exc:  # pragma: no cover - exercised through tests with invalid JSON / path
            raise PolicyLoadError(f'policy file is not valid JSON: {self.path}') from exc

        if not isinstance(raw, dict):
            raise PolicyLoadError('policy must be a JSON object')

        required_keys = (
            'policy_version',
            'approved_by',
            'approved_on',
            'completeness_threshold',
            'supported_types',
            'number_patterns',
            'mandatory_fields',
        )
        missing = [key for key in required_keys if key not in raw]
        if missing:
            raise PolicyLoadError(f'missing required policy keys: {missing}')

        if not isinstance(raw['policy_version'], str) or not re.fullmatch(r'\d+\.\d+\.\d+', raw['policy_version']):
            raise PolicyLoadError('policy_version must be semver like 1.0.0')
        if not isinstance(raw['approved_by'], str) or not raw['approved_by'].strip():
            raise PolicyLoadError('approved_by must be a non-empty string')
        if raw['approved_by'] not in _read_owner_roles(self.owners_path):
            raise PolicyLoadError(f'approved_by is not in OWNERS.md: {raw["approved_by"]}')
        if not isinstance(raw['approved_on'], str):
            raise PolicyLoadError('approved_on must be an ISO date string')
        try:
            date.fromisoformat(raw['approved_on'])
        except ValueError as exc:
            raise PolicyLoadError('approved_on must be a valid ISO date') from exc
        if not isinstance(raw['completeness_threshold'], (int, float)):
            raise PolicyLoadError('completeness_threshold must be numeric')
        if not isinstance(raw['supported_types'], list) or not raw['supported_types']:
            raise PolicyLoadError('supported_types must be a non-empty list')
        if not isinstance(raw['number_patterns'], dict) or not raw['number_patterns']:
            raise PolicyLoadError('number_patterns must be a non-empty object')
        if not isinstance(raw['mandatory_fields'], list) or not raw['mandatory_fields']:
            raise PolicyLoadError('mandatory_fields must be a non-empty list')

        return raw

    def get_policy(self) -> dict[str, Any]:
        return self._policy
