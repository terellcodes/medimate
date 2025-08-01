import os
import tempfile
import aiofiles
from typing import BinaryIO
from fastapi import UploadFile
from core.vector_store import vector_store_manager


class PDFService:
    """Service for handling PDF upload and processing."""
    
    def __init__(self):
        self.vector_manager = vector_store_manager
    
    async def process_predicate_device_pdf(self, file: UploadFile) -> dict:
        """Process uploaded 510(k) PDF and return document summary."""
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_path = temp_file.name
            
            # Write uploaded content to temp file
            content = await file.read()
            temp_file.write(content)
        
        try:
            # Process the PDF and load into vector store
            summary = await self.vector_manager.load_predicate_device_document(temp_path)
            return {
                "success": True,
                "message": "PDF processed successfully",
                "document_summary": summary
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing PDF: {str(e)}",
                "document_summary": None
            }
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    async def initialize_fda_guidelines(self, guidelines_pdf_path: str) -> bool:
        """Initialize FDA guidelines in vector store."""
        try:
            if os.path.exists(guidelines_pdf_path):
                await self.vector_manager.load_fda_guidelines(guidelines_pdf_path)
                return True
            else:
                print(f"FDA guidelines PDF not found at: {guidelines_pdf_path}")
                return False
        except Exception as e:
            print(f"Error loading FDA guidelines: {str(e)}")
            return False


# Global instance
pdf_service = PDFService()