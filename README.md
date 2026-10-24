# HackerRank Orchestrate - October 2026

## GhostTrace Guard candidate

**B: structurally valid with documented semantic uncertainty.** The candidate produces all 518 rows. Strict audit accepts 427 and withholds 91; seven previous blockers now pass the contract-based obligation check. All 1,031 cited steps pass source/time/provenance checks. Semantic certainty remains FAIL, including case_55's uncertainty-only empty plan. Do not interpret row coverage as proof that deletion is complete.

Public sample: primary 29/32 statuses; strict GhostGuard 24/32; every-row candidate 29/32. All variants have 9/32 exact cases. Exact accuracy has not substantially improved. There are 116 passing test methods. Reports include every sample case and all remaining limitations.

### Setup and execution

Python 3.12+ and `pip install -r code/requirements.txt` provide the parser dependency (pypdf). Windows screenshot extraction uses Windows.Media.Ocr with an English language pack and PowerShell; the source-hash cache is excluded from Git and ZIP. A fresh isolated dependency install is NOT VERIFIED. The installed runtime and cold OCR have been exercised. On another OS supply a compatible OCR adapter rather than assuming Windows OCR is available.

From the repository root:

```text
python -m unittest discover -s code/tests -v
python code/main.py --mode strict
python code/main.py --mode candidate
python code/validate_candidate.py
python code/validate_output.py
python code/evaluation/generate_reports.py
python code/release_check.py
```

Strict mode intentionally exits with unresolved cases and preserves the previous root output. Candidate mode validates shape before atomic replacement of root output.csv, and writes artifacts/SUBMISSION_UNCERTAINTY_REPORT.md. `validate_candidate.py` separately checks every emitted source/operation and reports semantic certainty. The unchanged strict `validate_output.py` rejects the unproven candidate; its failure is expected and is never reported as a PASS. The release checker runs source validation, two fresh processes, and clean ZIP extraction/execution. It writes artifacts/READINESS.md with separate gates and does not upload anything.

The WindowsApps Python alias on this workstation is unusable. Tested commands use:

```powershell
$py = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -X utf8 -m unittest discover -s code/tests -v
& $py -X utf8 code/main.py --mode candidate
& $py -X utf8 code/validate_candidate.py
& $py -X utf8 code/evaluation/generate_reports.py
& $py -X utf8 code/release_check.py
```

Provide unchanged `dataset/` beside the extracted source. `--dataset PATH`, `--cache-dir PATH`, `--output PATH`, `--metrics-path PATH`, and `--uncertainty-report PATH` support isolated runs. Sample answers are read only by evaluators after inference. `code/evaluation/baseline.md` records this implementation's historical abstentions for report comparisons; it is never an inference input.

### Decision modes and review

Strict audit rejects C required-proof gaps, D contradictions and E unsupported sources. A supported and B supported-but-nonessential missing observations can pass. The official contract applies policy to relevant records; it does not require a profile/tombstone step in every case. A retained journal alone cannot prove deletion; unobserved linked obligations or unidentified account rows in a subject-linked source still block COMPLETE. GhostGuard rereads source bytes and policy-critical fields and checks identity provenance, cutoffs, missing operations and intent. Shared domain parsers limit independence.

Candidate policy is explicitly limited: established violations predict INCOMPLETE; an unknown required state predicts INCOMPLETE without inventing a specific violation; otherwise observed compliant treatments predict COMPLETE under an unverified closed-evidence assumption. All 91 unsupported full-proof status inferences are recorded separately. No resource/evidence ID, restore-risk claim or missing step is fabricated. Case_55 contains no admissible allowed/blocked restoration fact, so it has no source-supported step to emit. Its shape-valid INCOMPLETE empty array does not satisfy strict semantic plan requirements.

### Optional local/cloud intent AI

AI runs only on deterministic intent abstentions and cannot generate IDs, policies or steps. Use `--ai` with explicit configuration. An already installed local model was tested on four authored intent fixtures: `gemma4:e4b` scored 4/4 including abstention versus deterministic 3/4. Initial formatting failures were rejected; explicit JSON-only instructions fixed them. The nine total experimental calls used 1,305 input and 181 output tokens. Zero API fee; local compute costs unmeasured. This small experiment does not show dataset-level gain. Final 518-case runtime uses zero model calls/tokens and $0 estimated API cost.

For an already running Ollama server on loopback:

```powershell
$env:GHOSTTRACE_AI_PROVIDER = 'ollama'
$env:GHOSTTRACE_AI_MODEL = 'gemma4:e4b' # Must match your installed model; no download is performed.
& $py -X utf8 code/main.py --mode candidate --ai
```

Transport is fixed to http://127.0.0.1:11434/api/chat and never sends cloud authorization headers. Exact quote grounding, strict two-field schema, cache versioning, eight-call/256-output-token/10-second default bounds and one transient retry remain enforced. Set GHOSTTRACE_AI_MAX_CALLS, GHOSTTRACE_AI_MAX_OUTPUT_TOKENS, GHOSTTRACE_AI_TIMEOUT_SECONDS and GHOSTTRACE_AI_RETRIES to reduce bounds. Local API price is zero; electricity/hardware is not estimated.

Cloud OpenAI transport requires OPENAI_API_KEY, GHOSTTRACE_AI_PROVIDER=openai, an explicit GHOSTTRACE_AI_MODEL and verified positive GHOSTTRACE_AI_INPUT_USD_PER_M / GHOSTTRACE_AI_OUTPUT_USD_PER_M prices. The estimated reservation budget defaults to $0.05 (GHOSTTRACE_AI_MAX_COST_USD). The prior HTTP 401 was not retried. No working cloud model is claimed. Read secrets only from the environment; never commit credentials, caches or private traces.

### Artifacts and limits

- output.csv: all 518 best-effort predictions, atomic shape validation passed.
- artifacts/SUBMISSION_UNCERTAINTY_REPORT.md: every uncertain prediction and omitted obligation.
- artifacts/READINESS.md and candidate_validation.json: executed independent gates.
- code/evaluation/evaluation_report.md and usage_report.md: required measured reports.
- code.zip: source-only package with clean extraction/execution checks; no datasets, caches, credentials, logs or nested archives.
- log.txt: private append-only transcript, separate from Git and the code ZIP.

Original session traces remain preserved. Follow agent_trace_instructions.md: finish sessions and close the app before copying relevant traces, redact staged copies, then archive separately. Final trace ZIP is NOT VERIFIED while this session is active. No HackerRank upload has occurred.

The original official starter instructions follow.

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
