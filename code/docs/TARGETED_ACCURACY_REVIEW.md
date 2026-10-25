# Final targeted ownership and accuracy review

Baseline: `43990d03ac6de69302e59585d1d3c6f12d7ab9e8`, preserved locally under artifacts/baseline-43990d0 with CSV/ZIP hashes and reports. Main and participant inputs remain unchanged. This evaluator runs after inference; reference IDs and answers never supply production bindings, policy or steps.

## Twelve attachment cases

All twelve have exact, dated subject associations and PRESENT attachment observations. No examined metadata contains shared_subjects, sole_owner or an exclusive-ownership catalog attestation. Uploader identity, a PII detector's matched selector, ticket ID, filename and multiple physical replicas establish association/existence, not exhaustive ownership. The only matched dated activities are deletion-worker claims; their success/failure does not establish state or sole ownership. No new source relationship or recoverable accuracy gain was found.

| Case / subject | Cutoff | Resource | Evidence / capture | Association selectors and source scope | Ownership / action |
|---|---|---|---|---|---|
| case_34 / user_11 | 2026-09-27T13:00:00Z | support_platform/support_9538 | evidence_01 2026-09-15T11:59:39Z | matched_value, scan_key; log:line:25 | UNKNOWN; abstain |
| case_203 / user_201 | 2026-07-08T09:00:00Z | support_platform/support_8903 | evidence_20 2026-07-08T09:00:00Z | uploaded_by; customer_data_primary:support_8903, customer_data_read_replica:support_8903 | UNKNOWN; abstain |
| case_263 / user_261 | 2026-06-08T10:00:00Z | support_platform/support_5234 | evidence_25 2026-06-08T09:58:28Z | matched_value, scan_key; log:line:75 | UNKNOWN; abstain |
| case_311 / user_309 | 2026-05-19T06:00:00Z | support_platform/support_4952 | evidence_29 2026-05-19T06:00:00Z | uploaded_by; customer_data_primary:support_4952, customer_data_replica_ap_south:support_4952, customer_data_replica_eu_west:support_4952 | UNKNOWN; abstain |
| case_359 / user_357 | 2026-04-24T08:00:00Z | support_platform/support_2537 | evidence_33 2026-04-24T08:00:00Z | uploaded_by; customer_data_primary:support_2537, customer_data_replica_ap_south:support_2537, customer_data_replica_eu_west:support_2537 | UNKNOWN; abstain |
| case_371 / user_369 | 2026-04-19T07:00:00Z | support_platform/support_3110 | evidence_34 2026-04-19T06:59:43Z | matched_value; log:line:87 | UNKNOWN; abstain |
| case_407 / user_405 | 2026-03-30T10:00:00Z | support_platform/support_3802 | evidence_38 2026-03-30T10:00:00Z | uploaded_by; customer_data_primary:support_3802, customer_data_replica_ap_south:support_3802, customer_data_replica_eu_west:support_3802 | UNKNOWN; abstain |
| case_419 / user_417 | 2026-03-25T09:00:00Z | support_platform/support_2944 | evidence_39 2026-03-25T08:59:44Z | matched_value, scan_key; log:line:7 | UNKNOWN; abstain |
| case_455 / user_453 | 2026-03-05T12:00:00Z | support_platform/support_2055 | evidence_43 2026-03-05T12:00:00Z | uploaded_by; customer_data_primary:support_2055, customer_data_reporting_replica:support_2055 | UNKNOWN; abstain |
| case_479 / user_477 | 2026-02-23T10:00:00Z | support_platform/support_4665 | evidence_45 2026-02-23T10:00:00Z | uploaded_by; json/10/ticket_attachments:0 | UNKNOWN; abstain |
| case_503 / user_501 | 2026-02-08T07:00:00Z | support_platform/support_2295 | evidence_47 2026-02-08T07:00:00Z | uploaded_by; customer_data_primary:support_2295, customer_data_reporting_replica:support_2295 | UNKNOWN; abstain |
| case_515 / user_513 | 2026-02-03T06:00:00Z | support_platform/support_4533 | evidence_48 2026-02-03T05:59:42Z | matched_value; log:line:97 | UNKNOWN; abstain |

