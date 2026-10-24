# GhostTrace Guard checkpoint and interview notes

## Accuracy-recovery continuation

The implementation now has 91 passing test methods, explicit dated resource-reference links, controlled source rereads and caches, conservative replica-state handling, activity state checks, semantic artifact validation and a bounded optional intent adapter. Exact public cases improved from 8/32 to 9/32. Primary/reviewed status accuracy remains 29/32 and 24/32. No cases from the original 98-case blocker set were defensibly recovered; the accepted partial artifact still has 420 rows. See RECOVERY_AUDIT.md and the regenerated evaluation/usage reports.

P1–P4 investigation and repairs are implemented and evaluated. P5's provider protocol/budgets/fallback are implemented and tested with mocked transport, while live model quality is NOT VERIFIED because model discovery returned HTTP 401. P6 shows a measured one-case exact improvement, not competitive correctness. P7 remains FAIL for the final 518-row output. P8's archive/extraction/reproducibility gates are executed by `code/release_check.py`; actual PASS/FAIL/NOT VERIFIED results are written to `artifacts/READINESS.md`. Raw traces remain separate until the session ends. No model can supply missing provenance.

The older G0–G5 table below describes the initial checkpoint. Current measured evidence takes precedence over its historical test counts and unimplemented-AI wording.

The official problem statement, AGENTS.md and immutable participant sources override the proposed root DOCS design pack. This is an implemented modular local Python CLI, not a finished submission or a cloud system.

Upstream was fetched again during this build. Commit `0eddbbd` only corrects the challenge URL in AGENTS.md from `wwww` to `www`; the dataset and output contract are unchanged. It was inspected, not merged. The fork's main remains untouched.

| Gate | Actual evidence | Status |
|---|---|---|
| G0 requirements, runtime, census | All required available docs read; measured CSV schemas/counts; all 94 evidence files ingested; PDF rendering and screenshot inspection; bundled Python 3.12.14 | Performed; absent companion docs noted |
| G1 runnable baseline and validator | `code/main.py`, `compiler.py`, `validator.py`, atomic output and exact schema tests | Implemented, but full 518-row acceptance fails |
| G2 primary investigation | `identity.py`, `adapters.py`, `engine.py`, `policy.py`; actual sample evaluation | Implemented baseline; retrieval/negative-state bindings remain incomplete |
| G3 independent review and selective AI | `reviewer.py` reopens/reparses source and rejects unsupported COMPLETE; tests exercise concrete challenges | Deterministic review active; optional LLM not implemented or used |
| G4 evaluation | 52 test methods; complete 32-sample denominator; full 518-case attempt; evaluation/usage Markdown | Measured, with explicit failures |
| G5 release artifacts | Source ZIP can be built and clean-extraction checked; partial predictions and private transcript preserved | NOT ready: no valid 518-row final output; trace close-and-package pending |

## Implemented boundaries

- Loader: exact CSV columns, duplicate keys, contained evidence paths and size bound. Failures are explicit.
- Identity: dated email/phone/hash aliases and stable IDs; rejects collisions; never joins by name or numeric suffix.
- Adapters: JSON snapshots/service exports/typed records; restricted fresh SQLite per dump; logfmt, JSON, bracket, pipe, syslog and cloud log wrappers; PDF text; Windows local OCR with content-hashed cache. Parsed facts retain source, scope, observed/captured dates and source locator.
- Temporal engine: exact-token subject retrieval, catalog-backed media links, source-specific inventory absence, cutoff checks and simultaneous replica conflict handling. It does not infer absence from a missing retrieved document.
- Policy/compiler: actions come from supplied policy CSV, with explicit retention, shared attachment, tombstone and restore handling. Findings are source-backed; incomplete-case future operations have empty evidence IDs. Canonical phase/operation/system/resource order and seven fields are enforced.
- GhostGuard: independent source retrieval and reparse, current source hash check, scope/citation checks, missing-risk/final-verification/retention checks, and explicit profile/tombstone proof before COMPLETE. At most one bounded recheck is allowed. Shared parsers mean this is not an independently authored reasoning engine.
- Evaluator: public references are read only after inference. It counts unresolved cases as failures and separately reports reference agreement versus source integrity.
- Runtime usage: no language-model calls; local OCR is the only machine-learning extraction service used. Coding-session token consumption is not represented by the runtime's zero API totals.

## Known design tradeoffs to explain in the interview

1. A successful deletion operation is a claim; snapshots/readbacks can contradict it.
2. Both capture and effective observation must precede `audit_at`; later restore success cannot prove past permission.
3. A stable tombstone reference may remain, while direct identifiers must be redacted.
4. Active connectors and open restore paths must be addressed before record changes; retained archives/journals are not deleted by default.
5. A COMPLETE draft backed only by a retained journal is withheld, even when that reduces sample status agreement.
6. Extra evidence-backed risks and missing source links are investigated as semantic differences; canonical sample arrays are never copied into the engine.
7. Optional language models cannot create absent evidence. Any future API task must have bounded calls, actual usage telemetry, source grounding and measured benefit.

Next implementation priority: improve explicit binding of identifier-free profile/readback rows without guessing IDs; strengthen media field scope/contradiction handling; then rerun all checks. See UNRESOLVED_ISSUES.md for each affected case. No root source instructions, datasets or problem statement were modified; only implementation instructions were added to README.
