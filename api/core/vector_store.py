from typing import Optional, List, Dict
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from config.settings import get_settings

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages vector stores for FDA guidelines and predicate device documents."""
    
    def __init__(self):
        self.embedding_model = None
        self.embedding_dim = 1536
        self.settings = get_settings()
        self.client = self._initialize_client()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize core collections
        self._initialize_core_collections()
    
    def _initialize_client(self) -> QdrantClient:
        """Initialize Qdrant client based on configuration."""
        mode = self.settings.QDRANT_MODE.lower()
        
        if mode == "memory":
            logger.info("Initializing Qdrant in memory mode")
            return QdrantClient(":memory:")
        
        elif mode == "local":
            path = Path(self.settings.QDRANT_PATH)
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initializing Qdrant in local mode at {path}")
            return QdrantClient(path=str(path))
        
        elif mode == "docker":
            logger.info(f"Initializing Qdrant in docker mode at {self.settings.QDRANT_HOST}:{self.settings.QDRANT_PORT}")
            return QdrantClient(
                host=self.settings.QDRANT_HOST,
                port=self.settings.QDRANT_PORT
            )
        
        elif mode == "cloud":
            if not self.settings.QDRANT_URL or not self.settings.QDRANT_API_KEY:
                raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set for cloud mode")
            logger.info(f"Initializing Qdrant in cloud mode at {self.settings.QDRANT_URL}")
            return QdrantClient(
                url=self.settings.QDRANT_URL,
                api_key=self.settings.QDRANT_API_KEY
            )
        
        else:
            raise ValueError(f"Invalid QDRANT_MODE: {mode}")
    
    def _get_embedding_model(self):
        """Lazy initialization of embedding model."""
        if self.embedding_model is None:
            self.embedding_model = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=self.settings.OPENAI_API_KEY
            )
        return self.embedding_model
    
    def _initialize_core_collections(self):
        """Initialize core Qdrant collections."""
        # Guidelines collection (permanent)
        if not self.client.collection_exists("guidelines"):
            logger.info("Creating guidelines collection")
            self.client.create_collection(
                collection_name="guidelines",
                vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
            )
        
        # Legacy predicate_device collection (for backward compatibility)
        if not self.client.collection_exists("predicate_device"):
            logger.info("Creating legacy predicate_device collection")
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
        """Get vector store for predicate device documents (legacy method)."""
        return QdrantVectorStore(
            client=self.client,
            collection_name="predicate_device",
            embedding=self._get_embedding_model(),
        )
    
    def get_predicate_collection_name(self, k_number: str) -> str:
        """Generate collection name for a specific predicate device."""
        # Clean k_number to be safe for collection names
        safe_k_number = k_number.replace("/", "_").replace("\\", "_").lower()
        return f"predicate_{safe_k_number}"
    
    def get_predicate_vector_store(self, k_number: str) -> QdrantVectorStore:
        """Get vector store for a specific predicate device."""
        collection_name = self.get_predicate_collection_name(k_number)
        
        # Create collection if it doesn't exist
        if not self.client.collection_exists(collection_name):
            logger.info(f"Creating collection for predicate {k_number}: {collection_name}")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
            )
        
        return QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=self._get_embedding_model(),
        )
    
    def predicate_collection_exists(self, k_number: str) -> bool:
        """Check if a predicate collection already exists."""
        collection_name = self.get_predicate_collection_name(k_number)
        return self.client.collection_exists(collection_name)
    
    def list_predicate_collections(self) -> List[str]:
        """List all predicate device collections."""
        collections = self.client.get_collections().collections
        predicate_collections = []
        
        for collection in collections:
            if collection.name.startswith("predicate_"):
                # Extract K-number from collection name
                k_number = collection.name.replace("predicate_", "").upper()
                predicate_collections.append(k_number)
        
        return predicate_collections
    
    def delete_predicate_collection(self, k_number: str) -> bool:
        """Delete a specific predicate collection."""
        collection_name = self.get_predicate_collection_name(k_number)
        
        if self.client.collection_exists(collection_name):
            logger.info(f"Deleting collection for predicate {k_number}: {collection_name}")
            self.client.delete_collection(collection_name)
            return True
        
        return False
    
    def cleanup_old_collections(self, keep_count: int = 20) -> List[str]:
        """
        Clean up old predicate collections, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent collections to keep
            
        Returns:
            List of deleted collection K-numbers
        """
        collections = self.client.get_collections().collections
        predicate_collections = []
        
        # Get all predicate collections with their point counts (as proxy for usage)
        for collection in collections:
            if collection.name.startswith("predicate_"):
                info = self.client.get_collection(collection.name)
                predicate_collections.append({
                    "name": collection.name,
                    "k_number": collection.name.replace("predicate_", "").upper(),
                    "points_count": info.points_count
                })
        
        # Sort by points count (assuming more points = more recent/important)
        predicate_collections.sort(key=lambda x: x["points_count"], reverse=True)
        
        # Delete old collections
        deleted = []
        for collection in predicate_collections[keep_count:]:
            self.delete_predicate_collection(collection["k_number"])
            deleted.append(collection["k_number"])
        
        if deleted:
            logger.info(f"Cleaned up {len(deleted)} old predicate collections")
        
        return deleted
    
    async def load_fda_guidelines(self, pdf_path: str) -> None:
        """Load FDA guidelines PDF into vector store."""
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Add to guidelines vector store
        guidelines_store = self.get_guidelines_vector_store()
        await guidelines_store.aadd_documents(documents=chunks)
        logger.info(f"Loaded FDA guidelines from {pdf_path}")
    
    async def load_predicate_device_document(self, pdf_path: str) -> dict:
        """
        Load predicate device PDF (legacy method for backward compatibility).
        This method clears and reloads the single predicate_device collection.
        """
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Clear existing predicate device data (only one at a time)
        self.client.delete_collection("predicate_device")
        self._initialize_core_collections()
        
        # Add to predicate device vector store
        predicate_store = self.get_predicate_device_vector_store()
        await predicate_store.aadd_documents(documents=chunks)
        
        # Use AI-powered extraction
        summary = await self._extract_document_summary_ai(predicate_store)
        return summary
    
    async def load_predicate_to_collection(self, k_number: str, pdf_path: str) -> dict:
        """
        Load a predicate device PDF into its own collection.
        
        Args:
            k_number: The K-number of the predicate device
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with extraction summary
        """
        # Check if collection already exists and has content
        if self.predicate_collection_exists(k_number):
            collection_info = self.client.get_collection(self.get_predicate_collection_name(k_number))
            if collection_info.points_count > 0:
                logger.info(f"Collection for {k_number} already exists with {collection_info.points_count} points")
                return {
                    "status": "exists",
                    "k_number": k_number,
                    "points_count": collection_info.points_count
                }
        
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Get vector store for this specific predicate
        predicate_store = self.get_predicate_vector_store(k_number)
        
        # Add documents to the collection
        await predicate_store.aadd_documents(documents=chunks)
        
        logger.info(f"Loaded {len(chunks)} chunks for predicate {k_number}")
        
        # Extract summary using AI
        summary = await self._extract_document_summary_ai(predicate_store)
        summary["k_number"] = k_number
        summary["chunks_loaded"] = len(chunks)
        
        return summary
    
    async def _extract_document_summary_ai(self, predicate_store: QdrantVectorStore) -> dict:
        """Extract document summary using AI-powered parallel extraction."""
        try:
            # Import here to avoid circular imports
            from services.document_parser_service import document_parser_service
            
            # Get retriever for the predicate device vector store
            retriever = predicate_store.as_retriever(search_kwargs={"k": 5})
            
            # Use parallel AI extraction
            extracted_fields = await document_parser_service.parse_document(retriever)
            
            return extracted_fields
            
        except Exception as e:
            logger.error(f"AI extraction failed: {str(e)}")
            # Fallback to simple extraction if AI fails
            return {
                "device_name": "Unknown",
                "manufacturer": "Unknown",
                "indication_of_use": "Not specified", 
                "description": "510(k) medical device"
            }


# Global instance
vector_store_manager = VectorStoreManager()