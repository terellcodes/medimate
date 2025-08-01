from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class Citation(BaseModel):
    """Citation from analysis tools."""
    tool: str
    text: str


class AnalysisResult(BaseModel):
    """Result of substantial equivalence analysis."""
    substantially_equivalent: bool
    reasons: List[str]
    citations: List[Citation]
    suggestions: List[str]


class AnalysisRequest(BaseModel):
    """Request for device analysis."""
    new_device_indication: str


class AnalysisResponse(BaseModel):
    """Response for analysis endpoint."""
    success: bool
    analysis: Optional[AnalysisResult] = None
    error: Optional[str] = None