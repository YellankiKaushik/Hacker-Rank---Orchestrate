# Source-verified repair checkpoint — 0.5.0

Classification **B: structurally valid with documented semantic uncertainty**. Semantic completeness and official plan validity remain FAIL. No hidden score, accuracy gain or new subject/resource relationship is claimed.

Recoverable pre-edit checkpoint: commit `5b9a0986f06003fb48c643082a8edcfa4b627a99`; local artifacts/baseline-5b9a098 preserves its CSV, ZIP and measurements. Baseline output SHA-256 `edc5a4ea5e0ea8376a6236524fb9eb1049657767c61cb72883fc5fef787ff7f3`; ZIP `e0d1a8da184c0c431d5e4dc45ac03f67bf66db5c6e986dd3dcf8539e59466150`.

## Verified defects repaired

- `ghosttrace/engine.py`, `adapters.py`, `reviewer.py`: partial service inventories cannot prove absence by same-file membership. Only complete physical primary-key captures with supported schema/snapshot metadata, or explicit source query observations, prove negative state. Both timestamps apply. Reviewer checks original bytes/schema, scope, resource selector, category and manifest time independently of Engine's exhaustive flag.
- `ghosttrace/controls.py`, `adapters.py`, `engine.py`: typed restore/config controls accept explicit booleans and numeric/string 0/1. Missing, null, malformed, mutually inconsistent fields and simultaneous conflicting controls remain UNKNOWN. Missing lookup result/count no longer implies ABSENT. A newer invalid control readback cannot inherit an older compliant setting. Mere archive existence never supplies permission.
- `ghosttrace/policy.py`: singleton shared_subjects proves one declared owner; multiple owners select redaction. Missing/malformed exclusivity proof stays UNKNOWN instead of authorizing deletion. Legal-hold/retention booleans normalize explicit false/0 and true/1. Invalid dates abstain. Supplied expired retention and inactive holds permit the policy's deletion action; active retention is preserved.
- `ghosttrace/intent_resolution.py`, `models.py`, `ai.py`, `candidate.py`, `main.py`, `validate_candidate.py`, `semantic_validation.py`, `validate_output.py`: intent provenance carries decision, method, original text, exact quote, validation and confidence through investigation, review and serialization validation. Optional local/cloud interpretation still requires independent contextual support; quotes alone never authorize deletion. Sidecars add no CSV fields. Unrecognized paraphrases/languages remain a documented abstention; the independent bridge currently understands only two anchored authored paraphrases.
- `adapters.py`, `models.py`, `engine.py`: explicit media panels bound identifier/flow interpretation. Unseparated multiple-subject regions stay UNKNOWN for these state claims. Typed primary/replica roles replace substring topology detection, including regional/read/reporting/failover relations. OCR still lacks general row geometry; this limitation remains open.
- `reviewer.py`: obligations are reparsed from original files before review, independent of the primary facts/token index. The reviewer checks newer source states and remaining physical replicas as well as policy/identity/source validity. Parsers, extraction and policy remain shared; this is stronger independence, not an independent semantic oracle.

## Before and after

| Metric | Preserved baseline | Repaired |
|---|---:|---:|
| Tests passed / failed | 118 / 0 | 136 / 0 |
| Primary sample status | 29/32 | 27/32 |
| Strict sample status | 24/32 | 22/32 |
| Candidate sample status | 29/32 | 29/32 |
| Exact ordered cases / sequences | 9/32 | 8/32 |
| Step precision | 114/164 (69.51%) | 107/158 (67.72%) |
| Step recall | 114/193 (59.07%) | 107/193 (55.44%) |
| Field agreement | 957/1379 (69.40%) | 917/1365 (67.18%) |
| Strict accepted | 427/518 | 415/518 |
| Candidate rows | 518/518 | 518/518 |
| Uncertain predictions | 91 | 103 |
| Missing / extra sample resources | 34 / 3 | 36 / 3 |
| Missing / extra sample operations | 34 / 5 | 40 / 5 |
| False COMPLETE / INCOMPLETE in public sample | 0 / 3 | 0 / 3 |

No regression thresholds were lowered. Exact-match regression remains a FAIL gate. The ownership safety correction removes unsupported attachment deletion triples. It exposes uncertainty rather than inventing sole ownership. No actual-dataset reduction in false COMPLETE has been measured: the prior sample already had zero. Adversarial tests demonstrate that the identified false-absence and control-value pathways now block unsupported COMPLETE.

Newly uncertain full cases compared with preserved local baseline: case_203, case_263, case_311, case_34, case_359, case_371, case_407, case_419, case_455, case_479, case_503, case_515.

## Accuracy recovery investigation and limits

The original 34 missing sample resources comprise 20 account, seven security and seven analytics resources. They remain unproven because selectors/readbacks are missing or captures are later than audit_at. The new attachment omissions additionally lack exclusive ownership. All three source-supported extra resources remain; removing them to fit a reference would hide supported obligations. `EXACT_CASE_AUDIT.md` lists each missing operation, admitted/excluded sources and whether policy proof or identity/state is missing. No numeric suffix, position, neighboring event, fuzzy name, manifest membership or future observation creates a link.

