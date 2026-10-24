"""Regenerate honest measured checkpoint reports and the unresolved-issue register."""
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import run,ROOT
from diagnostics import generate
from evaluation.main import compare
from ghosttrace.loader import read_csv
from ghosttrace.models import timestamp,tokens
from ghosttrace.engine import Engine
from audit_dataset import census
from ghosttrace.gaps import GapAuditor
from evaluation.evaluate_ai import evaluate as evaluate_ai


def ratio(a,b): return f'{a}/{b} ({100*a/b:.2f}%)' if b else 'not measured (zero denominator)'


def main():
    report_dir=ROOT/'code/evaluation'; docs=ROOT/'code/docs'; docs.mkdir(exist_ok=True)
    tests=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','code/tests','-q'],cwd=ROOT,capture_output=True,text=True)
    test_output=tests.stdout+tests.stderr
    if tests.returncode: raise RuntimeError(test_output)
    match=re.search(r'Ran (\d+) tests in ([\d.]+)s',test_output)
    count=int(match[1]); test_seconds=float(match[2])
    sample_path=ROOT/'dataset/sample_deletion_requests.csv'
    primary,primary_run,_,_=run(ROOT/'dataset',sample_path,ROOT/'tmp/sample_primary.csv',ROOT/'tmp/ocr',True,False)
    reviewed,sample_run,corpus,index=run(ROOT/'dataset',sample_path,ROOT/'tmp/sample_reviewed.csv',ROOT/'tmp/ocr',True,True)
    references=read_csv(ROOT/'dataset/sample_output.csv')
    p=compare(primary,references); m=compare(reviewed,references)
    final=generate()
    ai_controlled=evaluate_ai()
    engine=Engine(corpus,index)
    all_cases=read_csv(ROOT/'dataset/deletion_requests.csv')+read_csv(sample_path)
    case_map={c['case_id']:c for c in all_cases}
    now=datetime.now(timezone.utc).isoformat()
    gap_auditor=GapAuditor(corpus,index)
    gap_details=[gap_auditor.inspect(case_map[u['case_id']]) for u in final['unresolved']]
    prior_path=ROOT/'artifacts/baseline-01beaa1/UNRESOLVED_ISSUES.md'
    prior_ids=set(re.findall(r'\| evaluation / (case_\d+) \|',prior_path.read_text(encoding='utf-8'))) if prior_path.exists() else None
    current_ids={u['case_id'] for u in final['unresolved']}
    recovered=sorted(prior_ids-current_ids) if prior_ids is not None else None
    newly_blocked=sorted(current_ids-prior_ids) if prior_ids is not None else None
    primary_by_id={a.case['case_id']:a for a in primary}
    reviewed_ids={a.case['case_id'] for a in reviewed}
    reference_map={r['case_id']:r for r in references}
    benchmark_rejections=[c for c,a in primary_by_id.items() if c not in reviewed_ids and a.status==reference_map[c]['deletion_status']]
    rows=[
        ('Case status accuracy',ratio(m['status_correct'],m['cases'])),
        ('Exact case match (status + ordered seven-field steps)',ratio(m['exact_cases'],m['cases'])),
        ('Exact sequence match (phase/operation/system/resource)',ratio(m['sequence_correct'],m['cases'])),
        ('Field accuracy (position-aligned, missing/extra slots penalized)',ratio(m['field_matches'],m['field_total'])),
        ('Exact step precision (includes numbering and citation)',ratio(m['step_matches'],m['predicted_steps'])),
        ('Exact step recall',ratio(m['step_matches'],m['reference_steps'])),
        ('Reference citation agreement for emitted cited steps',ratio(m['evidence_reference_matches'],m['evidence_reference_total'])),
        ('Public sample inference + independent review runtime',f"{sample_run['runtime_seconds']:.4f} seconds"),
        ('False COMPLETE / false INCOMPLETE among emitted predictions',f"{m['false_complete']} / {m['false_incomplete']}"),
        ('Unresolved sample cases (included as failures)',str(m['unresolved_cases'])),
        ('Missing / extra reference resources',f"{m['missing_records']} / {m['extra_records']}"),
        ('Missing / extra reference scope/operations',f"{m['missing_operations']} / {m['extra_operations']}"),
    ]
    report=f'''# GhostTrace Guard evaluation checkpoint

Generated from local execution at {now}. **NOT submission-ready.** No hidden score is known.

## Measured sample results

All 32 public references are evaluated, including unresolved cases as failures. Reference distribution: 10 COMPLETE, 22 INCOMPLETE, 0 NOT_APPLICABLE. References are read only by this evaluator after inference, never by the engine, identity graph, adapters, policy or reviewer.

| Metric | Result |
|---|---|
'''+''.join(f'| {name} | {value} |\n' for name,value in rows)+f'''
The field denominator is seven times the sum of the larger of predicted and reference sequence lengths for each case. Missing predictions receive no matching fields. Step precision/recall uses multiset intersection of exact seven-field objects. Sequence accuracy ignores state and citation but requires exact ordered scope/operations. Reference citation agreement is distinct from source integrity: a valid real citation can differ from the canonical reference. All accepted emitted citations passed source-ID, timestamp and independent raw-source support checks; this is not a semantic accuracy guarantee.

## Baseline and review comparison

| Variant | Correct statuses | Exact cases | Unresolved samples | Seconds |
|---|---|---|---|---|
| Primary, no independent release review | {p['status_correct']}/32 | {p['exact_cases']}/32 | {len(primary_run['unresolved'])} | {primary_run['runtime_seconds']:.4f} |
| Source review and COMPLETE proof gate | {m['status_correct']}/32 | {m['exact_cases']}/32 | {len(sample_run['unresolved'])} | {sample_run['runtime_seconds']:.4f} |

Initial measured prototype: 25/32 statuses, 6/32 exact cases. Adding pipe-format logs, completed analytics readbacks, trace correlation and indirect erasure language improved the primary prototype to 29/32 statuses and 8/32 exact cases. Removing document-wide subject joins prevented unrelated retained records contaminating multiple cases. **Review does not improve public-sample status accuracy**: it withholds five otherwise correct reference statuses because the engine lacks profile/tombstone linkage proof. It is retained as a hard safety/uncertainty gate, not marketed as an accuracy improvement. There is no LLM reviewer; raw-source retrieval is independent, but parsing utilities are shared with ingestion.

Continuation from commit 01beaa1: explicit `source_resource_id` traversal, dated owner-system metadata and a scoped physical-table query recovered one complete sample verification sequence. Exact cases improved from **8/32 to {m['exact_cases']}/32**, and primary exact cases from 8/32 to {p['exact_cases']}/32. The reviewer still withholds {len(benchmark_rejections)} primary statuses that agree with public references: {', '.join(sorted(benchmark_rejections))}. These are benchmark false rejections/abstentions with a concrete missing-profile-link reason, not measured LLM-review gains. Current reviewer rejection categories: `{sample_run['rejection_categories']}`. Missing operations above exclude differences due only to numbering or citation, unlike exact-object metrics.

## Full participant run

The run processed all {final['cases']} input cases in {final['runtime_seconds']:.4f} seconds with a warm content-hashed OCR cache. It accepted {final['resolved']} decisions: {final['statuses']}. **{len(final['unresolved'])} cases remain unresolved.** Of these, 97 draft COMPLETE cases were blocked for missing linked profile absence/tombstone proof, and case_55 lacks restore-access proof at its cutoff. No valid 518-row root output.csv was produced. `artifacts/resolved_predictions.partial.csv` contains only accepted rows and must not be submitted as the final output. Even accepted rows may omit resources the engine cannot link; full semantic correctness is unproven.

Recovered from the archived 98-case blocker set: **{len(recovered) if recovered is not None else 'NOT VERIFIED (archive unavailable)'}**. Newly blocked: {newly_blocked if newly_blocked is not None else 'NOT VERIFIED'}. The unchanged blocked cluster is a measured result; no unsupported rows were filled. Targeted re-investigation reread {final['targeted_source_reads']} source files and reused {final['targeted_source_cache_hits']} source-view caches after verifying source hashes. Each challenged case has at most one retry and four reread sources. Rejection categories for this full attempt: `{final['rejection_categories']}`. See RECOVERY_AUDIT.md for all per-case candidate/link/cutoff evidence.

## Independent synthetic regression cases

{count} test methods passed in {test_seconds:.3f} seconds using `python -m unittest discover -s code/tests -v`. These are executed tests, not the architecture pack's proposed test count. Representative independent scenarios:

1. A request for an account-information copy with a present profile produces NOT_APPLICABLE and no steps. Additional opt-out, correction and explicit negation cases are covered. The public samples cannot measure NOT_APPLICABLE recall.
2. A present profile followed by future-only absence evidence remains INCOMPLETE at the earlier cutoff; a future-only case is unresolved, never defaulted COMPLETE.
3. A compliant tombstone, required retained journal and active restore path produce BLOCK_RESTORE and retain/redact verification, without deleting the archive or journal.
4. Simultaneous primary absence and replica presence remains INCOMPLETE.
5. Malicious SQL ATTACH/PRAGMA/extensions/triggers, path traversal, invented/future citations and evidence prompt injection are rejected or ignored as data.
6. GhostGuard detects a missing backup, missing final verification, forged state inconsistent with the reread log, and COMPLETE supported only by a retained journal.
7. A serialization failure preserves the previous output; CSV roundtrip and canonical flow-before-record ordering are checked.
8. An explicit upstream resource reference plus a dedicated physical capture recovers a missing account verification; unrelated inventory batches cannot clear an existing profile.
9. A deliberately damaged token index is repaired by rereading its original source, followed by independent review. Failed operation results supply owner metadata only, never absence proof.
10. Later primary absence cannot hide an older still-present replica; a later absence on that same replica supersedes its prior presence. An archive listing does not change known restore permissions.
11. Optional AI transport tests use unmistakable mock model names/tokens. Invented quotes, extra ID/action fields, authentication failures, retry bounds and cost/call limits are tested; these are not live provider benchmarks.

## Remaining sample failures

Each mismatch below comes from measured comparison, not an inference shortcut. Resource IDs from reference answers remain evaluation-only.

| Case | Predicted status | Missing reference scope/operation | Extra predicted scope/operation |
|---|---|---|---|
'''
    key=lambda s:(s['phase'],s['operation'],s['system_id'],s['resource_id'])
    for failure in m['failures']:
        missing=sorted({f"{s[1]}:{s[3]}" for s in failure['missing_operations']})
        extra=sorted({f"{s[1]}:{s[3]}" for s in failure['extra_operations']})
        report+=f"| {failure['case_id']} | {failure['predicted_status']} | {', '.join(missing) or 'none'} | {', '.join(extra) or 'none'} |\n"
    report+='''
## Limits and next changes

Prioritize recovering source-supported bindings for identifier-free readbacks, explicit scoped negative queries and retained-record checks. Never infer a resource ID from case/user number suffixes or copy IDs from sample answers into inference. Some expected account IDs cannot currently be tied to a subject without such an unsupported shortcut. Investigate catalog/display-identity contradictions and media scope further; local OCR is imperfect and its extracted text is not a proof of every visual relationship. Do not discard source-backed extra risks just to match a small public sample. Detailed per-case blockers and examined sources are in `code/docs/UNRESOLVED_ISSUES.md`.

The optional Responses-based intent path is implemented, bounded and tested with mocked transport. A real read-only model discovery check returned HTTP 401: no usable live model was verified, and no live inference call was made. It remains disabled by default and has no measured live accuracy benefit. Local Windows OCR is active. All measurements here describe this checkpoint, not a finished submission.

Reproduction: `python -m unittest discover -s code/tests -v`, `python code/evaluation/generate_reports.py`, `python code/main.py`, `python code/validate_output.py`, `python code/package_submission.py`. The last prediction gates remain failing while unresolved cases exist. Use the bundled interpreter command in README on this workstation.
'''
    report+=f"\nControlled intent fixtures: {ai_controlled['unambiguous_correct']}/{ai_controlled['unambiguous_fixtures']} unambiguous decisions correct, plus the expected abstention fixture. Live AI quality: **{ai_controlled['live_ai_quality']}** ({ai_controlled['live_ai_reason']}). No mock token counts enter runtime usage totals.\n"
    (report_dir/'evaluation_report.md').write_text(report,encoding='utf-8')
    usage=f'''# Runtime usage and cost checkpoint

Generated {now}, tied to the full {final['cases']}-case attempt that produced the {final['resolved']}-row **partial** artifact, SHA-256 `{final['partial_output_sha256']}`. There is no completed full-dataset final output yet.

| Provider / model | Calls | Input tokens | Output tokens | Total tokens | Estimated USD |
|---|---:|---:|---:|---:|---:|
| No language model invoked | 0 | 0 | 0 | 0 | 0.00 |
| Overall runtime API totals | 0 | 0 | 0 | 0 | 0.00 |

Runtime: {final['runtime_seconds']:.4f} seconds. Average tokens per input request: 0/518 = 0. Average estimated API cost per input request: $0/518 = $0. No provider price assumption is needed for zero calls. This counts inference/review API usage only; it excludes the Codex engineering session, whose token consumption and cost have not been obtained as per-request telemetry and must not be assumed zero.

PDF parsing uses pypdf 6.10.0. Windows.Media.Ocr performs local screenshot recognition (English language pack), with no network API, reported token counts or billed API model. Its internal OCR model identifier is not exposed by the Windows API. The final attempt used a warm source-SHA-256 OCR cache; cold OCR was separately exercised for all 11 screenshots. The optional intent adapter is implemented and transport-tested with mocks but is inactive in this full run. A real model-list availability request returned HTTP 401. No actual inference model identity, calls or token usage exists for that rejected availability check; model quality is NOT VERIFIED. Mock model IDs/tokens are test fixtures and are excluded here. Model/pricing configuration must be explicit; no model or rate is guessed.

The report must be regenerated with `python code/evaluation/generate_reports.py` after unresolved cases are fixed and a valid 518-row output exists. These truthful zeros do not prove the hackathon's desired AI-powered investigation capability is complete.
'''
    (report_dir/'usage_report.md').write_text(usage,encoding='utf-8')
    issues=f'''# Unresolved issues — GhostTrace Guard

Updated {now}. No clarification questions are required for ordinary execution. This is a checkpoint issue register, not a claim that the official dataset is defective. “Missing” below means the current engine could not establish the relationship/proof from admitted evidence; further parser or retrieval work may recover it.

## Verified case_55 evidence and missing fact

- Cutoff: `2026-04-30T11:00:00Z`.
- `evidence_32`, `dataset/evidence/images/backup_restore_console_20260429.png`, captured `2026-04-29T09:00:00Z`, shows the archive and storage properties. Visual inspection and OCR both performed.
- `activity_4006`, `2026-04-29T09:07:01Z`, links `backup_9287` to `user_16`; it does not prove restore permission.
- `activity_3387` is a later restore event and is excluded at this cutoff. Later log/SQL captures are not used to backdate capability.
- Missing: an admissible access-policy/configuration/readback observation proving whether this archive was restorable or blocked at the cutoff. Archive existence, neighboring restore history and generic restore success rates are insufficient.
- Impact: no defensible COMPLETE or INCOMPLETE restore verdict can be compiled for this case under the current schema. No UNKNOWN row or fabricated finding is exported.
- Next action: exhaust remaining scoped source relations and source timestamps; if no admissible fact exists, retain this blocker for the next checkpoint. No extra evidence has been verified.

The continuation independently inspected the actual screenshot again and searched all 27 manifest sources whose capture times precede this cutoff, plus admissible CSV activity/history. It distinguishes stored archive existence, catalog association, technical restore capability, and permission at cutoff. Only the first two are established. No direct restore-access configuration or admissible allowed/blocked observation was found; future material remains excluded.

## Per-case release blockers

For every row below, all manifest-listed sources were ingested, but only observations captured and observed at/before that case's cutoff were admitted. The sources column lists subject-linked admissible observations examined; an empty result is not absence proof. No raw personal identifiers are reproduced.

| Dataset / case | Evidence examined (subject-linked, admissible) | Missing information | Impact | Recommended next action |
|---|---|---|---|---|
'''
    for dataset_name,unresolved in [('evaluation',final['unresolved']),('public sample',sample_run['unresolved'])]:
        for issue in unresolved:
            case=case_map[issue['case_id']]; cutoff=timestamp(case['audit_at'])
            uid,aliases=engine.identity.resolve(case['email'],cutoff)
            linked=[f for f in index.facts if f.admissible(cutoff) and aliases & tokens(f.data.get('_bindings',f.data))]
            sources=sorted({f.source for f in linked})
            missing=issue['error'].replace('|','/')
            impact='Withheld; no final status exported'
            recommendation='Recover explicit dated subject/resource binding and source-backed profile absence or compliant tombstone; rerun review'
            if issue['case_id']=='case_55': recommendation='Find pre-cutoff restore-access proof; do not infer permission from storage'
            issues+=f"| {dataset_name} / {issue['case_id']} | {', '.join(sources) or 'No admissible linked state observation; identity/history/activity and negative source search examined'} | {missing} | {impact} | {recommendation} |\n"
    issues+=f'''
## Other verified limitations and open work

| Issue | Evidence / verified state | Impact | Recommended next action |
|---|---|---|---|
| Public sample reference differences | See every measured failure in evaluation_report.md | Exact-case accuracy is {m['exact_cases']}/32 | Improve general bindings and scoped readbacks; do not hardcode sample IDs |
| Media/catalog identity inconsistency | Some catalog-linked screenshots display contact fields differing from current identity snapshots; the marketing console is one example | Catalog links prove an association claim, not that every displayed contact value belongs to that subject | Recheck visual field scope and dated identity provenance; surface contradictions rather than merge people |
| Discovery coverage | 97 primary COMPLETE drafts lacked profile/tombstone proof; reviewer blocked them | A syntactically valid draft is not a complete deletion audit | Maintain the proof gate and improve source graph |
| Raw-source reviewer independence | Reviewer reopens and reparses source, but uses shared deterministic adapters | Not independent model reasoning or independent parser validation | Add adversarial fixtures and a separately implemented semantic review where useful |
| Optional language model | Bounded intent adapter and mock contract tests implemented; actual model discovery returned HTTP 401 | Live model quality and model availability are NOT VERIFIED; full-run model calls remain zero | Validate a usable environment credential/model and explicit prices before a controlled live test; do not use AI to create missing proof |
| SQL inventory scope | A global unrelated-inventory query experiment wrongly cleared a known profile and was reverted; regression test added | Inventory batches cannot be treated as a global customer census | Use subject-linked captures, or a real explicit reference and dedicated physical-table primary-key scope |
| Source docs | Only the three root DOCS files exist; referenced companion pack files were not present | Missing design companions, not a runtime data blocker | Continue from official contract and available design; don't claim absent files were read |
| Upstream documentation change | Fetched upstream/main at 0eddbbd; only the AGENTS.md challenge URL typo changes, with no dataset/contract changes | Update is inspected but not merged; local main is preserved | Reconcile the documentation update separately without automatic merging |
| Python alias | WindowsApps python.exe alias failed; bundled Python 3.12.14 works | Bare python command currently needs a proper Python install/PATH | Use documented bundled command or install Python; no global configuration was changed |
| Early test attempt | Default OS temporary directory caused sandbox permission failures; that attempt was interrupted | Initial run failed for environment reasons | Tests now use checkout-local tmp/tests; subsequent complete suite passed |
| Trace ZIP | Original Codex rollout remains in place; app session is still open | Final complete trace archive cannot yet be copied under official close-first instructions | Finish session, close app, copy only relevant rollout, inspect/redact and package separately |
| Final artifacts | No valid 518-row output; code.zip is a development checkpoint package | G1/G5 acceptance incomplete; not ready for HackerRank submission | Resolve blockers, rerun tests/evaluation/full validator and rebuild package |
'''
    (docs/'UNRESOLVED_ISSUES.md').write_text(issues,encoding='utf-8')
    gap_counts=Counter(g['reason'] for g in gap_details if g['case_id']!='case_55')
    gap_report=f'''# Recovery audit — source-supported links and remaining ambiguity

Measured {now}, continuing commit 01beaa1. This report uses participant observations and actual run diagnostics; sample references are evaluator-only. No ID suffix, case numbering, file naming, temporal-neighbor matching or answer-pattern assignment was used in inference.

## P1–P4 findings and implemented repairs

1. The original engine did not traverse explicit `source_resource_id` fields. The new dated relationship graph combines that field with independent activity owner-system metadata, treating operation success/failure only as a claim. The actual structured corpus exposes three such links, all in the dedicated search snapshot. This repaired a public-sample account verification sequence; it did not recover the blocked full-dataset cluster.
2. Inventory exports are scoped batches. An attempted cross-batch global absence rule wrongly cleared a known remaining profile and was reverted. The regression suite now prevents unrelated batch exports proving absence. Dedicated physical-table captures can answer an already-grounded resource-key query; ordinary inventory batches still require a linked source scope.
3. Source/proof IDs, observation/capture times, owner scope, lookup locators and reference paths are retained as binding provenance. Current/historical phone formats normalize to a conservative E.164 key. A stable subject conflicting with the matching email is rejected rather than merged.
4. OCR can replace an underscore with a space. Structural separator normalization is allowed only for an already-supplied catalog label and with word boundaries; it recovered a retained tombstone and security-record view. It does not perform fuzzy name or numeric-ID matching.
5. GhostGuard now distinguishes rejection categories and performs one targeted reread of at most four admissible source files. A regression with a deliberately damaged lookup index is repaired from raw source, then passes independent source review. Actual full-run rereads did not supply the missing subject selectors: `{final['rejection_categories']}` remain blocked.
6. An older still-present replica is not cleared by a later primary-only absence. A storage/existence listing does not supersede known restore-access configuration. Explicit readback activity cannot support a forged opposite state. Validator shape checks reject malformed input with controlled errors.

## Recovery outcome

- Previously blocked: 98 evaluation cases.
- Defensibly recovered from that archived set: {recovered if recovered is not None else 'NOT VERIFIED (prior archive not present)'}.
- Newly blocked relative to that set: {newly_blocked if newly_blocked is not None else 'NOT VERIFIED'}.
- Accepted rows: {final['resolved']}/{final['cases']}; remaining: {len(final['unresolved'])}.
- Missing-profile cluster diagnostic reasons: `{dict(gap_counts)}`.
- Primary versus reviewed public statuses: {p['status_correct']}/32 versus {m['status_correct']}/32; exact arrays {p['exact_cases']}/32 versus {m['exact_cases']}/32. No large accuracy recovery is claimed.

## Why orphan readbacks remain unresolved

A 404/anonymous row can prove a state for the supplied resource key without saying whose key it is. A retained journal in the same batch establishes that the person occurs in that batch, but does not identify which anonymous lookup belongs to that person. Batch position and one-to-one assignments are not stated in the source schema. Multiple assignments of anonymous resource rows can therefore remain consistent with the visible identifiers. A deletion-worker event near a case's report time does not supply the missing subject link in this global stream, which also contains unrelated people. A later capture with an earlier observation is still excluded when its capture is after the case cutoff.

The table records real candidate rows in admitted, linked sources without assigning any candidate to a subject. “Zero candidates” does not establish deletion. Some sources contain no root-account observation at all; others contain unbound root readbacks. This is an input/provenance limitation at this checkpoint, not a claim that every official file is defective or that no future parser improvement is possible.

| Case | Linked admitted sources | Unbound root candidates | Future-only root sources excluded | Reason | Reread sources attempted |
|---|---|---|---|---|---|
'''
    by_diagnostic={d['case_id']:d for d in final['case_diagnostics']}
    for gap in gap_details:
        candidates=', '.join(f'{source}:{resource}/{state}' for source,system,resource,state in gap['orphan_root_candidates']) or 'none'
        reread=by_diagnostic[gap['case_id']]['reinvestigation_sources']
        gap_report+=f"| {gap['case_id']} | {', '.join(gap['linked_sources']) or 'none'} | {candidates} | {', '.join(gap['future_root_sources']) or 'none'} | {gap['reason']} | {', '.join(reread) or 'primary evidence search only'} |\n"
    gap_report+='''
## case_55: four separate facts

| Proposition | Evidence examined | Result |
|---|---|---|
| Archive exists | evidence_32 original PNG, OCR and visual reinspection | Established for backup_9287 |
| Archive is linked to this subject | activity_4006 before cutoff, plus matching archive/contact field in the PNG | Catalog-supported association established |
| This archive is technically restorable | Storage size, encryption and a last-drill field; neighboring archives restored in the activity panel | Not established for this archive; the listed drill predates this archive's creation |
| Restore access was allowed/blocked at cutoff | All 27 eligible manifest sources and pre-cutoff CSV activities searched | No explicit configuration/access proof found |

The cutoff is 2026-04-30T11:00:00Z. The PNG capture and catalog linkage precede it. The later activity_3387 and later log/SQL captures are excluded. Generic restore-success percentages and a neighboring archive's restore are not used to infer permission for backup_9287. This case stays unresolved.

## P5 boundary and P7 decision

A bounded optional intent adapter is implemented and tested with mocked provider transport. Real model discovery returned HTTP 401; no usable live model was verified, no live inference calls were made, and no model/token/pricing identifier was fabricated. Live AI quality is NOT VERIFIED. The full dataset stays on deterministic inference and local OCR.

The final output gate remains FAIL because 518 supported predictions do not exist. The validated partial artifact and development ZIP remain separate from a finished submission. No unknown case is recast as NOT_APPLICABLE, no unsupported COMPLETE is forced, and no HackerRank upload occurred.
'''
    (docs/'RECOVERY_AUDIT.md').write_text(gap_report,encoding='utf-8')
    (ROOT/'tmp/recovery_gap_details.json').write_text(json.dumps(gap_details,indent=2),encoding='utf-8')
    inventory=census()
    audit_doc='# Measured participant dataset audit\n\n'
    audit_doc+='Read-only audit of participant-facing inputs. No organizer-only files or generator internals were accessed.\n\n| CSV | Data rows | Columns |\n|---|---:|---|\n'
    for name,value in inventory.items():
        if isinstance(value,dict) and 'rows' in value:
            audit_doc+=f"| {name} | {value['rows']} | {', '.join(value['columns'])} |\n"
    audit_doc+=f"\nEvidence formats: {inventory['evidence_formats']}. All 94 listed files were read.\n\n"
    audit_doc+='''Confirmed structures: nested JSON snapshots and per-service exports; generic typed operational records; SQLite primary/read/regional/reporting/failover snapshots; JSON/logfmt/bracket/pipe/syslog/cloud log dialects; four text-bearing business PDFs; eleven PNG admin screenshots. A representative PDF was rendered and visually inspected alongside screenshots; all PNGs were passed through local OCR.

Key discoveries: identity history changes email, phone and hash; manifest entries do not assign subjects. Trace-start lookup keys must be joined to completion observations. Analytics contacts can be SECONDARY_IDENTIFIER records requiring deletion rather than anonymization. Tombstones retain stable references but remove direct identifiers. Retained journals and legal holds are not ordinary deletion targets. Source capture time and fact observation time are independently checked. Same-time replica presence wins over primary absence. `reported_status`/operation success never establish resulting state.

PDFs are ordinary customer statements, retention records and a support attachment. Their business document identifiers require catalog-grounded resource linkage. Screenshots include unrelated table rows: document-wide identifier matches must not associate every visible resource with every person. OCR is source-derived and imperfect; content hashes invalidate its cache. The public references contain no NOT_APPLICABLE cases, so independent synthetic negatives are required. See UNRESOLVED_ISSUES.md for remaining proof gaps.
'''
    (docs/'DATASET_AUDIT.md').write_text(audit_doc,encoding='utf-8')
    (ROOT/'tmp/sample_metrics.json').write_text(json.dumps({**m,'run':sample_run,'primary':p},indent=2),encoding='utf-8')
    checkpoint={'tests':count,'test_runtime_seconds':test_seconds,'sample_status':m['status_correct'],
                'sample_exact':m['exact_cases'],'full_accepted':final['resolved'],'full_unresolved':len(final['unresolved'])}
    (ROOT/'tmp/checkpoint.json').write_text(json.dumps(checkpoint,indent=2),encoding='utf-8')
    print(json.dumps(checkpoint,indent=2))


if __name__=='__main__': main()
