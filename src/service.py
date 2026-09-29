from src.models import DocumentResult, CaseResult
from src.orchestrator.wiring import get_clock, get_extraction_provider, get_policy, get_tamper_provider
from src.repository import load_application
from src.validation.rules import completeness, validate
from src.validation.doctype import normalise
from src.ports import ExtractionUnavailable

RANK={'APPROVE':0,'REVIEW':1,'REJECT':2}


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
            policy_version=get_policy().get('policy_version'),
        )

    text = extraction.raw_text
    parsed_fields = {k: v.value for k, v in extraction.fields.items() if v.value is not None}
    document_type_field = extraction.fields.get('document_type')
    document_type = document_type_field.raw if document_type_field is not None else None
    policy = get_policy()
    supported = set(policy.get('supported_types', []))
    normalised = normalise(document_type)
    signals = get_tamper_provider().signals(extraction)
    decision, reasons, rule_warnings = validate(
        parsed_fields,
        policy,
        get_clock().today(),
        signals,
        text,
    )
    unsupported = normalised is None or normalised not in supported
    if unsupported and 'UNSUPPORTED_DOCUMENT_TYPE' not in reasons:
        reasons.append('UNSUPPORTED_DOCUMENT_TYPE')
    if unsupported and decision == 'REVIEW' and 'MANUAL_REVIEW_REQUIRED' not in reasons:
        reasons.append('MANUAL_REVIEW_REQUIRED')
    warnings = extraction.warnings + rule_warnings
    if any(warning.startswith('UNPARSED_LINE:') for warning in extraction.warnings):
        if 'UNREAD_EVIDENCE' not in reasons:
            reasons.append('UNREAD_EVIDENCE')
        if decision != 'REJECT':
            decision = 'REVIEW'
    if decision in {'REVIEW', 'REJECT'}:
        reasons = [reason for reason in reasons if reason != 'BASELINE_RULES_PASSED']
    return DocumentResult(
        document_id=document_id,
        document_type=document_type,
        decision=decision,
        reason_codes=reasons,
        parsed_fields=parsed_fields,
            completeness=completeness(parsed_fields, policy),
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
        policy_version=get_policy().get('policy_version'),
    )
