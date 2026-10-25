# GhostTrace Guard 0.6.0 — current measured status

**C — confirmed incomplete official plans; operational BEST-EFFORT candidate. Not fully contract-compliant or upload-ready.**

R04 authorization and R05 compliant-label contradictions are repaired. 154 tests pass, 0 fail, 0 skip. The original Phase 1 three counterexamples now produce INCOMPLETE with REPORT_EXPOSED_PII/REDACT_RECORD/VERIFY_RECORD_REDACTED, and two NOT_APPLICABLE empty plans. New real-source tests independently force both primary/reviewer parsers wrong and verify original-value vetoes still reject them.

Candidate rows 518/518; statuses {'INCOMPLETE': 355, 'COMPLETE': 153, 'NOT_APPLICABLE': 10}. Shared strict acceptances 415; uncertain COMPLETE 90, uncertain INCOMPLETE 13. These acceptances are bounded implementation checks, not an independent semantic certificate.

Independent sample status 29/32; exact ordered cases 8/32; precision 107/158, recall 107/193. No sample accuracy gain or hidden score is claimed. Output hash remains `b4301131db2c2f874feadff55dcc38fea0b595d9b1430d7a8f248ed63b57e283`: the demonstrated defects were on authored synthetic inputs, and their fixes do not change supplied-corpus predictions.

Official-plan gate FAIL for exactly case_479, case_503 and case_55. First two lack attachment exclusivity proof and emit verification only; case_55 lacks target restore permission and emits []. No dummy phase, invented ownership, permission or changed status was used to evade the contract. All 90 uncertain COMPLETE decisions and the three detailed plan decision records are in PHASE2_EVIDENCE_REVIEW.md. A bounded explicit-selector hypothesis recovered zero new links. No repeated blind scans or future inference were used.

Independent checker `python code/independent_contract.py` reports every invalid case and never waives phases for candidate mode. Separate gates: SHAPE_VALID PASS; EMITTED_CITATIONS_VALID PASS within source-parser scope; COMPLETE_PLAN_CONTRACT_VALID FAIL; STRICT_EVIDENCE_PROOF_VALID FAIL. The standalone schema checker does not itself certify source semantics.

GhostGuard independence: original authorization vetoes, raw structured identifier witnesses, positive-readback contradictions, original control/retention/ownership invariants are separate from primary intent/state/policy functions. SQL/JSON/media extraction, identity graph and some policy semantics remain shared. No second full inference oracle is claimed. Per-record locators prevent unrelated neighboring rows from contributing direct identifiers. Typed readback subject_reference selectors are distinguished from persisted analytics user_id/customer_reference fields; tombstones may retain permitted stable references.

Default strict mode withholds output on unresolved cases. Explicit candidate mode atomically writes all 518 rows with a separate uncertainty report. Local OCR + deterministic inference uses zero LLM calls/tokens/API cost; optional AI remains bounded and is not forced for metrics. OCR requires Windows English OCR outside restrictive sandbox contexts, or separately installed tesseract English on other platforms. Non-Windows fidelity is not verified.

Source ZIP and clean-extraction verification are recorded in FINAL_RELEASE_RECORD.md after packaging. Root log is append-only/private. Private staging may contain a PENDING PRIVACY REVIEW transcript copy; no active trace is exported and no fake/empty agent-trace.zip is created. Close all contributing sessions/applications before trace staging. No HackerRank upload or interview was performed.
