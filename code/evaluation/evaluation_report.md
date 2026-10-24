# GhostTrace Guard evaluation checkpoint

Generated from local execution at 2026-10-24T17:01:38.841587+00:00. **NOT submission-ready.** No hidden score is known.

## Measured sample results

All 32 public references are evaluated, including unresolved cases as failures. Reference distribution: 10 COMPLETE, 22 INCOMPLETE, 0 NOT_APPLICABLE. References are read only by this evaluator after inference, never by the engine, identity graph, adapters, policy or reviewer.

| Metric | Result |
|---|---|
| Case status accuracy | 24/32 (75.00%) |
| Exact case match (status + ordered seven-field steps) | 9/32 (28.12%) |
| Exact sequence match (phase/operation/system/resource) | 9/32 (28.12%) |
| Field accuracy (position-aligned, missing/extra slots penalized) | 915/1379 (66.35%) |
| Exact step precision (includes numbering and citation) | 114/150 (76.00%) |
| Exact step recall | 114/193 (59.07%) |
| Reference citation agreement for emitted cited steps | 45/46 (97.83%) |
| Public sample inference + independent review runtime | 0.6406 seconds |
| False COMPLETE / false INCOMPLETE among emitted predictions | 0 / 0 |
| Unresolved sample cases (included as failures) | 8 |
| Missing / extra reference resources | 48 / 3 |
| Missing / extra reference scope/operations | 48 / 5 |

The field denominator is seven times the sum of the larger of predicted and reference sequence lengths for each case. Missing predictions receive no matching fields. Step precision/recall uses multiset intersection of exact seven-field objects. Sequence accuracy ignores state and citation but requires exact ordered scope/operations. Reference citation agreement is distinct from source integrity: a valid real citation can differ from the canonical reference. All accepted emitted citations passed source-ID, timestamp and independent raw-source support checks; this is not a semantic accuracy guarantee.

## Baseline and review comparison

| Variant | Correct statuses | Exact cases | Unresolved samples | Seconds |
|---|---|---|---|---|
| Primary, no independent release review | 29/32 | 9/32 | 3 | 0.6345 |
| Source review and COMPLETE proof gate | 24/32 | 9/32 | 8 | 0.6406 |

Initial measured prototype: 25/32 statuses, 6/32 exact cases. Adding pipe-format logs, completed analytics readbacks, trace correlation and indirect erasure language improved the primary prototype to 29/32 statuses and 8/32 exact cases. Removing document-wide subject joins prevented unrelated retained records contaminating multiple cases. **Review does not improve public-sample status accuracy**: it withholds five otherwise correct reference statuses because the engine lacks profile/tombstone linkage proof. It is retained as a hard safety/uncertainty gate, not marketed as an accuracy improvement. There is no LLM reviewer; raw-source retrieval is independent, but parsing utilities are shared with ingestion.

Continuation from commit 01beaa1: explicit `source_resource_id` traversal, dated owner-system metadata and a scoped physical-table query recovered one complete sample verification sequence. Exact cases improved from **8/32 to 9/32**, and primary exact cases from 8/32 to 9/32. The reviewer still withholds 5 primary statuses that agree with public references: case_21, case_25, case_26, case_27, case_28. These are benchmark false rejections/abstentions with a concrete missing-profile-link reason, not measured LLM-review gains. Current reviewer rejection categories: `{'MISSING_EVIDENCE': 3, 'MISSING_PROFILE_LINK_OR_PROOF': 5}`. Missing operations above exclude differences due only to numbering or citation, unlike exact-object metrics.

## Full participant run

The run processed all 518 input cases in 4.5857 seconds with a warm content-hashed OCR cache. It accepted 420 decisions: {'INCOMPLETE': 354, 'COMPLETE': 56, 'NOT_APPLICABLE': 10}. **98 cases remain unresolved.** Of these, 97 draft COMPLETE cases were blocked for missing linked profile absence/tombstone proof, and case_55 lacks restore-access proof at its cutoff. No valid 518-row root output.csv was produced. `artifacts/resolved_predictions.partial.csv` contains only accepted rows and must not be submitted as the final output. Even accepted rows may omit resources the engine cannot link; full semantic correctness is unproven.

Recovered from the archived 98-case blocker set: **0**. Newly blocked: []. The unchanged blocked cluster is a measured result; no unsupported rows were filled. Targeted re-investigation reread 33 source files and reused 65 source-view caches after verifying source hashes. Each challenged case has at most one retry and four reread sources. Rejection categories for this full attempt: `{'MISSING_PROFILE_LINK_OR_PROOF': 97, 'MISSING_EVIDENCE': 1}`. See RECOVERY_AUDIT.md for all per-case candidate/link/cutoff evidence.

## Independent synthetic regression cases

