from fastapi import APIRouter, HTTPException
from models.schemas.predicate_discovery import (
    PredicateDiscoveryRequest,
    PredicateDiscoveryResponse,
    PredicateSearchParams
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