Exact source files and dated activities examined:

- case_34: `evidence/logs/service_events_ap_south_20260915.log`; activities `activity_3489` (DELETE_RECORD); binding EXACT_IDENTIFIER at evidence_01.
- case_203: `evidence/databases/customer_data_read_replica_20260708.sql`; activities `activity_2570` (DELETE_RECORD); binding EXACT_IDENTIFIER at evidence_20.
- case_263: `evidence/logs/cloud_runtime_export_us_west_20260608.log`; activities `activity_2119` (DELETE_RECORD); binding EXACT_IDENTIFIER at evidence_25.
- case_311: `evidence/databases/customer_data_regional_replicas_20260519.sql`; activities `activity_1673` (DELETE_RECORD); binding EXACT_IDENTIFIER at evidence_29.
- case_359: `evidence/databases/customer_data_regional_replicas_20260424.sql`; activities `activity_1199` (DELETE_RECORD); binding EXACT_IDENTIFIER at evidence_33.
- case_371: `evidence/logs/structured_service_events_ca_central_20260419.log`; activities `activity_1238` (DELETE_RECORD); binding EXACT_IDENTIFIER at evidence_34.
- case_407: `evidence/databases/customer_data_regional_replicas_20260330.sql`; activities `activity_1008` (DELETE_RECORD); binding EXACT_IDENTIFIER at evidence_38.
- case_419: `evidence/logs/syslog_archive_ap_southeast_20260325.log`; activities `activity_755` (DELETE_RECORD); binding EXACT_IDENTIFIER at evidence_39.
- case_455: `evidence/databases/customer_data_reporting_replica_20260305.sql`; activities `activity_529` (DELETE_RECORD); binding EXACT_IDENTIFIER at evidence_43.
- case_479: `evidence/records/customer_data_snapshot_bundle_20260223.json`; activities `activity_324` (DELETE_RECORD); binding EXACT_IDENTIFIER at evidence_45.
- case_503: `evidence/databases/customer_data_reporting_replica_20260208.sql`; activities `activity_339` (DELETE_RECORD); binding EXACT_IDENTIFIER at evidence_47.
- case_515: `evidence/logs/operations_stream_me_central_20260203.log`; activities `activity_81` (DELETE_RECORD); binding EXACT_IDENTIFIER at evidence_48.

## Ownership semantics corrected

Rule_06 says SUPPORT_ATTACHMENT / “Attachment belongs only to the deletion subject” / DELETE. It does not declare owner lists exhaustive and supplies no shared-attachment REDACT fallback. Rule_05's redaction condition applies to SUPPORT_MESSAGE, a different category. A singleton shared_subjects list may contain only known associations; duplicates add no owner information. Only an independent explicit exclusivity attestation supports SOLE. Two known distinct subjects suffice for SHARED even if the list is partial; neither SHARED nor UNKNOWN satisfies rule_06. Contradictory or malformed attestations abstain. No unattested completeness flag is fabricated. An explicitly supplied unconditional redaction rule would be honored, but none is supplied for these attachments.

The previous synthetic test's automatic shared-attachment redaction expectation was corrected to match the supplied conditional rule. New authored tests cover partial singleton/duplicates, explicit sole ownership, contradictory attestations, shared lower bounds versus actual policy authorization, and rejection of an invented sole_owner boolean during original-source review. The reviewer now compares that policy-critical boolean directly rather than relying on string-token containment.

## Lost exact match

case_13: old and reference have 8 steps; current has 5. All statuses are INCOMPLETE. Exact arrays are recorded below.

### old_5b9a098

