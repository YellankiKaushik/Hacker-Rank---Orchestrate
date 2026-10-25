# Optional configuration examples

Final inference requires no model configuration or credentials. Use `python code/main.py --mode candidate`; use `--ai` only for bounded ambiguous intent. Model output cannot create IDs, policies or steps. The two anchored contextual bridge forms are intentionally narrow; other ambiguities abstain.

For local Ollama, set GHOSTTRACE_AI_PROVIDER=ollama and GHOSTTRACE_AI_MODEL to an actually installed model name, then add --ai. The endpoint is fixed to loopback. No provider credential is sent there. Local hardware cost is not measured.

For OpenAI, set GHOSTTRACE_AI_PROVIDER=openai, GHOSTTRACE_AI_MODEL to an explicitly chosen available model, OPENAI_API_KEY in the environment, and positive GHOSTTRACE_AI_INPUT_USD_PER_M / GHOSTTRACE_AI_OUTPUT_USD_PER_M from verified provider pricing. No key belongs in source, reports, traces or this document. No default model/price is invented. Keep any local .env uncommitted; this application reads environment variables and does not automatically load .env.

Bounds: GHOSTTRACE_AI_MAX_CALLS (default 8), GHOSTTRACE_AI_MAX_COST_USD (default .05), GHOSTTRACE_AI_TIMEOUT_SECONDS (default 10), GHOSTTRACE_AI_RETRIES (default 1), GHOSTTRACE_AI_MAX_OUTPUT_TOKENS (default 256). See AIConfig constraints in ghosttrace/ai.py. Calls and actual tokens/API estimates are reported separately from cache hits and transport failures. Authentication failures stop retries. Historical local experiments are not final inference usage.

OCR: Windows English language pack and Windows.Media.Ocr access, or separately installed tesseract English elsewhere. pypdf is pinned in requirements.txt. Non-Windows OCR has not been validated on this release. Cache paths can be overridden; cache/venv/dataset/credentials never belong in code.zip.
