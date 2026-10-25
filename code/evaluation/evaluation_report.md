# GhostTrace Guard — measured evaluation

Runtime 0.6.0; final presentation/package audit preserves deletion inference and public sample metrics.

**C — confirmed incomplete official plans; operational BEST-EFFORT candidate. Not fully contract-compliant or upload-ready.**

R04 authorization and R05 compliant-label contradictions are repaired. 155 tests pass, 0 fail, 0 skip (154 prior regressions plus one clean-checkout source-packaging test). The original Phase 1 three counterexamples now produce INCOMPLETE with REPORT_EXPOSED_PII/REDACT_RECORD/VERIFY_RECORD_REDACTED, and two NOT_APPLICABLE empty plans. New real-source tests independently force both primary/reviewer parsers wrong and verify original-value vetoes still reject them.

Candidate rows 518/518; statuses {'INCOMPLETE': 355, 'COMPLETE': 153, 'NOT_APPLICABLE': 10}. Shared strict acceptances 415; uncertain COMPLETE 90, uncertain INCOMPLETE 13. These acceptances are bounded implementation checks, not an independent semantic certificate.

Independent sample status 29/32; exact ordered cases 8/32; precision 107/158, recall 107/193. No sample accuracy gain or hidden score is claimed. Output hash remains `b4301131db2c2f874feadff55dcc38fea0b595d9b1430d7a8f248ed63b57e283`: the demonstrated defects were on authored synthetic inputs, and their fixes do not change supplied-corpus predictions.

Official-plan gate FAIL for exactly case_479, case_503 and case_55. First two lack attachment exclusivity proof and emit verification only; case_55 lacks target restore permission and emits []. No dummy phase, invented ownership, permission or changed status was used to evade the contract. All 90 uncertain COMPLETE decisions and the three detailed plan decision records are in PHASE2_EVIDENCE_REVIEW.md. A bounded explicit-selector hypothesis recovered zero new links. No repeated blind scans or future inference were used.

## Independent all-32 scoring and reviewer ablation

| Metric | Primary | Strict GhostGuard | Candidate |
|---|---|---|---|
| Status correct /32 | 27 | 22 | 29 |
| Exact ordered cases /32 | 8 | 8 | 8 |
| Ordered sequence correct /32 | 8 | 8 | 8 |
| Padded field matches | 886 | 844 | 917 |
| Field denominator | 1365 | 1365 | 1365 |
| Exact step matches | 106 | 106 | 107 |
| Predicted steps | 150 | 136 | 158 |
| Reference steps | 193 | 193 | 193 |
| Citation matches | 56 | 42 | 57 |
| Cited predicted steps | 56 | 42 | 58 |
| Missing resources | 39 | 53 | 36 |
| Extra resources | 2 | 2 | 3 |
| Missing operations | 45 | 59 | 40 |
| Extra operations | 2 | 2 | 5 |

All 32 references remain in every denominator; unresolved predictions count as failures. Public samples contain 10 COMPLETE, 22 INCOMPLETE and zero NOT_APPLICABLE. Step precision/recall use multiset intersection of exact seven-field tuples including step_no/citation. Field agreement is position-aligned and padded to max array length. Sequence compares ordered phase/operation/system/resource. Citation agreement aligns scope/operation and is not a truth score. References are read only after inference; independent_score imports neither Engine nor production validators. Candidate 917/1365 fields, 57/58 citation agreement, 36/3 missing/extra resources and 40/5 operations reproduce the baseline. Primary/strict/candidate runtime seconds: [0.815489499999785, 0.8757628000003024, 1.2316212000000633].

## Independently authored cases and failures/improvements

1. Negated authorization and informational questions with deletion vocabulary: real JSON source/Engine/GhostGuard must yield NOT_APPLICABLE and []. Positive directives and legal-retention exceptions remain authorized. Tentative requests abstain.
2. REDACTED tombstone with exposed email/phone/nested fields must be INCOMPLETE and redact; stable internal user ID alone may remain. ANONYMIZED analytics with attributable stable ID must anonymize.
3. Deliberately correlated wrong parser states: original raw fields/control booleans/positive readbacks must veto false compliance/absence even when both parser passes agree.
4. Neighboring unrelated records cannot contaminate target identifiers. Incomplete-plan checker reports all invalid rows, including verification-only and empty plans.
5. Existing 140 regressions remain, including SQL/path safety, replicas/future captures, unknown ownership, legal holds, retained records, citation mutation and atomic writes. Fourteen new test methods extend them; subcases are not inflated into separate passing-test counts.

An early over-restrictive English rule missed procedural deletion requests and a past deletion continuation. General syntax rules plus positive regression cases corrected it; final sample metrics returned to 29/32 and 8/32. An original-control invariant initially applied present-state requirements to future verification of an ACTIVE process; this was corrected to distinguish planned checks from current compliance, with a regression assertion. No unsafe policy safeguards were weakened.

The old 9/32 exact baseline lost case_13 when unsupported attachment exclusivity was removed. That safety correction remains; it is not reversed to chase reference agreement. R04/R05 fix demonstrated general defects without claiming supplied-corpus gains. Final plan failures are case_479/503/55; 90 uncertain COMPLETE plus 13 uncertain INCOMPLETE remain. No hidden-answer accuracy, leaderboard score or comprehensive independent semantic proof is asserted.

## Presentation and clean-checkout packaging verification

One additional packaging regression proves --source-only needs neither a dataset nor a private checkpoint. Current suite: 155 passing, zero failures/skips. The 154-test Phase 2 baseline and prior semantic improvements remain unchanged. A curated actual-architecture document and corrected fork/feature-branch README replace the starter-dominated introduction. No prediction recovery or new LLM usage is claimed. Independent all-32 metrics were rechecked during final archive validation.
