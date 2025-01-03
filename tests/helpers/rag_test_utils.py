"""RAG testing utilities."""

from dataclasses import dataclass
from typing import List
import random

@dataclass
class RAGDocument:
    """Mock RAG document for testing."""
    content: str
    metadata: dict
    distance: float
    
    def to_dict(self):
        """Convert to dictionary format."""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "distance": self.distance
        }

class RAGTestUtils:
    """Utility class for RAG testing."""
    
    @staticmethod
    def create_mock_embeddings(dimensions: int = 3) -> List[float]:
        """Create mock embeddings vector."""
        return [random.random() for _ in range(dimensions)]
    
    @staticmethod
    def create_mock_documents(count: int = 1, base_similarity: float = 0.9) -> List[RAGDocument]:
        """Create mock RAG documents with decreasing similarity."""
        documents = []
        for i in range(count):
            doc = RAGDocument(
                content=f"Test document {i + 1}",
                metadata={"source": f"test_{i + 1}.txt"},
                distance=base_similarity - (i * 0.1)  # Decreasing similarity
            )
            documents.append(doc)
        return documents
