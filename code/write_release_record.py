"""Write a sanitized tracked record after measured release checks; never publishes files."""
import hashlib
import json
from pathlib import Path
import subprocess
from ghosttrace import __version__

ROOT=Path(__file__).resolve().parents[1]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def main():
    release=json.loads((ROOT/'artifacts/release_verification.json').read_text())
    sample=json.loads((ROOT/'tmp/sample_metrics.json').read_text())['candidate']
    usage=json.loads((ROOT/'tmp/candidate_run_metrics.json').read_text())
    publication=json.loads((ROOT/'artifacts/output_publication_check.json').read_text())
    if sha(ROOT/'output.csv')!=release['output_sha256'] or sha(ROOT/'code.zip')!=release['package']['sha256']:
        raise ValueError('Release artifact hashes changed after verification')
    commit=git('rev-parse','HEAD'); dataset=git('rev-parse','acb3dfc:dataset')
    tracked=subprocess.run(['git','ls-files','--error-unmatch','output.csv'],cwd=ROOT,capture_output=True).returncode==0
    intent_path=ROOT/'artifacts/local_ai_evaluation.json'; review_path=ROOT/'artifacts/source_review_ai_evaluation.json'
    experiment_text='- Local development experiment telemetry: NOT VERIFIED in this checkout; no unrecorded calls are assumed.\n'
    if intent_path.exists() and review_path.exists():
        intent=json.loads(intent_path.read_text()); review=json.loads(review_path.read_text())
        runs=[intent]+intent.get('previous_runs',[])
        calls=sum(v['usage']['attempts'] for v in runs); incoming=sum(v['usage']['input_tokens'] for v in runs)
        outgoing=sum(v['usage']['output_tokens'] for v in runs)
        experiment_text=(f"- Local intent experiment: {intent['requested_model']}, {calls} calls, {incoming} input/{outgoing} output tokens. Final authored-fixture score {intent['model_correct']}/4 including abstention versus {intent['baseline_correct']}/4 deterministic; no dataset gain claimed.\n"
            f"- New source-review experiment: {review['requested_model']}, {review['calls']} calls, {review['input_tokens']} input/{review['output_tokens']} output tokens. Accepted batches {sum(a['accepted'] for a in review['attempts'])}/2; deterministic baseline {review['baseline_correct']}/6. Valid-output reproducibility was not established; failed replies never enter inference.\n"
            f"- Combined prior development experiments: {calls+review['calls']} calls, {incoming+review['input_tokens']} input/{outgoing+review['output_tokens']} output tokens, zero API fee. Local hardware/electricity and Codex engineering cost are unmeasured. No rejected cloud credential was retried.\n")
    pipeline_path=ROOT/'artifacts/intent_pipeline_evaluation.json'
    if pipeline_path.exists():
        pipeline=json.loads(pipeline_path.read_text()); u=pipeline['usage']
        experiment_text+=(f"- Source-repair end-to-end intent experiment: `{pipeline['requested_model']}`, {u['successful_calls']} actual successful calls, "
            f"{u['input_tokens']} input/{u['output_tokens']} output tokens, API USD {u['estimated_cost_usd']:.2f}; accepted {pipeline['accepted']}/2 authored fixtures "
            "through source review, export and fresh validation. Initial sandbox socket denials are transport failures with no model usage returned. "
            "These measurements do not enter final inference totals or establish dataset accuracy gain.\n")
    record=f'''# Final release record — GhostTrace Guard {__version__}

Classification: **B — structurally valid with documented semantic uncertainty**. Fully evidence-proven submission readiness: **FAIL**. No upload, AI interview, hidden score or leaderboard position is claimed.

## Version and source revision

- Branch: `feat/orchestrate-october26`.
- Latest implementation commit: `{commit}`. This record is committed separately; its documentation-only commit does not change the implementation.
- Official participant/contract baseline: `acb3dfca6e94e4803a26e72c49074a488de93c93`.
- Official upstream main checked: `0eddbbd33f682eae0a2770d67412af8a3cf4af20`; its only change from the baseline corrects a URL in AGENTS.md. The dataset tree and problem contract are identical. Local official files remain unchanged as instructed.
- Dataset Git tree checked: `{dataset}`; official inputs unchanged: {release['official_inputs_unchanged']}.
- Official problem statement SHA-256: `{sha(ROOT/'problem_statement.md')}`.
- AGENTS.md SHA-256: `{sha(ROOT/'AGENTS.md')}`.
- Trace instructions SHA-256: `{sha(ROOT/'agent_trace_instructions.md')}`.

## Actual artifacts and commands

The final measured report/inference command from the repository root was:

```powershell
& '.\\tmp\\repair-venv\\Scripts\\python.exe' -X utf8 code/evaluation/generate_reports.py
& '.\\tmp\\repair-venv\\Scripts\\python.exe' -X utf8 code/release_check.py
```

The report command generates all 518 root predictions and both mandatory reports. Equivalent direct CLI `python code/main.py --mode candidate` was exercised in two fresh processes and clean extraction. Default strict mode remains separate and preserves prior output when proof is missing.

| Artifact | SHA-256 | Size |
|---|---|---:|
| output.csv | `{release['output_sha256']}` | {(ROOT/'output.csv').stat().st_size} bytes |
| code.zip | `{release['package']['sha256']}` | {(ROOT/'code.zip').stat().st_size} bytes |

The ZIP has {release['package']['members']} members. Fixed archive timestamp/permissions, sorted members and normalized LF source text make bytes independent of checkout mtimes/line endings. A second archive build has the identical SHA-256. Clean extraction runs tests, public samples, the expected strict block, every-row candidate generation and original-source validation. This hash-bearing FINAL_RELEASE_RECORD.md is excluded from code.zip to avoid a recursive hash dependency. The archive itself is ignored and not committed.

## Actual quality (preserved 5b9a098 baseline versus repaired current)

| Metric | Previous | Current |
|---|---|---|
| Candidate status accuracy | 29/32 | {sample['status_correct']}/32 |
| Strict sample statuses | 24/32 | {json.loads((ROOT/'tmp/sample_metrics.json').read_text())['strict']['status_correct']}/32 |
| Exact cases | 9/32 | {sample['exact_cases']}/32 |
| Exact seven-field step precision | 114/164 (69.51%) | {sample['step_matches']}/{sample['predicted_steps']} ({100*sample['step_precision']:.2f}%) |
| Exact seven-field step recall | 114/193 (59.07%) | {sample['step_matches']}/{sample['reference_steps']} ({100*sample['step_recall']:.2f}%) |
| Missing / extra reference resources | 34 / 3 | {sample['missing_records']} / {sample['extra_records']} |
| False COMPLETE / false INCOMPLETE | 0 / 3 | {sample['false_complete']} / {sample['false_incomplete']} |
| Strict accepted evaluation cases | 427/518 | {release['strict_accepted']}/518 |
| Candidate rows | 518/518 | {release['candidate_rows']}/518 |
| Uncertain predictions | 91 | {release['uncertain_predictions']} |

Safety repairs from baseline 5b9a098 reduce sample exact matches from 9/32 to 8/32 and strict acceptance from 427 to 415; no accuracy gain or new subject/resource link is claimed. Conditional attachment deletion is now withheld without exclusivity proof. Every missing reference resource is checked against admitted facts, raw source/OCR mentions, cutoffs and binding paths. The common gaps are anonymous readbacks without selectors, missing state observations and later-only captures. The three extras have source-backed relationships and remain. Evaluation-only expected IDs never enter production inference.

## Tests, isolation and usage

- {release['tests']} unit/synthetic integration tests passed; {release['test_failures']} failed. Two fresh candidate processes reproduced the exact output hash.
- Clean dependency installation: {release['fresh_isolated_dependency_install']}. Fresh Python venv, pinned pypdf 6.10.0 installed from official PyPI, package origin inside venv and user-site disabled. The sandbox TEMP ACL error was resolved with a workspace-local temporary directory. Full release and extracted execution used this environment.
- Source-backed cited steps: {release['source_backed_cited_steps']}; no fabricated references detected. Emitted source/operation checks do not prove missing obligations.
- Final 518-case model usage: {usage['model_calls']} calls, {usage['input_tokens']} input/{usage['output_tokens']} output tokens, ${usage['estimated_cost_usd']:.2f} estimated API fee. Deterministic inference plus local OCR; no LLM is required.
{experiment_text}

## Independent release gates

| Gate | Result |
|---|---|
'''
    record+=''.join(f'| {k} | {v} |\n' for k,v in release['gates'].items())
    record+=f'''
Regression gates compare the preceding checkpoint. Numerical sample quality is shown above, independently of tests and packaging. {sample['exact_cases']}/32 exact does not establish competitive quality; the exact no-regression gate is FAIL. Official contract validity and semantic certainty fail despite valid CSV shape.

## GitHub publication decision

Output content privacy: {publication['privacy_gate']}. The generated file has only prescribed fields, stable IDs/enums and numbering; no raw identities, source text, credentials or local paths were found. Public repository visibility was verified. output.csv currently tracked: **{tracked}**.

The user's output-publication instruction is conditional on contest-rule consistency. Contest-specific publication/sharing terms remain **NOT VERIFIED**: public event instructions and general content ownership were checked, but registration redirects to login and Windows browser automation stopped because it could not verify the active URL. The CSV is therefore preserved locally and its hash recorded here; `git add -f output.csv` was not performed. No rule prohibition or permission is invented. Source, tests and sanitized reports are pushed; raw log.txt, traces, ZIPs, env and caches remain excluded.

Checked public sources: [official event](https://www.hackerrank.com/hackerrank-orchestrate-october26), [general content terms](https://www.hackerrank.com/about-us/terms-of-service), and the unchanged participant contract. General ownership of participant content does not establish event-specific publication conditions.

## Reproduction and trace handoff

```powershell
$base = Join-Path $env:USERPROFILE '.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe'
$env:TEMP = Join-Path (Get-Location) 'tmp\\install-temp'
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Path $env:TEMP -Force | Out-Null
& $base -m venv tmp/repair-venv
& '.\\tmp\\repair-venv\\Scripts\\python.exe' -m pip install --index-url https://pypi.org/simple -r code/requirements.txt
& '.\\tmp\\repair-venv\\Scripts\\python.exe' -X utf8 code/verify_environment.py
& '.\\tmp\\repair-venv\\Scripts\\python.exe' -X utf8 code/evaluation/generate_reports.py
& '.\\tmp\\repair-venv\\Scripts\\python.exe' -X utf8 code/release_check.py
```

For a clean clone, provide the unchanged participant dataset beside code/. Windows screenshot OCR requires the English language pack. Raw source-hashed OCR caches are excluded from source distribution. Reports are in code/evaluation/; uncertainty is in artifacts/SUBMISSION_UNCERTAINTY_REPORT.md; executed gates in artifacts/READINESS.md. log.txt stays a separate append-only private transcript.

Trace ZIP: **NOT VERIFIED** while the session remains active. Follow code/docs/TRACE_FINALIZATION.md after finishing relevant sessions and quitting the application. Preserve structured rollouts, review/redact staged copies and exclude unrelated sessions/authentication/configuration. No live trace was copied as final.

## Remaining semantic failures

Required coverage/link and attachment ownership proof remain unresolved; see the per-case report. case_55 lacks target restore permission at 2026-04-30T11:00:00Z. Archive existence and association do not establish restoration access. No restore-risk or blocked-restoration step is fabricated. Its empty INCOMPLETE plan is structurally valid but does not fulfill semantic plan requirements. This is an available candidate for participant review, not a fully validated official-contract submission. No HackerRank upload occurred.
'''
    path=ROOT/'code/docs/FINAL_RELEASE_RECORD.md'; path.write_text(record,encoding='utf-8')
    print(json.dumps({'record':str(path.relative_to(ROOT)),'implementation_commit':commit,
                      'output_sha256':release['output_sha256'],'zip_sha256':release['package']['sha256'],
                      'output_tracked':tracked,'classification':'B'},indent=2))

if __name__=='__main__': main()
