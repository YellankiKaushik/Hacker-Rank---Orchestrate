"""Write current, sanitized Phase 2 status from executed measurements only."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def write_reports():
    r=ROOT;v=json.loads((r/'artifacts/phase2-verification.json').read_text());m=json.loads((r/'artifacts/candidate_run_metrics.json').read_text());d=r/'code/docs';e=r/'code/evaluation'
    tests=v['tests'];sample=v['sample_variants']['candidate']['independent_metrics']['counts'];sha=hashlib.sha256((r/'output.csv').read_bytes()).hexdigest()
    summary=f'''# GhostTrace Guard 0.6.0 — current measured status

**C — confirmed incomplete official plans; operational BEST-EFFORT candidate. Not fully contract-compliant or upload-ready.**

R04 authorization and R05 compliant-label contradictions are repaired. {tests['passed']} tests pass, {tests['failed']} fail, {tests['skipped']} skip. The original Phase 1 three counterexamples now produce INCOMPLETE with REPORT_EXPOSED_PII/REDACT_RECORD/VERIFY_RECORD_REDACTED, and two NOT_APPLICABLE empty plans. New real-source tests independently force both primary/reviewer parsers wrong and verify original-value vetoes still reject them.

Candidate rows {v['candidate_rows']}/518; statuses {v['statuses']}. Shared strict acceptances {v['strict_accepted']}; uncertain COMPLETE {v['uncertain_complete']}, uncertain INCOMPLETE {v['uncertain_incomplete']}. These acceptances are bounded implementation checks, not an independent semantic certificate.

Independent sample status {sample['status_correct']}/32; exact ordered cases {sample['exact_cases']}/32; precision {sample['step_matches']}/{sample['predicted_steps']}, recall {sample['step_matches']}/{sample['reference_steps']}. No sample accuracy gain or hidden score is claimed. Output hash remains `{sha}`: the demonstrated defects were on authored synthetic inputs, and their fixes do not change supplied-corpus predictions.

Official-plan gate FAIL for exactly case_479, case_503 and case_55. First two lack attachment exclusivity proof and emit verification only; case_55 lacks target restore permission and emits []. No dummy phase, invented ownership, permission or changed status was used to evade the contract. All 90 uncertain COMPLETE decisions and the three detailed plan decision records are in PHASE2_EVIDENCE_REVIEW.md. A bounded explicit-selector hypothesis recovered zero new links. No repeated blind scans or future inference were used.

Independent checker `python code/independent_contract.py` reports every invalid case and never waives phases for candidate mode. Separate gates: SHAPE_VALID PASS; EMITTED_CITATIONS_VALID PASS within source-parser scope; COMPLETE_PLAN_CONTRACT_VALID FAIL; STRICT_EVIDENCE_PROOF_VALID FAIL. The standalone schema checker does not itself certify source semantics.

GhostGuard independence: original authorization vetoes, raw structured identifier witnesses, positive-readback contradictions, original control/retention/ownership invariants are separate from primary intent/state/policy functions. SQL/JSON/media extraction, identity graph and some policy semantics remain shared. No second full inference oracle is claimed. Per-record locators prevent unrelated neighboring rows from contributing direct identifiers. Typed readback subject_reference selectors are distinguished from persisted analytics user_id/customer_reference fields; tombstones may retain permitted stable references.

Default strict mode withholds output on unresolved cases. Explicit candidate mode atomically writes all 518 rows with a separate uncertainty report. Local OCR + deterministic inference uses zero LLM calls/tokens/API cost; optional AI remains bounded and is not forced for metrics. OCR requires Windows English OCR outside restrictive sandbox contexts, or separately installed tesseract English on other platforms. Non-Windows fidelity is not verified.

Source ZIP and clean-extraction verification are recorded in FINAL_RELEASE_RECORD.md after packaging. Root log is append-only/private. Private staging may contain a PENDING PRIVACY REVIEW transcript copy; no active trace is exported and no fake/empty agent-trace.zip is created. Close all contributing sessions/applications before trace staging. No HackerRank upload or interview was performed.
'''
    (d/'IMPLEMENTATION_STATUS.md').write_text(summary,encoding='utf-8')
    # Supersede historical notes without disguising their prior measurements.
    for name in ('SOURCE_REPAIR_REPORT.md','RECOVERY_AUDIT.md','TARGETED_ACCURACY_REVIEW.md','EXACT_CASE_AUDIT.md'):
        p=d/name;old=p.read_text(encoding='utf-8');notice='> CURRENT PHASE 2 STATUS: see IMPLEMENTATION_STATUS.md and PHASE2_EVIDENCE_REVIEW.md. Historical checkpoint text below is superseded: current classification C; 154 tests; three invalid official plans, 415 shared strict acceptances/103 uncertain. R04/R05 fixed on authored tests; no supplied-corpus accuracy gain.\n\n'
        if not old.startswith('> CURRENT PHASE 2 STATUS:'):p.write_text(notice+old,encoding='utf-8')
    p=d/'UNRESOLVED_ISSUES.md';old=p.read_text(encoding='utf-8');p.write_text(summary+'\n## Per-case diagnostics from the final dataset run\n\n'+old,encoding='utf-8')
    evaluation='# Phase 2 measured evaluation — current release\n\n'+summary.split('Independent checker')[0]
    evaluation+='## Independent all-32 scoring and reviewer ablation\n\n| Metric | Primary | Strict GhostGuard | Candidate |\n|---|---|---|---|\n'
    variants=[v['sample_variants'][k]['independent_metrics']['counts'] for k in ('primary','strict','candidate')]
    for label,key in [('Status correct /32','status_correct'),('Exact ordered cases /32','exact_cases'),('Ordered sequence correct /32','sequence_correct'),('Padded field matches','field_matches'),('Field denominator','field_total'),('Exact step matches','step_matches'),('Predicted steps','predicted_steps'),('Reference steps','reference_steps'),('Citation matches','citation_agreement'),('Cited predicted steps','cited_steps'),('Missing resources','missing_resources'),('Extra resources','extra_resources'),('Missing operations','missing_operations'),('Extra operations','extra_operations')]:
        evaluation+='| '+label+' | '+' | '.join(str(x[key]) for x in variants)+' |\n'
    evaluation+='\nAll 32 references remain in every denominator; unresolved predictions count as failures. Public samples contain 10 COMPLETE, 22 INCOMPLETE and zero NOT_APPLICABLE. Step precision/recall use multiset intersection of exact seven-field tuples including step_no/citation. Field agreement is position-aligned and padded to max array length. Sequence compares ordered phase/operation/system/resource. Citation agreement aligns scope/operation and is not a truth score. References are read only after inference; independent_score imports neither Engine nor production validators. Candidate 917/1365 fields, 57/58 citation agreement, 36/3 missing/extra resources and 40/5 operations reproduce the baseline. Primary/strict/candidate runtime seconds: '+str([v['sample_variants'][k]['runtime_seconds'] for k in ('primary','strict','candidate')])+'.\n'
    evaluation+='''
## Independently authored cases and failures/improvements

1. Negated authorization and informational questions with deletion vocabulary: real JSON source/Engine/GhostGuard must yield NOT_APPLICABLE and []. Positive directives and legal-retention exceptions remain authorized. Tentative requests abstain.
2. REDACTED tombstone with exposed email/phone/nested fields must be INCOMPLETE and redact; stable internal user ID alone may remain. ANONYMIZED analytics with attributable stable ID must anonymize.
3. Deliberately correlated wrong parser states: original raw fields/control booleans/positive readbacks must veto false compliance/absence even when both parser passes agree.
4. Neighboring unrelated records cannot contaminate target identifiers. Incomplete-plan checker reports all invalid rows, including verification-only and empty plans.
5. Existing 140 regressions remain, including SQL/path safety, replicas/future captures, unknown ownership, legal holds, retained records, citation mutation and atomic writes. Fourteen new test methods extend them; subcases are not inflated into separate passing-test counts.

An early over-restrictive English rule missed procedural deletion requests and a past deletion continuation. General syntax rules plus positive regression cases corrected it; final sample metrics returned to 29/32 and 8/32. An original-control invariant initially applied present-state requirements to future verification of an ACTIVE process; this was corrected to distinguish planned checks from current compliance, with a regression assertion. No unsafe policy safeguards were weakened.

The old 9/32 exact baseline lost case_13 when unsupported attachment exclusivity was removed. That safety correction remains; it is not reversed to chase reference agreement. R04/R05 fix demonstrated general defects without claiming supplied-corpus gains. Final plan failures are case_479/503/55; 90 uncertain COMPLETE plus 13 uncertain INCOMPLETE remain. No hidden-answer accuracy, leaderboard score or comprehensive independent semantic proof is asserted.
'''
    (e/'evaluation_report.md').write_text(evaluation,encoding='utf-8')
    (e/'usage_report.md').write_text(f'''# Final 518-case inference usage — Phase 2

Final root output SHA-256 `{sha}`. Rows 518; shared strict acceptances {v['strict_accepted']}; uncertain {v['uncertain_complete']+v['uncertain_incomplete']}. Root-generation runtime {m['runtime_seconds']:.4f} seconds, warm cache. Two fresh-process reproducibility runtimes {[x['runtime_seconds'] for x in v['fresh_processes']]} seconds are verification runs, not silently combined production tokens.

| Final inference provider/model | Calls | Input | Output | Total tokens | Estimated API USD |
|---|---:|---:|---:|---:|---:|
| No language model invoked | 0 | 0 | 0 | 0 | 0.00 |
| Overall final 518-case run | 0 | 0 | 0 | 0 | 0.00 |

Average tokens/request 0/518=0. Average API cost/request $0/518=$0. No price/model is invented. Windows.Media.Ocr performs local screenshot extraction and exposes no model ID/token meter; pypdf 6.10.0 extracts PDF text. Local hardware/electricity/OCR compute cost and Codex development usage/cost are NOT MEASURED. No LLM call was forced to manufacture AI participation.

Historical development, separate from final inference: Ollama gemma4:e4b intent experiment 9 calls, 1305 input/181 output; source-review experiment 2 calls, 1240 input/1536 output (zero accepted batches); later authored integration experiment 2 calls, 309 input/49 output. Named historical experiments sum to 13 calls, 2854 input, 1766 output, 4620 tokens and zero API fees; this is not all engineering usage. These saved experiments were not rerun in Phase 2; transport-denied attempts and mock tests are not successful model calls. The temporary-suspension fixture is now deterministic, so prior experiment behavior must not be presented as current required model participation. Optional intent AI retains schema/quote/context/budget safeguards but has no measured full-dataset benefit. No rejected cloud credential was retried.
''',encoding='utf-8')
    old=(r/'README.md').read_text(encoding='utf-8');original=old[old.index('## Ghost Data Still Exists'):]
    readme='''# GhostTrace Guard 0.6.0 — HackerRank Orchestrate October 2026

**BEST-EFFORT / NOT FULLY VALIDATED — classification C.** The CLI runs, but three INCOMPLETE plans (case_479, case_503, case_55) fail the official plan contract. Candidate 518/518, shared strict acceptances 415, uncertainty 103 (90 COMPLETE/13 INCOMPLETE). Public candidate 29/32 statuses, 8/32 exact plans; precision 107/158 and recall 107/193. R04/R05 repaired; 154 tests pass. See code/docs/IMPLEMENTATION_STATUS.md and mandatory code/evaluation/ reports.

## Clean extraction and evaluator run

Extract code.zip into a new directory. Place unchanged participant dataset/ beside code/ and root README.md. Install Python 3.12+ and the platform OCR dependency, then from the extraction root:

```text
python -m venv .venv
.venv/Scripts/python -m pip install -r code/requirements.txt
.venv/Scripts/python -m unittest discover -s code/tests -v
.venv/Scripts/python code/main.py --mode candidate
.venv/Scripts/python code/independent_contract.py
```

On macOS/Linux replace .venv/Scripts/python with .venv/bin/python. Windows English OCR uses Windows.Media.Ocr and needs the English language pack plus file-access permissions; restrictive sandboxes may deny it. Other platforms require separately installed tesseract and English data. No warm OCR cache is supplied. Non-Windows extraction fidelity remains unverified.

The explicit candidate command atomically creates root output.csv and a separate uncertainty report. The independent checker currently exits nonzero and lists all three invalid plans: this is an expected honest failure, not an installation error. Default `python code/main.py` is strict and refuses output replacement with 103 unresolved cases. Never interpret all-row candidate coverage as full proof.

For an external dataset or isolated outputs use --dataset PATH, --requests PATH, --output PATH, --cache-dir PATH, --metrics-path PATH and --uncertainty-report PATH. Main paths default relative to extracted source root, not the current shell directory. `code/validate_candidate.py` performs shared source/identity/policy checks of emitted claims; `code/independent_contract.py` is independent CSV/JSON/plan validation; `code/validate_output.py` requires strict semantic acceptance. The latter currently rejects the candidate. No sample answers enter inference.

## Implementation and optional configuration

Deterministic investigation, dated identifiers/relations, heterogeneous evidence, policy, replicas and bounded source review run locally. Original-value reviewer vetoes are independent of primary intent/state/policy functions; schemas, extraction and some relationships remain shared. See code/CONFIGURATION.md for optional AI examples and limits. Final inference uses zero LLM calls/tokens/API fees; local OCR is real extraction. AI cannot emit resource IDs or steps. Unknown evidence never authorizes inventing a relation or action. Output/log/traces/staging remain private.

## Developer release commands

In a full development checkout with saved local diagnostic checkpoints (not the minimal evaluator workflow), code/evaluation/generate_reports.py, phase2_review.py, phase2_validate.py and phase2_reports.py regenerate measurements/docs. code/release_check.py rebuilds and checks the ZIP; it writes artifacts and reports failed semantic gates honestly. code/package_submission.py also rebuilds code.zip. These are maintenance commands with side effects/checkpoint dependencies, not prerequisites for main.py inference. Do not run them to overwrite a frozen release without a checkpoint.

Finish contributing sessions and quit apps before staging/redacting structured traces under agent_trace_instructions.md. No active session is packaged as complete. Private log originals remain append-only; any staged copy is separately reviewed. No HackerRank upload or interview is performed automatically.

The original official starter guidance follows; the measured release limits above supersede old implementation-readiness claims.

'''
    (r/'README.md').write_text(readme+original,encoding='utf-8')
    trace=d/'TRACE_FINALIZATION.md';text=trace.read_text(encoding='utf-8');notice='> PHASE 2 ADDENDUM — current session also contains the Phase 1 audit and Phase 2 repairs. Include the verified original build rollout and this audit/repair rollout after both finish and applications close. The older one-session example below is incomplete for the final release. No active trace export, fake ZIP or automatic app closure occurs. Staged log copies remain PENDING PRIVACY REVIEW until human review.\n\n'
    if not text.startswith('> PHASE 2 ADDENDUM'):trace.write_text(notice+text,encoding='utf-8')
    print('Updated current README, implementation, unresolved, evaluation, usage and trace documentation from executed results.')
if __name__=='__main__':write_reports()
