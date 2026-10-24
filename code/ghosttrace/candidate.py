"""Explicit prediction policy and structural/source gates, separate from strict audit.

No source is fabricated to fill coverage. Known violations imply INCOMPLETE.
Known required states that cannot be established also predict INCOMPLETE, without
claiming a particular violation. If all observed states comply but coverage is
unproven, predict COMPLETE under an explicitly unverified closed-evidence
assumption. This preserves demonstrated compliant treatments and avoids inventing
PII/restore risk. Neither inference is represented as an evidence-proven verdict.
"""
import json
from collections import Counter
from .models import Audit,timestamp
from .compiler import HEADER,FIELDS,OPERATIONS,sort_key
from .loader import read_csv
from .intent import deletion_intent

POLICY_VERSION='bounded-evidence-v1'


def validate_candidate_audit(audit,sources):
    """Shape/order/citation-time gate only; deliberately not strict semantics.

    An uncertainty-only INCOMPLETE row can have no findings/remediation: no
    supported violation exists to report. This passes JSON/CSV shape, but fails
    the official semantic requirement for a complete plan. The strict validator
    continues rejecting it. The uncertainty report records this discrepancy.
    """
    if audit.status not in ('COMPLETE','INCOMPLETE','NOT_APPLICABLE'):
        raise ValueError('Invalid candidate status')
    if not isinstance(audit.steps,list): raise ValueError('Candidate steps must be an array')
    intent=deletion_intent(audit.case['request_text'])
    if (audit.status=='NOT_APPLICABLE')!= (not intent):
        raise ValueError('Candidate status conflicts with deletion intent')
    if audit.status=='NOT_APPLICABLE' and audit.steps: raise ValueError('Non-deletion candidate has steps')
    seen=set()
    for n,s in enumerate(audit.steps,1):
        if not isinstance(s,dict) or set(s)!=FIELDS or type(s['step_no']) is not int or s['step_no']!=n:
            raise ValueError('Invalid candidate seven-field schema/numbering')
        if any(not isinstance(s[k],str) for k in FIELDS-{'step_no'}): raise ValueError('Non-string candidate field')
        if s['phase'] not in OPERATIONS or s['operation'] not in OPERATIONS[s['phase']]:
            raise ValueError('Invalid candidate phase/operation')
        if s['state']!=OPERATIONS[s['phase']][s['operation']]: raise ValueError('Invalid candidate operation/state')
        if not s['system_id'] or not s['resource_id']: raise ValueError('Empty candidate scope')
        key=(s['phase'],s['operation'],s['system_id'],s['resource_id'])
        if key in seen: raise ValueError('Duplicate candidate step')
        seen.add(key)
        if audit.status=='COMPLETE' and s['phase']!='VERIFICATION': raise ValueError('COMPLETE candidate has a finding/remedy')
        if s['phase']=='FINDING' or audit.status=='COMPLETE':
            if s['evidence_id'] not in sources or sources[s['evidence_id']]>timestamp(audit.case['audit_at']):
                raise ValueError('Invalid/future candidate citation')
        elif s['evidence_id']: raise ValueError('Candidate future work cites evidence')
    if audit.steps!=sorted(audit.steps,key=sort_key): raise ValueError('Noncanonical candidate ordering')


def validate_candidate_file(path,cases,sources):
    rows=read_csv(path,','.join(HEADER))
    if [r['case_id'] for r in rows]!=sorted(c['case_id'] for c in cases):
        raise ValueError('Missing, duplicate, extra or unsorted candidate case')
    by_id={c['case_id']:c for c in cases}
    for row in rows:
        validate_candidate_audit(Audit(by_id[row['case_id']],'',[],row['deletion_status'],json.loads(row['steps_json'])),sources)
    return len(rows)


