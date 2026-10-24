# GhostTrace Guard evaluation checkpoint

Generated from local execution at 2026-10-24T15:58:12.183564+00:00. **NOT submission-ready.** No hidden score is known.

## Measured sample results

All 32 public references are evaluated, including unresolved cases as failures. Reference distribution: 10 COMPLETE, 22 INCOMPLETE, 0 NOT_APPLICABLE. References are read only by this evaluator after inference, never by the engine, identity graph, adapters, policy or reviewer.

| Metric | Result |
|---|---|
| Case status accuracy | 24/32 (75.00%) |
| Exact case match (status + ordered seven-field steps) | 8/32 (25.00%) |
| Exact sequence match (phase/operation/system/resource) | 8/32 (25.00%) |
| Field accuracy (position-aligned, missing/extra slots penalized) | 906/1372 (66.03%) |
| Exact step precision (includes numbering and citation) | 112/148 (75.68%) |
| Exact step recall | 112/193 (58.03%) |
| Reference citation agreement for emitted cited steps | 45/46 (97.83%) |
| Public sample inference + independent review runtime | 0.6229 seconds |

The field denominator is seven times the sum of the larger of predicted and reference sequence lengths for each case. Missing predictions receive no matching fields. Step precision/recall uses multiset intersection of exact seven-field objects. Sequence accuracy ignores state and citation but requires exact ordered scope/operations. Reference citation agreement is distinct from source integrity: a valid real citation can differ from the canonical reference. All accepted emitted citations passed source-ID, timestamp and independent raw-source support checks; this is not a semantic accuracy guarantee.

## Baseline and review comparison

| Variant | Correct statuses | Exact cases | Unresolved samples | Seconds |
|---|---|---|---|---|
| Primary, no independent release review | 29/32 | 8/32 | 3 | 0.6975 |
| Source review and COMPLETE proof gate | 24/32 | 8/32 | 8 | 0.6229 |

Initial measured prototype: 25/32 statuses, 6/32 exact cases. Adding pipe-format logs, completed analytics readbacks, trace correlation and indirect erasure language improved the primary prototype to 29/32 statuses and 8/32 exact cases. Removing document-wide subject joins prevented unrelated retained records contaminating multiple cases. **Review does not improve public-sample status accuracy**: it withholds five otherwise correct reference statuses because the engine lacks profile/tombstone linkage proof. It is retained as a hard safety/uncertainty gate, not marketed as an accuracy improvement. There is no LLM reviewer; raw-source retrieval is independent, but parsing utilities are shared with ingestion.

## Full participant run

The run processed all 518 input cases in 5.9706 seconds with a warm content-hashed OCR cache. It accepted 420 decisions: {'INCOMPLETE': 354, 'COMPLETE': 56, 'NOT_APPLICABLE': 10}. **98 cases remain unresolved.** Of these, 97 draft COMPLETE cases were blocked for missing linked profile absence/tombstone proof, and case_55 lacks restore-access proof at its cutoff. No valid 518-row root output.csv was produced. `artifacts/resolved_predictions.partial.csv` contains only accepted rows and must not be submitted as the final output. Even accepted rows may omit resources the engine cannot link; full semantic correctness is unproven.

## Independent synthetic regression cases

