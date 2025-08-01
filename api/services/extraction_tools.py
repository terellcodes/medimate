"""
Generic extraction tools for document field extraction.
"""

from typing import List, Dict, Any
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from config.settings import get_settings
import asyncio


class GenericExtractionTool:
    """Generic tool for extracting any field from documents using vector search + LLM."""
    
    def __init__(self):
        self.llm = None
    
    def _get_llm(self):
        """Lazy initialization of LLM."""
        if self.llm is None:
            settings = get_settings()
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                openai_api_key=settings.OPENAI_API_KEY
            )
        return self.llm
    
    async def extract_field(
        self, 
        retriever: VectorStoreRetriever,
        field_config: Dict[str, Any]
    ) -> str:
        """
        Extract a single field using vector search and LLM processing.
        
        Args:
            retriever: Vector store retriever for the document
            field_config: Configuration containing 'queries' and 'prompt'
            
        Returns:
            Extracted field value as string
        """
        try:
            # Step 1: Gather relevant chunks using multiple queries
            all_chunks = []
            for query in field_config["queries"]:
                chunks = await self._search_chunks(retriever, query)
                all_chunks.extend(chunks)
            
            # Step 2: Remove duplicates and combine text
            unique_chunks = list({chunk.page_content: chunk for chunk in all_chunks}.values())
            combined_text = "\n\n".join([chunk.page_content for chunk in unique_chunks[:5]])  # Limit to top 5 chunks
            
            if not combined_text.strip():
                return "Unknown"
            
            # Step 3: Use LLM to extract the specific field
            llm = self._get_llm()
            prompt = field_config["prompt"].format(text=combined_text)
            
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            extracted_value = response.content.strip()
            
            return extracted_value if extracted_value else "Unknown"
            
        except Exception as e:
            print(f"Error extracting field: {str(e)}")
            return "Unknown"
    
    async def _search_chunks(self, retriever: VectorStoreRetriever, query: str):
        """Search for relevant chunks using a query."""
        try:
            # Use asynchronous retrieval if available, otherwise use sync
            if hasattr(retriever, 'ainvoke'):
                return await retriever.ainvoke(query)
            else:
                # Run sync retrieval in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, retriever.invoke, query)
        except Exception as e:
            print(f"Error searching chunks for query '{query}': {str(e)}")
            return []


class ParallelExtractor:
    """Coordinates parallel extraction of multiple fields."""
    
    def __init__(self):
        self.extraction_tool = GenericExtractionTool()
    
    async def extract_all_fields(
        self, 
        retriever: VectorStoreRetriever,
        extraction_config: Dict[str, Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Extract all configured fields in parallel.
        
        Args:
            retriever: Vector store retriever for the document
            extraction_config: Dictionary of field configurations
            
        Returns:
            Dictionary mapping field names to extracted values
        """
        # Create extraction tasks for all fields
        extraction_tasks = [
            self._extract_single_field(field_name, field_config, retriever)
            for field_name, field_config in extraction_config.items()
        ]
        
        # Execute all extractions concurrently
        field_values = await asyncio.gather(*extraction_tasks, return_exceptions=True)
        
        # Build result dictionary, handling any exceptions
        results = {}
        for i, (field_name, field_value) in enumerate(zip(extraction_config.keys(), field_values)):
            if isinstance(field_value, Exception):
                print(f"Error extracting {field_name}: {field_value}")
                results[field_name] = "Unknown"
            else:
                results[field_name] = field_value
        
        return results
    
    async def _extract_single_field(
        self,
        field_name: str,
        field_config: Dict[str, Any],
        retriever: VectorStoreRetriever
    ) -> str:
        """Extract a single field (used as async task)."""
        return await self.extraction_tool.extract_field(retriever, field_config)