# Final release record — presentation and package audit

Runtime 0.6.0. **Classification C — operational BEST-EFFORT, official plan compliance FAIL.** This current record supersedes older package hashes/counts; historical Phase 1/2 artifacts remain preserved privately. No hidden score, upload or completed interview is claimed.

Packaged source/implementation revision: `26a9e02c9c1247de2a5af52ab4aa26a7e1451db5` on feat/orchestrate-october26. This hash-bearing record is committed separately and excluded from code.zip, avoiding recursive hashes. The final documentation-only commit and verified remote SHA are recorded in the private FINAL_GITHUB_AND_SUBMISSION_AUDIT.md after push.

## GitHub presentation

The judge-safe source URL is https://github.com/YellankiKaushik/Hacker-Rank---Orchestrate/tree/feat/orchestrate-october26 . Remote default branch remains main at starter `acb3dfca6e94e4803a26e72c49074a488de93c93`; the root URL therefore opens starter content, not the implementation. No default-branch change, merge into main or force push was performed. Empty repository description remains an owner metadata action; available connector capabilities do not edit it.

README now documents the fork/feature clone, actual GhostTrace/GhostGuard/AuditShield flow, evidence/policy/provenance controls, strict versus candidate modes, current metrics/failures, optional AI truthfully and clean-checkout source ZIP reproduction. ACTUAL_ARCHITECTURE.md is a sanitized implemented-capability map; untracked DOCS proposals were not blindly published. Legacy metric-report code no longer overwrites the curated README.

## Current artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| output.csv | 530496 | b4301131db2c2f874feadff55dcc38fea0b595d9b1430d7a8f248ed63b57e283 |
| code.zip | 184021 | 73fd043222e281c0e99d3c1bde49e38e1134011f3454c7818561b148ff2668b5 |

Previous ZIP SHA-256 `040644f738fe8c651db4eb6be10f179b1e6fc1b2ebf3b6fb7bcaec4b481271fb` was superseded because README/docs/packaging sources changed. It is not the new upload archive. CSV bytes and inference behavior remain unchanged.

## Actual validation

155 tests pass, 0 failures/errors/skips: prior 154 plus one meaningful source-only packaging regression requiring no dataset/private checkpoint. Fresh Python 3.12.14 environment installed pypdf 6.10.0 from official PyPI. Cold Windows English OCR succeeded; non-Windows fidelity remains unverified. Extracted tests, independent all-32 scorer and two full candidate processes succeeded; extracted source-only ZIP rebuild produced identical archive bytes. All 76 literal members, CRC, safe selection, required reports/config/OCR/source/tests and source matching were checked. No dataset, raw log/trace, credentials, environment/cache or nested archive was packaged. Bounded secret scans are not a comprehensive security audit.

Public sample primary/strict/candidate statuses: 27/32, 22/32, 29/32; exact/sequence 8/32. Candidate exact step precision 107/158, recall 107/193; fields 917/1365; reference citation agreement 57/58; missing/extra resources 36/3. No algorithm accuracy gain claimed.

518 expected rows: 355 INCOMPLETE, 153 COMPLETE, 10 NOT_APPLICABLE. Shared strict accepts 415; unproven candidate decisions 90 COMPLETE/13 INCOMPLETE. Emitted source/citation/time checks pass within documented interpretation for 1019 cited steps. Independent plan checker fails case_479, case_503 (verification-only; no exclusive attachment ownership) and case_55 (empty; no target restore permission). No guessed identity, owner, permission, dummy finding or evasive label was introduced. Full semantic certainty/official readiness remain FAIL.

Final inference still uses zero LLM calls/input/output/total tokens, zero average tokens/request and estimated API $0 total/per request. Local OCR and compute/engineering costs are distinct/unmeasured. Historical Ollama experiments remain separate; no artificial model call occurred.

## Reproduce from the clean solution branch

```text
python -m venv .venv
.venv/Scripts/python -m pip install -r code/requirements.txt
.venv/Scripts/python -m unittest discover -s code/tests -v
.venv/Scripts/python code/main.py --mode candidate
.venv/Scripts/python code/independent_contract.py
.venv/Scripts/python code/package_submission.py --source-only --output code.zip
```

Supply external participant dataset and platform OCR. The checker correctly exits nonzero for the three failed plans. Source-only packaging checks selection/integrity, not runtime predictions; full validation was executed separately. Default strict mode refuses export while 103 unresolved cases remain. Development release tools may still require saved checkpoints; they are not the evaluator's minimal path.

Official dataset tree `9a1e5358fad9a29e37f5d61177aaf5041d1112d6`, main, AGENTS.md, problem statement and trace instructions are preserved. Root original log remains append-only. Private staged code ZIP must be synchronized to this new hash; transcript automated review is separate from HUMAN PRIVACY REVIEW PENDING. The real agent-trace.zip remains absent until contributing sessions end/apps close and reviewed copies are explicitly approved. No private artifacts were committed, and no HackerRank upload/interview occurred.