def validate_emitted_sources(audit,guard,policy,aliases):
    """Reject E/D steps, even when C coverage is permitted for prediction only."""
    cutoff=timestamp(audit.case['audit_at'])
    facts={(f.system,f.resource):f for f in audit.facts}
    cited=0
    for step in audit.steps:
        key=step['system_id'],step['resource_id']
        fact=facts.get(key)
        if fact is None or not fact.admissible(cutoff) or fact.state=='UNKNOWN':
            raise ValueError('Candidate step has no established admissible fact')
        link=audit.bindings.get(key)
        if link is None or not guard.relationships.validates(key,link,aliases,cutoff,audit.bindings):
            raise ValueError('Candidate step has no verified identity binding')
        if not guard.source_supports(fact): raise ValueError('Candidate fact fails original source reread')
        finding,remedy,verify=policy.operations(fact,cutoff)
        if fact.state=='ABSENT' and verify in ('VERIFY_RECORD_REDACTED','VERIFY_RECORD_ANONYMIZED'):
            verify='VERIFY_RECORD_ABSENT'
        permitted={('VERIFICATION',verify)}
        if policy.violation(fact,cutoff): permitted|={('FINDING',finding),('REMEDIATION',remedy)}
        if (step['phase'],step['operation']) not in permitted:
            raise ValueError('Candidate policy operation is unsupported')
        if audit.status=='COMPLETE' and policy.violation(fact,cutoff):
            raise ValueError('COMPLETE candidate contradicts an established violation')
        if step['evidence_id']:
            if step['evidence_id']!=fact.source: raise ValueError('Candidate citation does not prove this fact')
            cited+=1
    return cited


def uncertainty(case,audit,error,guard,policy,aliases):
    assessment=guard.assess_obligations(audit,policy,aliases)
    missing=sorted(set(assessment['blocking_issues']+audit.issues+[str(error)]))
    return {'case_id':case['case_id'],'status':audit.status,'classification':assessment['classification']
            if assessment['classification'] not in ('A','B') else 'C',
            'policy':POLICY_VERSION,'uncertainties':missing,
            'status_inference':('Unestablished required state predicts INCOMPLETE; no specific violation is asserted.'
                if audit.status=='INCOMPLETE' else
                'Observed states comply; COMPLETE assumes no additional untreated relevant copy. This is not proven.'),
            'omitted_obligations':assessment['missing_bound_resources'],
            'unsupported_status_inferences':1,'fabricated_source_references':0,
            'confidence':'LIMITED','emitted_cited_steps':sum(bool(s['evidence_id']) for s in audit.steps)}


def write_uncertainty(path,metrics):
    from pathlib import Path
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    report='# Submission uncertainty report\n\n'
    report+=('This is a prediction artifact, not a certificate of complete deletion. '
             'Strict source review is preserved. No unbound IDs are assigned by position, timing or numeric suffix.\n\n')
    report+=f"Policy: `{POLICY_VERSION}`. Candidate rows: {metrics['resolved']}/{metrics['cases']}; strict decisions: {metrics['strict_resolved']}; uncertain predictions: {len(metrics['uncertain_cases'])}.\n\n"
    report+=('Established violations predict INCOMPLETE. An unknown required state predicts INCOMPLETE without '
             'inventing a violation or remedy. If all observed states comply, unproven coverage predicts COMPLETE '
             'under the limited closed-evidence assumption. Every such status inference is counted as unsupported '
             'by full proof. No workflow status is used. Empty uncertainty-only rows satisfy CSV/JSON shape '
             'but fail strict semantic plan requirements.\n\n')
    for issue in metrics['uncertain_cases']:
        report+=f"## {issue['case_id']} — {issue['status']} (C, LIMITED)\n\n{issue['status_inference']}\n\n"
        report+='\n'.join('- '+v for v in issue['uncertainties'])+'\n\n'
        report+=f"Omitted bound obligations: `{issue['omitted_obligations']}`. Source-backed cited steps emitted: {issue['emitted_cited_steps']}. Next action: obtain admissible binding/readback for these gaps, then rerun strict audit.\n\n"
    path.write_text(report,encoding='utf-8')
