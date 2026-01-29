"""FastAPI RAG-as-a-Service - Multimodal RAG with Evaluation.

REST API for querying RAG and getting evaluation scores.
Target: Architect / Software & AI Director demos.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from config import get_settings, ensure_dirs
from src.rag.hybrid_rag import HybridRAGPipeline
from src.evaluation.ragas_evaluator import RagasEvaluator


# Request/Response models
class QueryRequest(BaseModel):
    question: str
    evaluate: bool = True


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: Optional[list[dict]] = None
    faithfulness: Optional[float] = None
    answer_relevancy: Optional[float] = None


# App
app = FastAPI(
    title="Multimodal RAG with Evaluation",
    description="RAG-as-a-Service: Hybrid search (Vector + BM25), PDF table parsing, Ragas evaluation",
    version="1.0.0",
)

# Lazy-loaded singletons
_rag: Optional[HybridRAGPipeline] = None
_evaluator: Optional[RagasEvaluator] = None


def get_rag() -> HybridRAGPipeline:
    global _rag
    if _rag is None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")
        ensure_dirs(settings)
        _rag = HybridRAGPipeline(
            chroma_persist_dir=settings.chroma_persist_dir,
            llm_model=settings.llm_model,
            embedding_model=settings.embedding_model,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            top_k=settings.top_k_retrieval,
        )
    return _rag


def get_evaluator() -> RagasEvaluator:
    global _evaluator
    if _evaluator is None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")
        _evaluator = RagasEvaluator(model=settings.ragas_evaluator_model)
    return _evaluator


@app.get("/health")
def health():
    return {"status": "ok", "service": "multimodal-rag-eval"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """Query RAG and optionally evaluate with Ragas."""
    try:
        rag = get_rag()
        result = rag.query(request.question, return_sources=True)
        answer = result.get("answer", "")
        sources = result.get("sources", [])
        contexts = result.get("retrieved_contexts", [])

        response = QueryResponse(
            question=request.question,
            answer=answer,
            sources=sources,
        )

        if request.evaluate and contexts:
            evaluator = get_evaluator()
            eval_result = evaluator.evaluate_single(
                question=request.question,
                answer=answer,
                retrieved_contexts=contexts,
            )
            response.faithfulness = eval_result.faithfulness
            response.answer_relevancy = eval_result.answer_relevancy

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {
        "service": "Multimodal RAG with Evaluation",
        "docs": "/docs",
        "health": "/health",
        "query": "POST /query",
    }
