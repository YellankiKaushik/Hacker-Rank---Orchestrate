# Final full-candidate runtime usage

Generated 2026-10-24T18:55:03.992821+00:00. Run generated all 518 of 518 predictions; output SHA-256 `edc5a4ea5e0ea8376a6236524fb9eb1049657767c61cb72883fc5fef787ff7f3`. Strict accepted 427, uncertain 91. Warm-cache runtime 10.9115 seconds.

| Final runtime provider/model | Calls | Input tokens | Output tokens | Total tokens | Estimated API USD |
|---|---:|---:|---:|---:|---:|
| No language model invoked | 0 | 0 | 0 | 0 | 0.00 |
| Overall final 518-case run | 0 | 0 | 0 | 0 | 0.00 |

Average tokens per request: 0/518 = 0. Average API cost per request: $0/518 = $0. These figures exclude Codex engineering-session usage/cost, which is unmeasured here. Windows.Media.Ocr is local screenshot extraction, exposes no model ID/token usage, and uses a source-hashed cache. pypdf 6.10.0 extracts PDF text. No cloud model/rate is invented.

## Separate live local development experiment

Ollama loopback, installed model `gemma4:e4b`: 9 actual calls, 1305 input + 181 output = 1486 tokens. Per-model totals equal these experimental overall totals. Includes initial four formatting failures, one diagnostic and final four-fixture check (4/4 including abstention versus 3/4 baseline). Actual server usage is measured; mock tokens excluded. Zero API fee; hardware/electricity cost NOT VERIFIED. These experimental tokens are not final 518-case inference.

Optional AI is bounded to deterministic intent abstentions. Strict two-field schema, exact input quotes, cache invalidation by provider/model/schema/prompt/input, call/output/timeout limits, and fallback remain enforced. It cannot generate IDs, policy or steps. Cloud access remains unverified after the historical HTTP 401 and was not retried. The deterministic full run does not claim an LLM investigation or an AI dataset accuracy gain.
