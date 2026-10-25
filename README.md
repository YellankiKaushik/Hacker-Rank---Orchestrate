# GhostTrace Guard 0.6.0 — HackerRank Orchestrate October 2026

**BEST-EFFORT / NOT FULLY VALIDATED — classification C.** The CLI runs, but three INCOMPLETE plans (case_479, case_503, case_55) fail the official plan contract. Candidate 518/518, shared strict acceptances 415, uncertainty 103 (90 COMPLETE/13 INCOMPLETE). Public candidate 29/32 statuses, 8/32 exact plans; precision 107/158 and recall 107/193. R04/R05 repaired; 154 tests pass. See code/docs/IMPLEMENTATION_STATUS.md and mandatory code/evaluation/ reports.

## Clean extraction and evaluator run

Extract code.zip into a new directory. Place unchanged participant dataset/ beside code/ and root README.md. Install Python 3.12+ and the platform OCR dependency, then from the extraction root:

```text
python -m venv .venv
.venv/Scripts/python -m pip install -r code/requirements.txt
.venv/Scripts/python -m unittest discover -s code/tests -v
.venv/Scripts/python code/main.py --mode candidate
.venv/Scripts/python code/independent_contract.py
```

On macOS/Linux replace .venv/Scripts/python with .venv/bin/python. Windows English OCR uses Windows.Media.Ocr and needs the English language pack plus file-access permissions; restrictive sandboxes may deny it. Other platforms require separately installed tesseract and English data. No warm OCR cache is supplied. Non-Windows extraction fidelity remains unverified.

The explicit candidate command atomically creates root output.csv and a separate uncertainty report. The independent checker currently exits nonzero and lists all three invalid plans: this is an expected honest failure, not an installation error. Default `python code/main.py` is strict and refuses output replacement with 103 unresolved cases. Never interpret all-row candidate coverage as full proof.

For an external dataset or isolated outputs use --dataset PATH, --requests PATH, --output PATH, --cache-dir PATH, --metrics-path PATH and --uncertainty-report PATH. Main paths default relative to extracted source root, not the current shell directory. `code/validate_candidate.py` performs shared source/identity/policy checks of emitted claims; `code/independent_contract.py` is independent CSV/JSON/plan validation; `code/validate_output.py` requires strict semantic acceptance. The latter currently rejects the candidate. No sample answers enter inference.

## Implementation and optional configuration

Deterministic investigation, dated identifiers/relations, heterogeneous evidence, policy, replicas and bounded source review run locally. Original-value reviewer vetoes are independent of primary intent/state/policy functions; schemas, extraction and some relationships remain shared. See code/CONFIGURATION.md for optional AI examples and limits. Final inference uses zero LLM calls/tokens/API fees; local OCR is real extraction. AI cannot emit resource IDs or steps. Unknown evidence never authorizes inventing a relation or action. Output/log/traces/staging remain private.

## Developer release commands

In a full development checkout with saved local diagnostic checkpoints (not the minimal evaluator workflow), code/evaluation/generate_reports.py, phase2_review.py, phase2_validate.py and phase2_reports.py regenerate measurements/docs. code/release_check.py rebuilds and checks the ZIP; it writes artifacts and reports failed semantic gates honestly. code/package_submission.py also rebuilds code.zip. These are maintenance commands with side effects/checkpoint dependencies, not prerequisites for main.py inference. Do not run them to overwrite a frozen release without a checkpoint.

Finish contributing sessions and quit apps before staging/redacting structured traces under agent_trace_instructions.md. No active session is packaged as complete. Private log originals remain append-only; any staged copy is separately reviewed. No HackerRank upload or interview is performed automatically.

The original official starter guidance follows; the measured release limits above supersede old implementation-readiness claims.

## Ghost Data Still Exists

Build an AI agent that audits whether a user's personal data was actually deleted.

A deletion workflow may report **Complete** while data still exists in databases, logs, support attachments, exports, search indexes, archives, or backups. Sync and restore processes may also bring deleted data back.

For each request, the agent must first determine whether deletion was actually requested. It then returns `COMPLETE`, `INCOMPLETE`, or `NOT_APPLICABLE`, reports any remaining data or recreation risk, and produces the ordered remediation and verification steps required to finish an authorized deletion safely.

Read [`problem_statement.md`](./problem_statement.md) for the complete challenge contract.

---

## Quick Start

Clone the repository and move into the project directory:

```bash
git clone https://github.com/interviewstreet/hackerrank-orchestrate-october26.git
cd hackerrank-orchestrate-october26
```

Start your AI coding tool from the **repository root** so it automatically reads [`AGENTS.md`](./AGENTS.md) and logs your session turns to `log.txt` in the root directory.

Build your solution in `code/main.py`, or use another language and document its setup and run command clearly in your README.

Your solution must:

- Read the input files from `dataset/`
- Generate one prediction row for every request in `dataset/deletion_requests.csv`
- Write the final predictions to `output.csv` in the repository root

Run the starter Python entry point with:

```bash
python3 code/main.py
```

The blank template at `dataset/output.csv` is provided as a reference. Your final generated file for submission must be the root-level `output.csv`.


## Dataset

All participant-facing files are in `dataset/`:

| File | Contents |
| --- | --- |
| `deletion_requests.csv` | 518 requests |
| `sample_deletion_requests.csv` | 32 sample requests |
| `sample_output.csv` | Correct sample answers |
| `user_identities.csv` | Current user identities |
| `user_audit_log.csv` | Historical identity changes |
| `system_activity.csv` | Activity across services and data processes |
| `deletion_rules.csv` | Required treatment for each data category |
| `evidence_files.csv` | Manifest of supplied evidence files |
| `output.csv` | Blank output template |

