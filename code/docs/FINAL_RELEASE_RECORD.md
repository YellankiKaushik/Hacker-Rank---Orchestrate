# Final release record — GhostTrace Guard 0.5.1

Classification: **B — structurally valid with documented semantic uncertainty**. Fully evidence-proven submission readiness: **FAIL**. No upload, AI interview, hidden score or leaderboard position is claimed.

## Version and source revision

- Branch: `feat/orchestrate-october26`.
- Latest implementation commit: `98ff287ba8c64424cbf622fff02196104ba973fa`. This record is committed separately; its documentation-only commit does not change the implementation.
- Official participant/contract baseline: `acb3dfca6e94e4803a26e72c49074a488de93c93`.
- Official upstream main checked: `0eddbbd33f682eae0a2770d67412af8a3cf4af20`; its only change from the baseline corrects a URL in AGENTS.md. The dataset tree and problem contract are identical. Local official files remain unchanged as instructed.
- Dataset Git tree checked: `9a1e5358fad9a29e37f5d61177aaf5041d1112d6`; official inputs unchanged: PASS.
- Official problem statement SHA-256: `8f795329dd20b97c96d74fdfbc4ecc892c95bb3de2f2262a6e75d6547e621b18`.
- AGENTS.md SHA-256: `5f1898f12d7c7e9991c4e4b1c038dbab478d64b154a384d27ed7f67066474157`.
- Trace instructions SHA-256: `a7d9dd5882178dec57b95101d5364f8bf8588a4e0c68967ae6eb9f0e0945ba14`.

## Actual artifacts and commands

The final measured report/inference command from the repository root was:

```powershell
& '.\tmp\repair-venv\Scripts\python.exe' -X utf8 code/evaluation/generate_reports.py
& '.\tmp\repair-venv\Scripts\python.exe' -X utf8 code/release_check.py
```

The report command generates all 518 root predictions and both mandatory reports. Equivalent direct CLI `python code/main.py --mode candidate` was exercised in two fresh processes and clean extraction. Default strict mode remains separate and preserves prior output when proof is missing.

| Artifact | SHA-256 | Size |
|---|---|---:|
| output.csv | `b4301131db2c2f874feadff55dcc38fea0b595d9b1430d7a8f248ed63b57e283` | 530496 bytes |
| code.zip | `9d1c08bd05ddea7ebc3980b9cd94db466a53c350d8d07785d4c6b31accb577ec` | 157836 bytes |

The ZIP has 66 members. Fixed archive timestamp/permissions, sorted members and normalized LF source text make bytes independent of checkout mtimes/line endings. A second archive build has the identical SHA-256. Clean extraction runs tests, public samples, the expected strict block, every-row candidate generation and original-source validation. This hash-bearing FINAL_RELEASE_RECORD.md is excluded from code.zip to avoid a recursive hash dependency. The archive itself is ignored and not committed.

## Actual quality (preserved 5b9a098 baseline versus repaired current)

| Metric | Previous | Current |
|---|---|---|
| Candidate status accuracy | 29/32 | 29/32 |
| Strict sample statuses | 24/32 | 22/32 |
| Exact cases | 9/32 | 8/32 |
| Exact seven-field step precision | 114/164 (69.51%) | 107/158 (67.72%) |
| Exact seven-field step recall | 114/193 (59.07%) | 107/193 (55.44%) |
| Missing / extra reference resources | 34 / 3 | 36 / 3 |
| False COMPLETE / false INCOMPLETE | 0 / 3 | 0 / 3 |
| Strict accepted evaluation cases | 427/518 | 415/518 |
| Candidate rows | 518/518 | 518/518 |
| Uncertain predictions | 91 | 103 |

Safety repairs from baseline 5b9a098 reduce sample exact matches from 9/32 to 8/32 and strict acceptance from 427 to 415; no accuracy gain or new subject/resource link is claimed. Conditional attachment deletion is now withheld without exclusivity proof. Every missing reference resource is checked against admitted facts, raw source/OCR mentions, cutoffs and binding paths. The common gaps are anonymous readbacks without selectors, missing state observations and later-only captures. The three extras have source-backed relationships and remain. Evaluation-only expected IDs never enter production inference.

