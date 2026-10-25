"""Measured source-repair checkpoint; historical comparisons never enter inference."""
import csv
import json
from pathlib import Path


def generate(root,full,sample,index):
    current=sample['candidate']; docs=root/'code/docs'
    prior=root/'artifacts/baseline-5b9a098'
    baseline=json.loads((prior/'candidate_run_metrics.json').read_text()) if (prior/'candidate_run_metrics.json').exists() else None
    new_ids=sorted({u['case_id'] for u in full['unresolved']}-
                   {u['case_id'] for u in baseline['unresolved']}) if baseline else []
    from ghosttrace.policy import attachment_ownership
    from ghosttrace.loader import read_csv
    from ghosttrace.models import timestamp
    cutoffs={c['case_id']:timestamp(c['audit_at']) for c in read_csv(root/'dataset/deletion_requests.csv')}
    ownership_notes='\n## Unresolved attachment policy conditions\n\nAssociation and observed existence are verified; exclusive ownership is not. These omissions prevent an unsupported DELETE and lower accepted coverage.\n\n| Case | Resource | Admitted evidence examined | Missing fact, impact and next action |\n|---|---|---|---|\n'
    for issue in full['uncertain_cases']:
        for system,resource in issue['omitted_obligations']:
            observations=[f for f in index.by_resource[(system,resource)] if f.category=='SUPPORT_ATTACHMENT'
                          and f.admissible(cutoffs[issue['case_id']])
                          and attachment_ownership(f.data)=='UNKNOWN']
            if observations:
                sources=', '.join(sorted({f.source for f in observations}))
                ownership_notes+=f"| {issue['case_id']} | {system}/{resource} | {sources} | Sole/shared ownership unresolved; no attachment deletion emitted. Obtain an explicit cutoff-admissible ownership record, then rerun strict policy review. |\n"
    report=f'''# Source-verified repair checkpoint — 0.5.1

Classification **B: structurally valid with documented semantic uncertainty**. Semantic completeness and official plan validity remain FAIL. No hidden score, accuracy gain or new subject/resource relationship is claimed.

Recoverable pre-edit checkpoint: commit `5b9a0986f06003fb48c643082a8edcfa4b627a99`; local artifacts/baseline-5b9a098 preserves its CSV, ZIP and measurements. Baseline output SHA-256 `edc5a4ea5e0ea8376a6236524fb9eb1049657767c61cb72883fc5fef787ff7f3`; ZIP `e0d1a8da184c0c431d5e4dc45ac03f67bf66db5c6e986dd3dcf8539e59466150`.

## Verified defects repaired

- `ghosttrace/engine.py`, `adapters.py`, `reviewer.py`: partial service inventories cannot prove absence by same-file membership. Only complete physical primary-key captures with supported schema/snapshot metadata, or explicit source query observations, prove negative state. Both timestamps apply. Reviewer checks original bytes/schema, scope, resource selector, category and manifest time independently of Engine's exhaustive flag.
- `ghosttrace/controls.py`, `adapters.py`, `engine.py`: typed restore/config controls accept explicit booleans and numeric/string 0/1. Missing, null, malformed, mutually inconsistent fields and simultaneous conflicting controls remain UNKNOWN. Missing lookup result/count no longer implies ABSENT. A newer invalid control readback cannot inherit an older compliant setting. Mere archive existence never supplies permission.
- `ghosttrace/policy.py`: a singleton shared_subjects list is not exhaustive; only independent explicit exclusivity proves SOLE. Multiple distinct owners prove SHARED, but the supplied attachment rule has no REDACT fallback. Missing/malformed exclusivity proof stays UNKNOWN instead of authorizing deletion. Legal-hold/retention booleans normalize explicit false/0 and true/1. Invalid dates abstain. Supplied expired retention and inactive holds permit the policy's deletion action; active retention is preserved.
- `ghosttrace/intent_resolution.py`, `models.py`, `ai.py`, `candidate.py`, `main.py`, `validate_candidate.py`, `semantic_validation.py`, `validate_output.py`: intent provenance carries decision, method, original text, exact quote, validation and confidence through investigation, review and serialization validation. Optional local/cloud interpretation still requires independent contextual support; quotes alone never authorize deletion. Sidecars add no CSV fields. Unrecognized paraphrases/languages remain a documented abstention; the independent bridge currently understands only two anchored authored paraphrases.
- `adapters.py`, `models.py`, `engine.py`: explicit media panels bound identifier/flow interpretation. Unseparated multiple-subject regions stay UNKNOWN for these state claims. Typed primary/replica roles replace substring topology detection, including regional/read/reporting/failover relations. OCR still lacks general row geometry; this limitation remains open.
- `reviewer.py`: obligations are reparsed from original files before review, independent of the primary facts/token index. The reviewer checks newer source states and remaining physical replicas as well as policy/identity/source validity. Parsers, extraction and policy remain shared; this is stronger independence, not an independent semantic oracle.

## Before and after

| Metric | Preserved baseline | Repaired |
|---|---:|---:|
| Tests passed / failed | 118 / 0 | {sample['tests']} / 0 |
| Primary sample status | 29/32 | {sample['primary']['status_correct']}/32 |
| Strict sample status | 24/32 | {sample['strict']['status_correct']}/32 |
| Candidate sample status | 29/32 | {current['status_correct']}/32 |
| Exact ordered cases / sequences | 9/32 | {current['exact_cases']}/32 |
| Step precision | 114/164 (69.51%) | {current['step_matches']}/{current['predicted_steps']} ({current['step_precision']:.2%}) |
| Step recall | 114/193 (59.07%) | {current['step_matches']}/{current['reference_steps']} ({current['step_recall']:.2%}) |
| Field agreement | 957/1379 (69.40%) | {current['field_matches']}/{current['field_total']} ({current['field_accuracy']:.2%}) |
| Strict accepted | 427/518 | {full['strict_resolved']}/518 |
| Candidate rows | 518/518 | {full['resolved']}/518 |
| Uncertain predictions | 91 | {len(full['uncertain_cases'])} |
| Missing / extra sample resources | 34 / 3 | {current['missing_records']} / {current['extra_records']} |
| Missing / extra sample operations | 34 / 5 | {current['missing_operations']} / {current['extra_operations']} |
| False COMPLETE / INCOMPLETE in public sample | 0 / 3 | {current['false_complete']} / {current['false_incomplete']} |

No regression thresholds were lowered. Exact-match regression remains a FAIL gate. The ownership safety correction removes unsupported attachment deletion triples. It exposes uncertainty rather than inventing sole ownership. No actual-dataset reduction in false COMPLETE has been measured: the prior sample already had zero. Adversarial tests demonstrate that the identified false-absence and control-value pathways now block unsupported COMPLETE.

Newly uncertain full cases compared with preserved local baseline: {', '.join(new_ids) if new_ids else 'see current per-case uncertainty report (baseline comparison unavailable in a clean clone)'}.

## Accuracy recovery investigation and limits

The original 34 missing sample resources comprise 20 account, seven security and seven analytics resources. They remain unproven because selectors/readbacks are missing or captures are later than audit_at. The new attachment omissions additionally lack exclusive ownership. All three source-supported extra resources remain; removing them to fit a reference would hide supported obligations. `EXACT_CASE_AUDIT.md` lists each missing operation, admitted/excluded sources and whether policy proof or identity/state is missing. No numeric suffix, position, neighboring event, fuzzy name, manifest membership or future observation creates a link.

case_55 remains unchanged: cutoff 2026-04-30T11:00:00Z, evidence_32 and activity_4006 prove archive existence/association, not restoration permission. Its empty INCOMPLETE candidate fails strict semantic plan requirements. Current per-case evidence, impact and next action are in `UNRESOLVED_ISSUES.md` and local `artifacts/SUBMISSION_UNCERTAINTY_REPORT.md`.

## New regression scenarios

`tests/test_source_repairs.py` adds 18 methods covering same-file partial decoys; future observations; all six missing/malformed control events; typed flags; latest/simultaneous control conflicts; missing lookup results; singleton/shared/unknown ownership and owner/subject agreement; hold/retention types/expiry; original SQL negative-proof verification; neighboring media panels; typed replica scope; independent obligation recovery after primary fact-list erasure; independent stale-state rejection; positive/negative AI review/export/fresh strict and candidate validation; unsupported/cherry-picked intent rejection; and transcript metadata versus quoted log templates. Existing regression scenarios also pass.
'''
    pipeline=root/'artifacts/intent_pipeline_evaluation.json'
    if pipeline.exists():
        p=json.loads(pipeline.read_text()); u=p['usage']
        report+=f"\n## Live optional AI integration\n\nOllama loopback `{p['requested_model']}` accepted {p['accepted']}/2 authored requests through source review, export and fresh validation. Measured calls {u['successful_calls']}, input {u['input_tokens']}, output {u['output_tokens']}, API USD {u['estimated_cost_usd']:.2f}; wall time {p['seconds']:.3f}s. Both deterministic baselines abstain. Two earlier sandbox-denied transport attempts returned no model response/usage and are separately recorded. No live rejected response became a fact. Mock usage stays out of reports. No dataset accuracy benefit is claimed; final inference uses zero model calls/tokens. Prior experiments remain historical and separately reported.\n"
    report+='''
## Reproduction, source safety and final artifacts

```powershell
& '.\\tmp\\repair-venv\\Scripts\\python.exe' -X utf8 -m unittest discover -s code/tests -v
& '.\\tmp\\repair-venv\\Scripts\\python.exe' -X utf8 code/evaluation/generate_reports.py
& '.\\tmp\\repair-venv\\Scripts\\python.exe' -X utf8 code/release_check.py
```

Release verification separately records original-source and both-cutoff validation, unchanged official inputs/main, clean dependency origin, two fresh processes, deterministic ZIP rebuild, clean extraction/tests/execution and secret scans. Read the executed gates in `artifacts/READINESS.md` and sanitized `FINAL_RELEASE_RECORD.md`; these are not blanket semantic PASS claims. Output/ZIP/log/traces remain local. The final trace archive awaits session completion under the official instructions; no upload was performed.
'''
    (docs/'SOURCE_REPAIR_REPORT.md').write_text(report+ownership_notes,encoding='utf-8')
    for target in ('code/evaluation/evaluation_report.md','code/docs/RECOVERY_AUDIT.md','code/docs/UNRESOLVED_ISSUES.md'):
        destination=root/target
        body=destination.read_text(encoding='utf-8').split('\n## Source repair checkpoint\n',1)[0]
        with destination.open('w',encoding='utf-8') as stream:
            stream.write(body)
            stream.write('\n## Source repair checkpoint\n\nSee SOURCE_REPAIR_REPORT.md for exact defects, the preserved baseline and measured safety-driven regression. Missing attachment exclusivity is an unresolved policy condition; it does not authorize DELETE. General media row geometry and broader ambiguous intent remain limited.\n')
            if target.endswith('UNRESOLVED_ISSUES.md'): stream.write(ownership_notes)
    readme=root/'README.md'; content=readme.read_text(encoding='utf-8')
    marker='## Ghost Data Still Exists\n'
    original=content[content.index(marker):]
    intro=f'''# HackerRank Orchestrate - October 2026

## GhostTrace Guard 0.5.1

**B: structurally valid with documented semantic uncertainty.** Candidate rows {full['resolved']}/518; strict accepted {full['strict_resolved']}; uncertain {len(full['uncertain_cases'])}. Source/citation/time checks validate emitted claims, not missing obligations. The official strict validator rejects the unproven candidate, including case_55's empty plan.

Public sample: primary statuses {sample['primary']['status_correct']}/32, reviewed {sample['strict']['status_correct']}/32, candidate {current['status_correct']}/32; exact candidate {current['exact_cases']}/32. Precision {current['step_precision']:.2%}, recall {current['step_recall']:.2%}. Tests {sample['tests']} passed, zero failed. Safety corrections reduce exact matches from 9 to {current['exact_cases']}; no accuracy gain or hidden score is claimed. See `code/docs/SOURCE_REPAIR_REPORT.md` and mandatory `code/evaluation/evaluation_report.md` / `usage_report.md`.

### Run

Python 3.12+, `pip install -r code/requirements.txt`. Windows English OCR uses Windows.Media.Ocr; other platforms need tesseract English. Provide unchanged participant `dataset/` beside `code/`. No sample answers enter inference. Run from repository root:

```text
python -m unittest discover -s code/tests -v
python code/main.py --mode strict
python code/main.py --mode candidate
python code/validate_candidate.py
python code/validate_output.py
python code/evaluation/generate_reports.py
python code/release_check.py
```

Strict mode preserves existing output when unresolved. Candidate mode writes all rows atomically and local artifacts/SUBMISSION_UNCERTAINTY_REPORT.md. `--dataset`, `--requests`, `--cache-dir`, `--output`, `--metrics-path`, `--uncertainty-report` support isolated runs. The release checker runs two fresh processes, original-source validation and clean ZIP extraction/execution. Hashes and executed gates are recorded in `code/docs/FINAL_RELEASE_RECORD.md`.

### Optional AI and limits

Final 518-case inference uses zero model calls/tokens/API fee. `--ai` enables bounded ambiguous-intent interpretation only. Configure GHOSTTRACE_AI_PROVIDER=ollama and GHOSTTRACE_AI_MODEL for the installed loopback model, or explicit cloud model/prices plus OPENAI_API_KEY. Bounds remain in `ghosttrace/ai.py`. Credentials come only from environment. AI cannot emit IDs or steps. An exact quote and independent contextual validation are mandatory; the bridge currently supports only two anchored authored paraphrases and otherwise abstains. AI runs write an output.intent.json provenance sidecar; both validators accept `--intent-resolutions PATH` and revalidate it against the original requests. No provenance columns are added to CSV. Live end-to-end and historical experiment usage are separate from final inference usage.

Partial inventories never prove absence. Ownership association never proves sole ownership. Missing control/ownership conditions stay UNKNOWN. GhostGuard independently reparses original obligations and chronology; extraction/policy remain shared. Media panels are bounded where explicit; general column-major OCR row reconstruction remains limited. Missing selectors, future-only captures and case_55 restore permission remain unresolved. Three source-supported extra resources remain despite reference omissions.

Output.csv, code.zip, private log.txt and raw traces remain local. Source ZIP excludes datasets, caches, environments, private traces and nested archives. `FINAL_RELEASE_RECORD.md` is excluded to avoid recursive hashes; `code/check_tracked_archive.py` checks ZIP against committed source. Follow `agent_trace_instructions.md` and `code/docs/TRACE_FINALIZATION.md` after ending sessions/closing the app before final trace archival. No HackerRank upload occurred.

The original official starter instructions follow.

'''
    readme.write_text(intro+original,encoding='utf-8')
