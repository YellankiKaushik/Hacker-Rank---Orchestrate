> PHASE 2 ADDENDUM — current session also contains the Phase 1 audit and Phase 2 repairs. Include the verified original build rollout and this audit/repair rollout after both finish and applications close. The older one-session example below is incomplete for the final release. No active trace export, fake ZIP or automatic app closure occurs. Staged log copies remain PENDING PRIVACY REVIEW until human review.

# Final trace handoff — perform after session end

Status **NOT VERIFIED while the contributing session is active**. No live rollout has been copied or described as a final archive. Follow the unchanged agent_trace_instructions.md: finish relevant sessions, then quit the app/CLI before copying files. Preserve originals unchanged.

The three primary submission files are output.csv, code.zip and the private root log.txt (chat_transcript). The additional structured archive is agent-trace.zip, separate from code.zip and log.txt. The AI interview is a separate explanation of architecture, source investigation, policy, ordering, measured accuracy failures, limitations and actual inference usage. No upload has been performed.

## Confirmed trace selection

The directly contributing coding session used Codex Desktop. Its structured rollout is:

`%USERPROFILE%\.codex\sessions\2026\10\24\rollout-2026-10-24T18-58-34-01a16e19-4e9b-7ab3-a545-29b51a31636b.jsonl`

The targeted review checked the two earlier matching-CWD candidates. User-message purpose and role/type metadata identify automatic permission-assessment sessions, each with zero tool calls, rather than additional interactive coding sessions:

- `sessions/2026/10/24/rollout-2026-10-24T18-58-59-01a16e19-b04d-78d3-864f-1fba4d5559b9.jsonl`
- `sessions/2026/10/25/rollout-2026-10-25T00-09-48-01a16f36-3f3c-76e0-8758-913dd5481956.jsonl`

These originals remain preserved. They are excluded from the default coding-trace copy, not automatically copied just because the working directory matches. No internal assessment messages or reasoning are included in this handoff. The main rollout retains the coding prompts, assistant actions, tool requests and returned results.

No other harness was used by this implementation run. If the participant separately used another coding/planning/debugging/review session, include its original relevant structured export in that harness's own staging subfolder, following the official instructions. An open IDE window alone does not establish a separate agent session; do not invent a conversation ID or copy an entire application-data directory.

## Exact post-session Windows procedure

1. Finish this session and every additional contributing session, then quit Codex/the other contributing apps. Open a separate PowerShell window at the repository root.
2. Run the following only after closure. It creates new staging and preserves the original date structure. If CODEX_HOME was customized, set $traceHome to that verified directory instead of the default below.

```powershell
$traceHome = Join-Path $env:USERPROFILE '.codex'
$relativeTrace = 'sessions\2026\10\24\rollout-2026-10-24T18-58-34-01a16e19-4e9b-7ab3-a545-29b51a31636b.jsonl'
$sourceTrace = Join-Path $traceHome $relativeTrace
$stageRoot = Join-Path (Get-Location) 'agent-trace'
if (-not (Test-Path -LiteralPath $sourceTrace -PathType Leaf)) { throw 'Verified rollout file is missing' }
if (Test-Path -LiteralPath $stageRoot) { throw 'Use a new empty agent-trace staging directory; preserve prior copies' }
$destination = Join-Path $stageRoot (Join-Path 'codex' $relativeTrace)
New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
Copy-Item -LiteralPath $sourceTrace -Destination $destination
```

3. Review staged copies before sharing. Remove/redact keys, tokens, passwords, cookies, private keys, personal information, unrelated source/window inventories, other projects and material not permitted to share. Preserve JSONL structure and valid JSON escaping. Keep originals untouched. Exclude auth.json, config.toml, settings, credential stores, .env, the whole .codex directory and unrelated session-index entries. Add separately confirmed contributing sessions only after the same relevance/privacy review.
4. Validate redacted JSONL without printing its contents:

```powershell
Get-ChildItem -LiteralPath '.\agent-trace' -Filter '*.jsonl' -File -Recurse | ForEach-Object {
    Get-Content -LiteralPath $_.FullName -Encoding utf8 | ForEach-Object {
        $null = ConvertFrom-Json -InputObject $_ -ErrorAction Stop
    }
}
```

5. Only after review/validation, create the separate ZIP and record its hash:

```powershell
Compress-Archive -LiteralPath '.\agent-trace' -DestinationPath '.\agent-trace.zip'
Get-FileHash -LiteralPath '.\agent-trace.zip' -Algorithm SHA256
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead((Join-Path (Get-Location) 'agent-trace.zip'))
try { $archive.Entries | Select-Object -ExpandProperty FullName } finally { $archive.Dispose() }
```

6. Confirm the ZIP contains only intended redacted structured traces, date folders and deliberately included supporting artifacts. Keep log.txt separate. Neither traces nor log.txt belong in the public Git repository or code.zip. A successful ZIP build is not a privacy review; inspect contents before submission. Submit only when the participant explicitly authorizes it. The exact portal field for the additional trace ZIP remains unverified; no upload or completed interview is claimed.