91 test methods passed in 0.074 seconds using `python -m unittest discover -s code/tests -v`. These are executed tests, not the architecture pack's proposed test count. Representative independent scenarios:

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
| case_01 | UNRESOLVED | VERIFY_RECORD_ABSENT:account_001 | none |
| case_02 | UNRESOLVED | VERIFY_RECORD_ABSENT:account_002 | none |
| case_03 | COMPLETE | VERIFY_RECORD_ANONYMIZED:analytics_9406 | none |
| case_04 | UNRESOLVED | VERIFY_RECORD_ABSENT:account_004, VERIFY_RECORD_ANONYMIZED:analytics_901 | none |
| case_07 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_007 | DELETE_RECORD:object_19, REPORT_REMAINING_RECORD:object_19, VERIFY_RECORD_ABSENT:object_19 |
| case_08 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_008 | none |
| case_09 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_3960, VERIFY_RECORD_PRESENT:audit_record_4902 | none |
| case_10 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_010 | none |
| case_17 | INCOMPLETE | none | VERIFY_RECORD_ABSENT:account_6523, VERIFY_RECORD_REDACTED:tombstone_17 |
| case_18 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_5521, VERIFY_RECORD_PRESENT:audit_record_6645 | none |
| case_20 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_5037, VERIFY_RECORD_PRESENT:audit_record_5569 | none |
| case_21 | UNRESOLVED | VERIFY_RECORD_ABSENT:account_6440, VERIFY_RECORD_ANONYMIZED:analytics_5335, VERIFY_RECORD_PRESENT:audit_record_3737 | none |
| case_22 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_4990 | none |
| case_23 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_410, VERIFY_RECORD_PRESENT:audit_record_4128 | none |
| case_24 | INCOMPLETE | VERIFY_RECORD_PRESENT:audit_record_7095 | none |
| case_25 | UNRESOLVED | VERIFY_RECORD_ABSENT:account_3136, VERIFY_RECORD_ANONYMIZED:analytics_1895, VERIFY_RECORD_PRESENT:audit_record_451 | none |
| case_26 | UNRESOLVED | VERIFY_DATA_FLOW_DISABLED:data_flow_6244, VERIFY_RECORD_ABSENT:account_5684, VERIFY_RECORD_ANONYMIZED:analytics_4566, VERIFY_RECORD_PRESENT:audit_record_5416, VERIFY_RECORD_REDACTED:support_4715, VERIFY_RESTORE_BLOCKED:backup_3120 | none |
| case_27 | UNRESOLVED | VERIFY_DATA_FLOW_DISABLED:data_flow_2295, VERIFY_RECORD_ABSENT:account_3866, VERIFY_RECORD_ANONYMIZED:analytics_4574, VERIFY_RECORD_PRESENT:audit_record_3830, VERIFY_RECORD_REDACTED:support_4707, VERIFY_RESTORE_BLOCKED:backup_5970 | none |
| case_28 | UNRESOLVED | VERIFY_DATA_FLOW_DISABLED:data_flow_2337, VERIFY_RECORD_ABSENT:account_5482, VERIFY_RECORD_ANONYMIZED:analytics_6077, VERIFY_RECORD_PRESENT:audit_record_9265, VERIFY_RECORD_REDACTED:support_2351, VERIFY_RESTORE_BLOCKED:backup_838 | none |
| case_29 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_7012, VERIFY_RECORD_PRESENT:audit_record_3954 | none |
| case_30 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_4163, VERIFY_RECORD_PRESENT:audit_record_1707 | none |
| case_31 | COMPLETE | VERIFY_RECORD_ABSENT:account_4857 | none |
| case_32 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_8858 | none |

## Limits and next changes

Prioritize recovering source-supported bindings for identifier-free readbacks, explicit scoped negative queries and retained-record checks. Never infer a resource ID from case/user number suffixes or copy IDs from sample answers into inference. Some expected account IDs cannot currently be tied to a subject without such an unsupported shortcut. Investigate catalog/display-identity contradictions and media scope further; local OCR is imperfect and its extracted text is not a proof of every visual relationship. Do not discard source-backed extra risks just to match a small public sample. Detailed per-case blockers and examined sources are in `code/docs/UNRESOLVED_ISSUES.md`.

The optional Responses-based intent path is implemented, bounded and tested with mocked transport. A real read-only model discovery check returned HTTP 401: no usable live model was verified, and no live inference call was made. It remains disabled by default and has no measured live accuracy benefit. Local Windows OCR is active. All measurements here describe this checkpoint, not a finished submission.

Reproduction: `python -m unittest discover -s code/tests -v`, `python code/evaluation/generate_reports.py`, `python code/main.py`, `python code/validate_output.py`, `python code/package_submission.py`. The last prediction gates remain failing while unresolved cases exist. Use the bundled interpreter command in README on this workstation.

Controlled intent fixtures: 13/13 unambiguous decisions correct, plus the expected abstention fixture. Live AI quality: **NOT VERIFIED** (HTTP 401). No mock token counts enter runtime usage totals.
