"""Hybrid RAG Pipeline: Vector (Semantic) + BM25 (Keyword) Search.

Combines dense retrieval (ChromaDB) with sparse retrieval (BM25) for
improved accuracy on technical documents with specific terminology.
"""

import os

# Required for QueryFusionRetriever async in sync contexts (Streamlit, scripts)
import nest_asyncio
nest_asyncio.apply()
from pathlib import Path
from typing import Optional

import chromadb
from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

try:
    from llama_index.retrievers.bm25 import BM25Retriever
    import Stemmer
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False


class HybridRAGPipeline:
    """RAG pipeline with hybrid Vector + BM25 retrieval."""

    def __init__(
        self,
        chroma_persist_dir: str = "./chroma_db",
        collection_name: str = "multimodal_rag",
        llm_model: str = "gpt-4o-mini",
        embedding_model: str = "text-embedding-3-small",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        top_k: int = 5,
        openai_api_key: Optional[str] = None,
    ):
        self.chroma_persist_dir = chroma_persist_dir
        self.collection_name = collection_name
        self.top_k = top_k

        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set")

        # Configure LlamaIndex Settings
        Settings.llm = OpenAI(model=llm_model, api_key=api_key)
        Settings.embed_model = OpenAIEmbedding(
            model=embedding_model,
            api_key=api_key,
        )

        self._splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        # Initialize ChromaDB
        Path(chroma_persist_dir).mkdir(parents=True, exist_ok=True)
        self._chroma_client = chromadb.PersistentClient(path=chroma_persist_dir)
        self._chroma_collection = self._chroma_client.get_or_create_collection(
            collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._vector_store = ChromaVectorStore(chroma_collection=self._chroma_collection)

        self._docstore: Optional[SimpleDocumentStore] = None
        self._index: Optional[VectorStoreIndex] = None
        self._query_engine: Optional[RetrieverQueryEngine] = None

    def _ensure_index(self) -> VectorStoreIndex:
        """Ensure index exists; create empty if needed."""
        if self._index is not None:
            return self._index

        self._docstore = SimpleDocumentStore()
        storage_context = StorageContext.from_defaults(
            docstore=self._docstore,
            vector_store=self._vector_store,
        )
        self._index = VectorStoreIndex(
            nodes=[],
            storage_context=storage_context,
        )
        return self._index

    def ingest_documents(self, documents: list[Document]) -> None:
        """Ingest documents into the hybrid index."""
        index = self._ensure_index()
        nodes = self._splitter.get_nodes_from_documents(documents)
        self._docstore.add_documents(nodes)
        index.insert_nodes(nodes)
        self._index = index
        self._query_engine = None  # Rebuild on next query

    def _build_query_engine(self) -> RetrieverQueryEngine:
        """Build query engine with hybrid retriever."""
        if self._query_engine is not None:
            return self._query_engine

        index = self._ensure_index()
        vector_retriever = index.as_retriever(similarity_top_k=self.top_k)

        if HAS_BM25:
            bm25_retriever = BM25Retriever.from_defaults(
                docstore=index.docstore,
                similarity_top_k=self.top_k,
                stemmer=Stemmer.Stemmer("english"),
                language="english",
            )
            retriever = QueryFusionRetriever(
                [vector_retriever, bm25_retriever],
                num_queries=1,
                use_async=True,
            )
        else:
            retriever = vector_retriever

        self._query_engine = RetrieverQueryEngine.from_retriever(retriever)
        return self._query_engine

    def query(
        self,
        question: str,
        return_sources: bool = True,
    ) -> dict:
        """Query the RAG pipeline and return response with optional sources."""
        engine = self._build_query_engine()
        response = engine.query(question)

        result = {
            "answer": str(response),
            "question": question,
        }

        if return_sources and response.source_nodes:
            result["sources"] = [
                {
                    "text": node.text[:500] + "..." if len(node.text) > 500 else node.text,
                    "score": getattr(node, "score", None),
                }
                for node in response.source_nodes
            ]
            result["retrieved_contexts"] = [node.text for node in response.source_nodes]

        return result

    def get_retrieved_contexts(self, question: str) -> list[str]:
        """Get retrieved context strings for evaluation (Ragas)."""
        engine = self._build_query_engine()
        retriever = engine.retriever
        nodes = retriever.retrieve(question)
        return [node.text for node in nodes]
