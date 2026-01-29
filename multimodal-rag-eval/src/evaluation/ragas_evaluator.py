"""Ragas-based RAG evaluation - Faithfulness & Answer Relevancy.

Measures hallucination rates and answer quality:
- Faithfulness: How factually consistent is the response with retrieved context?
- Answer Relevancy: Does the answer directly address the user's question?
"""

import os
from dataclasses import dataclass
from typing import Optional

try:
    from ragas import evaluate
    from ragas.metrics import Faithfulness, AnswerRelevancy
    from ragas import EvaluationDataset
    from langchain_openai import ChatOpenAI
    try:
        from ragas.llms import LangchainLLMWrapper
        _USE_LLM_WRAPPER = True
    except ImportError:
        LangchainLLMWrapper = None
        _USE_LLM_WRAPPER = False
    HAS_RAGAS = True
except ImportError:
    HAS_RAGAS = False
    LangchainLLMWrapper = None
    _USE_LLM_WRAPPER = False


@dataclass
class EvaluationResult:
    """Result of a single query evaluation."""

    question: str
    answer: str
    faithfulness: float
    answer_relevancy: float
    retrieved_contexts: list[str]


class RagasEvaluator:
    """Evaluate RAG responses using Ragas (Faithfulness + Answer Relevancy)."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        openai_api_key: Optional[str] = None,
    ):
        if not HAS_RAGAS:
            raise ImportError(
                "Install ragas: pip install ragas langchain-openai"
            )

        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set")

        self._llm = ChatOpenAI(model=model, api_key=api_key)
        self._evaluator_llm = LangchainLLMWrapper(self._llm) if _USE_LLM_WRAPPER else self._llm

    def evaluate_single(
        self,
        question: str,
        answer: str,
        retrieved_contexts: list[str],
    ) -> EvaluationResult:
        """Evaluate a single query-response pair."""
        # Ragas expects retrieved_contexts as list of strings per sample
        data = [{
            "user_input": question,
            "retrieved_contexts": retrieved_contexts,
            "response": answer,
        }]
        dataset = EvaluationDataset.from_list(data)

        eval_kwargs = {"dataset": dataset, "metrics": [Faithfulness(), AnswerRelevancy()]}
        if self._evaluator_llm is not None:
            eval_kwargs["llm"] = self._evaluator_llm
        result = evaluate(**eval_kwargs)

        # Handle both dict and Result object
        if hasattr(result, "to_pandas"):
            df = result.to_pandas()
            faithfulness = float(df["faithfulness"].iloc[0]) if "faithfulness" in df.columns else 0.0
            answer_relevancy = float(df["answer_relevancy"].iloc[0]) if "answer_relevancy" in df.columns else 0.0
        else:
            faithfulness = float(result.get("faithfulness", 0.0))
            answer_relevancy = float(result.get("answer_relevancy", 0.0))

        return EvaluationResult(
            question=question,
            answer=answer,
            faithfulness=faithfulness,
            answer_relevancy=answer_relevancy,
            retrieved_contexts=retrieved_contexts,
        )

    def evaluate_batch(
        self,
        data: list[dict],
    ) -> list[EvaluationResult]:
        """Evaluate a batch of query-response pairs.

        Each item in data should have: user_input, response, retrieved_contexts
        """
        dataset = EvaluationDataset.from_list(data)
        eval_kwargs = {"dataset": dataset, "metrics": [Faithfulness(), AnswerRelevancy()]}
        if self._evaluator_llm is not None:
            eval_kwargs["llm"] = self._evaluator_llm
        result = evaluate(**eval_kwargs)

        # Ragas returns per-sample scores in result
        results = []
        if hasattr(result, "to_pandas"):
            df = result.to_pandas()
            for i, row in df.iterrows():
                item = data[i] if i < len(data) else {}
                results.append(EvaluationResult(
                    question=item.get("user_input", ""),
                    answer=item.get("response", ""),
                    faithfulness=float(row.get("faithfulness", 0.0)),
                    answer_relevancy=float(row.get("answer_relevancy", 0.0)),
                    retrieved_contexts=item.get("retrieved_contexts", []),
                ))
        else:
            # Fallback: run single evaluations
            for item in data:
                single = self.evaluate_single(
                    question=item["user_input"],
                    answer=item["response"],
                    retrieved_contexts=item["retrieved_contexts"],
                )
                results.append(single)

        return results
