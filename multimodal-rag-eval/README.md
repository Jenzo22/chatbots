# Multimodal RAG with Evaluation (RAG-as-a-Service)

**Target Roles:** Western Union (Architect), Redwire Space (Software & AI Director)

A production-grade RAG system that processes **text, technical diagrams, and tables**, with a built-in **Evaluator** to measure hallucination rates. Goes beyond "Naive RAG" to demonstrate RAG Evaluation (RAGAS)—a critical skill for Principal/Architect roles.

## Key Features

| Feature | Implementation |
|---------|----------------|
| **Complex Parsing** | Unstructured.io for PDF table extraction |
| **Hybrid Search** | Vector (ChromaDB) + BM25 (keyword) retrieval |
| **Evaluation** | Ragas: Faithfulness & Answer Relevancy |
| **Dashboard** | Streamlit UI with per-query scores |
| **API** | FastAPI RAG-as-a-Service |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                       │
│         Faithfulness & Answer Relevancy per Query            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI RAG Service                       │
│                   POST /query with evaluation                 │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Hybrid RAG Pipeline                       │
│  Vector Search (ChromaDB)  +  BM25 (Keyword)  →  Fusion     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Document Ingestion                        │
│  Unstructured (PDF tables)  →  Chunking  →  Dual Index       │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
cd multimodal-rag-eval
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-your-key
```

### 3. Ingest Documents

```bash
# Ingest sample text document
python scripts/ingest.py data/sample_technical_doc.txt

# Or ingest PDFs (requires Unstructured)
python scripts/ingest.py data/
```

### 4. Run the Evaluation Dashboard

```bash
streamlit run app/dashboard.py
```

### 5. Run the API (optional)

```bash
uvicorn api.main:app --reload --port 8000
```

## Usage

### Streamlit Dashboard

1. **Query & Evaluate** tab: Enter a question, get RAG answer + Faithfulness & Answer Relevancy scores
2. **Evaluation History** tab: View all past queries with scores
3. **Ingest Documents** tab: Upload PDFs or load sample data

### API

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the system specifications?", "evaluate": true}'
```

Response:
```json
{
  "question": "What are the system specifications?",
  "answer": "The system has 8 CPU cores, 32GB RAM, NVMe SSD storage...",
  "faithfulness": 0.92,
  "answer_relevancy": 0.88,
  "sources": [...]
}
```

## Evaluation Metrics (Ragas)

- **Faithfulness** (0-1): How factually consistent is the response with retrieved context? Higher = less hallucination.
- **Answer Relevancy** (0-1): Does the answer directly address the user's question?

## Tech Stack

- **RAG:** LlamaIndex, ChromaDB, BM25
- **Parsing:** Unstructured (PDF tables), fallback: SimpleDirectoryReader
- **Evaluation:** Ragas (Faithfulness, AnswerRelevancy)
- **UI:** Streamlit
- **API:** FastAPI

## Why This Gets You Hired

Most candidates build "Naive RAG" (basic vector search + LLM). This project demonstrates:

1. **RAG Evaluation** – Understanding hallucination rates and relevancy metrics
2. **Hybrid Search** – Combining semantic + keyword retrieval for technical docs
3. **Complex Parsing** – Table extraction from PDFs (Unstructured)
4. **Production Patterns** – API-as-a-Service, evaluation dashboard, configurable pipeline

## Project Structure

```
multimodal-rag-eval/
├── app/
│   └── dashboard.py      # Streamlit evaluation UI
├── api/
│   └── main.py           # FastAPI RAG service
├── src/
│   ├── parsers/          # Unstructured PDF, fallback
│   ├── rag/              # Hybrid RAG pipeline
│   └── evaluation/       # Ragas evaluator
├── scripts/
│   └── ingest.py         # Document ingestion
├── data/                 # Sample docs, uploads
├── config.py
├── requirements.txt
└── README.md
```

## License

MIT