case_55 remains unchanged: cutoff 2026-04-30T11:00:00Z, evidence_32 and activity_4006 prove archive existence/association, not restoration permission. Its empty INCOMPLETE candidate fails strict semantic plan requirements. Current per-case evidence, impact and next action are in `UNRESOLVED_ISSUES.md` and local `artifacts/SUBMISSION_UNCERTAINTY_REPORT.md`.

## New regression scenarios

`tests/test_source_repairs.py` adds 18 methods covering same-file partial decoys; future observations; all six missing/malformed control events; typed flags; latest/simultaneous control conflicts; missing lookup results; singleton/shared/unknown ownership and owner/subject agreement; hold/retention types/expiry; original SQL negative-proof verification; neighboring media panels; typed replica scope; independent obligation recovery after primary fact-list erasure; independent stale-state rejection; positive/negative AI review/export/fresh strict and candidate validation; unsupported/cherry-picked intent rejection; and transcript metadata versus quoted log templates. Existing regression scenarios also pass.

## Live optional AI integration

Ollama loopback `gemma4:e4b` accepted 2/2 authored requests through source review, export and fresh validation. Measured calls 2, input 309, output 49, API USD 0.00; wall time 18.044s. Both deterministic baselines abstain. Two earlier sandbox-denied transport attempts returned no model response/usage and are separately recorded. No live rejected response became a fact. Mock usage stays out of reports. No dataset accuracy benefit is claimed; final inference uses zero model calls/tokens. Prior experiments remain historical and separately reported.

## Reproduction, source safety and final artifacts

```powershell
& '.\tmp\repair-venv\Scripts\python.exe' -X utf8 -m unittest discover -s code/tests -v
& '.\tmp\repair-venv\Scripts\python.exe' -X utf8 code/evaluation/generate_reports.py
& '.\tmp\repair-venv\Scripts\python.exe' -X utf8 code/release_check.py
```

Release verification separately records original-source and both-cutoff validation, unchanged official inputs/main, clean dependency origin, two fresh processes, deterministic ZIP rebuild, clean extraction/tests/execution and secret scans. Read the executed gates in `artifacts/READINESS.md` and sanitized `FINAL_RELEASE_RECORD.md`; these are not blanket semantic PASS claims. Output/ZIP/log/traces remain local. The final trace archive awaits session completion under the official instructions; no upload was performed.

## Unresolved attachment policy conditions

Association and observed existence are verified; exclusive ownership is not. These omissions prevent an unsupported DELETE and lower accepted coverage.

| Case | Resource | Admitted evidence examined | Missing fact, impact and next action |
|---|---|---|---|
| case_203 | support_platform/support_8903 | evidence_20 | Sole/shared ownership unresolved; no attachment deletion emitted. Obtain an explicit cutoff-admissible ownership record, then rerun strict policy review. |
| case_263 | support_platform/support_5234 | evidence_25 | Sole/shared ownership unresolved; no attachment deletion emitted. Obtain an explicit cutoff-admissible ownership record, then rerun strict policy review. |
| case_311 | support_platform/support_4952 | evidence_29 | Sole/shared ownership unresolved; no attachment deletion emitted. Obtain an explicit cutoff-admissible ownership record, then rerun strict policy review. |
| case_34 | support_platform/support_9538 | evidence_01 | Sole/shared ownership unresolved; no attachment deletion emitted. Obtain an explicit cutoff-admissible ownership record, then rerun strict policy review. |
| case_359 | support_platform/support_2537 | evidence_33 | Sole/shared ownership unresolved; no attachment deletion emitted. Obtain an explicit cutoff-admissible ownership record, then rerun strict policy review. |
| case_371 | support_platform/support_3110 | evidence_34 | Sole/shared ownership unresolved; no attachment deletion emitted. Obtain an explicit cutoff-admissible ownership record, then rerun strict policy review. |
| case_407 | support_platform/support_3802 | evidence_38 | Sole/shared ownership unresolved; no attachment deletion emitted. Obtain an explicit cutoff-admissible ownership record, then rerun strict policy review. |
| case_419 | support_platform/support_2944 | evidence_39 | Sole/shared ownership unresolved; no attachment deletion emitted. Obtain an explicit cutoff-admissible ownership record, then rerun strict policy review. |
| case_455 | support_platform/support_2055 | evidence_43 | Sole/shared ownership unresolved; no attachment deletion emitted. Obtain an explicit cutoff-admissible ownership record, then rerun strict policy review. |
| case_479 | support_platform/support_4665 | evidence_45 | Sole/shared ownership unresolved; no attachment deletion emitted. Obtain an explicit cutoff-admissible ownership record, then rerun strict policy review. |
| case_503 | support_platform/support_2295 | evidence_47 | Sole/shared ownership unresolved; no attachment deletion emitted. Obtain an explicit cutoff-admissible ownership record, then rerun strict policy review. |
| case_515 | support_platform/support_4533 | evidence_48 | Sole/shared ownership unresolved; no attachment deletion emitted. Obtain an explicit cutoff-admissible ownership record, then rerun strict policy review. |
