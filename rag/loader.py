"""
loader.py — Document loader for the SmartFarmingAI RAG pipeline.

Supports PDF, DOCX, TXT, and CSV files from the knowledge base directory.
"""

import os
from pathlib import Path
from typing import List
from loguru import logger
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader,
    DirectoryLoader,
)
from langchain.schema import Document


class DocumentLoader:
    """Load all knowledge-base documents from a directory."""

    LOADER_MAP = {
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".csv": CSVLoader,
        ".docx": Docx2txtLoader,
    }

    def __init__(self, knowledge_base_path: str):
        self.kb_path = Path(knowledge_base_path)
        if not self.kb_path.exists():
            self.kb_path.mkdir(parents=True, exist_ok=True)
            logger.warning(f"Knowledge base directory created at {self.kb_path}")

    def load_all(self) -> List[Document]:
        """Recursively load all supported documents from the knowledge base."""
        documents: List[Document] = []
        for ext, loader_cls in self.LOADER_MAP.items():
            pattern = f"**/*{ext}"
            files = list(self.kb_path.glob(pattern))
            logger.info(f"Found {len(files)} {ext} files.")
            for file_path in files:
                try:
                    docs = loader_cls(str(file_path)).load()
                    for doc in docs:
                        doc.metadata["source"] = str(file_path.name)
                        doc.metadata["file_type"] = ext
                    documents.extend(docs)
                    logger.info(f"Loaded: {file_path.name} ({len(docs)} chunks)")
                except Exception as exc:
                    logger.error(f"Failed to load {file_path}: {exc}")
        logger.info(f"Total documents loaded: {len(documents)}")
        return documents

    def load_file(self, file_path: str) -> List[Document]:
        """Load a single document by path."""
        path = Path(file_path)
        ext = path.suffix.lower()
        loader_cls = self.LOADER_MAP.get(ext)
        if not loader_cls:
            raise ValueError(f"Unsupported file type: {ext}")
        docs = loader_cls(str(path)).load()
        for doc in docs:
            doc.metadata["source"] = path.name
        return docs
