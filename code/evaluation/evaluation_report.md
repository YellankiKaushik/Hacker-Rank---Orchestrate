# Measured two-mode evaluation

Generated 2026-10-24T18:55:03.992821+00:00. **B: structurally valid candidate with documented semantic uncertainty.** There is no hidden-answer score. Full candidate coverage is 518/518; strict evidence-proven coverage under the implemented finite-source review is 427/518. This is not exhaustive knowledge of every possible copy.

## Public sample: all 32 cases

| Variant | Status correct | Exact ordered seven-field cases | Withheld / uncertain |
|---|---|---|---|
| Previous primary, 2ada359 | 29/32 | 9/32 | 3 withheld |
| Previous strict review, 2ada359 | 24/32 | 9/32 | 8 withheld |
| Current primary | 29/32 | 9/32 | 3 withheld |
| Current strict review | 24/32 | 9/32 | 8 withheld |
| Current every-row candidate | 29/32 | 9/32 | 8 uncertain, none withheld |

Every-row candidate metrics include all 32 generated predictions. Exact-case accuracy has not substantially improved. All 518 evaluation predictions exist, but their accuracy is NOT VERIFIED because no participant reference answers are available. References are loaded by this evaluator only after inference; no production module reads sample_output.csv.

| Candidate metric | Measurement |
|---|---|
| Status accuracy | 29/32 (90.62%) |
| Exact case accuracy | 9/32 (28.12%) |
| Sequence accuracy | 9/32 (28.12%) |
| Position-aligned field accuracy | 957/1379 (69.40%) |
| Exact seven-field step precision | 114/164 (69.51%) |
| Exact seven-field step recall | 114/193 (59.07%) |
| Reference citation agreement | 59/60 (98.33%) |
| False COMPLETE / false INCOMPLETE | 0 / 3 |
| Missing / extra reference resources | 34 / 3 |
| Missing / extra scope operations | 34 / 5 |

Field accuracy pads both arrays to the larger length, comparing all seven fields per position. Step precision/recall is multiset intersection including numbering and citations. Sequence accuracy compares ordered phase/operation/system/resource. Reference citation agreement is distinct from actual source support.

## Proof-gate analysis and measured GhostGuard effect

The official contract requires appropriate treatment of every relevant copy, required retention and prevention of active recreation paths. It does not require a profile/tombstone check in every case. GhostGuard now independently enumerates dated bound obligations and distinguishes A supported, B supported with a nonessential missing profile observation, C required proof missing, D contradicted, and E unsupported/fabricated. Only A/B accept strict review.

A retained journal alone cannot establish account deletion. A known linked record without a readback, or an unidentified account row in the admitted subject-linked source, remains C. A substantive compliant secondary treatment can qualify B when every grounded obligation is covered and no such ambiguity remains. All previous 97 missing-profile cases were re-evaluated: **7 now qualify B, 90 remain C**. Recovered cases: case_112, case_155, case_204, case_213, case_297, case_308, case_57. No new identity assignment was fabricated.

GhostGuard does not improve measured sample status accuracy: 29/32 primary versus 24/32 reviewed. Five withheld primary statuses match references while necessary linkage/scope proof is absent. Source rereading independently checks original bytes and hashes and catches injected source/citation/state/intent/operation errors in tests. Shared domain adapters/policy limit independence; there is no LLM reviewer or hidden-answer oracle.

## Full run: coverage versus certainty

- Strict accepted: 427/518; unresolved: 91.
- Candidate: 518/518; statuses `{'INCOMPLETE': 355, 'COMPLETE': 153, 'NOT_APPLICABLE': 10}`.
- Uncertain predictions: 91; unsupported full-proof status inferences: 91; fabricated references: 0.
- Source-backed cited steps: 1031/1031. Future work uses empty evidence IDs.
- Structure, emitted citation/time/provenance/policy-operation gates PASS. Semantic certainty FAIL.
- Output SHA-256 `edc5a4ea5e0ea8376a6236524fb9eb1049657767c61cb72883fc5fef787ff7f3`; warm-cache seconds 10.9115.
- Targeted rereads 33, source-view cache hits 58; at most one retry/four source files per challenged case.

