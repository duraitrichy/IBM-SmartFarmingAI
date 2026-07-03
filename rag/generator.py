"""
generator.py — RAG answer generator using IBM Granite + retrieved context.
"""

from typing import Any, Dict, List
from loguru import logger
from langchain.schema import Document
from .retriever import FarmingRetriever
from agents.base_agent import BaseAgent


RAG_PROMPT = """You are an expert agricultural advisor with access to a comprehensive farming knowledge base.

Context from Knowledge Base:
{context}

Farmer's Question: {query}

Farmer Profile:
- Location: {location}
- Crop: {crop}
- Season: {season}
- Experience: {experience} years

Using the above context AND your agricultural expertise, provide a DETAILED and ACCURATE answer.

Important:
- Cite the knowledge source where relevant [e.g., "According to [Source Name]..."]
- If context doesn't cover the question, use your general knowledge but state clearly.
- Keep the answer practical and actionable.
- Use simple language suitable for a farmer.
- Mention applicable government schemes if relevant."""


class RAGGenerator(BaseAgent):
    """Generate answers using RAG — retrieval + IBM Granite generation."""

    def __init__(self):
        super().__init__()
        self.retriever = FarmingRetriever(k=5)

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("query", "")
        if not query:
            return {"error": "No query provided."}

        # Retrieve context
        docs: List[Document] = self.retriever.retrieve(query)
        context = self.retriever.format_context(docs)

        # Build prompt
        prompt = RAG_PROMPT.format(
            context=context if context else "No relevant context found in knowledge base.",
            query=query,
            location=inputs.get("location", "India"),
            crop=inputs.get("crop", "Not specified"),
            season=inputs.get("season", "Kharif"),
            experience=inputs.get("experience", 0),
        )

        answer = self.generate(prompt)

        return {
            "query": query,
            "answer": answer,
            "sources": [d.metadata.get("source", "Unknown") for d in docs],
            "context_used": len(docs),
            "confidence_score": 0.87 if docs else 0.65,
        }

    def index_knowledge_base(self, kb_path: str) -> Dict[str, Any]:
        """Load, chunk, and index all documents in the knowledge base."""
        from .loader import DocumentLoader
        from .chunker import DocumentChunker

        loader = DocumentLoader(kb_path)
        chunker = DocumentChunker()

        docs = loader.load_all()
        if not docs:
            return {"status": "warning", "message": "No documents found in knowledge base."}

        chunks = chunker.chunk(docs)
        self.retriever.vector_store.add_documents(chunks)

        return {
            "status": "success",
            "documents_loaded": len(docs),
            "chunks_indexed": len(chunks),
        }
