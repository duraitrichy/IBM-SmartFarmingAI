"""
vector_store.py — ChromaDB vector store management.

Uses langchain_community.vectorstores.Chroma — compatible with chromadb 0.5.x
and requires no separate langchain-chroma package.
"""

from typing import List, Optional
from pathlib import Path
from loguru import logger
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from .embeddings import GraniteEmbeddings
from config import ActiveConfig


class FarmingVectorStore:
    """Manages the ChromaDB vector store for farming knowledge."""

    def __init__(self):
        self.config = ActiveConfig
        self.embeddings = GraniteEmbeddings()
        self._store: Optional[Chroma] = None
        Path(self.config.CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)

    @property
    def store(self) -> Chroma:
        if self._store is None:
            self._store = Chroma(
                collection_name=self.config.CHROMA_COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=self.config.CHROMA_DB_PATH,
            )
        return self._store

    def add_documents(self, documents: List[Document]) -> None:
        """Add chunked documents to the vector store."""
        if not documents:
            logger.warning("No documents to add.")
            return
        self.store.add_documents(documents)
        logger.info(f"Added {len(documents)} chunks to ChromaDB.")

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve top-k similar documents for a query."""
        try:
            return self.store.similarity_search(query, k=k)
        except Exception as exc:
            logger.error(f"similarity_search failed: {exc}")
            return []

    def get_collection_count(self) -> int:
        """Return total document count in the collection."""
        try:
            return self.store._collection.count()
        except Exception:
            return 0

    def reset(self) -> None:
        """Delete and recreate the collection (use with caution)."""
        try:
            self.store.delete_collection()
            self._store = None
            logger.warning("ChromaDB collection deleted and reset.")
        except Exception as exc:
            logger.error(f"Failed to reset collection: {exc}")
