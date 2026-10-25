# GhostTrace Guard 0.6.0 — current measured status

**C — confirmed incomplete official plans; operational BEST-EFFORT candidate. Not fully contract-compliant or upload-ready.**

R04 authorization and R05 compliant-label contradictions are repaired. 155 tests pass, 0 fail, 0 skip (154 prior regressions plus one clean-checkout source-packaging test). The original Phase 1 three counterexamples now produce INCOMPLETE with REPORT_EXPOSED_PII/REDACT_RECORD/VERIFY_RECORD_REDACTED, and two NOT_APPLICABLE empty plans. New real-source tests independently force both primary/reviewer parsers wrong and verify original-value vetoes still reject them.

Candidate rows 518/518; statuses {'INCOMPLETE': 355, 'COMPLETE': 153, 'NOT_APPLICABLE': 10}. Shared strict acceptances 415; uncertain COMPLETE 90, uncertain INCOMPLETE 13. These acceptances are bounded implementation checks, not an independent semantic certificate.

Independent sample status 29/32; exact ordered cases 8/32; precision 107/158, recall 107/193. No sample accuracy gain or hidden score is claimed. Output hash remains `b4301131db2c2f874feadff55dcc38fea0b595d9b1430d7a8f248ed63b57e283`: the demonstrated defects were on authored synthetic inputs, and their fixes do not change supplied-corpus predictions.

Official-plan gate FAIL for exactly case_479, case_503 and case_55. First two lack attachment exclusivity proof and emit verification only; case_55 lacks target restore permission and emits []. No dummy phase, invented ownership, permission or changed status was used to evade the contract. All 90 uncertain COMPLETE decisions and the three detailed plan decision records are in PHASE2_EVIDENCE_REVIEW.md. A bounded explicit-selector hypothesis recovered zero new links. No repeated blind scans or future inference were used.

Independent checker `python code/independent_contract.py` reports every invalid case and never waives phases for candidate mode. Separate gates: SHAPE_VALID PASS; EMITTED_CITATIONS_VALID PASS within source-parser scope; COMPLETE_PLAN_CONTRACT_VALID FAIL; STRICT_EVIDENCE_PROOF_VALID FAIL. The standalone schema checker does not itself certify source semantics.

GhostGuard independence: original authorization vetoes, raw structured identifier witnesses, positive-readback contradictions, original control/retention/ownership invariants are separate from primary intent/state/policy functions. SQL/JSON/media extraction, identity graph and some policy semantics remain shared. No second full inference oracle is claimed. Per-record locators prevent unrelated neighboring rows from contributing direct identifiers. Typed readback subject_reference selectors are distinguished from persisted analytics user_id/customer_reference fields; tombstones may retain permitted stable references.

Default strict mode withholds output on unresolved cases. Explicit candidate mode atomically writes all 518 rows with a separate uncertainty report. Local OCR + deterministic inference uses zero LLM calls/tokens/API cost; optional AI remains bounded and is not forced for metrics. OCR requires Windows English OCR outside restrictive sandbox contexts, or separately installed tesseract English on other platforms. Non-Windows fidelity is not verified.

Source ZIP and clean-extraction verification are recorded in FINAL_RELEASE_RECORD.md after packaging. Root log is append-only/private. Private staging may contain a PENDING PRIVACY REVIEW transcript copy; no active trace is exported and no fake/empty agent-trace.zip is created. Close all contributing sessions/applications before trace staging. No HackerRank upload or interview was performed.

## Per-case diagnostics from the final dataset run

# Unresolved evidence and execution issues

Updated 2026-10-25T05:40:39.224113+00:00. Strict unresolved 103; candidate 518 rows; uncertain 103. Recovered B: case_112, case_155, case_204, case_213, case_297, case_308, case_57. Candidate row coverage does not resolve source gaps. Separate per-case assumptions/omitted obligations are in artifacts/SUBMISSION_UNCERTAINTY_REPORT.md.

