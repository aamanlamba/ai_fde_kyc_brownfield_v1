from src.adapters.file_policy_source import FilePolicySource
from src.models import DocumentResult, CaseResult
from src.orchestrator.wiring import get_extraction_provider
from src.parser import parse_legacy_ocr
from src.repository import load_application
from src.rules import evaluate, completeness
from src.validation.doctype import normalise
from src.ports import ExtractionUnavailable

RANK={'APPROVE':0,'REVIEW':1,'REJECT':2}
_POLICY = FilePolicySource()


def verify_document(document_id: str) -> DocumentResult:
    provider = get_extraction_provider()
    try:
        extraction = provider.extract(document_id)
    except ExtractionUnavailable:
        return DocumentResult(
            document_id=document_id,
            document_type=None,
            decision='REVIEW',
            reason_codes=['EXTRACTION_UNAVAILABLE'],
            parsed_fields={},
            completeness=0.0,
            warnings=[],
            missing_fields=[],
            policy_version=_POLICY.get_policy().get('policy_version'),
        )

    text = extraction.raw_text
    legacy_fields, parse_warnings = parse_legacy_ocr(text)
    parsed_fields = {k: v.value for k, v in extraction.fields.items() if v.value is not None}
    document_type = legacy_fields.get('document_type')
    policy = _POLICY.get_policy()
    supported = set(policy.get('supported_types', []))
    normalised = normalise(document_type)
    if (document_type is None) or (normalised is None) or (normalised not in supported):
        return DocumentResult(
            document_id=document_id,
            document_type=document_type,
            decision='REVIEW',
            reason_codes=['UNSUPPORTED_DOCUMENT_TYPE', 'MANUAL_REVIEW_REQUIRED'],
            parsed_fields=parsed_fields,
            completeness=completeness(parsed_fields),
            warnings=parse_warnings,
            missing_fields=extraction.missing_fields,
            policy_version=policy.get('policy_version'),
        )

    decision, reasons, rule_warnings = evaluate(parsed_fields, text)
    warnings = list(dict.fromkeys(parse_warnings + rule_warnings + extraction.warnings))
    if any('UNPARSED_LINE:' in warning for warning in warnings):
        reasons = ['UNREAD_EVIDENCE'] + [r for r in reasons if r != 'UNREAD_EVIDENCE']
        decision = 'REVIEW'
    return DocumentResult(
        document_id=document_id,
        document_type=document_type,
        decision=decision,
        reason_codes=reasons,
        parsed_fields=parsed_fields,
        completeness=completeness(parsed_fields),
        warnings=warnings,
        missing_fields=extraction.missing_fields,
        policy_version=policy.get('policy_version'),
    )


def verify_case(case_id: str) -> CaseResult:
    app = load_application(case_id)
    docs = [verify_document(x) for x in app['document_ids']]
    worst = max(docs, key=lambda x: RANK[x.decision]).decision
    reason_codes = sorted({r for d in docs for r in d.reason_codes})
    return CaseResult(
        case_id=case_id,
        decision=worst,
        reason_codes=reason_codes,
        documents=docs,
        limitation_notice='Repo 1.0 aggregates document decisions only; it does not perform robust cross-document identity resolution.',
        policy_version=_POLICY.get_policy().get('policy_version'),
    )
