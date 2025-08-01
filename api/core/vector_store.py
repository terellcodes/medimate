from typing import Optional
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import os
from config.settings import get_settings


class VectorStoreManager:
    """Manages vector stores for FDA guidelines and predicate device documents."""
    
    def __init__(self):
        self.embedding_model = None
        self.embedding_dim = 1536
        self.client = QdrantClient(":memory:")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize collections
        self._initialize_collections()
    
    def _get_embedding_model(self):
        """Lazy initialization of embedding model."""
        if self.embedding_model is None:
            settings = get_settings()
            self.embedding_model = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=settings.OPENAI_API_KEY
            )
        return self.embedding_model
        
    def _initialize_collections(self):
        """Initialize Qdrant collections for guidelines and predicate devices."""
        # Guidelines collection
        if not self.client.collection_exists("guidelines"):
            self.client.create_collection(
                collection_name="guidelines",
                vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
            )
        
        # Predicate device collection
        if not self.client.collection_exists("predicate_device"):
            self.client.create_collection(
                collection_name="predicate_device",
                vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
            )
    
    def get_guidelines_vector_store(self) -> QdrantVectorStore:
        """Get vector store for FDA guidelines."""
        return QdrantVectorStore(
            client=self.client,
            collection_name="guidelines",
            embedding=self._get_embedding_model(),
        )
    
    def get_predicate_device_vector_store(self) -> QdrantVectorStore:
        """Get vector store for predicate device documents."""
        return QdrantVectorStore(
            client=self.client,
            collection_name="predicate_device",
            embedding=self._get_embedding_model(),
        )
    
    async def load_fda_guidelines(self, pdf_path: str) -> None:
        """Load FDA guidelines PDF into vector store."""
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Add to guidelines vector store
        guidelines_store = self.get_guidelines_vector_store()
        await guidelines_store.aadd_documents(documents=chunks)
        
    async def load_predicate_device_document(self, pdf_path: str) -> dict:
        """Load predicate device PDF and return summary info."""
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Clear existing predicate device data (only one at a time)
        self.client.delete_collection("predicate_device")
        self._initialize_collections()
        
        # Add to predicate device vector store
        predicate_store = self.get_predicate_device_vector_store()
        await predicate_store.aadd_documents(documents=chunks)
        
        # Extract summary information from the document
        summary = self._extract_document_summary(documents[0] if documents else None)
        return summary
    
    def _extract_document_summary(self, document: Optional[Document]) -> dict:
        """Extract key information from a 510(k) document."""
        if not document:
            return {
                "device_name": "Unknown",
                "description": "No description available",
                "indication_of_use": "Not specified",
                "manufacturer": "Unknown"
            }
        
        content = document.page_content.lower()
        
        # Simple extraction logic - in production, this could use LLM for better extraction
        device_name = "Unknown"
        manufacturer = "Unknown"
        indication = "Not specified"
        
        # Look for common patterns in 510(k) documents
        lines = document.page_content.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            if 'trade name:' in line_lower or 'device name:' in line_lower:
                device_name = line.split(':', 1)[-1].strip()
            elif 'manufacturer' in line_lower and ':' in line:
                manufacturer = line.split(':', 1)[-1].strip()
            elif 'indication' in line_lower and 'use' in line_lower:
                indication = line.strip()
        
        return {
            "device_name": device_name,
            "description": f"510(k) medical device - {device_name}",
            "indication_of_use": indication,
            "manufacturer": manufacturer
        }


# Global instance
vector_store_manager = VectorStoreManager()