52 test methods passed in 0.046 seconds using `python -m unittest discover -s code/tests -v`. These are executed tests, not the architecture pack's proposed test count. Representative independent scenarios:

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
| case_01 | UNRESOLVED | VERIFY_RECORD_ABSENT:account_001 | none |
| case_02 | UNRESOLVED | VERIFY_RECORD_ABSENT:account_002 | none |
| case_03 | COMPLETE | VERIFY_RECORD_ANONYMIZED:analytics_9406 | none |
| case_04 | UNRESOLVED | VERIFY_RECORD_ABSENT:account_004, VERIFY_RECORD_ANONYMIZED:analytics_901 | none |
| case_06 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_006, VERIFY_RECORD_ABSENT:search_001 | VERIFY_RECORD_ABSENT:search_001 |
| case_07 | INCOMPLETE | DELETE_RECORD:support_001, REPORT_REMAINING_RECORD:support_001, VERIFY_RECORD_ABSENT:account_007, VERIFY_RECORD_ABSENT:support_001 | DELETE_RECORD:object_19, DELETE_RECORD:support_001, REPORT_REMAINING_RECORD:object_19, REPORT_REMAINING_RECORD:support_001, VERIFY_RECORD_ABSENT:object_19, VERIFY_RECORD_ABSENT:support_001 |
| case_08 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_008, VERIFY_RECORD_ABSENT:export_001 | VERIFY_RECORD_ABSENT:export_001 |
| case_09 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_3960, VERIFY_RECORD_PRESENT:audit_record_4902, VERIFY_RESTORE_BLOCKED:backup_4978 | VERIFY_RESTORE_BLOCKED:backup_4978 |
| case_10 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_010, VERIFY_RECORD_ABSENT:support_002 | VERIFY_RECORD_ABSENT:support_002 |
| case_17 | INCOMPLETE | VERIFY_RECORD_PRESENT:audit_record_1797, VERIFY_RESTORE_BLOCKED:backup_3245 | VERIFY_RECORD_ABSENT:account_6523, VERIFY_RECORD_PRESENT:audit_record_1797, VERIFY_RESTORE_BLOCKED:backup_3245 |
| case_18 | INCOMPLETE | VERIFY_DATA_FLOW_DISABLED:data_flow_4890, VERIFY_RECORD_ABSENT:account_5521, VERIFY_RECORD_ABSENT:search_4013, VERIFY_RECORD_ANONYMIZED:analytics_037, VERIFY_RECORD_PRESENT:audit_record_6645, VERIFY_RECORD_REDACTED:support_5569 | VERIFY_DATA_FLOW_DISABLED:data_flow_4890, VERIFY_RECORD_ABSENT:search_4013, VERIFY_RECORD_ANONYMIZED:analytics_037, VERIFY_RECORD_REDACTED:support_5569 |
| case_20 | INCOMPLETE | VERIFY_DATA_FLOW_DISABLED:data_flow_1770, VERIFY_RECORD_ABSENT:account_5037, VERIFY_RECORD_ABSENT:search_4262, VERIFY_RECORD_PRESENT:audit_record_5569 | VERIFY_DATA_FLOW_DISABLED:data_flow_1770, VERIFY_RECORD_ABSENT:search_4262 |
| case_21 | UNRESOLVED | VERIFY_RECORD_ABSENT:account_6440, VERIFY_RECORD_ANONYMIZED:analytics_5335, VERIFY_RECORD_PRESENT:audit_record_3737 | none |
| case_22 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_4990, VERIFY_RECORD_ABSENT:search_8911, VERIFY_RECORD_ANONYMIZED:analytics_4440, VERIFY_RECORD_PRESENT:audit_record_3482 | VERIFY_RECORD_ABSENT:search_8911, VERIFY_RECORD_ANONYMIZED:analytics_4440, VERIFY_RECORD_PRESENT:audit_record_3482 |
| case_23 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_410, VERIFY_RECORD_ABSENT:export_7364, VERIFY_RECORD_ABSENT:search_898, VERIFY_RECORD_PRESENT:audit_record_4128 | VERIFY_RECORD_ABSENT:export_7364, VERIFY_RECORD_ABSENT:search_898 |
| case_24 | INCOMPLETE | VERIFY_RECORD_PRESENT:audit_record_7095 | none |
| case_25 | UNRESOLVED | VERIFY_RECORD_ABSENT:account_3136, VERIFY_RECORD_ANONYMIZED:analytics_1895, VERIFY_RECORD_PRESENT:audit_record_451 | none |
| case_26 | UNRESOLVED | VERIFY_DATA_FLOW_DISABLED:data_flow_6244, VERIFY_RECORD_ABSENT:account_5684, VERIFY_RECORD_ANONYMIZED:analytics_4566, VERIFY_RECORD_PRESENT:audit_record_5416, VERIFY_RECORD_REDACTED:support_4715, VERIFY_RESTORE_BLOCKED:backup_3120 | none |
| case_27 | UNRESOLVED | VERIFY_DATA_FLOW_DISABLED:data_flow_2295, VERIFY_RECORD_ABSENT:account_3866, VERIFY_RECORD_ANONYMIZED:analytics_4574, VERIFY_RECORD_PRESENT:audit_record_3830, VERIFY_RECORD_REDACTED:support_4707, VERIFY_RESTORE_BLOCKED:backup_5970 | none |
| case_28 | UNRESOLVED | VERIFY_DATA_FLOW_DISABLED:data_flow_2337, VERIFY_RECORD_ABSENT:account_5482, VERIFY_RECORD_ANONYMIZED:analytics_6077, VERIFY_RECORD_PRESENT:audit_record_9265, VERIFY_RECORD_REDACTED:support_2351, VERIFY_RESTORE_BLOCKED:backup_838 | none |
| case_29 | INCOMPLETE | VERIFY_DATA_FLOW_DISABLED:data_flow_3827, VERIFY_RECORD_ABSENT:account_7012, VERIFY_RECORD_ABSENT:search_1993, VERIFY_RECORD_ANONYMIZED:analytics_5208, VERIFY_RECORD_PRESENT:audit_record_3954, VERIFY_RECORD_REDACTED:support_5281 | VERIFY_DATA_FLOW_DISABLED:data_flow_3827, VERIFY_RECORD_ABSENT:search_1993, VERIFY_RECORD_ANONYMIZED:analytics_5208, VERIFY_RECORD_REDACTED:support_5281 |
| case_30 | INCOMPLETE | VERIFY_DATA_FLOW_DISABLED:data_flow_8524, VERIFY_RECORD_ABSENT:account_4163, VERIFY_RECORD_ABSENT:search_9359, VERIFY_RECORD_ANONYMIZED:analytics_3697, VERIFY_RECORD_PRESENT:audit_record_1707, VERIFY_RECORD_REDACTED:support_6477 | VERIFY_DATA_FLOW_DISABLED:data_flow_8524, VERIFY_RECORD_ABSENT:search_9359, VERIFY_RECORD_ANONYMIZED:analytics_3697, VERIFY_RECORD_REDACTED:support_6477 |
| case_31 | COMPLETE | VERIFY_RECORD_ABSENT:account_4857, VERIFY_RECORD_PRESENT:audit_record_6909, VERIFY_RECORD_REDACTED:tombstone_440 | VERIFY_RECORD_PRESENT:audit_record_6909, VERIFY_RECORD_REDACTED:tombstone_440 |
| case_32 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_8858, VERIFY_RECORD_PRESENT:audit_record_7068, VERIFY_RECORD_REDACTED:tombstone_9178 | VERIFY_RECORD_PRESENT:audit_record_7068, VERIFY_RECORD_REDACTED:tombstone_9178 |

## Limits and next changes

Prioritize recovering source-supported bindings for identifier-free readbacks, explicit scoped negative queries and retained-record checks. Never infer a resource ID from case/user number suffixes or copy IDs from sample answers into inference. Some expected account IDs cannot currently be tied to a subject without such an unsupported shortcut. Investigate catalog/display-identity contradictions and media scope further; local OCR is imperfect and its extracted text is not a proof of every visual relationship. Do not discard source-backed extra risks just to match a small public sample. Detailed per-case blockers and examined sources are in `code/docs/UNRESOLVED_ISSUES.md`.

No substantive language-model runtime path is implemented or benchmarked. Optional AI was deferred because the main current failures concern absent bindings/proof, which a model must not invent. Local Windows OCR is active. All measurements here describe this checkpoint, not a finished submission.