```json
{
  "status": "INCOMPLETE",
  "steps": [
    {
      "step_no": 1,
      "phase": "FINDING",
      "system_id": "search_service",
      "resource_id": "search_1308",
      "operation": "REPORT_REMAINING_RECORD",
      "state": "PRESENT",
      "evidence_id": "evidence_03"
    },
    {
      "step_no": 2,
      "phase": "FINDING",
      "system_id": "support_platform",
      "resource_id": "support_4218",
      "operation": "REPORT_REMAINING_RECORD",
      "state": "PRESENT",
      "evidence_id": "evidence_03"
    },
    {
      "step_no": 3,
      "phase": "REMEDIATION",
      "system_id": "search_service",
      "resource_id": "search_1308",
      "operation": "DELETE_RECORD",
      "state": "ABSENT",
      "evidence_id": ""
    },
    {
      "step_no": 4,
      "phase": "REMEDIATION",
      "system_id": "support_platform",
      "resource_id": "support_4218",
      "operation": "DELETE_RECORD",
      "state": "ABSENT",
      "evidence_id": ""
    },
    {
      "step_no": 5,
      "phase": "VERIFICATION",
      "system_id": "account_service",
      "resource_id": "account_9335",
      "operation": "VERIFY_RECORD_ABSENT",
      "state": "ABSENT",
      "evidence_id": ""
    },
    {
      "step_no": 6,
      "phase": "VERIFICATION",
      "system_id": "search_service",
      "resource_id": "search_1308",
      "operation": "VERIFY_RECORD_ABSENT",
      "state": "ABSENT",
      "evidence_id": ""
    },
    {
      "step_no": 7,
      "phase": "VERIFICATION",
      "system_id": "support_platform",
      "resource_id": "support_4218",
      "operation": "VERIFY_RECORD_ABSENT",
      "state": "ABSENT",
      "evidence_id": ""
    },
    {
      "step_no": 8,
      "phase": "VERIFICATION",
      "system_id": "security_service",
      "resource_id": "audit_record_4816",
      "operation": "VERIFY_RECORD_PRESENT",
      "state": "PRESENT",
      "evidence_id": ""
    }
  ]
}
```

### current

```json
{
  "status": "INCOMPLETE",
  "steps": [
    {
      "step_no": 1,
      "phase": "FINDING",
      "system_id": "search_service",
      "resource_id": "search_1308",
      "operation": "REPORT_REMAINING_RECORD",
      "state": "PRESENT",
      "evidence_id": "evidence_03"
    },
    {
      "step_no": 2,
      "phase": "REMEDIATION",
      "system_id": "search_service",
      "resource_id": "search_1308",
      "operation": "DELETE_RECORD",
      "state": "ABSENT",
      "evidence_id": ""
    },
    {
      "step_no": 3,
      "phase": "VERIFICATION",
      "system_id": "account_service",
      "resource_id": "account_9335",
      "operation": "VERIFY_RECORD_ABSENT",
      "state": "ABSENT",
      "evidence_id": ""
    },
    {
      "step_no": 4,
      "phase": "VERIFICATION",
      "system_id": "search_service",
      "resource_id": "search_1308",
      "operation": "VERIFY_RECORD_ABSENT",
      "state": "ABSENT",
      "evidence_id": ""
    },
    {
      "step_no": 5,
      "phase": "VERIFICATION",
      "system_id": "security_service",
      "resource_id": "audit_record_4816",
      "operation": "VERIFY_RECORD_PRESENT",
      "state": "PRESENT",
      "evidence_id": ""
    }
  ]
}
```

### public_reference

