"""Ingest documents into the RAG index.

Usage:
  python scripts/ingest.py data/
  python scripts/ingest.py path/to/file.pdf
"""

import os
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import get_settings, ensure_dirs
from llama_index.core import Document
from src.rag.hybrid_rag import HybridRAGPipeline

try:
    from src.parsers.unstructured_parser import UnstructuredPDFParser
    PARSER_CLS = UnstructuredPDFParser
except ImportError:
    from src.parsers.fallback_parser import FallbackPDFParser
    PARSER_CLS = FallbackPDFParser


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest.py <path_to_pdf_or_directory>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Path not found: {path}")
        sys.exit(1)

    settings = get_settings()
    if not settings.openai_api_key:
        print("Set OPENAI_API_KEY in .env or environment")
        sys.exit(1)

    ensure_dirs(settings)

    # For PDFs use Unstructured/Fallback; for txt use SimpleDirectoryReader
    if path.suffix.lower() == ".pdf":
        parser = PARSER_CLS(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        if path.is_file():
            docs = parser.parse_file(path)
        else:
            docs = parser.parse_directory(path)
    else:
        # Text/markdown - use SimpleDirectoryReader
        from llama_index.core import SimpleDirectoryReader
        from llama_index.core.node_parser import SentenceSplitter
        reader = SimpleDirectoryReader(input_files=[str(path)] if path.is_file() else str(path))
        raw_docs = reader.load_data()
        splitter = SentenceSplitter(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
        nodes = splitter.get_nodes_from_documents(raw_docs)
        docs = [Document(text=n.text, metadata=n.metadata) for n in nodes]

    if not docs:
        print("No documents extracted. Check file format.")
        sys.exit(1)

    rag = HybridRAGPipeline(
        chroma_persist_dir=settings.chroma_persist_dir,
        llm_model=settings.llm_model,
        embedding_model=settings.embedding_model,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        top_k=settings.top_k_retrieval,
    )

    rag.ingest_documents(docs)
    print(f"Ingested {len(docs)} chunks from {path}")


if __name__ == "__main__":
    main()
