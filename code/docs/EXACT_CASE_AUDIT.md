# Exact-case mismatch source audit

All public mismatches are audited after inference. Expected resource IDs are evaluator-only. No future-only evidence, numeric suffix, batch position or neighboring event is used as a binding.

Mismatching cases: 24; operation categories: `{'1_ACCOUNT_ABSENCE': 20, '3_ANALYTICS_ANONYMIZATION': 7, '8_POLICY_ACTION': 6, '5_EXTRA_RESOURCE': 3, '2_RETAINED_VERIFICATION': 7}`; source causes: `{'NO_STATE_OBSERVATION': 16, 'MISSING_SUBJECT_SELECTOR': 12, 'MISSING_CONDITIONAL_POLICY_PROOF': 6, 'EXPLICIT_ADMITTED_RELATIONSHIP_DIFFERS_FROM_REFERENCE': 3, 'ONLY_POST_CUTOFF_OBSERVATIONS': 6}`.

| Case | Category | Missing/extra operation and resource | Source cause | Admitted sources | Excluded later sources |
|---|---|---|---|---|---|
| case_01 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_001 | NO_STATE_OBSERVATION | none | none |
| case_02 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_002 | NO_STATE_OBSERVATION | none | none |
| case_03 | 3_ANALYTICS_ANONYMIZATION | VERIFY_RECORD_ANONYMIZED:analytics_9406 | MISSING_SUBJECT_SELECTOR | evidence_94 | none |
| case_04 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_004 | NO_STATE_OBSERVATION | none | none |
| case_04 | 3_ANALYTICS_ANONYMIZATION | VERIFY_RECORD_ANONYMIZED:analytics_901 | MISSING_SUBJECT_SELECTOR | evidence_56 | none |
| case_07 | 8_POLICY_ACTION | REPORT_REMAINING_RECORD:support_001 | MISSING_CONDITIONAL_POLICY_PROOF | evidence_58 | none |
| case_07 | 8_POLICY_ACTION | DELETE_RECORD:support_001 | MISSING_CONDITIONAL_POLICY_PROOF | evidence_58 | none |
| case_07 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_007 | NO_STATE_OBSERVATION | none | none |
| case_07 | 8_POLICY_ACTION | VERIFY_RECORD_ABSENT:support_001 | MISSING_CONDITIONAL_POLICY_PROOF | evidence_58 | none |
| case_07 | 5_EXTRA_RESOURCE | extra resource:object_19 | EXPLICIT_ADMITTED_RELATIONSHIP_DIFFERS_FROM_REFERENCE | evidence_46 | none |
| case_08 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_008 | NO_STATE_OBSERVATION | none | none |
| case_09 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_3960 | ONLY_POST_CUTOFF_OBSERVATIONS | none | evidence_06 |
| case_09 | 2_RETAINED_VERIFICATION | VERIFY_RECORD_PRESENT:audit_record_4902 | ONLY_POST_CUTOFF_OBSERVATIONS | none | evidence_06 |
| case_10 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_010 | NO_STATE_OBSERVATION | none | none |
| case_13 | 8_POLICY_ACTION | REPORT_REMAINING_RECORD:support_4218 | MISSING_CONDITIONAL_POLICY_PROOF | evidence_03 | none |
| case_13 | 8_POLICY_ACTION | DELETE_RECORD:support_4218 | MISSING_CONDITIONAL_POLICY_PROOF | evidence_03 | none |
| case_13 | 8_POLICY_ACTION | VERIFY_RECORD_ABSENT:support_4218 | MISSING_CONDITIONAL_POLICY_PROOF | evidence_03 | none |
| case_17 | 5_EXTRA_RESOURCE | extra resource:account_6523 | EXPLICIT_ADMITTED_RELATIONSHIP_DIFFERS_FROM_REFERENCE | evidence_67 | none |
| case_17 | 5_EXTRA_RESOURCE | extra resource:tombstone_17 | EXPLICIT_ADMITTED_RELATIONSHIP_DIFFERS_FROM_REFERENCE | evidence_42 | none |
| case_18 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_5521 | NO_STATE_OBSERVATION | none | none |
| case_18 | 2_RETAINED_VERIFICATION | VERIFY_RECORD_PRESENT:audit_record_6645 | NO_STATE_OBSERVATION | none | none |
| case_20 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_5037 | NO_STATE_OBSERVATION | none | none |
| case_20 | 2_RETAINED_VERIFICATION | VERIFY_RECORD_PRESENT:audit_record_5569 | NO_STATE_OBSERVATION | none | none |
| case_21 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_6440 | MISSING_SUBJECT_SELECTOR | evidence_92 | none |
| case_21 | 3_ANALYTICS_ANONYMIZATION | VERIFY_RECORD_ANONYMIZED:analytics_5335 | MISSING_SUBJECT_SELECTOR | evidence_92 | evidence_02 |
| case_22 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_4990 | NO_STATE_OBSERVATION | none | none |
| case_23 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_410 | NO_STATE_OBSERVATION | none | none |
| case_23 | 2_RETAINED_VERIFICATION | VERIFY_RECORD_PRESENT:audit_record_4128 | ONLY_POST_CUTOFF_OBSERVATIONS | none | evidence_02 |
| case_24 | 2_RETAINED_VERIFICATION | VERIFY_RECORD_PRESENT:audit_record_7095 | ONLY_POST_CUTOFF_OBSERVATIONS | none | evidence_02 |
| case_25 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_3136 | MISSING_SUBJECT_SELECTOR | evidence_92 | none |
| case_25 | 3_ANALYTICS_ANONYMIZATION | VERIFY_RECORD_ANONYMIZED:analytics_1895 | MISSING_SUBJECT_SELECTOR | evidence_92 | evidence_02 |
| case_26 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_5684 | MISSING_SUBJECT_SELECTOR | evidence_92 | evidence_02 |
| case_26 | 3_ANALYTICS_ANONYMIZATION | VERIFY_RECORD_ANONYMIZED:analytics_4566 | MISSING_SUBJECT_SELECTOR | evidence_92 | evidence_02 |
| case_27 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_3866 | MISSING_SUBJECT_SELECTOR | evidence_92 | evidence_02 |
| case_27 | 3_ANALYTICS_ANONYMIZATION | VERIFY_RECORD_ANONYMIZED:analytics_4574 | MISSING_SUBJECT_SELECTOR | evidence_92 | evidence_02 |
| case_28 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_5482 | MISSING_SUBJECT_SELECTOR | evidence_92 | none |
| case_28 | 3_ANALYTICS_ANONYMIZATION | VERIFY_RECORD_ANONYMIZED:analytics_6077 | MISSING_SUBJECT_SELECTOR | evidence_92 | evidence_02 |
| case_29 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_7012 | NO_STATE_OBSERVATION | none | none |
| case_29 | 2_RETAINED_VERIFICATION | VERIFY_RECORD_PRESENT:audit_record_3954 | ONLY_POST_CUTOFF_OBSERVATIONS | none | evidence_02 |
| case_30 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_4163 | NO_STATE_OBSERVATION | none | none |
| case_30 | 2_RETAINED_VERIFICATION | VERIFY_RECORD_PRESENT:audit_record_1707 | ONLY_POST_CUTOFF_OBSERVATIONS | none | evidence_02 |
| case_31 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_4857 | NO_STATE_OBSERVATION | none | none |
| case_32 | 1_ACCOUNT_ABSENCE | VERIFY_RECORD_ABSENT:account_8858 | NO_STATE_OBSERVATION | none | none |

    The common proof gaps are missing selectors on anonymous readbacks, post-cutoff captures, and unverified attachment exclusivity. Missing conditional-policy proof is deliberately withheld; it is distinguished from a repairable engine omission. Every missing resource is also searched literally in raw admitted text/OCR; a mention alone is not a proven state or sole ownership. Later sources explain benchmark mismatches only and never supply earlier decisions.

All nine requested root-cause classes were considered. Categories 6 (identity) and 7 (time) are represented by the selector/capture causes; category 8 would identify a missing known policy operation. Category 9 is measured separately. The three extra resources have explicit admitted source relationships; deleting them solely to match reference answers would remove supported obligations.
