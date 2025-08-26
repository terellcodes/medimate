from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class PredicateSearchParams(BaseModel):
    """Request parameters for predicate device search."""
    search_term: Optional[str] = None
    product_code: Optional[str] = None
    max_downloads: int = 5
    include_recalled: bool = False


class DeviceInfo(BaseModel):
    """Information about a medical device from 510(k) database."""
    k_number: str
    device_name: str
    applicant: str
    decision_date: str
    product_code: Optional[str] = None
    has_510k_document: bool
    document_type: Optional[str] = None
    decision_description: Optional[str] = None
    safety_status: Optional[str] = "unknown"  # For future recall checking


class DownloadedDevice(BaseModel):
    """Information about a successfully downloaded device PDF."""
    device_name: str
    k_number: str
    applicant: str
    decision_date: str
    filepath: str
    pdf_url: str


class PredicateSearchSummary(BaseModel):
    """Summary statistics for predicate search."""
    total_found: int
    devices_with_documents: int
    downloads_attempted: int
    downloads_successful: int
    max_downloads_requested: int


class PredicateDiscoveryResult(BaseModel):
    """Complete result of predicate discovery process."""
    downloads: List[DownloadedDevice]
    all_devices: List[DeviceInfo]
    devices_with_510k: List[DeviceInfo]
    devices_without_510k: List[DeviceInfo]
    summary: PredicateSearchSummary
    search_params: PredicateSearchParams


class PredicateDiscoveryRequest(BaseModel):
    """Request for predicate device discovery."""
    search_params: PredicateSearchParams


class PredicateDiscoveryResponse(BaseModel):
    """Response from predicate discovery endpoint."""
    success: bool
    result: Optional[PredicateDiscoveryResult] = None
    error: Optional[str] = None


class BulkIFURequest(BaseModel):
    """Request for bulk IFU (Indications for Use) fetching."""
    k_numbers: List[str]


class IFUExtraction(BaseModel):
    """Extracted IFU information from a device document."""
    k_number: str
    device_name: str
    ifu_text: Optional[str] = None
    extraction_status: str  # 'success', 'no_pdf', 'extraction_failed', 'no_ifu_found'
    error_message: Optional[str] = None
    pdf_url: Optional[str] = None


class BulkIFUResult(BaseModel):
    """Result of bulk IFU extraction process."""
    extractions: List[IFUExtraction]
    summary: Dict[str, int]  # Status counts: success, failed, no_pdf, etc.
    total_processed: int


class BulkIFUResponse(BaseModel):
    """Response from bulk IFU extraction endpoint."""
    success: bool
    result: Optional[BulkIFUResult] = None
    error: Optional[str] = None


class PredicateEquivalenceRequest(BaseModel):
    """Request for checking substantial equivalence against a specific predicate."""
    device_intended_use: str
    technical_characteristics: str
    predicate_k_number: str


class PredicateEquivalenceResponse(BaseModel):
    """Response from predicate equivalence checking endpoint."""
    success: bool
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None