# Final full-candidate runtime usage

Generated 2026-10-25T01:21:20.924479+00:00. Run generated all 518 of 518 predictions; output SHA-256 `b4301131db2c2f874feadff55dcc38fea0b595d9b1430d7a8f248ed63b57e283`. Strict accepted 415, uncertain 103. Warm-cache runtime 7.9360 seconds.

| Final runtime provider/model | Calls | Input tokens | Output tokens | Total tokens | Estimated API USD |
|---|---:|---:|---:|---:|---:|
| No language model invoked | 0 | 0 | 0 | 0 | 0.00 |
| Overall final 518-case run | 0 | 0 | 0 | 0 | 0.00 |

Average tokens per request: 0/518 = 0. Average API cost per request: $0/518 = $0. These figures exclude Codex engineering-session usage/cost, which is unmeasured here. Windows.Media.Ocr is local screenshot extraction, exposes no model ID/token usage, and uses a source-hashed cache. pypdf 6.10.0 extracts PDF text. No cloud model/rate is invented.

## Separate live local development experiment

Ollama loopback, installed model `gemma4:e4b`: 9 actual calls, 1305 input + 181 output = 1486 tokens. Per-model totals equal these experimental overall totals. Includes initial four formatting failures, one diagnostic and final four-fixture check (4/4 including abstention versus 3/4 baseline). Actual server usage is measured; mock tokens excluded. Zero API fee; hardware/electricity cost NOT VERIFIED. These experimental tokens are not final 518-case inference.

Optional AI is bounded to deterministic intent abstentions. Strict two-field schema, exact input quotes, cache invalidation by provider/model/schema/prompt/input, call/output/timeout limits, and fallback remain enforced. It cannot generate IDs, policy or steps. Cloud access remains unverified after the historical HTTP 401 and was not retried. The deterministic full run does not claim an LLM investigation or an AI dataset accuracy gain.

Additional source-review experiment on gemma4:e4b: 2 calls, 1240 input + 1536 output tokens, zero API fee. Both bounded batches failed validation and were excluded from inference. Combined observed development experiments: 11 calls, 2545 input + 1717 output tokens. These are separate from the final run's zeros. Local hardware/electricity and Codex engineering cost remain unmeasured.

## Source-repair intent integration experiment

Ollama loopback `gemma4:e4b`: 2 actual calls, 309 input + 49 output = 358 tokens; API fee $0.00. End-to-end accepted 2/2 authored fixtures (one deletion, one temporary suspension), through Engine, Guard, atomic CSV writing and fresh source validation. Both deterministic baselines abstain. No dataset accuracy improvement is inferred. Initial sandbox socket denials made two transport attempts, zero successful model calls and no returned token usage; they are recorded separately, not as zero-token completions. The final 518-case run above still uses zero model calls.