Evidence is stored under `dataset/evidence/` and may include PDFs, images, logs, JSON, plain text, or SQL snapshot exports. SQL captures may contain a primary database, regional replicas, a reporting replica, or a failover replica so replication drift can be investigated directly. The `.sql` files are readable as text and executable with SQLite.

Only `deletion_requests.csv` requires answers. The other files provide evidence and context.

---

## Output

Create `output.csv` with these columns in this exact order:

```text
case_id,deletion_status,steps_json
```

Produce exactly one row per request. `deletion_status` is `COMPLETE`, `INCOMPLETE`, or `NOT_APPLICABLE`. `steps_json` is an ordered JSON array containing findings, remediation actions, and verification checks. Use an empty array (`[]`) for `NOT_APPLICABLE`. Evidence references may be a `file_id`, `activity_id`, or `audit_id`. Determine the resource state at `audit_at` from the available evidence; reported workflow statuses and operation results are claims. Use `dataset/sample_output.csv` as the format reference.

The final file must contain 518 data rows sorted by `case_id` (plus the header row). The grader parses `steps_json` as JSON, so object-key order and whitespace do not matter; array order does. Order findings, remediation, and verification in that phase order. Within a phase, follow the operation order in the problem statement, then sort by `system_id` and `resource_id`.

---

## Evaluation

`output.csv` will be compared with hidden canonical answers. Scoring considers:

- deletion assessment accuracy;
- current and historical identity resolution;
- discovery of remaining data and recreation risks;
- correct policy application and evidence references; and
- completeness and ordering of remediation and verification steps.

Your `code.zip` must include:

```text
code/evaluation/evaluation_report.md
code/evaluation/usage_report.md
```

- `evaluation_report.md` must cover case, row, field, and sequence accuracy, at least three additional evaluation cases created by you, failures found, and improvements made.
- `usage_report.md` must cover the final full-dataset run, including model providers and names, model calls, input and output tokens, total and average tokens per request, and estimated total and per-request cost. Include per-model and overall totals when using multiple models.

**Important:** Place `evaluation_report.md` and `usage_report.md` inside `code/evaluation/` (matching `code/evaluation/main.py` in this starter layout), write your complete evaluation metrics, custom evaluation test cases, and token/cost breakdowns directly inside those Markdown files, and keep prompts in source code or Markdown files. Automated code evaluation ignores raw data files (`.csv`, `.tsv`, `.json`, `.jsonl`, `.sql`, `.log`), so content stored only in those formats will not be visible to the code judge or AI interviewer.

---

## Chat Transcript

This repository includes [`AGENTS.md`](./AGENTS.md), which instructs compatible AI coding tools to append conversation summaries to `log.txt` in the repository root:

| Platform | Path |
| --- | --- |
| macOS / Linux | `<repo root>/log.txt` |
| Windows | `<repo root>\log.txt` |

- Always launch your AI coding agent from the repository root (or explicitly ask it to read `./AGENTS.md` first) so every turn is logged to `log.txt` with the required `User Prompt`, `Agent Response Summary`, `Actions`, and `Context` sections.
- Upload `log.txt` directly as your `chat_transcript` submission on HackerRank.
- Do not include API keys, tokens, credentials, or secrets in prompts, code, configuration, or `log.txt`.

---

## Packaging `code.zip` and Submission

| Item | Description |
| --- | --- |
| `code.zip` | Runnable solution, prompts, configuration, `README.md`, and `evaluation/` reports |
| `output.csv` | One answer row for each of the 518 requests in `dataset/deletion_requests.csv` |
| `chat_transcript` | The root `log.txt` file generated by your coding agent |
| AI interview | Live explanation of your architecture, approach, and evaluation |

You may use any programming language, model, framework, or retrieval approach. Include clear setup and execution instructions in `README.md` inside `code.zip`.

To package `code.zip` from the repository root without bundling the dataset:

**macOS / Linux:**

```bash
zip -r code.zip README.md code -x "*/__pycache__/*" "*/.venv/*" "*/venv/*" "*/node_modules/*" "*/.git/*" "*/.DS_Store"
```

**Windows (PowerShell):**

```powershell
Compress-Archive -Path README.md, code -DestinationPath code.zip -Force
```

When packaging `code.zip`:

- Keep your evaluation reports in `code/evaluation/` so they are bundled automatically with `code` (or add `evaluation` to the archive command above if you placed them in a top-level `evaluation/` directory).
- Do **not** include `dataset/`, virtual environments (`.venv`, `venv`, `node_modules`), or build caches (`__pycache__`). On Windows, keep `.venv` at the repository root (outside `code/`) and remove any `code/__pycache__` folders before running `Compress-Archive`.
- Do **not** include nested archives (`.zip`, `.tar`, `.gz`, `.tgz`, `.7z`, `.rar`) inside `code.zip` — submissions containing nested archive files will be rejected.

Before submitting, confirm that:

- `output.csv` has the exact header `case_id,deletion_status,steps_json` and contains all 518 data rows sorted by `case_id`;
- every `steps_json` value is a valid JSON array with consecutive step numbers starting at `1`;
- findings cite valid evidence IDs, and `COMPLETE` verification steps cite evidence proving the current state;
- proposed remediation and future verification steps use an empty `evidence_id` (`""`);
- `code.zip` includes your runnable code, `README.md`, `code/evaluation/evaluation_report.md`, and `code/evaluation/usage_report.md`;
- `log.txt` follows the `AGENTS.md` turn format and is uploaded to the `chat_transcript` slot; and
- no API keys, credentials, real personal data, or sensitive configuration values are included.
