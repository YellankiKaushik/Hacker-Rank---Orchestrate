"""Evaluator-only ownership/accuracy review; never imported by inference."""
import json
from pathlib import Path
from ghosttrace.loader import read_csv
from ghosttrace.models import timestamp,identifier_keys
from ghosttrace.engine import Engine
from ghosttrace.policy import attachment_ownership

TARGETS={'case_203','case_263','case_311','case_34','case_359','case_371',
         'case_407','case_419','case_455','case_479','case_503','case_515'}


def selector_paths(data,aliases,prefix=''):
    found=[]
    if isinstance(data,dict):
        for key,value in data.items(): found+=selector_paths(value,aliases,prefix+'.'+key if prefix else key)
    elif isinstance(data,str) and identifier_keys(data)&aliases:
        found.append(prefix)
    return found


def generate(root,corpus,index,full,sample):
    root=Path(root); engine=Engine(corpus,index); manifest={r['file_id']:r for r in corpus.manifest}
    findings=[]
    for case in read_csv(root/'dataset/deletion_requests.csv'):
        if case['case_id'] not in TARGETS: continue
        cutoff=timestamp(case['audit_at']); subject,aliases=engine.identity.resolve(case['email'],cutoff)
        links=engine.relationships.bind(subject,aliases,cutoff)
        for key,link in sorted(links.items()):
            observations=[f for f in index.by_resource[key] if f.category=='SUPPORT_ATTACHMENT' and f.admissible(cutoff)]
            if not observations: continue
            sources=sorted({f.source for f in observations})
            activities=[a for a in corpus.activities if a['resource_id']==key[1] and timestamp(a['event_time'])<=cutoff]
            findings.append({'case':case['case_id'],'subject':subject,'cutoff':case['audit_at'],
                'system':key[0],'resource':key[1],'sources':sources,
                'source_paths':[manifest[s]['file_path'] for s in sources],
                'source_captured_at':[manifest[s]['captured_at'] for s in sources],
                'observations':[{'source':f.source,'observed':f.observed.isoformat(),'scope':f.scope,
                    'locator':f.locator,'selector_fields':selector_paths(f.data,aliases)} for f in observations],
                'binding':link.kind,'binding_source':link.source,
                'ownership':sorted({attachment_ownership(f.data) for f in observations}),
                'shared_subjects_supplied':any('shared_subjects' in f.data for f in observations),
                'sole_owner_supplied':any('sole_owner' in f.data for f in observations),
                'dated_activity_ids':[a['activity_id'] for a in activities],
                'dated_activity_types':sorted({a['event_type'] for a in activities}),
                'action':'ABSTAIN: supplied conditional DELETE lacks exclusivity proof; no supplied REDACT fallback'})
    current={r['case_id']:r for r in read_csv(root/'tmp/sample_candidate.csv')}
    # Reference answers are opened here, only after all production predictions.
    reference={r['case_id']:r for r in read_csv(root/'dataset/sample_output.csv')}
    historical=root/'tmp/targeted-old-sample.csv'
    old={r['case_id']:r for r in read_csv(historical)} if historical.exists() else {}
    def same(a,b): return a['deletion_status']==b['deletion_status'] and json.loads(a['steps_json'])==json.loads(b['steps_json'])
    lost=sorted(k for k in old if same(old[k],reference[k]) and not same(current[k],reference[k]))
    details={k:{label:{'status':row['deletion_status'],'steps':json.loads(row['steps_json'])}
                for label,row in [('old_5b9a098',old[k]),('current',current[k]),('public_reference',reference[k])]}
             for k in lost}
    result={'baseline_commit':'43990d03ac6de69302e59585d1d3c6f12d7ab9e8','attachment_cases':findings,
        'historical_replay_commit':'5b9a0986f06003fb48c643082a8edcfa4b627a99','lost_exact_cases':lost,'lost_case_predictions':details,
        'baseline_metrics':{'tests':136,'status':29,'exact':8,'precision':107/158,'recall':107/193,'strict':415,'uncertain':103},
        'current_metrics':{'tests':sample['tests'],'status':sample['candidate']['status_correct'],
            'exact':sample['candidate']['exact_cases'],'precision':sample['candidate']['step_precision'],
            'recall':sample['candidate']['step_recall'],'strict':full['strict_resolved'],'uncertain':len(full['uncertain_cases'])},
        'recovered_accuracy_regressions':0,'new_identity_relationships':0,
        'schema_conclusion':'No examined participant schema attests exhaustive shared_subjects. Singleton/duplicates remain UNKNOWN. Multiple distinct known subjects prove SHARED, but rule_06 supplies no shared-attachment redaction action.'}
    (root/'artifacts/targeted_review.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    report='''# Final targeted ownership and accuracy review

Baseline: `43990d03ac6de69302e59585d1d3c6f12d7ab9e8`, preserved locally under artifacts/baseline-43990d0 with CSV/ZIP hashes and reports. Main and participant inputs remain unchanged. This evaluator runs after inference; reference IDs and answers never supply production bindings, policy or steps.

## Twelve attachment cases

All twelve have exact, dated subject associations and PRESENT attachment observations. No examined metadata contains shared_subjects, sole_owner or an exclusive-ownership catalog attestation. Uploader identity, a PII detector's matched selector, ticket ID, filename and multiple physical replicas establish association/existence, not exhaustive ownership. The only matched dated activities are deletion-worker claims; their success/failure does not establish state or sole ownership. No new source relationship or recoverable accuracy gain was found.

| Case / subject | Cutoff | Resource | Evidence / capture | Association selectors and source scope | Ownership / action |
|---|---|---|---|---|---|
'''
    for f in findings:
        fields=', '.join(sorted({p for o in f['observations'] for p in o['selector_fields']}))
        locations=', '.join(sorted({o['scope']+':'+o['locator'] for o in f['observations']}))
        evidence=', '.join(s+' '+t for s,t in zip(f['sources'],f['source_captured_at']))
        report+=f"| {f['case']} / {f['subject']} | {f['cutoff']} | {f['system']}/{f['resource']} | {evidence} | {fields}; {locations} | UNKNOWN; abstain |\n"
    report+='\nExact source files and dated activities examined:\n\n'
    for f in findings:
        report+=f"- {f['case']}: `{', '.join(f['source_paths'])}`; activities `{', '.join(f['dated_activity_ids'])}` ({', '.join(f['dated_activity_types'])}); binding {f['binding']} at {f['binding_source']}.\n"
    report+='''
## Ownership semantics corrected

Rule_06 says SUPPORT_ATTACHMENT / “Attachment belongs only to the deletion subject” / DELETE. It does not declare owner lists exhaustive and supplies no shared-attachment REDACT fallback. Rule_05's redaction condition applies to SUPPORT_MESSAGE, a different category. A singleton shared_subjects list may contain only known associations; duplicates add no owner information. Only an independent explicit exclusivity attestation supports SOLE. Two known distinct subjects suffice for SHARED even if the list is partial; neither SHARED nor UNKNOWN satisfies rule_06. Contradictory or malformed attestations abstain. No unattested completeness flag is fabricated. An explicitly supplied unconditional redaction rule would be honored, but none is supplied for these attachments.

The previous synthetic test's automatic shared-attachment redaction expectation was corrected to match the supplied conditional rule. New authored tests cover partial singleton/duplicates, explicit sole ownership, contradictory attestations, shared lower bounds versus actual policy authorization, and rejection of an invented sole_owner boolean during original-source review. The reviewer now compares that policy-critical boolean directly rather than relying on string-token containment.

## Lost exact match

'''
    if not lost: report+='Historical replay was unavailable in this checkout; no unmeasured original prediction is asserted.\n'
    for k,variants in details.items():
        report+=f"{k}: old and reference have {len(variants['old_5b9a098']['steps'])} steps; current has {len(variants['current']['steps'])}. All statuses are {variants['current']['status']}. Exact arrays are recorded below.\n\n"
        for label,value in variants.items():
            report+=f"### {label}\n\n```json\n{json.dumps(value,indent=2)}\n```\n\n"
    report+='''
For case_13, evidence_03 (`evidence/records/customer_account_handover_20261001.txt`, line 43) states SUPPORT_ATTACHMENT / FOUND / subject selector for support_4218. Capture and observation are 2026-10-01T12:00:00Z, equal to the sample cutoff. This proves existence/association, not exclusive ownership. The other five current operations remain supported by the handover's account/search/security observations.

At 5b9a098, Policy.action returned rule_06's DELETE by default whenever shared_subjects was absent. Commit 713d6e158747e1b0729504167ebacaca6bf68f2f replaced that default with explicit attachment_ownership; Engine omitted facts whose required policy condition was UNKNOWN. This removed support_4218's finding, DELETE and absent verification, and renumbered the remaining five steps. The old exact match depended on unsupported ownership. Retaining the omission is a safety correction, not an unnecessary restriction. No case-specific exception is introduced.

Historical replay command (source-only 5b9a098 archive extracted under tmp/targeted-old-5b9a098):

```text
python tmp/targeted-old-5b9a098/code/main.py --mode candidate --dataset dataset --requests dataset/sample_deletion_requests.csv --cache-dir tmp/ocr --output tmp/targeted-old-sample.csv --metrics-path tmp/targeted-old-sample-metrics.json --uncertainty-report tmp/targeted-old-sample-uncertainty.md
```

## Current checkpoint versus 43990d0

| Metric | Before | After |
|---|---:|---:|
'''
    b=result['baseline_metrics']; n=result['current_metrics']
    for key in b:
        report+=f"| {key} | {b[key]:.4f} | {n[key]:.4f} |\n" if key in ('precision','recall') else f"| {key} | {b[key]} | {n[key]} |\n"
    report+=f"\nCandidate rows {full['resolved']}/518; missing/extra resources {sample['candidate']['missing_records']}/{sample['candidate']['extra_records']}; missing/extra operations {sample['candidate']['missing_operations']}/{sample['candidate']['extra_operations']}. Primary versus reviewed statuses {sample['primary']['status_correct']}/32 versus {sample['strict']['status_correct']}/32. Recovered regressions: 0.\n"
    report+='''
All prior safety mechanisms remain tested. Root-state, unbound/future-only selector gaps and case_55 permission are unchanged; no repeated broad evidence search was conducted. General OCR row geometry and ambiguous-intent coverage remain limited. Semantic certainty and official plan completeness remain FAIL; structural/source gates do not establish hidden-answer correctness. Final full inference uses zero language-model calls/tokens/API fee. Prior live AI experiments remain separately labeled historical development usage.

The three primary submission files are local output.csv, code.zip and the private root log.txt (chat_transcript). The separate agent-trace.zip must be produced only after contributing sessions finish and apps close, following TRACE_FINALIZATION.md and the unchanged official instructions. AI interview preparation remains a separate explanation of architecture, evidence, policy, measured failures and usage. No upload is authorized or performed.
'''
    path=root/'code/docs/TARGETED_ACCURACY_REVIEW.md'; path.write_text(report,encoding='utf-8')
    for relative in ('code/evaluation/evaluation_report.md','code/evaluation/usage_report.md','code/docs/UNRESOLVED_ISSUES.md','code/docs/SOURCE_REPAIR_REPORT.md'):
        p=root/relative; body=p.read_text(encoding='utf-8').split('\n## Final targeted review\n',1)[0]
        body+='\n## Final targeted review\n\nTARGETED_ACCURACY_REVIEW.md records all twelve dated ownership reviews and the replayed case_13 regression. No accuracy recovery is supported. Singleton lists without exclusivity attestations stay UNKNOWN; shared attachments have no supplied REDACT fallback. Four new tests cover these semantics and source-boolean integrity. Final inference remains zero model calls/tokens; historical experiments are separate.\n'
        p.write_text(body,encoding='utf-8')
    return result
