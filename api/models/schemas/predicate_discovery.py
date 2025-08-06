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