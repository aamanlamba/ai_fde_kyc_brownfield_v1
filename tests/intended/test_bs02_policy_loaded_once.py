from pathlib import Path

from src.service import verify_case


def test_bs02_policy_loaded_once(monkeypatch):
    original_read_text = Path.read_text
    reads = []

    def track_read_text(path, *args, **kwargs):
        if path.name in {'policy_v1.json', 'OWNERS.md'}:
            reads.append(path.name)
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'read_text', track_read_text)
    verify_case('CASE-001')
    assert reads == []