| Case | Admitted evidence examined | Missing fact and impact | Candidate; recommended next action |
|---|---|---|---|
| case_103 | evidence_10 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_107 | evidence_10 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_108 | evidence_10 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_111 | evidence_10 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_126 | evidence_87 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_127 | evidence_87 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_150 | evidence_86 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_151 | evidence_86 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_152 | evidence_86 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_157 | evidence_15 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_162 | evidence_15 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_175 | evidence_84 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_178 | evidence_84 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_183 | evidence_83 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_190 | evidence_83 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_191 | evidence_83 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_203 | evidence_20 | case_203: Unresolved state: support_platform/support_8903 | INCOMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_206 | evidence_20 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_215 | evidence_81 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_218 | evidence_81 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_219 | evidence_81 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_221 | evidence_81 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_225 | evidence_80 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_226 | evidence_80 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_231 | evidence_80 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_243 | evidence_78 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_244 | evidence_78 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_253 | evidence_24 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_257 | evidence_24 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_260 | evidence_24 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_263 | evidence_25 | case_263: Unresolved state: support_platform/support_5234 | INCOMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_274 | evidence_77 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_276 | evidence_77 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_277 | evidence_77 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_294 | evidence_75 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_295 | evidence_75 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_299 | evidence_75 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_304 | evidence_29 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_309 | evidence_29 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_311 | evidence_29 | case_311: Unresolved state: support_platform/support_4952 | INCOMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_313 | evidence_74 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_314 | evidence_74 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_319 | evidence_74 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_322 | evidence_74 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_335 | evidence_72 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_336 | evidence_72 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_339 | evidence_72 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_34 | evidence_01, evidence_04 | case_34: Unresolved state: support_platform/support_9538 | INCOMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_343 | evidence_71 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_345 | evidence_71 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_346 | evidence_71 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_351 | evidence_71 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_354 | evidence_33 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_359 | evidence_33 | case_359: Unresolved state: support_platform/support_2537 | INCOMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_362 | evidence_33 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_371 | evidence_34 | case_371: Unresolved state: support_platform/support_3110 | INCOMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_393 | evidence_69 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_395 | evidence_69 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_398 | evidence_69 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_403 | evidence_38 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_407 | evidence_38 | case_407: Unresolved state: support_platform/support_3802 | INCOMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_408 | evidence_38 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_409 | evidence_38 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_411 | evidence_38 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_412 | evidence_38 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_419 | evidence_39 | case_419: Unresolved state: support_platform/support_2944 | INCOMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_423 | evidence_68 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_424 | evidence_68 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_427 | evidence_68 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_430 | evidence_68 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_448 | evidence_66 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_45 | evidence_37, evidence_55 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_452 | evidence_66 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_455 | evidence_43 | case_455: Unresolved state: support_platform/support_2055 | INCOMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_456 | evidence_43 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_457 | evidence_43 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_458 | evidence_43 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_462 | evidence_43 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_463 | evidence_65 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_464 | evidence_65 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_467 | evidence_65 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_470 | evidence_65 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_479 | evidence_45 | case_479: Unresolved state: support_platform/support_4665 | INCOMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_480 | evidence_45 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_493 | evidence_63 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_494 | evidence_63 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_497 | evidence_63 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_502 | evidence_63 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_503 | evidence_47 | case_503: Unresolved state: support_platform/support_2295 | INCOMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_506 | evidence_47 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_512 | evidence_47 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_515 | evidence_48 | case_515: Unresolved state: support_platform/support_4533 | INCOMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_524 | evidence_62 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_530 | evidence_62 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_532 | evidence_62 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_55 | evidence_32 | case_55: Unresolved state: backup_service/backup_9287 | INCOMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_58 | evidence_05 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_59 | evidence_05 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_60 | evidence_05 | Unsupported COMPLETE: required deletion coverage is unproven; retention alone does not prove deletion | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_64 | evidence_93 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_69 | evidence_93 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_70 | evidence_93 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |
| case_97 | evidence_89 | Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source | COMPLETE unproven; obtain explicit pre-cutoff selector/state readback, then rerun strict audit |

## Public sample blockers

- case_01: case_01: no admissible subject-linked state evidence
- case_02: case_02: no admissible subject-linked state evidence
- case_04: case_04: no admissible subject-linked state evidence
- case_07: case_07: Unresolved state: support_platform/support_001
- case_13: case_13: Unresolved state: support_platform/support_4218
- case_21: Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source
- case_25: Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source
- case_26: Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source
- case_27: Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source
- case_28: Unsupported COMPLETE: required deletion coverage is unproven; unbound account readbacks in admitted source

## Shared limitations and next action

- case_55 storage/association facts are verified; restoration permission is not. All 27 eligible sources and activity/history were examined. Its empty candidate plan is a semantic limitation; obtain an explicit pre-cutoff access observation. No REPORT_RESTORE_RISK or VERIFY_RESTORE_BLOCKED is emitted.
- Unsupported COMPLETE predictions assume no additional untreated copy; unknown-required-state INCOMPLETE does not assert an active violation. Every assumption is counted separately. Emitted citation/operation PASS checks do not establish global semantic certainty.
- Missing sample account/analytics/security operations lack admissible bindings or exist only in excluded later captures. Evidence-supported attachment/account/tombstone extras remain even when omitted from public references. More linkage cannot be obtained by copying golden IDs.
- Installed local AI works on four bounded authored intent fixtures; final runtime needs zero calls. Initial malformed replies were rejected, then fixed by explicit JSON instructions. Tiny fixture success does not establish full-dataset gain. The rejected cloud credential was not retried.
- A fresh isolated virtualenv installed pinned pypdf from official PyPI after a workspace TEMP workaround for sandbox ACL. verify_environment.py checks dependency origin/user-site isolation; the release checker records actual clean execution. Final raw trace export waits until session ends and app closes as required by official instructions. Originals remain preserved. No HackerRank upload occurred.
- Output privacy review passes. Contest-specific public-publication terms remain NOT VERIFIED: the registration page requires login, and Windows browser automation stopped because it could not verify the URL. The conditional public output commit is withheld; its hash is recorded in the sanitized GitHub release record. General content ownership does not establish event-specific permission.
- New source-review AI batches failed bounded validation and were not used. No accuracy benefit or complete reproducibility is claimed for that optional experiment.

## Source repair checkpoint

See SOURCE_REPAIR_REPORT.md for exact defects, the preserved baseline and measured safety-driven regression. Missing attachment exclusivity is an unresolved policy condition; it does not authorize DELETE. General media row geometry and broader ambiguous intent remain limited.

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

## Final targeted review

TARGETED_ACCURACY_REVIEW.md records all twelve dated ownership reviews and the replayed case_13 regression. No accuracy recovery is supported. Singleton lists without exclusivity attestations stay UNKNOWN; shared attachments have no supplied REDACT fallback. Four new tests cover these semantics and source-boolean integrity. Final inference remains zero model calls/tokens; historical experiments are separate.

## Current repository presentation

See ACTUAL_ARCHITECTURE.md for implemented capabilities and boundaries. README now clones the fork feature branch, highlights default-main risk and documents source-only ZIP reproduction without private development checkpoints. Inference remains unchanged; all three plan failures and 103 uncertain decisions remain.