```json
{
  "status": "INCOMPLETE",
  "steps": [
    {
      "step_no": 1,
      "phase": "FINDING",
      "system_id": "search_service",
      "resource_id": "search_1308",
      "operation": "REPORT_REMAINING_RECORD",
      "state": "PRESENT",
      "evidence_id": "evidence_03"
    },
    {
      "step_no": 2,
      "phase": "FINDING",
      "system_id": "support_platform",
      "resource_id": "support_4218",
      "operation": "REPORT_REMAINING_RECORD",
      "state": "PRESENT",
      "evidence_id": "evidence_03"
    },
    {
      "step_no": 3,
      "phase": "REMEDIATION",
      "system_id": "search_service",
      "resource_id": "search_1308",
      "operation": "DELETE_RECORD",
      "state": "ABSENT",
      "evidence_id": ""
    },
    {
      "step_no": 4,
      "phase": "REMEDIATION",
      "system_id": "support_platform",
      "resource_id": "support_4218",
      "operation": "DELETE_RECORD",
      "state": "ABSENT",
      "evidence_id": ""
    },
    {
      "step_no": 5,
      "phase": "VERIFICATION",
      "system_id": "account_service",
      "resource_id": "account_9335",
      "operation": "VERIFY_RECORD_ABSENT",
      "state": "ABSENT",
      "evidence_id": ""
    },
    {
      "step_no": 6,
      "phase": "VERIFICATION",
      "system_id": "search_service",
      "resource_id": "search_1308",
      "operation": "VERIFY_RECORD_ABSENT",
      "state": "ABSENT",
      "evidence_id": ""
    },
    {
      "step_no": 7,
      "phase": "VERIFICATION",
      "system_id": "support_platform",
      "resource_id": "support_4218",
      "operation": "VERIFY_RECORD_ABSENT",
      "state": "ABSENT",
      "evidence_id": ""
    },
    {
      "step_no": 8,
      "phase": "VERIFICATION",
      "system_id": "security_service",
      "resource_id": "audit_record_4816",
      "operation": "VERIFY_RECORD_PRESENT",
      "state": "PRESENT",
      "evidence_id": ""
    }
  ]
}
```


For case_13, evidence_03 (`evidence/records/customer_account_handover_20261001.txt`, line 43) states SUPPORT_ATTACHMENT / FOUND / subject selector for support_4218. Capture and observation are 2026-10-01T12:00:00Z, equal to the sample cutoff. This proves existence/association, not exclusive ownership. The other five current operations remain supported by the handover's account/search/security observations.

At 5b9a098, Policy.action returned rule_06's DELETE by default whenever shared_subjects was absent. Commit 713d6e158747e1b0729504167ebacaca6bf68f2f replaced that default with explicit attachment_ownership; Engine omitted facts whose required policy condition was UNKNOWN. This removed support_4218's finding, DELETE and absent verification, and renumbered the remaining five steps. The old exact match depended on unsupported ownership. Retaining the omission is a safety correction, not an unnecessary restriction. No case-specific exception is introduced.

Historical replay command (source-only 5b9a098 archive extracted under tmp/targeted-old-5b9a098):

```text
python tmp/targeted-old-5b9a098/code/main.py --mode candidate --dataset dataset --requests dataset/sample_deletion_requests.csv --cache-dir tmp/ocr --output tmp/targeted-old-sample.csv --metrics-path tmp/targeted-old-sample-metrics.json --uncertainty-report tmp/targeted-old-sample-uncertainty.md
```

## Current checkpoint versus 43990d0

| Metric | Before | After |
|---|---:|---:|
| tests | 136 | 140 |
| status | 29 | 29 |
| exact | 8 | 8 |
| precision | 0.6772 | 0.6772 |
| recall | 0.5544 | 0.5544 |
| strict | 415 | 415 |
| uncertain | 103 | 103 |

Candidate rows 518/518; missing/extra resources 36/3; missing/extra operations 40/5. Primary versus reviewed statuses 27/32 versus 22/32. Recovered regressions: 0.

All prior safety mechanisms remain tested. Root-state, unbound/future-only selector gaps and case_55 permission are unchanged; no repeated broad evidence search was conducted. General OCR row geometry and ambiguous-intent coverage remain limited. Semantic certainty and official plan completeness remain FAIL; structural/source gates do not establish hidden-answer correctness. Final full inference uses zero language-model calls/tokens/API fee. Prior live AI experiments remain separately labeled historical development usage.

The three primary submission files are local output.csv, code.zip and the private root log.txt (chat_transcript). The separate agent-trace.zip must be produced only after contributing sessions finish and apps close, following TRACE_FINALIZATION.md and the unchanged official instructions. AI interview preparation remains a separate explanation of architecture, evidence, policy, measured failures and usage. No upload is authorized or performed.
