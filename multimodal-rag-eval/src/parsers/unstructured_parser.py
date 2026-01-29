"""PDF parsing with Unstructured - extracts text, tables, and image metadata.

Supports complex technical documents with:
- Table extraction (structured data from PDFs)
- Image/diagram metadata (for multimodal processing)
- Hierarchical content preservation
"""

from pathlib import Path
from typing import Iterator

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter

try:
    from unstructured.partition.auto import partition
    from unstructured.chunking.title import chunk_by_title
    HAS_UNSTRUCTURED = True
except ImportError:
    HAS_UNSTRUCTURED = False


class UnstructuredPDFParser:
    """Parse PDFs using Unstructured.io - extracts tables and preserves structure."""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        strategy: str = "hi_res",  # "fast" or "hi_res" for better table extraction
    ):
        if not HAS_UNSTRUCTURED:
            raise ImportError(
                "Install unstructured: pip install 'unstructured[pdf]' 'unstructured[all-docs]'"
            )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        self._splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def _partition_pdf(self, file_path: Path) -> list:
        """Partition PDF into elements (text, tables, images)."""
        elements = partition(
            filename=str(file_path),
            strategy=self.strategy,
            infer_table_structure=True,  # Critical for table extraction
            include_page_breaks=True,
        )
        return list(elements)

    def _element_to_text(self, element) -> str:
        """Convert Unstructured element to text with type metadata."""
        text = str(element)
        elem_type = type(element).__name__
        if elem_type == "Table":
            return f"[TABLE]\n{text}\n[/TABLE]"
        if elem_type == "Image":
            return f"[IMAGE: {getattr(element, 'metadata', {}).get('image_path', 'diagram')}]\n{text}"
        return text

    def parse_file(self, file_path: str | Path) -> list[Document]:
        """Parse a PDF file into LlamaIndex Documents."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        elements = self._partition_pdf(path)
        full_text_parts = []
        metadata_base = {"source": str(path), "file_name": path.name}

        for elem in elements:
            elem_text = self._element_to_text(elem)
            if elem_text.strip():
                full_text_parts.append(elem_text)

        full_text = "\n\n".join(full_text_parts)
        if not full_text.strip():
            return []

        # Create single document, then split into chunks
        doc = Document(text=full_text, metadata=metadata_base)
        nodes = self._splitter.get_nodes_from_documents([doc])

        # Convert nodes back to Documents for compatibility
        documents = []
        for i, node in enumerate(nodes):
            doc = Document(
                text=node.text,
                metadata={**metadata_base, "chunk_id": i, "node_id": node.node_id},
            )
            documents.append(doc)

        return documents

    def parse_directory(self, directory: str | Path) -> list[Document]:
        """Parse all PDFs in a directory."""
        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {dir_path}")

        all_docs = []
        for pdf_path in dir_path.glob("**/*.pdf"):
            try:
                docs = self.parse_file(pdf_path)
                all_docs.extend(docs)
            except Exception as e:
                print(f"Warning: Failed to parse {pdf_path}: {e}")

        return all_docs
