"""
retriever.py — Context retriever for RAG pipeline.
"""

from typing import List, Tuple
from loguru import logger
from langchain.schema import Document
from .vector_store import FarmingVectorStore


class FarmingRetriever:
    """Retrieve relevant farming knowledge chunks for a given query."""

    def __init__(self, k: int = 5):
        self.k = k
        self.vector_store = FarmingVectorStore()

    def retrieve(self, query: str) -> List[Document]:
        """Return top-k relevant documents for the query."""
        docs = self.vector_store.similarity_search(query, k=self.k)
        logger.info(f"Retrieved {len(docs)} documents for query: {query[:60]}")
        return docs

    def retrieve_with_scores(self, query: str) -> List[Tuple[Document, float]]:
        """Return documents with similarity scores."""
        try:
            results = self.vector_store.store.similarity_search_with_score(query, k=self.k)
            return results
        except Exception as exc:
            logger.error(f"retrieve_with_scores failed: {exc}")
            return []

    def format_context(self, documents: List[Document], max_chars: int = 3000) -> str:
        """Format retrieved documents into a context string for the LLM."""
        context_parts = []
        total = 0
        for doc in documents:
            source = doc.metadata.get("source", "Knowledge Base")
            text = doc.page_content.strip()
            if total + len(text) > max_chars:
                break
            context_parts.append(f"[Source: {source}]\n{text}")
            total += len(text)
        return "\n\n---\n\n".join(context_parts)
