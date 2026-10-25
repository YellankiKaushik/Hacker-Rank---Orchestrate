"""Evaluator-only root causes. Expected IDs never enter production inference."""
from collections import Counter
import json
from pathlib import Path
from ghosttrace.loader import read_csv
from ghosttrace.models import timestamp,tokens
from ghosttrace.engine import Engine
from ghosttrace.gaps import GapAuditor


def classify(operation,category,extra=False):
    if extra: return '5_EXTRA_RESOURCE'
    if operation=='VERIFY_RECORD_ABSENT' and category in ('USER_PROFILE','ACCOUNT_TOMBSTONE',''):
        return '1_ACCOUNT_ABSENCE'
    if operation=='VERIFY_RECORD_PRESENT': return '2_RETAINED_VERIFICATION'
    if operation=='VERIFY_RECORD_ANONYMIZED': return '3_ANALYTICS_ANONYMIZATION'
    if operation in ('VERIFY_DATA_FLOW_DISABLED','VERIFY_RESTORE_BLOCKED'): return '4_FLOW_RESTORE_VERIFICATION'
    return '8_POLICY_ACTION'


def audit(root,corpus,index,metrics):
    """Join evaluator mismatches to original facts, cutoffs and actual binding paths."""
    root=Path(root); engine=Engine(corpus,index)
    raw=[]
    for row in corpus.manifest:
        path=corpus.root/row['file_path']
        content=index.media.get(row['file_id'],'') if path.suffix in ('.pdf','.png') else path.read_text(encoding='utf-8')
        raw.append((row['file_id'],timestamp(row['captured_at']),content))
    cases={c['case_id']:c for c in read_csv(root/'dataset/sample_deletion_requests.csv')}
    reasons=Counter(); taxonomy=Counter(); details=[]
    for mismatch in metrics['failures']:
        case=cases[mismatch['case_id']]; cut=timestamp(case['audit_at'])
        subject,aliases=engine.identity.resolve(case['email'],cut)
        links=engine.relationships.bind(subject,aliases,cut)
        for key in mismatch['missing_operations']:
            phase,operation,system,resource=key
            observations=index.by_resource.get((system,resource),[])
            admitted=[f for f in observations if f.admissible(cut)]
            category=admitted[0].category if admitted else observations[0].category if observations else ''
            cause=('ENGINE_OMISSION' if admitted and (system,resource) in links else
                   'MISSING_SUBJECT_SELECTOR' if admitted else
                   'ONLY_POST_CUTOFF_OBSERVATIONS' if observations else 'NO_STATE_OBSERVATION')
            if admitted and (system,resource) in links and any(engine.policy.action(f,cut)=='UNKNOWN' for f in admitted):
                cause='MISSING_CONDITIONAL_POLICY_PROOF'
            raw_admitted=sorted(source for source,time,content in raw if time<=cut and resource in content)
            if not observations and raw_admitted: cause='RAW_SOURCE_MENTION_REQUIRES_STATE_INTERPRETATION'
            taxonomy[classify(operation,category)]+=1; reasons[cause]+=1
            details.append({'case_id':case['case_id'],'type':classify(operation,category),'operation':operation,
                'system':system,'resource':resource,'cause':cause,
                'admitted_sources':sorted({f.source for f in admitted}),
                'excluded_sources':sorted({f.source for f in observations if not f.admissible(cut)}),
                'raw_admitted_mentions':raw_admitted,
                'binding':links[(system,resource)].kind if (system,resource) in links else None})
        for system,resource in mismatch['extra_records']:
            fs=[f for f in index.by_resource.get((system,resource),[]) if f.admissible(cut)]
            link=links.get((system,resource))
            cause='EXPLICIT_ADMITTED_RELATIONSHIP_DIFFERS_FROM_REFERENCE' if link else 'EXTRA_WITHOUT_BINDING'
            taxonomy['5_EXTRA_RESOURCE']+=1; reasons[cause]+=1
            details.append({'case_id':case['case_id'],'type':'5_EXTRA_RESOURCE','system':system,'resource':resource,
                'operation':'extra resource','cause':cause,'admitted_sources':sorted({f.source for f in fs}),
                'excluded_sources':[],'binding':link.kind if link else None})
        if mismatch['citation_differences']:
            taxonomy['9_CITATION_ORDERING']+=len(mismatch['citation_differences'])
    # Global explicit identifiers, not nearest-time or filename assumptions.
    activity_links=[]
    for case in cases.values():
        cut=timestamp(case['audit_at']); _,aliases=engine.identity.resolve(case['email'],cut)
        hits=[r['activity_id'] for r in corpus.activities if r['event_type']!='LINK_RESOURCE_IDENTITY'
              and timestamp(r['event_time'])<=cut and aliases & tokens(r['details'])]
        if hits: activity_links.append({'case_id':case['case_id'],'sources':hits})
    result={'case_mismatches':len(metrics['failures']),'taxonomy':dict(taxonomy),'causes':dict(reasons),
            'repairable_engine_omissions':sum(d['cause']=='ENGINE_OMISSION' for d in details),
            'explicit_non_catalog_activity_links':activity_links,'details':details,
            'note':'These reference IDs are evaluator diagnostics only. They do not create resource bindings or output steps.'}
    path=root/'artifacts/mismatch_audit.json'; path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result,indent=2),encoding='utf-8')
    report='# Exact-case mismatch source audit\n\n'
    report+='All public mismatches are audited after inference. Expected resource IDs are evaluator-only. No future-only evidence, numeric suffix, batch position or neighboring event is used as a binding.\n\n'
    report+=f"Mismatching cases: {len(metrics['failures'])}; operation categories: `{dict(taxonomy)}`; source causes: `{dict(reasons)}`.\n\n"
    report+='| Case | Category | Missing/extra operation and resource | Source cause | Admitted sources | Excluded later sources |\n|---|---|---|---|---|---|\n'
    for d in details:
        report+=f"| {d['case_id']} | {d['type']} | {d['operation']}:{d['resource']} | {d['cause']} | {', '.join(d['admitted_sources']) or 'none'} | {', '.join(d['excluded_sources']) or 'none'} |\n"
    report+='''
    The common proof gaps are missing selectors on anonymous readbacks, post-cutoff captures, and unverified attachment exclusivity. Missing conditional-policy proof is deliberately withheld; it is distinguished from a repairable engine omission. Every missing resource is also searched literally in raw admitted text/OCR; a mention alone is not a proven state or sole ownership. Later sources explain benchmark mismatches only and never supply earlier decisions.

All nine requested root-cause classes were considered. Categories 6 (identity) and 7 (time) are represented by the selector/capture causes; category 8 would identify a missing known policy operation. Category 9 is measured separately. The three extra resources have explicit admitted source relationships; deleting them solely to match reference answers would remove supported obligations.
'''
    (root/'code/docs/EXACT_CASE_AUDIT.md').write_text(report,encoding='utf-8')
    return result