Unknown required state predicts INCOMPLETE without inventing a particular violation. Observed compliant states with unproven scope predict COMPLETE under an explicitly unverified closed-evidence assumption. Every such inference appears in artifacts/SUBMISSION_UNCERTAINTY_REPORT.md. case_55 has no source-supported current-state check: INCOMPLETE with an empty array satisfies CSV/JSON shape but fails strict semantic plan completeness. The existing strict validator remains unchanged and rejects the unproven candidate.

## Regression coverage and additional participant cases

116 unit/synthetic integration test methods pass. Representative independently authored cases:

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
| case_01 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_001 | none |
| case_02 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_002 | none |
| case_03 | COMPLETE | VERIFY_RECORD_ANONYMIZED:analytics_9406 | none |
| case_04 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_004, VERIFY_RECORD_ANONYMIZED:analytics_901 | none |
| case_07 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_007 | DELETE_RECORD:object_19, REPORT_REMAINING_RECORD:object_19, VERIFY_RECORD_ABSENT:object_19 |
| case_08 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_008 | none |
| case_09 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_3960, VERIFY_RECORD_PRESENT:audit_record_4902 | none |
| case_10 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_010 | none |
| case_17 | INCOMPLETE | none | VERIFY_RECORD_ABSENT:account_6523, VERIFY_RECORD_REDACTED:tombstone_17 |
| case_18 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_5521, VERIFY_RECORD_PRESENT:audit_record_6645 | none |
| case_20 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_5037, VERIFY_RECORD_PRESENT:audit_record_5569 | none |
| case_21 | COMPLETE | VERIFY_RECORD_ABSENT:account_6440, VERIFY_RECORD_ANONYMIZED:analytics_5335 | none |
| case_22 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_4990 | none |
| case_23 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_410, VERIFY_RECORD_PRESENT:audit_record_4128 | none |
| case_24 | INCOMPLETE | VERIFY_RECORD_PRESENT:audit_record_7095 | none |
| case_25 | COMPLETE | VERIFY_RECORD_ABSENT:account_3136, VERIFY_RECORD_ANONYMIZED:analytics_1895 | none |
| case_26 | COMPLETE | VERIFY_RECORD_ABSENT:account_5684, VERIFY_RECORD_ANONYMIZED:analytics_4566 | none |
| case_27 | COMPLETE | VERIFY_RECORD_ABSENT:account_3866, VERIFY_RECORD_ANONYMIZED:analytics_4574 | none |
| case_28 | COMPLETE | VERIFY_RECORD_ABSENT:account_5482, VERIFY_RECORD_ANONYMIZED:analytics_6077 | none |
| case_29 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_7012, VERIFY_RECORD_PRESENT:audit_record_3954 | none |
| case_30 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_4163, VERIFY_RECORD_PRESENT:audit_record_1707 | none |
| case_31 | COMPLETE | VERIFY_RECORD_ABSENT:account_4857 | none |
| case_32 | INCOMPLETE | VERIFY_RECORD_ABSENT:account_8858 | none |

Missing account/anonymous analytics verifications lack admitted subject selectors, or occur only in post-cutoff files. Several expected security-record checks are available only in excluded later captures. Assigning anonymous rows by position, event proximity or numeric suffix would fabricate identity relationships. These operations remain omitted and documented. The attachment discrepancy was checked: activity_4007 explicitly associates object_19 with the subject and evidence_46 establishes its storage. It remains despite its omission from the public reference. Source-backed account/tombstone extras likewise remain. Future verification covers each known remediated record/process; active flows and restores require explicit configuration/readback evidence. No golden case/resource ID or expected sequence was added to production logic. No substantial exact-case gain is claimed.

## Actual bounded local AI

Installed model `gemma4:e4b`: initial four replies failed strict JSON checks; one diagnostic identified formatting failure. An explicit JSON-only instruction repaired it. Final authored fixture score 4/4 including one abstention versus deterministic 3/4. This tiny intent benchmark does not demonstrate dataset gain. All experimental calls including rejected replies: 9, input tokens 1305, output tokens 181. No API fee; local compute cost unmeasured. Rejected cloud credentials were not retried. Final dataset runtime uses zero model calls.