## Tests, isolation and usage

- 140 unit/synthetic integration tests passed; 0 failed. Two fresh candidate processes reproduced the exact output hash.
- Clean dependency installation: PASS. Fresh Python venv, pinned pypdf 6.10.0 installed from official PyPI, package origin inside venv and user-site disabled. The sandbox TEMP ACL error was resolved with a workspace-local temporary directory. Full release and extracted execution used this environment.
- Source-backed cited steps: 1019; no fabricated references detected. Emitted source/operation checks do not prove missing obligations.
- Final 518-case model usage: 0 calls, 0 input/0 output tokens, $0.00 estimated API fee. Deterministic inference plus local OCR; no LLM is required.
- Local intent experiment: gemma4:e4b, 9 calls, 1305 input/181 output tokens. Final authored-fixture score 4/4 including abstention versus 3/4 deterministic; no dataset gain claimed.
- New source-review experiment: gemma4:e4b, 2 calls, 1240 input/1536 output tokens. Accepted batches 0/2; deterministic baseline 6/6. Valid-output reproducibility was not established; failed replies never enter inference.
- Combined prior development experiments: 11 calls, 2545 input/1717 output tokens, zero API fee. Local hardware/electricity and Codex engineering cost are unmeasured. No rejected cloud credential was retried.
- Source-repair end-to-end intent experiment: `gemma4:e4b`, 2 actual successful calls, 309 input/49 output tokens, API USD 0.00; accepted 2/2 authored fixtures through source review, export and fresh validation. Initial sandbox socket denials are transport failures with no model usage returned. These measurements do not enter final inference totals or establish dataset accuracy gain.


## Independent release gates

| Gate | Result |
|---|---|
| CLEAN_DEPENDENCY_INSTALL | PASS |
| CODE_TESTS | PASS |
| SAMPLE_STATUS_NO_REGRESSION | PASS |
| SAMPLE_EXACT_NO_REGRESSION | FAIL |
| HIDDEN_OR_COMPETITIVE_QUALITY | NOT VERIFIED |
| OUTPUT_CONTENT_PRIVACY | PASS |
| CSV_SCHEMA_VALIDITY | PASS |
| CITATION_INTEGRITY | PASS |
| TEMPORAL_VALIDITY | PASS |
| POLICY_VALIDITY | PASS |
| SOURCE_PROVENANCE | PASS |
| SEMANTIC_CERTAINTY | FAIL |
| SUBMISSION_ROW_COUNT | PASS |
| STRICT_AUDIT_COVERAGE | FAIL |
| OFFICIAL_CONTRACT_VALIDITY | FAIL |
| REPRODUCIBILITY | PASS |
| USAGE_REPORT | PASS |
| CODE_ZIP | PASS |
| CHAT_TRANSCRIPT | PASS |
| AGENT_TRACE | NOT VERIFIED |
| OVERALL_SUBMISSION_READINESS | FAIL |

Regression gates compare the preceding checkpoint. Numerical sample quality is shown above, independently of tests and packaging. 8/32 exact does not establish competitive quality; the exact no-regression gate is FAIL. Official contract validity and semantic certainty fail despite valid CSV shape.

## GitHub publication decision

Output content privacy: PASS. The generated file has only prescribed fields, stable IDs/enums and numbering; no raw identities, source text, credentials or local paths were found. Public repository visibility was verified. output.csv currently tracked: **False**.

The user's output-publication instruction is conditional on contest-rule consistency. Contest-specific publication/sharing terms remain **NOT VERIFIED**: public event instructions and general content ownership were checked, but registration redirects to login and Windows browser automation stopped because it could not verify the active URL. The CSV is therefore preserved locally and its hash recorded here; `git add -f output.csv` was not performed. No rule prohibition or permission is invented. Source, tests and sanitized reports are pushed; raw log.txt, traces, ZIPs, env and caches remain excluded.

