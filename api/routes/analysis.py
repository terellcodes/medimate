from fastapi import APIRouter, HTTPException
from models.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisResult, Citation
from services.analysis_service import analysis_service

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze_device", response_model=AnalysisResponse)
async def analyze_device_equivalence(request: AnalysisRequest):
    """
    Analyze if a new device is substantially equivalent to the uploaded predicate device.
    
    Takes the indication of use for the new device and runs the regulatory agent
    to determine substantial equivalence based on FDA guidelines and the predicate device.
    """
    try:
        result = await analysis_service.analyze_device_equivalence(request.new_device_indication)
        
        if result["success"]:
            analysis_data = result["analysis"]
            
            # Convert citations to Citation objects if they exist
            citations = []
            if "citations" in analysis_data:
                citations = [Citation(**citation) for citation in analysis_data["citations"]]
            
            analysis_result = AnalysisResult(
                substantially_equivalent=analysis_data.get("substantially_equivalent", False),
                reasons=analysis_data.get("reasons", []),
                citations=citations,
                suggestions=analysis_data.get("suggestions", [])
            )
            
            return AnalysisResponse(
                success=True,
                analysis=analysis_result
            )
        else:
            return AnalysisResponse(
                success=False,
                error=result["error"],
                analysis=None
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")