from pydantic import BaseModel
from typing import Optional


class DocumentSummary(BaseModel):
    """Summary of an uploaded 510(k) document."""
    device_name: str
    description: str
    indication_of_use: str
    manufacturer: str


class UploadResponse(BaseModel):
    """Response for PDF upload endpoint."""
    success: bool
    message: str
    document_summary: Optional[DocumentSummary] = None