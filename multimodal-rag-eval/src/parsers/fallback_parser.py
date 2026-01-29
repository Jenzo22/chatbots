"""Fallback parser for when Unstructured is not available - uses SimpleDirectoryReader."""

from pathlib import Path

from llama_index.core import Document
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter


class FallbackPDFParser:
    """Simple PDF/text parser using LlamaIndex when Unstructured is unavailable."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def parse_file(self, file_path: str | Path) -> list[Document]:
        """Parse a file using SimpleDirectoryReader."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        reader = SimpleDirectoryReader(input_files=[str(path)])
        docs = reader.load_data()
        nodes = self._splitter.get_nodes_from_documents(docs)

        documents = []
        for i, node in enumerate(nodes):
            doc = Document(
                text=node.text,
                metadata={**node.metadata, "chunk_id": i, "node_id": node.node_id},
            )
            documents.append(doc)

        return documents

    def parse_directory(self, directory: str | Path) -> list[Document]:
        """Parse all supported files in a directory."""
        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {dir_path}")

        reader = SimpleDirectoryReader(input_dir=str(dir_path), recursive=True)
        docs = reader.load_data()
        nodes = self._splitter.get_nodes_from_documents(docs)

        documents = []
        for i, node in enumerate(nodes):
            doc = Document(
                text=node.text,
                metadata={**node.metadata, "chunk_id": i, "node_id": node.node_id},
            )
            documents.append(doc)

        return documents
