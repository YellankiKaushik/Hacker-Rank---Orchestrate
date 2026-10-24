# Runtime usage and cost checkpoint

Generated 2026-10-24T17:01:38.841587+00:00, tied to the full 518-case attempt that produced the 420-row **partial** artifact, SHA-256 `042163b15224a55db16d7141bb43bc068b1c62ee557b479badf99cc07021dadd`. There is no completed full-dataset final output yet.

| Provider / model | Calls | Input tokens | Output tokens | Total tokens | Estimated USD |
|---|---:|---:|---:|---:|---:|
| No language model invoked | 0 | 0 | 0 | 0 | 0.00 |
| Overall runtime API totals | 0 | 0 | 0 | 0 | 0.00 |

Runtime: 4.5857 seconds. Average tokens per input request: 0/518 = 0. Average estimated API cost per input request: $0/518 = $0. No provider price assumption is needed for zero calls. This counts inference/review API usage only; it excludes the Codex engineering session, whose token consumption and cost have not been obtained as per-request telemetry and must not be assumed zero.

PDF parsing uses pypdf 6.10.0. Windows.Media.Ocr performs local screenshot recognition (English language pack), with no network API, reported token counts or billed API model. Its internal OCR model identifier is not exposed by the Windows API. The final attempt used a warm source-SHA-256 OCR cache; cold OCR was separately exercised for all 11 screenshots. The optional intent adapter is implemented and transport-tested with mocks but is inactive in this full run. A real model-list availability request returned HTTP 401. No actual inference model identity, calls or token usage exists for that rejected availability check; model quality is NOT VERIFIED. Mock model IDs/tokens are test fixtures and are excluded here. Model/pricing configuration must be explicit; no model or rate is guessed.

The report must be regenerated with `python code/evaluation/generate_reports.py` after unresolved cases are fixed and a valid 518-row output exists. These truthful zeros do not prove the hackathon's desired AI-powered investigation capability is complete.
