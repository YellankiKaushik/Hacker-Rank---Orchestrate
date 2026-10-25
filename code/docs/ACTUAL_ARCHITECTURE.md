# GhostTrace Guard — actual implementation and boundaries

This document describes the implemented local Python CLI, not the original untracked design proposal. Runtime version remains 0.6.0. Current classification C: three invalid plans and 103 unproven candidate decisions. Presentation polish adds a source-only packaging option and one packaging regression; deletion inference is unchanged.

## Actual flow

`main.run` loads the participant corpus, case rows and evidence index. `intent.deletion_intent` and `intent_resolution` establish authorization before subject deletion analysis. `IdentityGraph.aliases/resolve` admits dated snapshot/history identifiers and requires a unique subject. `RelationshipIndex.bind/validates` traverses exact identifiers, dated catalogs and explicit upstream-resource references.

`EvidenceIndex` reads SQL/JSON/log/text and PDF/PNG text. Each `Fact` retains source, capture/observation time, scope and locator. `Fact.admissible` checks both times. `Engine.investigate` selects as-of states across supported physical copies and explicit negative queries, applies `Policy`, and compiles a draft through `compiler.compile_steps`.

`GhostGuard.review` reopens source bytes/hashes, checks citations/relationships/chronology/known obligations, and permits one bounded reread of at most four files. `invariants.py` separately checks authorization, raw identifiers, positive readback contradictions, controls and unsafe retention/ownership operations. Extraction, schemas, identity and some domain logic remain shared; rereading is not a fully independent truth oracle.

Strict mode withholds output on unresolved proof. Explicit candidate mode discloses assumptions in a side report and atomically serializes all rows. `independent_contract.check` independently checks CSV/JSON/order/citation-reference/required phases without Engine imports; candidate mode does not waive its failures. `validate_candidate.validate` checks emitted source-grounded claims with shared domain code and raw invariants, not every possible missing obligation.

## Capability coverage

| Capability | Classification | Actual code / tests | Limits |
|---|---|---|---|
| Authorization | PARTIAL | `intent.py`, `intent_resolution.py`, `invariants.authorization_veto`; `Phase2Tests.test_negation_and_information_real_source_end_to_end` | R04 demonstrated forms fixed; arbitrary language remains limited |
| Historical identity | IMPLEMENTED | `IdentityGraph.aliases/resolve`; `IdentityTests`, `RelationshipRecoveryTests` | Unique dated aliases; no anonymous assignments; alias sets flatten edge detail |
| Supplied evidence formats | PARTIAL | `EvidenceIndex`, `media.image_text/pdf_text`; format/security tests and 94-file execution | General OCR geometry and non-Windows fidelity limited |
| Provenance-aware resources | IMPLEMENTED | `Fact`, `Link`, `Reference`, `RelationshipIndex`; explicit-reference tests | Only actual supplied relations, not exhaustive extraction |
| Temporal cutoff controls | IMPLEMENTED | `Fact.admissible`, Engine selection, reviewer chronology; future-evidence tests | Admissibility alone is not semantic correctness |
| Replicas / secondary copies | IMPLEMENTED | `Fact.copy_role`, Engine replica selection; temporal/replica regressions | Supported known topology/scope only |
| Conditional retention | PARTIAL | `Policy.action/violation/operations`; typed flags/date/legal-hold tests | Missing conditions remain unknown |
| Active flow / restore | PARTIAL | `control_state`, adapters and raw invariants; control/restore tests | Archive existence is not permission; case_55 unproven |
| Tombstone direct identifiers | IMPLEMENTED for tested structured fields | `state_of`, `identifying`, independent `identifier_paths`; R05 nested/null/stable-ID tests | Unknown schemas/media retain limits |
| Original-source reread | IMPLEMENTED | `GhostGuard.source_supports/review`; source-mutation/stale-state tests | Common adapters/relationships remain |
| Independent high-risk vetoes | IMPLEMENTED within bounded invariants | `invariants.py`; correlated wrong parser/authorization, controls and positive-readback tests | Not a second whole solver or full security audit |
| Remediation / final checks | PARTIAL | `compile_steps`, validators; sequence/atomic tests | Three missing lawful plans; no generic dependency-DAG planner |
| Exact output serialization | IMPLEMENTED | `write_output`, independent all-case checker | Shape does not certify full plan semantics |
| Optional model intent | PARTIAL | `IntentAI`, schema/quote/context/bounds tests | Narrow contextual bridge; no final LLM calls or demonstrated dataset gain |
| Runtime LLM reviewer | NOT IMPLEMENTED | Historical source-review batches rejected; no runtime claim | Separate deployed reviewer not required |
| Tests / release / source packaging | IMPLEMENTED | 155 tests; source-only packaging regression, extracted runs, Git-blob consistency | Source-only integrity does not validate predictions; full maintenance tools use development checkpoints |
| Hosted SaaS/frontend | NOT APPLICABLE | Local fixed batch CLI | No deployment/auth/tenancy claim |
| Hidden accuracy / live portal | NOT VERIFIED | No hidden labels or authenticated receipt | No score/rank/upload/interview claim |

## Measured proof boundary

Candidate 518/518: 355 INCOMPLETE, 153 COMPLETE, 10 NOT_APPLICABLE. Shared strict acceptance 415; uncertainty 90 COMPLETE/13 INCOMPLETE. Public candidate status 29/32, exact/sequence 8/32, exact step precision 107/158 and recall 107/193. These are measured reference-agreement metrics, not hidden quality guarantees.

case_479/503 have only retained-record verification while attachment exclusivity is unproven. case_55 has unknown target restore permission and no plan. The independent plan gate fails all three. No future capture, dummy finding, guessed owner or evasive status repairs those gaps. See the [bounded case review](PHASE2_EVIDENCE_REVIEW.md).

The mandatory [evaluation](../evaluation/evaluation_report.md) and [usage](../evaluation/usage_report.md) reports cover current measurements. Final inference uses zero LLM calls/tokens/API fees plus local OCR; historical local experiments remain separate and compute/engineering costs are unknown.

The GitHub default main branch is starter content; use the solution branch. Root README plus code/ are packaged with fixed metadata/LF, deliberately excluding the hash-bearing release record. Private answers, logs, traces and staging do not belong in code.zip or public commits. Human privacy review and post-closure trace export remain pending.
