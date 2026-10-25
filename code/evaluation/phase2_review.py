"""Bounded evaluator-only review of known proof gaps. Never used for inference."""
import json
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ghosttrace.loader import Corpus,read_csv
from ghosttrace.adapters import EvidenceIndex
from ghosttrace.engine import Engine
from ghosttrace.reviewer import GhostGuard
from ghosttrace.models import timestamp,tokens
from ghosttrace.gaps import GapAuditor
from ghosttrace.policy import attachment_ownership

ROOT=Path(__file__).resolve().parents[2]
def review(root=ROOT):
    root=Path(root);c=Corpus(root/'dataset');i=EvidenceIndex(c,root/'tmp/ocr');e=Engine(c,i);g=GhostGuard(c,i);gap=GapAuditor(c,i)
    metrics=json.loads((root/'artifacts/candidate_run_metrics.json').read_text());uncertain={v['case_id']:v for v in metrics['uncertain_cases']}
    records=[];plans=[]
    for case in read_csv(root/'dataset/deletion_requests.csv'):
        cid=case['case_id']
        if cid not in uncertain:continue
        a=e.investigate(case,permit_partial=True);cutoff=timestamp(case['audit_at']);aliases=e.identity.aliases(cutoff)[a.subject]
        assessment=g.assess_obligations(a,e.policy,aliases);diagnostic=gap.inspect(case)
        # One actionable hypothesis: an explicit admitted structured selector or
        # upstream resource edge was present but omitted by the relation index.
        # Only already-observed records in linked sources are examined. No
        # anonymous source positions, suffixes, or future rows are assigned.
        sources=set(diagnostic['linked_sources'])
        possible=[f for f in i.facts if f.admissible(cutoff) and f.source in sources
                  and aliases & tokens(f.data) and (f.system,f.resource) not in a.bindings]
        record={'case_id':cid,'candidate_status':a.status,'proof_classification':assessment['classification'],
                'known_sources':sorted(sources),'known_bound_resources':[list(k) for k in sorted(a.bindings)],
                'exact_missing_obligations':assessment['missing_bound_resources'],'proof_gap':uncertain[cid]['uncertainties'],
                'root_diagnostic':diagnostic['reason'],'anonymous_root_count':len(diagnostic['orphan_root_candidates']),
                'retention_only':bool(a.facts) and all(e.policy.action(f,cutoff)=='RETAIN' for f in a.facts),
                'omitted_explicit_selector_hypothesis':[{'source':f.source,'system':f.system,'resource':f.resource} for f in possible],
                'recovered':False,'decision':'Keep explicit best-effort assumption; strict proof remains unresolved. No invented relation.'}
        records.append(record)
        if cid in ('case_479','case_503','case_55'):
            missing=[]
            for key in assessment['missing_bound_resources']:
                observations=[f for f in i.by_resource[tuple(key)] if f.admissible(cutoff)]
                missing.append({'system':key[0],'resource':key[1],'sources':sorted({f.source for f in observations}),
                                'observed_states':sorted({f.state for f in observations}),
                                'ownership':sorted({attachment_ownership(f.data) for f in observations if f.category=='SUPPORT_ATTACHMENT'}),
                                'permission_fields':[sorted(k for k in f.data if k in ('restore_allowed','restore_blocked','eligible','decision')) for f in observations if f.category=='BACKUP_ARCHIVE']})
            plans.append({'case_id':cid,'cutoff':case['audit_at'],'official_rule':'rule_14 BACKUP_ARCHIVE / retain; restore access requires actual permission proof' if cid=='case_55' else 'rule_06 SUPPORT_ATTACHMENT / DELETE only when belongs solely to subject; rule_12 retains security record',
                          'subject_resource_relation':'Dated exact identifier or supplied catalog identity link; association is established, ownership/permission is not',
                          'admissible_observations':missing,'known_retained_facts':[{'system':f.system,'resource':f.resource,'source':f.source,'state':f.state} for f in a.facts],
                          'actual_violation':'NOT ESTABLISHED for the missing conditional obligation','authorized_remediation':'NOT ESTABLISHED; do not delete attachment or assert restore block without source proof',
                          'future_verification':'Retained known security record must remain; missing attachment/restore checks depend on establishing the condition',
                          'lawful_complete_plan_possible':False,'proof_unavailable':True,'official_plan_gate':'FAIL'})
    report='# Phase 2 bounded evidence review\n\nOne explicit-selector/upstream-link hypothesis was checked per uncertain case using admitted known-source records. It recovered no new relation; no repeated whole-corpus guessing or future inference was used. Shared parser/index limitations remain.\n\n'
    report+='## Three plan-contract decision records\n\n'
    for p in plans:
        report+=f"### {p['case_id']} — FAIL\n\n"+'\n'.join('- '+k+': '+json.dumps(v,ensure_ascii=False) for k,v in p.items() if k!='case_id')+'\n\n'
    report+='## Every uncertain COMPLETE decision\n\n| Case | Sources | Known bound resources | Missing obligations / exact gap | Retention only / anonymous roots | Decision |\n|---|---|---|---|---|---|\n'
    for r in records:
        if r['candidate_status']!='COMPLETE':continue
        report+=f"| {r['case_id']} | {', '.join(r['known_sources'])} | {r['known_bound_resources']} | {'; '.join(r['proof_gap'])} | {r['retention_only']} / {r['anonymous_root_count']} | Unresolved; no new admissible selector; candidate assumption preserved |\n"
    result={'uncertain_cases':len(records),'uncertain_statuses':dict(Counter(r['candidate_status'] for r in records)),
            'recovered_cases':0,'omitted_selector_hypotheses':sum(len(r['omitted_explicit_selector_hypothesis']) for r in records),
            'decisions':records,'plan_decisions':plans}
    (root/'artifacts/phase2-evidence-review.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (root/'code/docs/PHASE2_EVIDENCE_REVIEW.md').write_text(report,encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('decisions','plan_decisions')},indent=2))
    return result
if __name__=='__main__':review()
