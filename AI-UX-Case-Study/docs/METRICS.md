# Metrics: Performance, Accuracy, Latency, Cost

This document details how we measure and report metrics for the AI UX Case Study.

---

## Performance

| Metric | Description | How we measure |
|--------|-------------|----------------|
| **Latency (ms)** | Time from API request to response | `Date.now()` before/after `generateResponse()` in API route; stored in BigQuery as `latency_ms`. |
| **Target** | p95 < 3s for Vertex AI | Monitor via BigQuery: `SELECT APPROX_QUANTILES(latency_ms, 100)[OFFSET(95)] FROM ...` |

**Local (mock):** ~800–1200 ms simulated. **Vertex AI Gemini Flash:** typically 1–4 s depending on prompt length and region.

---

## Accuracy (proxy)

We do not have ground-truth labels. We use **confidence** and **hedging** as proxies:

| Proxy | Description | How we derive it |
|-------|-------------|------------------|
| **Confidence** | 0–1 score | Heuristic: if hedging phrases detected in response → lower confidence (e.g. 0.65); else higher (e.g. 0.85). Mock varies 0.6–0.95. |
| **Hedging** | Whether the model expressed uncertainty | Detect phrases like "might", "could", "I think", "it depends" in the response text. Stored as `has_hedging` (boolean). |

**Target:** Prefer higher average confidence and fewer low-confidence responses. Use BigQuery to track `AVG(confidence)` and `COUNTIF(confidence < 0.5) / COUNT(*)`.

---

## Latency

- **Measured:** Per request, server-side, in the `/api/generate` route.
- **Logged:** In BigQuery as `latency_ms`.
- **Displayed:** In the UI under "Response metrics" (e.g. "1,234ms latency").

Example query for p50/p95 latency by model:

```sql
SELECT
  model_used,
  APPROX_QUANTILES(latency_ms, 100)[OFFSET(50)] AS p50_ms,
  APPROX_QUANTILES(latency_ms, 100)[OFFSET(95)] AS p95_ms,
  COUNT(*) AS n
FROM `ai_ux_metrics.interactions`
GROUP BY model_used;
```

---

## Cost

- **Vertex AI:** Billed per input/output token (see [Vertex AI pricing](https://cloud.google.com/vertex-ai/pricing)). We do not log token counts in this case study; you can add token counting via the Vertex AI client and store in BigQuery.
- **BigQuery:** Streaming insert and storage/query costs; typically small for this workload.
- **Cloud Run:** Billed per request and CPU/memory time; scales to zero when idle.

To estimate cost: use GCP Billing reports filtered by project and service (Vertex AI, BigQuery, Cloud Run).

---

## Reproducibility

- **Local:** No GCP cost; metrics go to console only.
- **GCP:** Same code path; set env vars and run. Metrics in BigQuery are reproducible for the same inputs (mock is non-deterministic; Vertex AI may vary slightly by run).
