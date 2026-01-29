# Self-Correcting Enterprise Invoice Agent

A **multi-agent system** that executes a complex business process (automated invoice reconciliation) and handles its own errors via a **Manager** agent. Built for **recruiter impact**: run with `docker-compose up` and see it in ~30 seconds.

---

## The "Why"

**Built to solve the problem of unreliable tool-calling in financial workflows.**

- **Tool calls fail** (API timeouts, rate limits, bad payloads). This agent **catches errors and retries or applies a fallback** instead of crashing.
- **High-stakes actions** (e.g. paying a $10k invoice) **require human approval**. The agent **pauses and waits for explicit approve/reject** before executing payment.
- **Long-running reconciliation jobs** must survive restarts. **State is persisted to a database** so a task can be resumed from the last checkpoint.

---

## Architecture

```mermaid
flowchart LR
    subgraph LangGraph["LangGraph (State)"]
        START --> Reconcile
        Reconcile --> Route{"Manager: route"}
        Route -->|pending_payment| CheckApproval
        Route -->|failed| END
        CheckApproval -->|amount >= threshold| HITL["HITL: interrupt()"]
        HITL -->|Command(resume)| Resume
        Resume --> ExecuteOrCancel{"approved?"}
        CheckApproval -->|amount < threshold| ExecutePayment
        ExecuteOrCancel -->|yes| ExecutePayment
        ExecuteOrCancel -->|no| END
        ExecutePayment --> END
    end

    subgraph Worker["Worker (type-safe tools)"]
        Fetch[fetch_pending_invoices]
        Match[match_invoice_to_po]
        Retry[retry + fallback]
    end

    Reconcile --> Fetch
    Fetch --> Retry
    Retry --> Match
```

**Flow in short:**

1. **Reconcile** node runs the worker: fetch invoices (with **retry/fallback** on timeout) and match to POs. Type-safe tools use **Pydantic** input/output.
2. **Manager** routes: if there’s a **pending payment**, go to **Check approval**; if **failed**, end.
3. **Human-in-the-loop (HITL):** If amount ≥ threshold (e.g. $5k), **`interrupt(prompt)`** runs and the graph **pauses**. Caller sees `__interrupt__` and can show “Approve?” in UI. Resuming with **`Command(resume=True|False)`** continues the graph.
4. **Execute payment** runs only after approval (or when amount &lt; threshold). **State is persisted** at each step via LangGraph checkpointer (SQLite), so the run can be **resumed** after interrupt or restart.

---

## Quick Start

**Prerequisites:** Docker and Docker Compose.

```bash
git clone <repo>
cd enterprise-invoice-agent
docker-compose up
```

- **API:** http://localhost:8000  
- **Interactive docs:** http://localhost:8000/docs  

**Try it:**

1. **Start a run**  
   `POST /run` with body: `{"thread_id": "demo-1", "vendor_id": null}`

2. If the response contains **`__interrupt__`**, the agent is waiting for approval. Example:
   ```json
   {"__interrupt__": [{"value": {"question": "Ready to pay this $10,000.00 invoice. Approve?", ...}}], ...}
   ```

3. **Resume (approve or reject)**  
   `POST /resume` with body: `{"thread_id": "demo-1", "approved": true}` or `"approved": false`

4. **Inspect state**  
   `GET /state?thread_id=demo-1`

---

## Production

Explicit choices for **error handling**, **security (PII)**, and **cost**:

| Concern | How it’s handled |
|--------|-------------------|
| **Error handling** | **Self-correction loop:** Tool calls (e.g. `fetch_pending_invoices`) are wrapped in retry (configurable `MAX_TOOL_RETRIES`). On repeated failure, a fallback (e.g. empty list) is used and the graph continues or marks the run as failed so the Manager can route accordingly. Exceptions are stored in state as `last_error` and are not swallowed. |
| **Security (PII)** | **PII filtering:** Responses from `/run`, `/resume`, and `/state` are passed through `redact_pii()` before JSON is returned. Keys in `PII_KEYS` (e.g. `vendor_tax_id`, `bank_account`, `vendor_email`, `buyer_email`) are replaced with `[REDACTED]`. Configurable in `config.PII_KEYS`. |
| **Cost** | **No LLM in critical path by default:** The reconciliation worker uses **deterministic, type-safe tools** (Pydantic in/out). Optional LLM can be added for routing or summaries; model and provider are set via env (`OPENAI_MODEL`, `ANTHROPIC_MODEL`) so you can use smaller/cheaper models. |

---

## Tech Stack

- **Python 3.11+**
- **LangGraph** – state machine, checkpointing, interrupts (HITL)
- **Pydantic / PydanticAI** – type-safe tool I/O (e.g. `FetchInvoicesInput` → `list[dict]`); optional `pydantic_ai_agent.py` wires the same tools to a PydanticAI agent for LLM-driven tool choice
- **LangGraph Checkpoint SQLite** – state persistence for resume and HITL
- **FastAPI** – HTTP API for run, resume, state

---

## Project layout

```
enterprise-invoice-agent/
├── docker-compose.yml   # docker-compose up
├── Dockerfile
├── README.md
├── main.py              # uvicorn entrypoint
├── pyproject.toml
├── requirements.txt
└── src/enterprise_invoice_agent/
    ├── __init__.py
    ├── app.py            # FastAPI: /run, /resume, /state
    ├── config.py         # HITL threshold, retries, PII keys, model
    ├── graph.py          # LangGraph: reconcile → approval → execute
    ├── models.py         # Pydantic: Invoice, PO, ReconciliationResult
    ├── persistence.py    # SqliteSaver checkpointer
    ├── security.py       # redact_pii()
    ├── state.py          # InvoiceReconciliationState (TypedDict)
    ├── tools.py          # fetch_invoices, match_invoice, execute_payment
    └── worker.py         # run_fetch_invoices, reconcile_step, retry/fallback
```

---

## Configuration (env)

| Variable | Default | Description |
|----------|---------|-------------|
| `HITL_APPROVAL_THRESHOLD_USD` | `5000` | Payments at or above this amount require human approval. |
| `MAX_TOOL_RETRIES` | `3` | Retries for tool calls before using fallback. |
| `DB_PATH` | `./data/checkpoints.db` | SQLite path for state persistence (e.g. for Docker volume). |
| `OPENAI_MODEL` / `ANTHROPIC_MODEL` | (see `config.py`) | Used if you add LLM-based nodes. |

---

## License

MIT.
