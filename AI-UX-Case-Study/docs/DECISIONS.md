# Decision Log: AI UX Case Study

This document captures the **why** behind key design and implementation choices.

---

## 1. Mock-first AI client

**Decision:** Abstract AI behind `generateResponse()`. Use mock when GCP is not configured; use Vertex AI when `GOOGLE_CLOUD_PROJECT` and `GOOGLE_APPLICATION_CREDENTIALS` are set.

**Rationale:**
- Anyone can run the app locally without a GCP account.
- UX patterns (uncertainty, progressive disclosure, accessibility) can be developed and tested without API keys.
- Production path is a config change, not a code change.

**Alternatives considered:** Requiring Vertex AI from day one—rejected because it blocks reproducibility for contributors without GCP.

---

## 2. Confidence and hedging

**Decision:** Vertex AI does not return confidence scores. We derive a heuristic: detect hedging phrases (“might”, “could”, “I think”) and show a lower confidence band + banner when present.

**Rationale:**
- Users benefit from knowing when the model is uncertain.
- Heuristic is transparent and reproducible; we document it in the UI (“Detected hedging: …”).

**Alternatives considered:** Not showing uncertainty—rejected because it misleads users. Using a separate classifier for confidence—rejected for scope; heuristic is sufficient for the case study.

---

## 3. Progressive disclosure

**Decision:** One primary surface (Prompt Playground). Other patterns (Uncertainty, Progressive Disclosure, Accessibility) are separate sections revealed via tabs.

**Rationale:**
- Reduces cognitive load: users see one main task first.
- Aligns with “progressive disclosure” as a pattern we’re demonstrating.
- Sections are still reachable for evaluators and case-study readers.

---

## 4. Accessibility-first

**Decision:** Implement keyboard navigation, visible focus (`:focus-visible`), ARIA (labels, live regions, roles), and `prefers-reduced-motion` / `prefers-contrast` from the start.

**Rationale:**
- AI interfaces are often text-heavy and dynamic; screen reader and keyboard users must be supported.
- Documenting these choices in the UI reinforces the case study’s “accessibility-first AI” message.

---

## 5. BigQuery for metrics

**Decision:** Log each interaction (latency, confidence, template, hedging) to BigQuery when GCP is configured; otherwise log to console.

**Rationale:**
- Enables analysis of latency, accuracy proxies, and cost over time.
- Optional: no BigQuery setup required for local runs.
- Schema is simple (timestamp, lengths, latencyMs, confidence, modelUsed, templateId, hasHedging, sessionId).

---

## 6. Next.js API route for generate

**Decision:** Single `POST /api/generate` that calls `generateResponse()` and `recordInteraction()`.

**Rationale:**
- Keeps API keys and Vertex AI on the server.
- One place to add rate limiting, validation, and metrics.
- Frontend stays framework-agnostic of GCP SDK.

---

## 7. Cloud Run deployment

**Decision:** Dockerfile uses Next.js `output: 'standalone'`; Cloud Build builds the image and deploys to Cloud Run.

**Rationale:**
- Serverless, scales to zero, pay-per-use.
- Fits “reproducible deployment” requirement; others can run the same pipeline with their project.
