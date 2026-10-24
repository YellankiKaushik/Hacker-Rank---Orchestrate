# Final trace handoff — perform after session end

Status: **NOT VERIFIED**. No live rollout was copied or represented as final. The official agent_trace_instructions.md requires finishing relevant sessions and quitting the coding application before copying files.

The harness used here is Codex Desktop. Metadata-only discovery found these exact-project-CWD session candidates. Review additional sessions' relevance before inclusion; a matching working directory alone is not proof that every turn is relevant:

- `%USERPROFILE%\.codex\sessions\2026\10\24\rollout-2026-10-24T18-58-34-01a16e19-4e9b-7ab3-a545-29b51a31636b.jsonl` — active engineering session.
- `%USERPROFILE%\.codex\sessions\2026\10\24\rollout-2026-10-24T18-58-59-01a16e19-b04d-78d3-864f-1fba4d5559b9.jsonl` — additional project session candidate.
- `%USERPROFILE%\.codex\sessions\2026\10\25\rollout-2026-10-25T00-09-48-01a16f36-3f3c-76e0-8758-913dd5481956.jsonl` — additional project session candidate discovered in final census.

No other coding harness was used by this engineering run. An open Antigravity IDE project window does not establish whether the participant used a separate coding-agent session. If it was used for this challenge, include its corresponding structured conversation folder under `%USERPROFILE%\.gemini\antigravity\brain\<conversation-id>\`, or the CLI/IDE variant named in the official instructions. Its exact conversation ID is NOT VERIFIED; do not copy the whole brain directory or unrelated projects.

After finishing sessions and closing Codex, run the following from the repository root in a separate PowerShell window. The destinations stay inside the explicit agent-trace folder. Preserve originals unchanged.

```powershell
$stage = Join-Path (Get-Location) 'agent-trace\codex'
New-Item -ItemType Directory -Path $stage -Force | Out-Null
$trace1 = Join-Path $env:USERPROFILE '.codex\sessions\2026\10\24\rollout-2026-10-24T18-58-34-01a16e19-4e9b-7ab3-a545-29b51a31636b.jsonl'
Copy-Item -LiteralPath $trace1 -Destination $stage
# Only after confirming relevance, copy the second project-session candidate:
$trace2 = Join-Path $env:USERPROFILE '.codex\sessions\2026\10\24\rollout-2026-10-24T18-58-59-01a16e19-b04d-78d3-864f-1fba4d5559b9.jsonl'
Copy-Item -LiteralPath $trace2 -Destination $stage
$trace3 = Join-Path $env:USERPROFILE '.codex\sessions\2026\10\25\rollout-2026-10-25T00-09-48-01a16f36-3f3c-76e0-8758-913dd5481956.jsonl'
Copy-Item -LiteralPath $trace3 -Destination $stage
```

Review staged copies before sharing. Redact keys/tokens/passwords/cookies, personal information, unrelated window inventory, unrelated projects and other material not permitted to share. Preserve valid JSONL and original structured formats; do not replace raw traces with screenshots or summaries. Exclude auth.json, config.toml, credential stores, settings, .env, the entire .codex directory and unrelated session_index entries. Inspect the staged copies after redaction.

Only after that review:

```powershell
Compress-Archive -LiteralPath '.\agent-trace' -DestinationPath '.\agent-trace.zip'
Get-FileHash -LiteralPath '.\agent-trace.zip' -Algorithm SHA256
```

Inspect archive members and validate the staged JSONL files before uploading. Keep log.txt as the separate chat transcript. Neither log.txt nor raw traces belong in the public Git repository or code.zip. No HackerRank upload has occurred; the exact portal destination for the extra trace ZIP remains unverified.
