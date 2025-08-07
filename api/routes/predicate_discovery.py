from fastapi import APIRouter, HTTPException
from models.schemas.predicate_discovery import (
    PredicateDiscoveryRequest,
    PredicateDiscoveryResponse,
    PredicateSearchParams,
    BulkIFURequest,
    BulkIFUResponse,
    PredicateEquivalenceRequest,
    PredicateEquivalenceResponse
)
from services.predicate_discovery_service import predicate_discovery_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["predicate-discovery"])


@router.post("/discover-predicates", response_model=PredicateDiscoveryResponse)
async def discover_predicate_devices(request: PredicateDiscoveryRequest):
    """
    Discover predicate devices from FDA 510(k) database.
    
    Searches the openFDA 510(k) database for devices matching the search criteria,
    downloads available PDFs, and returns comprehensive device information.
    
    Supports:
    - Device name search
    - Product code search  
    - Combined search (product code + device name)
    - Configurable download limits
    """
    try:
        # Validate search parameters
        if not request.search_params.search_term and not request.search_params.product_code:
            raise HTTPException(
                status_code=400, 
                detail="Must provide either search_term or product_code"
            )
        
        logger.info(f"Starting predicate discovery request: {request.search_params}")
        
        # Execute predicate discovery
        result = await predicate_discovery_service.discover_predicates(request.search_params)
        
        return PredicateDiscoveryResponse(
            success=True,
            result=result
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Predicate discovery failed: {e}")
        return PredicateDiscoveryResponse(
            success=False,
            error=f"Predicate discovery failed: {str(e)}"
        )


@router.post("/search-devices", response_model=PredicateDiscoveryResponse)
async def search_devices_only(request: PredicateDiscoveryRequest):
    """
    Search for devices without downloading PDFs.
    
    Returns device metadata and availability information without attempting
    to download any PDF files. Useful for browsing available devices.
    """
    try:
        # Validate search parameters
        if not request.search_params.search_term and not request.search_params.product_code:
            raise HTTPException(
                status_code=400, 
                detail="Must provide either search_term or product_code"
            )
        
        # Set max_downloads to 0 for search-only
        search_params = request.search_params.model_copy()
        search_params.max_downloads = 0
        
        logger.info(f"Starting device search request: {search_params}")
        
        # Execute search without downloads
        result = await predicate_discovery_service.discover_predicates(search_params)
        
        return PredicateDiscoveryResponse(
            success=True,
            result=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Device search failed: {e}")
        return PredicateDiscoveryResponse(
            success=False,
            error=f"Device search failed: {str(e)}"
        )


@router.post("/fetch-bulk-ifu", response_model=BulkIFUResponse)
async def fetch_bulk_ifu(request: BulkIFURequest):
    """
    Fetch IFU (Indications for Use) text from multiple device PDFs.
    
    Downloads PDFs for the specified K-numbers and extracts the IFU sections
    using AI-powered document parsing. Returns extracted IFU text for each device.
    """
    try:
        if not request.k_numbers:
            raise HTTPException(
                status_code=400,
                detail="Must provide at least one K-number"
            )
        
        if len(request.k_numbers) > 50:  # Reasonable limit for bulk processing
            raise HTTPException(
                status_code=400,
                detail="Too many devices requested. Maximum 50 devices per request."
            )
        
        logger.info(f"Starting bulk IFU extraction for {len(request.k_numbers)} devices")
        
        # Execute bulk IFU extraction
        result = await predicate_discovery_service.extract_bulk_ifu(request.k_numbers)
        
        return BulkIFUResponse(
            success=True,
            result=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk IFU extraction failed: {e}")
        return BulkIFUResponse(
            success=False,
            error=f"Bulk IFU extraction failed: {str(e)}"
        )


@router.post("/check-predicate-equivalence", response_model=PredicateEquivalenceResponse)
async def check_predicate_equivalence(request: PredicateEquivalenceRequest):
    """
    Check substantial equivalence against a specific predicate device.
    
    This endpoint:
    1. Loads the specified predicate PDF into the vector store
    2. Uses the existing analysis service to check substantial equivalence
    3. Returns the analysis results
    """
    try:
        if not request.device_intended_use.strip():
            raise HTTPException(
                status_code=400,
                detail="Device intended use cannot be empty"
            )
        
        if not request.predicate_k_number.strip():
            raise HTTPException(
                status_code=400,
                detail="Predicate K-number cannot be empty"
            )
        
        logger.info(f"Starting equivalence check for device against predicate {request.predicate_k_number}")
        
        # Step 1: Load predicate PDF into vector store
        pdf_loaded = await predicate_discovery_service.load_predicate_pdf_to_vector_store(request.predicate_k_number)
        
        if not pdf_loaded:
            return PredicateEquivalenceResponse(
                success=False,
                error=f"Failed to load predicate device PDF for {request.predicate_k_number}. Ensure the PDF was downloaded during IFU extraction."
            )
        
        # Step 2: Run analysis using existing analysis service
        from services.analysis_service import analysis_service
        
        result = await analysis_service.analyze_device_equivalence(request.device_intended_use)
        
        return PredicateEquivalenceResponse(
            success=result["success"],
            analysis=result.get("analysis"),
            error=result.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Predicate equivalence check failed: {e}")
        return PredicateEquivalenceResponse(
            success=False,
            error=f"Equivalence check failed: {str(e)}"
        )