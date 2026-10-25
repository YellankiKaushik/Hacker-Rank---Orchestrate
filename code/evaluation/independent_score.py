"""Standalone reference scorer; no production engine/validator imports."""
import csv
import json
from collections import Counter

FIELDS=('step_no','phase','system_id','resource_id','operation','state','evidence_id')
def read(path):
    with open(path,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def score(predictions,references):
    by_id={r['case_id']:r for r in predictions};counts=Counter();failures=[]
    sig=lambda s:(s['phase'],s['operation'],s['system_id'],s['resource_id'])
    resources=lambda ss:{(s['system_id'],s['resource_id']) for s in ss}
    canonical=lambda s:tuple(s[k] for k in FIELDS)
    for ref in references:
        row=by_id.get(ref['case_id'],{});ss=json.loads(row.get('steps_json','[]'));gs=json.loads(ref['steps_json'])
        same=row.get('deletion_status')==ref['deletion_status']
        counts['cases']+=1;counts['status_correct']+=same;counts['exact_cases']+=same and ss==gs
        counts['sequence_correct']+=list(map(sig,ss))==list(map(sig,gs))
        counts['field_total']+=7*max(len(ss),len(gs))
        for n in range(min(len(ss),len(gs))):counts['field_matches']+=sum(ss[n][k]==gs[n][k] for k in FIELDS)
        counts['step_matches']+=sum((Counter(map(canonical,ss))&Counter(map(canonical,gs))).values())
        counts['predicted_steps']+=len(ss);counts['reference_steps']+=len(gs)
        counts['missing_resources']+=len(resources(gs)-resources(ss));counts['extra_resources']+=len(resources(ss)-resources(gs))
        counts['missing_operations']+=len(set(map(sig,gs))-set(map(sig,ss)));counts['extra_operations']+=len(set(map(sig,ss))-set(map(sig,gs)))
        gold={sig(s):s for s in gs}
        for s in ss:
            if s['evidence_id']:
                counts['cited_steps']+=1;counts['citation_agreement']+=sig(s) in gold and s['evidence_id']==gold[sig(s)]['evidence_id']
        if not same or ss!=gs:failures.append(ref['case_id'])
    return {'counts':dict(counts),'mismatching_cases':failures}
