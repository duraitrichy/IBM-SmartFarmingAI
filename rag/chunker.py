"""
chunker.py — Text chunking for the RAG pipeline.

Uses recursive character splitting with token-aware overlap.
"""

from typing import List
from loguru import logger
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import ActiveConfig


class DocumentChunker:
    """Split documents into overlapping chunks suitable for embedding."""

    def __init__(
        self,
        chunk_size: int = ActiveConfig.CHUNK_SIZE,
        chunk_overlap: int = ActiveConfig.CHUNK_OVERLAP,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )

    def chunk(self, documents: List[Document]) -> List[Document]:
        """Split a list of documents into smaller chunks."""
        chunks = self.splitter.split_documents(documents)
        logger.info(
            f"Chunked {len(documents)} documents → {len(chunks)} chunks "
            f"(size={self.chunk_size}, overlap={self.chunk_overlap})"
        )
        return chunks
