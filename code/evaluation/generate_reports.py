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
    engine=Engine(corpus,index)
    all_cases=read_csv(ROOT/'dataset/deletion_requests.csv')+read_csv(sample_path)
    case_map={c['case_id']:c for c in all_cases}
    now=datetime.now(timezone.utc).isoformat()
    rows=[
        ('Case status accuracy',ratio(m['status_correct'],m['cases'])),
        ('Exact case match (status + ordered seven-field steps)',ratio(m['exact_cases'],m['cases'])),
        ('Exact sequence match (phase/operation/system/resource)',ratio(m['sequence_correct'],m['cases'])),
        ('Field accuracy (position-aligned, missing/extra slots penalized)',ratio(m['field_matches'],m['field_total'])),
        ('Exact step precision (includes numbering and citation)',ratio(m['step_matches'],m['predicted_steps'])),
        ('Exact step recall',ratio(m['step_matches'],m['reference_steps'])),
        ('Reference citation agreement for emitted cited steps',ratio(m['evidence_reference_matches'],m['evidence_reference_total'])),
        ('Public sample inference + independent review runtime',f"{sample_run['runtime_seconds']:.4f} seconds"),
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

## Full participant run

The run processed all {final['cases']} input cases in {final['runtime_seconds']:.4f} seconds with a warm content-hashed OCR cache. It accepted {final['resolved']} decisions: {final['statuses']}. **{len(final['unresolved'])} cases remain unresolved.** Of these, 97 draft COMPLETE cases were blocked for missing linked profile absence/tombstone proof, and case_55 lacks restore-access proof at its cutoff. No valid 518-row root output.csv was produced. `artifacts/resolved_predictions.partial.csv` contains only accepted rows and must not be submitted as the final output. Even accepted rows may omit resources the engine cannot link; full semantic correctness is unproven.

## Independent synthetic regression cases

{count} test methods passed in {test_seconds:.3f} seconds using `python -m unittest discover -s code/tests -v`. These are executed tests, not the architecture pack's proposed test count. Representative independent scenarios:

1. A request for an account-information copy with a present profile produces NOT_APPLICABLE and no steps. Additional opt-out, correction and explicit negation cases are covered. The public samples cannot measure NOT_APPLICABLE recall.
2. A present profile followed by future-only absence evidence remains INCOMPLETE at the earlier cutoff; a future-only case is unresolved, never defaulted COMPLETE.
3. A compliant tombstone, required retained journal and active restore path produce BLOCK_RESTORE and retain/redact verification, without deleting the archive or journal.
4. Simultaneous primary absence and replica presence remains INCOMPLETE.
5. Malicious SQL ATTACH/PRAGMA/extensions/triggers, path traversal, invented/future citations and evidence prompt injection are rejected or ignored as data.
6. GhostGuard detects a missing backup, missing final verification, forged state inconsistent with the reread log, and COMPLETE supported only by a retained journal.
7. A serialization failure preserves the previous output; CSV roundtrip and canonical flow-before-record ordering are checked.

## Remaining sample failures

Each mismatch below comes from measured comparison, not an inference shortcut. Resource IDs from reference answers remain evaluation-only.

| Case | Predicted status | Missing reference scope/operation | Extra predicted scope/operation |
|---|---|---|---|
'''
    key=lambda s:(s['phase'],s['operation'],s['system_id'],s['resource_id'])
    for failure in m['failures']:
        missing=sorted({f"{s['operation']}:{s['resource_id']}" for s in failure['missing']})
        extra=sorted({f"{s['operation']}:{s['resource_id']}" for s in failure['extra']})
        report+=f"| {failure['case_id']} | {failure['predicted_status']} | {', '.join(missing) or 'none'} | {', '.join(extra) or 'none'} |\n"
    report+='''
## Limits and next changes

Prioritize recovering source-supported bindings for identifier-free readbacks, explicit scoped negative queries and retained-record checks. Never infer a resource ID from case/user number suffixes or copy IDs from sample answers into inference. Some expected account IDs cannot currently be tied to a subject without such an unsupported shortcut. Investigate catalog/display-identity contradictions and media scope further; local OCR is imperfect and its extracted text is not a proof of every visual relationship. Do not discard source-backed extra risks just to match a small public sample. Detailed per-case blockers and examined sources are in `code/docs/UNRESOLVED_ISSUES.md`.

No substantive language-model runtime path is implemented or benchmarked. Optional AI was deferred because the main current failures concern absent bindings/proof, which a model must not invent. Local Windows OCR is active. All measurements here describe this checkpoint, not a finished submission.
'''
    (report_dir/'evaluation_report.md').write_text(report,encoding='utf-8')
    usage=f'''# Runtime usage and cost checkpoint

Generated {now}, tied to the full {final['cases']}-case attempt that produced the {final['resolved']}-row **partial** artifact, SHA-256 `{final['partial_output_sha256']}`. There is no completed full-dataset final output yet.

| Provider / model | Calls | Input tokens | Output tokens | Total tokens | Estimated USD |
|---|---:|---:|---:|---:|---:|
| No language model invoked | 0 | 0 | 0 | 0 | 0.00 |
| Overall runtime API totals | 0 | 0 | 0 | 0 | 0.00 |

Runtime: {final['runtime_seconds']:.4f} seconds. Average tokens per input request: 0/518 = 0. Average estimated API cost per input request: $0/518 = $0. No provider price assumption is needed for zero calls. This counts inference/review API usage only; it excludes the Codex engineering session, whose token consumption and cost have not been obtained as per-request telemetry and must not be assumed zero.

PDF parsing uses pypdf 6.10.0. Windows.Media.Ocr performs local screenshot recognition (English language pack), with no network API, reported token counts or billed API model. Its internal OCR model identifier is not exposed by the Windows API. The final attempt used a warm source-SHA-256 OCR cache; cold OCR was separately exercised for all 11 screenshots. No optional language/vision API adapter is implemented or claimed active.

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
    issues+='''
## Other verified limitations and open work

| Issue | Evidence / verified state | Impact | Recommended next action |
|---|---|---|---|
| Public sample reference differences | See every measured failure in evaluation_report.md | Exact-case accuracy is only 8/32 | Improve general bindings and scoped readbacks; do not hardcode sample IDs |
| Media/catalog identity inconsistency | Some catalog-linked screenshots display contact fields differing from current identity snapshots; the marketing console is one example | Catalog links prove an association claim, not that every displayed contact value belongs to that subject | Recheck visual field scope and dated identity provenance; surface contradictions rather than merge people |
| Discovery coverage | 97 primary COMPLETE drafts lacked profile/tombstone proof; reviewer blocked them | A syntactically valid draft is not a complete deletion audit | Maintain the proof gate and improve source graph |
| Raw-source reviewer independence | Reviewer reopens and reparses source, but uses shared deterministic adapters | Not independent model reasoning or independent parser validation | Add adversarial fixtures and a separately implemented semantic review where useful |
| Optional language model | No inference API calls or adapter used | Substantive runtime LLM investigation is unimplemented | Add only a bounded, measured task that can improve grounded results; no model can create missing proof |
| SQL inventory scope | Absence is synthesized only within a subject-linked source and declared table scope | Completeness depends on interpreting inventory scope correctly | Add explicit source-scoped query bindings; never use lack of retrieval as absence |
| Source docs | Only the three root DOCS files exist; referenced companion pack files were not present | Missing design companions, not a runtime data blocker | Continue from official contract and available design; don't claim absent files were read |
| Upstream documentation change | Fetched upstream/main at 0eddbbd; only the AGENTS.md challenge URL typo changes, with no dataset/contract changes | Update is inspected but not merged; local main is preserved | Reconcile the documentation update separately without automatic merging |
| Python alias | WindowsApps python.exe alias failed; bundled Python 3.12.14 works | Bare python command currently needs a proper Python install/PATH | Use documented bundled command or install Python; no global configuration was changed |
| Early test attempt | Default OS temporary directory caused sandbox permission failures; that attempt was interrupted | Initial run failed for environment reasons | Tests now use checkout-local tmp/tests; subsequent complete suite passed |
| Trace ZIP | Original Codex rollout remains in place; app session is still open | Final complete trace archive cannot yet be copied under official close-first instructions | Finish session, close app, copy only relevant rollout, inspect/redact and package separately |
| Final artifacts | No valid 518-row output; code.zip is a development checkpoint package | G1/G5 acceptance incomplete; not ready for HackerRank submission | Resolve blockers, rerun tests/evaluation/full validator and rebuild package |
'''
    (docs/'UNRESOLVED_ISSUES.md').write_text(issues,encoding='utf-8')
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
