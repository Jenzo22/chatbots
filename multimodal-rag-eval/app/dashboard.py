"""Streamlit Evaluation Dashboard - Faithfulness & Answer Relevancy scores.

Shows per-query evaluation metrics for RAG responses.
Target: Architect / Principal Engineer demos.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from config import get_settings, ensure_dirs
from src.rag.hybrid_rag import HybridRAGPipeline
from src.evaluation.ragas_evaluator import RagasEvaluator


def init_session_state():
    """Initialize session state for evaluation history."""
    if "eval_history" not in st.session_state:
        st.session_state.eval_history = []
    if "rag" not in st.session_state:
        st.session_state.rag = None
    if "evaluator" not in st.session_state:
        st.session_state.evaluator = None


def load_rag_pipeline():
    """Load or create RAG pipeline."""
    if st.session_state.rag is not None:
        return st.session_state.rag

    settings = get_settings()
    if not settings.openai_api_key:
        st.error("Set OPENAI_API_KEY in .env or environment")
        return None

    ensure_dirs(settings)
    rag = HybridRAGPipeline(
        chroma_persist_dir=settings.chroma_persist_dir,
        llm_model=settings.llm_model,
        embedding_model=settings.embedding_model,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        top_k=settings.top_k_retrieval,
    )
    st.session_state.rag = rag
    return rag


def load_evaluator():
    """Load or create Ragas evaluator."""
    if st.session_state.evaluator is not None:
        return st.session_state.evaluator

    settings = get_settings()
    if not settings.openai_api_key:
        return None

    evaluator = RagasEvaluator(model=settings.ragas_evaluator_model)
    st.session_state.evaluator = evaluator
    return evaluator


def main():
    st.set_page_config(
        page_title="RAG Evaluation Dashboard",
        page_icon="📊",
        layout="wide",
    )

    init_session_state()

    st.title("📊 Multimodal RAG Evaluation Dashboard")
    st.markdown(
        "**Faithfulness** (hallucination rate) & **Answer Relevancy** scores for every query. "
        "Built for Principal/Architect-level RAG evaluation."
    )

    # Sidebar - API key check
    with st.sidebar:
        st.header("Configuration")
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Required for RAG and Ragas evaluation",
            )
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key

        st.divider()
        st.markdown("### Metrics")
        st.markdown("- **Faithfulness**: Factual consistency with retrieved context (0-1)")
        st.markdown("- **Answer Relevancy**: How well the answer addresses the question (0-1)")
        st.markdown("Lower faithfulness = higher hallucination risk")

    # Main content
    tab1, tab2, tab3 = st.tabs(["🔍 Query & Evaluate", "📈 Evaluation History", "📁 Ingest Documents"])

    with tab1:
        st.subheader("Query RAG & Get Evaluation Scores")

        query = st.text_input(
            "Enter your question",
            placeholder="e.g., What are the key specifications in the technical document?",
        )

        if st.button("Query & Evaluate", type="primary"):
            if not query.strip():
                st.warning("Enter a question first")
            elif not os.getenv("OPENAI_API_KEY"):
                st.error("Set OPENAI_API_KEY in sidebar or .env")
            else:
                with st.spinner("Querying RAG and evaluating..."):
                    rag = load_rag_pipeline()
                    evaluator = load_evaluator()

                    if rag is None or evaluator is None:
                        st.error("Failed to initialize RAG or Evaluator")
                    else:
                        try:
                            result = rag.query(query, return_sources=True)
                            answer = result.get("answer", "")
                            contexts = result.get("retrieved_contexts", [])

                            if not contexts:
                                st.warning("No documents ingested. Add documents in the Ingest tab first.")
                                st.info("Using sample context for evaluation demo.")
                                contexts = ["Sample context: No documents loaded. Ingest PDFs to enable retrieval."]

                            eval_result = evaluator.evaluate_single(
                                question=query,
                                answer=answer,
                                retrieved_contexts=contexts,
                            )

                            # Store in history
                            st.session_state.eval_history.insert(0, {
                                "question": query,
                                "answer": eval_result.answer,
                                "faithfulness": eval_result.faithfulness,
                                "answer_relevancy": eval_result.answer_relevancy,
                            })

                            # Display results
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(
                                    "Faithfulness",
                                    f"{eval_result.faithfulness:.2%}",
                                    help="Higher = less hallucination",
                                )
                            with col2:
                                st.metric(
                                    "Answer Relevancy",
                                    f"{eval_result.answer_relevancy:.2%}",
                                    help="Higher = more relevant to question",
                                )

                            st.subheader("Answer")
                            st.write(answer)

                            with st.expander("Retrieved Contexts"):
                                for i, ctx in enumerate(contexts[:3]):
                                    st.markdown(f"**Context {i+1}**")
                                    st.text(ctx[:500] + "..." if len(ctx) > 500 else ctx)
                                    st.divider()

                        except Exception as e:
                            st.error(f"Error: {e}")
                            st.exception(e)

    with tab2:
        st.subheader("Evaluation History")

        if not st.session_state.eval_history:
            st.info("No evaluations yet. Run a query in the first tab.")
        else:
            for i, item in enumerate(st.session_state.eval_history):
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**Q:** {item['question']}")
                    with col2:
                        st.metric("Faithfulness", f"{item['faithfulness']:.2%}")
                    with col3:
                        st.metric("Relevancy", f"{item['answer_relevancy']:.2%}")
                    st.markdown(f"**A:** {item['answer'][:200]}...")
                    st.divider()

    with tab3:
        st.subheader("Ingest Documents")

        st.markdown(
            "Upload PDFs or add files to `data/` directory. "
            "Uses **Unstructured** for table extraction from PDFs."
        )

        uploaded_files = st.file_uploader(
            "Upload PDFs",
            type=["pdf"],
            accept_multiple_files=True,
        )

        if st.button("Ingest Uploaded Files"):
            if not uploaded_files:
                st.warning("Upload PDF files first")
            else:
                settings = get_settings()
                ensure_dirs(settings)
                uploads_dir = Path(settings.uploads_dir)
                uploads_dir.mkdir(parents=True, exist_ok=True)

                for f in uploaded_files:
                    path = uploads_dir / f.name
                    with open(path, "wb") as out:
                        out.write(f.getbuffer())

                st.success(f"Saved {len(uploaded_files)} files to {uploads_dir}")

                # Parse and ingest
                try:
                    from src.parsers.unstructured_parser import UnstructuredPDFParser
                except ImportError:
                    from src.parsers.fallback_parser import FallbackPDFParser
                    parser = FallbackPDFParser(
                        chunk_size=settings.chunk_size,
                        chunk_overlap=settings.chunk_overlap,
                    )
                else:
                    parser = UnstructuredPDFParser(
                        chunk_size=settings.chunk_size,
                        chunk_overlap=settings.chunk_overlap,
                    )

                from llama_index.core import Document

                all_docs = []
                for f in uploaded_files:
                    path = uploads_dir / f.name
                    docs = parser.parse_file(path)
                    all_docs.extend(docs)

                if all_docs:
                    rag = load_rag_pipeline()
                    if rag:
                        rag.ingest_documents(all_docs)
                        st.success(f"Ingested {len(all_docs)} chunks from {len(uploaded_files)} PDFs")
                    else:
                        st.error("Failed to load RAG pipeline")
                else:
                    st.warning("No content extracted from PDFs")

        # Sample data option
        st.divider()
        st.subheader("Quick Start: Sample Data")
        if st.button("Load Sample Technical Document"):
            from llama_index.core import Document
            sample_text = """
            [TABLE]
            Component | Specification | Value
            CPU | Cores | 8
            RAM | Capacity | 32GB
            Storage | Type | NVMe SSD
            [/TABLE]

            System Architecture Diagram: The Redwire Space payload processing unit connects
            to the Western Union payment gateway via secure API. Data flows through
            encrypted channels with TLS 1.3.

            Key integration points:
            - Payment validation: 99.9% uptime SLA
            - Transaction latency: < 200ms p95
            - Compliance: PCI-DSS Level 1
            """
            docs = [Document(text=sample_text, metadata={"source": "sample"})]
            rag = load_rag_pipeline()
            if rag:
                rag.ingest_documents(docs)
                st.success("Loaded sample technical document. Try querying: 'What are the system specifications?'")
            else:
                st.error("Set OPENAI_API_KEY first")


if __name__ == "__main__":
    main()
