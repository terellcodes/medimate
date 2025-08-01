"""
Document Parser Service using parallel extraction.
"""

from typing import Dict, Any
from langchain_core.vectorstores import VectorStoreRetriever
from services.extraction_tools import ParallelExtractor
from services.extraction_config import EXTRACTION_CONFIG
import asyncio


class DocumentParserService:
    """
    Service for parsing 510(k) documents using AI-powered parallel extraction.
    """
    
    def __init__(self):
        self.parallel_extractor = ParallelExtractor()
        self.extraction_config = EXTRACTION_CONFIG
    
    async def parse_document(self, retriever: VectorStoreRetriever) -> Dict[str, str]:
        """
        Parse a 510(k) document and extract all key fields in parallel.
        
        Args:
            retriever: Vector store retriever for the uploaded document
            
        Returns:
            Dictionary with extracted document information:
            {
                "device_name": "...",
                "manufacturer": "...", 
                "indication_of_use": "...",
                "description": "..."
            }
        """
        print("🔍 Starting parallel document extraction...")
        
        try:
            # Extract all fields in parallel
            extracted_fields = await self.parallel_extractor.extract_all_fields(
                retriever=retriever,
                extraction_config=self.extraction_config
            )
            
            # Post-process results
            processed_results = self._post_process_results(extracted_fields)
            
            print("✅ Document extraction completed successfully")
            return processed_results
            
        except Exception as e:
            print(f"❌ Error during document parsing: {str(e)}")
            return self._get_fallback_results()
    
    def _post_process_results(self, raw_results: Dict[str, str]) -> Dict[str, str]:
        """
        Post-process extracted results for consistency and quality.
        """
        processed = {}
        
        for field, value in raw_results.items():
            # Clean up the extracted value
            cleaned_value = self._clean_extracted_value(value)
            processed[field] = cleaned_value
        
        # Generate description if it's too generic
        if processed.get("description") in ["Unknown", "Not specified", ""]:
            device_name = processed.get("device_name", "Unknown")
            if device_name != "Unknown":
                processed["description"] = f"510(k) medical device - {device_name}"
        
        return processed
    
    def _clean_extracted_value(self, value: str) -> str:
        """Clean and normalize extracted values."""
        if not value or value.strip() in ["", "None", "N/A"]:
            return "Unknown"
        
        # Remove common prefixes that LLMs sometimes include
        prefixes_to_remove = [
            "Device Name:",
            "Manufacturer:",
            "Indication:",
            "Description:",
            "Answer:",
            "Result:"
        ]
        
        cleaned = value.strip()
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        return cleaned if cleaned else "Unknown"
    
    def _get_fallback_results(self) -> Dict[str, str]:
        """Return fallback results if extraction fails."""
        return {
            "device_name": "Unknown",
            "manufacturer": "Unknown", 
            "indication_of_use": "Not specified",
            "description": "510(k) medical device"
        }
    
    def add_custom_field(self, field_name: str, queries: list, prompt: str):
        """
        Add a custom extraction field to the configuration.
        
        Args:
            field_name: Name of the field to extract
            queries: List of search queries for vector retrieval
            prompt: LLM prompt template for extraction
        """
        self.extraction_config[field_name] = {
            "queries": queries,
            "prompt": prompt
        }
        print(f"✅ Added custom extraction field: {field_name}")


# Global instance
document_parser_service = DocumentParserService()


# Example of how to add custom fields:
# document_parser_service.add_custom_field(
#     "clearance_date",
#     ["clearance date", "FDA clearance", "approval date", "510k clearance"],
#     """
# Extract the FDA clearance date from the following text.
# Look for dates related to FDA clearance, 510(k) approval, or device clearance.
# Return the date in MM/DD/YYYY format if found, otherwise return "Unknown".
# 
# Text:
# {text}
# 
# Clearance Date:"""
# )