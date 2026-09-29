from src.orchestrator.wiring import get_extraction_provider


def extract_text(document_id: str) -> str:
	return get_extraction_provider().extract(document_id).raw_text

__all__ = ['extract_text']