Checked public sources: [official event](https://www.hackerrank.com/hackerrank-orchestrate-october26), [general content terms](https://www.hackerrank.com/about-us/terms-of-service), and the unchanged participant contract. General ownership of participant content does not establish event-specific publication conditions.

## Reproduction and trace handoff

```powershell
$base = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:TEMP = Join-Path (Get-Location) 'tmp\install-temp'
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Path $env:TEMP -Force | Out-Null
& $base -m venv tmp/repair-venv
& '.\tmp\repair-venv\Scripts\python.exe' -m pip install --index-url https://pypi.org/simple -r code/requirements.txt
& '.\tmp\repair-venv\Scripts\python.exe' -X utf8 code/verify_environment.py
& '.\tmp\repair-venv\Scripts\python.exe' -X utf8 code/evaluation/generate_reports.py
& '.\tmp\repair-venv\Scripts\python.exe' -X utf8 code/release_check.py
```

For a clean clone, provide the unchanged participant dataset beside code/. Windows screenshot OCR requires the English language pack. Raw source-hashed OCR caches are excluded from source distribution. Reports are in code/evaluation/; uncertainty is in artifacts/SUBMISSION_UNCERTAINTY_REPORT.md; executed gates in artifacts/READINESS.md. log.txt stays a separate append-only private transcript.

Trace ZIP: **NOT VERIFIED** while the session remains active. Follow code/docs/TRACE_FINALIZATION.md after finishing relevant sessions and quitting the application. Preserve structured rollouts, review/redact staged copies and exclude unrelated sessions/authentication/configuration. No live trace was copied as final.

## Remaining semantic failures

Required coverage/link and attachment ownership proof remain unresolved; see the per-case report. case_55 lacks target restore permission at 2026-04-30T11:00:00Z. Archive existence and association do not establish restoration access. No restore-risk or blocked-restoration step is fabricated. Its empty INCOMPLETE plan is structurally valid but does not fulfill semantic plan requirements. This is an available candidate for participant review, not a fully validated official-contract submission. No HackerRank upload occurred.

## Final targeted ownership and accuracy review

Baseline 43990d0: 136 tests, 29/32 statuses, 8/32 exact, 107/158 precision, 107/193 recall, 415 strict accepted and 103 uncertain. All twelve attachment cases remain UNKNOWN: dated association is proven, exclusivity is not. Replayed 5b9a098 exactly matched reference case_13 by assuming sole ownership of support_4218; the source only proves FOUND and association. No safe accuracy recovery or new relationship was found. Singleton lists now require an explicit exclusivity attestation; shared attachments cannot acquire an unsupplied REDACT action. Four new tests cover these semantics and original-source boolean integrity. See TARGETED_ACCURACY_REVIEW.md for exact original/current/reference arrays and all twelve source/selector/cutoff findings. Current measurements and all release gates are shown above.

## Changed files for the targeted review

Implementation commit 98ff287ba8c64424cbf622fff02196104ba973fa changes these 18 source/test/documentation files relative to the preserved 43990d0 checkpoint. The hash-bearing release record is committed separately and excluded from code.zip.

- `README.md`
- `code/docs/RECOVERY_AUDIT.md`
- `code/docs/SOURCE_REPAIR_REPORT.md`
- `code/docs/TARGETED_ACCURACY_REVIEW.md`
- `code/docs/TRACE_FINALIZATION.md`
- `code/docs/UNRESOLVED_ISSUES.md`
- `code/evaluation/candidate_reports.py`
- `code/evaluation/evaluation_report.md`
- `code/evaluation/repair_report.py`
- `code/evaluation/targeted_review.py`
- `code/evaluation/usage_report.md`
- `code/ghosttrace/__init__.py`
- `code/ghosttrace/policy.py`
- `code/ghosttrace/reviewer.py`
- `code/tests/test_core.py`
- `code/tests/test_source_repairs.py`
- `code/tests/test_targeted_ownership.py`
- `code/write_release_record.py`

Tracked-source reconstruction of code.zip passed with 66 members and SHA-256 9d1c08bd05ddea7ebc3980b9cd94db466a53c350d8d07785d4c6b31accb577ec. Local artifacts/SHA256SUMS.txt records output.csv and code.zip hashes.
