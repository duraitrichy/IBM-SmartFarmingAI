"""
embeddings.py — IBM Granite Embedding wrapper for LangChain.
"""

from typing import List
from loguru import logger
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models.embeddings import Embeddings as WxEmbeddings
from langchain.embeddings.base import Embeddings
from config import ActiveConfig


class GraniteEmbeddings(Embeddings):
    """LangChain-compatible wrapper around IBM Granite Embedding model."""

    def __init__(self):
        self.config = ActiveConfig
        credentials = Credentials(
            url=self.config.IBM_WATSONX_URL,
            api_key=self.config.IBM_API_KEY,
        )
        client = APIClient(credentials=credentials, project_id=self.config.IBM_PROJECT_ID)
        self._model = WxEmbeddings(
            model_id=self.config.GRANITE_EMBEDDING_MODEL,
            api_client=client,
            project_id=self.config.IBM_PROJECT_ID,
        )
        logger.info(f"GraniteEmbeddings initialised with model: {self.config.GRANITE_EMBEDDING_MODEL}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of document texts."""
        try:
            results = self._model.embed_documents(texts)
            return [r for r in results]
        except Exception as exc:
            logger.error(f"embed_documents failed: {exc}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string."""
        try:
            return self._model.embed_query(text)
        except Exception as exc:
            logger.error(f"embed_query failed: {exc}")
            raise
