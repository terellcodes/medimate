from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas.upload import UploadResponse, DocumentSummary
from services.pdf_service import pdf_service

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload_pdf", response_model=UploadResponse)
async def upload_predicate_device_pdf(file: UploadFile = File(...)):
    """
    Upload a 510(k) PDF document for a predicate device.
    
    The PDF will be processed, chunked, and loaded into the vector store.
    Returns a summary of the document including device name, description,
    indication of use, and manufacturer.
    """
    try:
        result = await pdf_service.process_predicate_device_pdf(file)
        
        if result["success"]:
            return UploadResponse(
                success=True,
                message=result["message"],
                document_summary=DocumentSummary(**result["document_summary"])
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")