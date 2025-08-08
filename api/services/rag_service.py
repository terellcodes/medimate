from typing import Annotated, List, Optional
from langchain_core.tools import tool
from langchain_core.vectorstores import VectorStoreRetriever
from core.vector_store import vector_store_manager


class RAGService:
    """Service for Retrieval Augmented Generation operations."""
    
    def __init__(self):
        self.vector_manager = vector_store_manager
        self.current_predicate_k_number: Optional[str] = None
    
    def get_guidelines_retriever(self) -> VectorStoreRetriever:
        """Get retriever for FDA guidelines."""
        guidelines_store = self.vector_manager.get_guidelines_vector_store()
        return guidelines_store.as_retriever(search_kwargs={"k": 5})
    
    def get_predicate_device_retriever(self) -> VectorStoreRetriever:
        """Get retriever for predicate device documents."""
        if self.current_predicate_k_number:
            # Use specific predicate collection
            predicate_store = self.vector_manager.get_predicate_vector_store(self.current_predicate_k_number)
        else:
            # Fallback to legacy collection
            predicate_store = self.vector_manager.get_predicate_device_vector_store()
        
        return predicate_store.as_retriever(search_kwargs={"k": 5})
    
    def set_current_predicate(self, k_number: str) -> None:
        """Set the current predicate device for analysis."""
        self.current_predicate_k_number = k_number
    
    def clear_current_predicate(self) -> None:
        """Clear the current predicate device context."""
        self.current_predicate_k_number = None


# Initialize service
rag_service = RAGService()

# Define tools for the agent
@tool
def retrieve_fda_guidelines(
    query: Annotated[str, "query to ask the retrieve fda guidelines tool"]
) -> List[str]:
    """Use Retrieval Augmented Generation to retrieve information from FDA guidelines for determining substantial equivalence between a target device and a predicate device."""
    retriever = rag_service.get_guidelines_retriever()
    documents = retriever.invoke(query)
    return [doc.page_content for doc in documents]


@tool
def retrieve_predicate_device_details(
    query: Annotated[str, "query to ask the retrieve predicate device details tool"]
) -> List[str]:
    """Use Retrieval Augmented Generation to retrieve details about a predicate device from its 510(k) filing."""
    retriever = rag_service.get_predicate_device_retriever()
    documents = retriever.invoke(query)
    return [doc.page_content for doc in documents]