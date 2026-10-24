# Measured participant dataset audit

Read-only audit of participant-facing inputs. No organizer-only files or generator internals were accessed.

| CSV | Data rows | Columns |
|---|---:|---|
| deletion_requests.csv | 518 | case_id, email, requested_at, reported_status, reported_at, audit_at, request_text |
| deletion_rules.csv | 15 | rule_id, data_category, condition, required_action |
| evidence_files.csv | 94 | file_id, file_path, origin, captured_at |
| output.csv | 0 | case_id, deletion_status, steps_json |
| sample_deletion_requests.csv | 32 | case_id, email, requested_at, reported_status, reported_at, audit_at, request_text |
| sample_output.csv | 32 | case_id, deletion_status, steps_json |
| system_activity.csv | 4011 | activity_id, event_time, event_type, source_system, target_system, resource_id, reported_result, details |
| user_audit_log.csv | 306 | audit_id, user_id, event_time, field_name, old_value, new_value |
| user_identities.csv | 850 | user_id, name, email, phone, email_hash, updated_at |

Evidence formats: {'.sql': 24, '.pdf': 4, '.png': 11, '.log': 26, '.json': 28, '.txt': 1}. All 94 listed files were read.

Confirmed structures: nested JSON snapshots and per-service exports; generic typed operational records; SQLite primary/read/regional/reporting/failover snapshots; JSON/logfmt/bracket/pipe/syslog/cloud log dialects; four text-bearing business PDFs; eleven PNG admin screenshots. A representative PDF was rendered and visually inspected alongside screenshots; all PNGs were passed through local OCR.

Key discoveries: identity history changes email, phone and hash; manifest entries do not assign subjects. Trace-start lookup keys must be joined to completion observations. Analytics contacts can be SECONDARY_IDENTIFIER records requiring deletion rather than anonymization. Tombstones retain stable references but remove direct identifiers. Retained journals and legal holds are not ordinary deletion targets. Source capture time and fact observation time are independently checked. Same-time replica presence wins over primary absence. `reported_status`/operation success never establish resulting state.

PDFs are ordinary customer statements, retention records and a support attachment. Their business document identifiers require catalog-grounded resource linkage. Screenshots include unrelated table rows: document-wide identifier matches must not associate every visible resource with every person. OCR is source-derived and imperfect; content hashes invalidate its cache. The public references contain no NOT_APPLICABLE cases, so independent synthetic negatives are required. See UNRESOLVED_ISSUES.md for remaining proof gaps.
