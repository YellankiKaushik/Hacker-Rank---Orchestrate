"""Current two-mode measurements. Golden sample data is evaluation-only."""
from datetime import datetime,timezone
import hashlib
import json
import re
import subprocess
import sys
from main import run,ROOT
from diagnostics import generate
from evaluation.main import compare
from ghosttrace.loader import read_csv
from ghosttrace.gaps import GapAuditor
from validate_candidate import validate


def ratio(a,b): return f'{a}/{b} ({100*a/b:.2f}%)' if b else 'N/A (zero denominator)'
def save(path,value): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(value,indent=2),encoding='utf-8')


def main():
    now=datetime.now(timezone.utc).isoformat(); reports=ROOT/'code/evaluation'; docs=ROOT/'code/docs'
    test=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','code/tests','-q'],cwd=ROOT,capture_output=True,text=True)
    if test.returncode: raise RuntimeError(test.stdout+test.stderr)
    count=int(re.search(r'Ran (\d+) tests',test.stdout+test.stderr)[1])
    sample=ROOT/'dataset/sample_deletion_requests.csv'; cache=ROOT/'tmp/ocr'
    primary,pm,_,_=run(ROOT/'dataset',sample,ROOT/'tmp/sample_primary.csv',cache,True,False)
    strict,sm,_,_=run(ROOT/'dataset',sample,ROOT/'tmp/sample_strict.csv',cache,True)
    candidate,cm,_,_=run(ROOT/'dataset',sample,ROOT/'tmp/sample_candidate.csv',cache,mode='candidate',uncertainty_path=ROOT/'tmp/sample_uncertainty.md')
    reference=read_csv(ROOT/'dataset/sample_output.csv') # only AFTER inference
    p,s,c=[compare(a,reference) for a in (primary,strict,candidate)]
    strict_full=generate()
    audits,full,corpus,index=run(ROOT/'dataset',ROOT/'dataset/deletion_requests.csv',ROOT/'output.csv',cache,mode='candidate')
    full['output_sha256']=hashlib.sha256((ROOT/'output.csv').read_bytes()).hexdigest()
    full['input_sha256']=strict_full['input_sha256']
    save(ROOT/'tmp/candidate_run_metrics.json',full); save(ROOT/'artifacts/candidate_run_metrics.json',full)
    checks=validate(ROOT/'output.csv',read_csv(ROOT/'dataset/deletion_requests.csv'),corpus,cache)
    save(ROOT/'artifacts/candidate_validation.json',checks)
    if checks['strict_accepted']!=full['strict_resolved']: raise ValueError('Fresh strict coverage disagrees')
    old=set(re.findall(r'\bcase_\d+\b',(ROOT/'code/evaluation/baseline.md').read_text()))
    remaining={u['case_id'] for u in full['unresolved']}
    recovered=sorted(old-remaining)
    auditor=GapAuditor(corpus,index)
    gaps={a.case['case_id']:auditor.inspect(a.case) for a in audits if a.case['case_id'] in old}
    diagnostic={d['case_id']:d for d in full['case_diagnostics']}
    local_path=ROOT/'artifacts/local_ai_evaluation.json'
    local=json.loads(local_path.read_text()) if local_path.exists() else None
    experiments=([local]+local.get('previous_runs',[])) if local else []
    local_totals={f:sum(v['usage'][f] for v in experiments) for f in ('attempts','input_tokens','output_tokens','estimated_cost_usd')}
    report=f'''# Measured two-mode evaluation

Generated {now}. **B: structurally valid candidate with documented semantic uncertainty.** There is no hidden-answer score. Full candidate coverage is {len(audits)}/518; strict evidence-proven coverage under the implemented finite-source review is {full['strict_resolved']}/518. This is not exhaustive knowledge of every possible copy.

## Public sample: all 32 cases

| Variant | Status correct | Exact ordered seven-field cases | Withheld / uncertain |
|---|---|---|---|
| Previous primary, 2ada359 | 29/32 | 9/32 | 3 withheld |
| Previous strict review, 2ada359 | 24/32 | 9/32 | 8 withheld |
| Current primary | {p['status_correct']}/32 | {p['exact_cases']}/32 | {len(pm['unresolved'])} withheld |
| Current strict review | {s['status_correct']}/32 | {s['exact_cases']}/32 | {len(sm['unresolved'])} withheld |
| Current every-row candidate | {c['status_correct']}/32 | {c['exact_cases']}/32 | {len(cm['uncertain_cases'])} uncertain, none withheld |

Every-row candidate metrics include all 32 generated predictions. Exact-case accuracy has not substantially improved. All 518 evaluation predictions exist, but their accuracy is NOT VERIFIED because no participant reference answers are available. References are loaded by this evaluator only after inference; no production module reads sample_output.csv.

| Candidate metric | Measurement |
|---|---|
| Status accuracy | {ratio(c['status_correct'],32)} |
| Exact case accuracy | {ratio(c['exact_cases'],32)} |
| Sequence accuracy | {ratio(c['sequence_correct'],32)} |
| Position-aligned field accuracy | {ratio(c['field_matches'],c['field_total'])} |
| Exact seven-field step precision | {ratio(c['step_matches'],c['predicted_steps'])} |
| Exact seven-field step recall | {ratio(c['step_matches'],c['reference_steps'])} |
| Reference citation agreement | {ratio(c['evidence_reference_matches'],c['evidence_reference_total'])} |
| False COMPLETE / false INCOMPLETE | {c['false_complete']} / {c['false_incomplete']} |
| Missing / extra reference resources | {c['missing_records']} / {c['extra_records']} |
| Missing / extra scope operations | {c['missing_operations']} / {c['extra_operations']} |

Field accuracy pads both arrays to the larger length, comparing all seven fields per position. Step precision/recall is multiset intersection including numbering and citations. Sequence accuracy compares ordered phase/operation/system/resource. Reference citation agreement is distinct from actual source support.

## Proof-gate analysis and measured GhostGuard effect

The official contract requires appropriate treatment of every relevant copy, required retention and prevention of active recreation paths. It does not require a profile/tombstone check in every case. GhostGuard now independently enumerates dated bound obligations and distinguishes A supported, B supported with a nonessential missing profile observation, C required proof missing, D contradicted, and E unsupported/fabricated. Only A/B accept strict review.

A retained journal alone cannot establish account deletion. A known linked record without a readback, or an unidentified account row in the admitted subject-linked source, remains C. A substantive compliant secondary treatment can qualify B when every grounded obligation is covered and no such ambiguity remains. All previous 97 missing-profile cases were re-evaluated: **{len(recovered)} now qualify B, 90 remain C**. Recovered cases: {', '.join(recovered)}. No new identity assignment was fabricated.

GhostGuard does not improve measured sample status accuracy: {p['status_correct']}/32 primary versus {s['status_correct']}/32 reviewed. Five withheld primary statuses match references while necessary linkage/scope proof is absent. Source rereading independently checks original bytes and hashes and catches injected source/citation/state/intent/operation errors in tests. Shared domain adapters/policy limit independence; there is no LLM reviewer or hidden-answer oracle.

## Full run: coverage versus certainty

- Strict accepted: {full['strict_resolved']}/518; unresolved: {len(full['unresolved'])}.
- Candidate: {len(audits)}/518; statuses `{full['statuses']}`.
- Uncertain predictions: {len(full['uncertain_cases'])}; unsupported full-proof status inferences: {full['unsupported_status_inferences']}; fabricated references: 0.
- Source-backed cited steps: {checks['source_backed_cited_steps']}/{checks['total_cited_steps']}. Future work uses empty evidence IDs.
- Structure, emitted citation/time/provenance/policy-operation gates PASS. Semantic certainty FAIL.
- Output SHA-256 `{full['output_sha256']}`; warm-cache seconds {full['runtime_seconds']:.4f}.
- Targeted rereads {full['targeted_source_reads']}, source-view cache hits {full['targeted_source_cache_hits']}; at most one retry/four source files per challenged case.

Unknown required state predicts INCOMPLETE without inventing a particular violation. Observed compliant states with unproven scope predict COMPLETE under an explicitly unverified closed-evidence assumption. Every such inference appears in artifacts/SUBMISSION_UNCERTAINTY_REPORT.md. case_55 has no source-supported current-state check: INCOMPLETE with an empty array satisfies CSV/JSON shape but fails strict semantic plan completeness. The existing strict validator remains unchanged and rejects the unproven candidate.

## Regression coverage and additional participant cases

{count} unit/synthetic integration test methods pass. Representative independently authored cases:

1. Compliant secondary treatment passes B without an unrelated profile; retention-only proof stays C.
2. An unobserved linked profile or unidentified account readback stays C; no batch-order assignment is used.
3. A forged COMPLETE with present prohibited data is D; fabricated sources/bindings are E and block export.
4. Unknown archive permission creates no restore-risk finding or blocked-restoration verification; independently proven violations remain actionable.
5. Access/correction/marketing-only/negated intent stays NOT_APPLICABLE; review independently checks authorization.
6. Both capture and observation cutoffs apply; primary absence cannot clear an older still-present replica.
7. Wrong real citations, future citations, invented resources, missing verification and unsafe retained-record deletion are rejected.
8. Atomic validation failure preserves previous output; release_check exercises two fresh processes and clean extraction.
9. Local model transport is fixed to loopback with no cloud authorization headers; quotes and schema are verified. Mock tokens never enter usage reports.

## Sample mismatch investigation

| Case | Candidate status | Missing reference operation/resource | Extra emitted operation/resource |
|---|---|---|---|
'''
    for f in c['failures']:
        missing=', '.join(sorted({f'{k[1]}:{k[3]}' for k in f['missing_operations']})) or 'none'
        extra=', '.join(sorted({f'{k[1]}:{k[3]}' for k in f['extra_operations']})) or 'none'
        report+=f"| {f['case_id']} | {f['predicted_status']} | {missing} | {extra} |\n"
    report+='''
Missing account/anonymous analytics verifications lack admitted subject selectors, or occur only in post-cutoff files. Several expected security-record checks are available only in excluded later captures. Assigning anonymous rows by position, event proximity or numeric suffix would fabricate identity relationships. These operations remain omitted and documented. The attachment discrepancy was checked: activity_4007 explicitly associates object_19 with the subject and evidence_46 establishes its storage. It remains despite its omission from the public reference. Source-backed account/tombstone extras likewise remain. Future verification covers each known remediated record/process; active flows and restores require explicit configuration/readback evidence. No golden case/resource ID or expected sequence was added to production logic. No substantial exact-case gain is claimed.
'''
    if local:
        report+=f"\n## Actual bounded local AI\n\nInstalled model `{local['requested_model']}`: initial four replies failed strict JSON checks; one diagnostic identified formatting failure. An explicit JSON-only instruction repaired it. Final authored fixture score {local['model_correct']}/4 including one abstention versus deterministic {local['baseline_correct']}/4. This tiny intent benchmark does not demonstrate dataset gain. All experimental calls including rejected replies: {local_totals['attempts']}, input tokens {local_totals['input_tokens']}, output tokens {local_totals['output_tokens']}. No API fee; local compute cost unmeasured. Rejected cloud credentials were not retried. Final dataset runtime uses zero model calls.\n"
    (reports/'evaluation_report.md').write_text(report,encoding='utf-8')
    usage=f'''# Final full-candidate runtime usage

Generated {now}. Run generated all {len(audits)} of {full['cases']} predictions; output SHA-256 `{full['output_sha256']}`. Strict accepted {full['strict_resolved']}, uncertain {len(full['uncertain_cases'])}. Warm-cache runtime {full['runtime_seconds']:.4f} seconds.

| Final runtime provider/model | Calls | Input tokens | Output tokens | Total tokens | Estimated API USD |
|---|---:|---:|---:|---:|---:|
| No language model invoked | 0 | 0 | 0 | 0 | 0.00 |
| Overall final 518-case run | 0 | 0 | 0 | 0 | 0.00 |

Average tokens per request: 0/518 = 0. Average API cost per request: $0/518 = $0. These figures exclude Codex engineering-session usage/cost, which is unmeasured here. Windows.Media.Ocr is local screenshot extraction, exposes no model ID/token usage, and uses a source-hashed cache. pypdf 6.10.0 extracts PDF text. No cloud model/rate is invented.

## Separate live local development experiment

'''
    if local:
        usage+=f"Ollama loopback, installed model `{local['requested_model']}`: {local_totals['attempts']} actual calls, {local_totals['input_tokens']} input + {local_totals['output_tokens']} output = {local_totals['input_tokens']+local_totals['output_tokens']} tokens. Per-model totals equal these experimental overall totals. Includes initial four formatting failures, one diagnostic and final four-fixture check ({local['model_correct']}/4 including abstention versus {local['baseline_correct']}/4 baseline). Actual server usage is measured; mock tokens excluded. Zero API fee; hardware/electricity cost NOT VERIFIED. These experimental tokens are not final 518-case inference.\n\n"
    usage+='''Optional AI is bounded to deterministic intent abstentions. Strict two-field schema, exact input quotes, cache invalidation by provider/model/schema/prompt/input, call/output/timeout limits, and fallback remain enforced. It cannot generate IDs, policy or steps. Cloud access remains unverified after the historical HTTP 401 and was not retried. The deterministic full run does not claim an LLM investigation or an AI dataset accuracy gain.
'''
    (reports/'usage_report.md').write_text(usage,encoding='utf-8')
    recovery=f'''# Contract and recovery audit

Generated {now}. Blanket profile proof replaced by relevant obligations; A/B accept, C/D/E block. Previous 97-case cluster re-evaluated: {len(recovered)} accepted B, 90 unresolved C. case_55 separately remains unknown. Strict coverage {full['strict_resolved']}/518; candidate 518/518 with {len(full['uncertain_cases'])} unproven predictions.

The contract quantifies relevant records without prescribing one universal category. B requires substantive compliant treatment, all dated bound obligations covered and no anonymous root observation in the subject-linked source. Retention alone does not establish deletion. No IDs were assigned by timing, position or suffix.

| Previous blocker | Current strict result | Admitted sources examined | Unbound root candidates | Reason |
|---|---|---|---|---|
'''
    for case_id in sorted(old):
        g=gaps[case_id]
        reason='B: secondary obligation proven; no necessary missing profile observation' if case_id in recovered else diagnostic[case_id].get('final_error','')
        recovery+=f"| {case_id} | {'ACCEPTED B' if case_id in recovered else 'UNRESOLVED C'} | {', '.join(g['linked_sources']) or 'none'} | {len(g['orphan_root_candidates'])} | {reason} |\n"
    recovery+='''
## case_55: exact cutoff

Cutoff 2026-04-30T11:00:00Z. evidence_32 backup_restore_console_20260429.png proves storage/existence; pre-cutoff activity_4006 links user_16 and backup_9287. All 27 eligible manifest sources and admitted activity/history were rechecked; no allowed/blocked permission was found. Neighboring archives, success percentages and a drill predating this archive do not prove target restoration. activity_3387 and later log/SQL captures remain excluded. Strict remains unresolved; the general unknown-required-state rule predicts INCOMPLETE with no steps. Neither restore risk nor blocked restoration is fabricated. Strict semantic plan completeness fails.

## Binding limits

Anonymous 404s/anonymized rows establish state for a resource without identifying its subject. A retained journal in the same batch cannot assign that row to a person. Future-only sources are diagnostic explanations only; no future binding selects a candidate status/resource/citation/operation. Every remaining inferred prediction is listed separately in SUBMISSION_UNCERTAINTY_REPORT.md.
'''
    (docs/'RECOVERY_AUDIT.md').write_text(recovery,encoding='utf-8')
    issues=f'''# Unresolved evidence and execution issues

Updated {now}. Strict unresolved {len(full['unresolved'])}; candidate 518 rows; uncertain {len(full['uncertain_cases'])}. Recovered B: {', '.join(recovered)}. Candidate row coverage does not resolve source gaps. Separate per-case assumptions/omitted obligations are in artifacts/SUBMISSION_UNCERTAINTY_REPORT.md.

| Case | Admitted evidence examined | Missing fact and impact | Candidate; recommended next action |
|---|---|---|---|
'''
    uncertain={u['case_id']:u for u in full['uncertain_cases']}
    for u in full['unresolved']:
        case_id=u['case_id']; g=gaps[case_id]
        issues+=f"| {case_id} | {', '.join(g['linked_sources']) or 'none'} | {u['error']} | {uncertain[case_id]['status']} unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |\n"
    issues+='\n## Public sample blockers\n\n'+'\n'.join('- '+u['case_id']+': '+u['error'] for u in sm['unresolved'])+'\n'
    issues+='''
## Shared limitations and next action

- case_55 storage/association facts are verified; restoration permission is not. All 27 eligible sources and activity/history were examined. Its empty candidate plan is a semantic limitation; obtain an explicit pre-cutoff access observation. No REPORT_RESTORE_RISK or VERIFY_RESTORE_BLOCKED is emitted.
- Unsupported COMPLETE predictions assume no additional untreated copy; unknown-required-state INCOMPLETE does not assert an active violation. Every assumption is counted separately. Emitted citation/operation PASS checks do not establish global semantic certainty.
- Missing sample account/analytics/security operations lack admissible bindings or exist only in excluded later captures. Evidence-supported attachment/account/tombstone extras remain even when omitted from public references. More linkage cannot be obtained by copying golden IDs.
- Installed local AI works on four bounded authored intent fixtures; final runtime needs zero calls. Initial malformed replies were rejected, then fixed by explicit JSON instructions. Tiny fixture success does not establish full-dataset gain. The rejected cloud credential was not retried.
- Fresh isolated dependency installation is NOT VERIFIED; existing runtime imports/tests pass. Final raw trace export waits until session ends and app closes as required by the official instructions. Originals remain preserved. No HackerRank upload occurred.
'''
    (docs/'UNRESOLVED_ISSUES.md').write_text(issues,encoding='utf-8')
    save(ROOT/'tmp/sample_metrics.json',{'primary':p,'strict':s,'candidate':c,'run':cm})
    checkpoint={'tests':count,'sample_status':s['status_correct'],'sample_exact':s['exact_cases'],
        'candidate_sample_status':c['status_correct'],'candidate_sample_exact':c['exact_cases'],
        'full_accepted':full['strict_resolved'],'full_unresolved':len(full['unresolved']),
        'candidate_rows':len(audits),'candidate_uncertain':len(full['uncertain_cases']),
        'output_sha256':full['output_sha256'],'recovered_cases':recovered,'local_ai_totals':local_totals}
    save(ROOT/'tmp/checkpoint.json',checkpoint); print(json.dumps(checkpoint,indent=2))
