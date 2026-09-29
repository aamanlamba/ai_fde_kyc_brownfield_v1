from __future__ import annotations

import re


def normalise(raw: str | None) -> str | None:
    if raw is None:
        return None
    cleaned = raw.strip().lower()
    cleaned = cleaned.replace('-', '_')
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned or None
