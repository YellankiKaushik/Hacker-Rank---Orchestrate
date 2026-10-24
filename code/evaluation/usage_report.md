# Runtime usage and cost checkpoint

Generated 2026-10-24T15:58:12.183564+00:00, tied to the full 518-case attempt that produced the 420-row **partial** artifact, SHA-256 `8f4bcd41e6baf4a5ca41ddff5e04749f04e82cc271342662d9a2c41a853b3497`. There is no completed full-dataset final output yet.

| Provider / model | Calls | Input tokens | Output tokens | Total tokens | Estimated USD |
|---|---:|---:|---:|---:|---:|
| No language model invoked | 0 | 0 | 0 | 0 | 0.00 |
| Overall runtime API totals | 0 | 0 | 0 | 0 | 0.00 |

Runtime: 5.9706 seconds. Average tokens per input request: 0/518 = 0. Average estimated API cost per input request: $0/518 = $0. No provider price assumption is needed for zero calls. This counts inference/review API usage only; it excludes the Codex engineering session, whose token consumption and cost have not been obtained as per-request telemetry and must not be assumed zero.

PDF parsing uses pypdf 6.10.0. Windows.Media.Ocr performs local screenshot recognition (English language pack), with no network API, reported token counts or billed API model. Its internal OCR model identifier is not exposed by the Windows API. The final attempt used a warm source-SHA-256 OCR cache; cold OCR was separately exercised for all 11 screenshots. No optional language/vision API adapter is implemented or claimed active.

The report must be regenerated with `python code/evaluation/generate_reports.py` after unresolved cases are fixed and a valid 518-row output exists. These truthful zeros do not prove the hackathon's desired AI-powered investigation capability is complete.
