"""FIBO API Pydantic schemas"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class AspectRatio(str, Enum):
    """Valid aspect ratios for FIBO image generation"""
    SQUARE = "1:1"
    PORTRAIT_2_3 = "2:3"
    LANDSCAPE_3_2 = "3:2"
    PORTRAIT_3_4 = "3:4"
    LANDSCAPE_4_3 = "4:3"
    PORTRAIT_4_5 = "4:5"
    LANDSCAPE_5_4 = "5:4"
    PORTRAIT_9_16 = "9:16"
    LANDSCAPE_16_9 = "16:9"


# List of valid aspect ratio string values for validation
VALID_ASPECT_RATIOS = [ratio.value for ratio in AspectRatio]


class GenerateRequest(BaseModel):
    """Request to generate a new visualization
    
    Requirements: 2.1, 6.2, 6.3
    """
    prompt: str = Field(..., description="Text prompt for image generation")
    aspect_ratio: str = Field(
        default="1:1",
        description="Aspect ratio for the generated image"
    )
    negative_prompt: Optional[str] = Field(
        default=None,
        description="Negative prompt to exclude certain elements"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for conversation continuity"
    )

    @field_validator("aspect_ratio")
    @classmethod
    def validate_aspect_ratio(cls, v: str) -> str:
        """Validate that aspect_ratio is one of the valid options"""
        if v not in VALID_ASPECT_RATIOS:
            valid_options = ", ".join(VALID_ASPECT_RATIOS)
            raise ValueError(
                f"Invalid aspect ratio '{v}'. Valid options are: {valid_options}"
            )
        return v


class RefineRequest(BaseModel):
    """Request to refine an existing visualization
    
    Requirements: 3.1
    """
    prompt: str = Field(..., description="Refinement instruction prompt")
    seed: Optional[int] = Field(
        default=None,
        description="Seed value for deterministic refinement"
    )


class VisualizationResponse(BaseModel):
    """Response containing visualization details
    
    Requirements: 2.1, 3.1, 6.2, 6.3
    """
    visualization_id: str = Field(..., description="Unique identifier for the visualization")
    image_url: str = Field(..., description="URL to the generated image")
    structured_prompt: dict = Field(..., description="FIBO structured prompt object")
    seed: int = Field(..., description="Seed value used for generation")
    parent_id: Optional[str] = Field(
        default=None,
        description="Parent visualization ID for refinements"
    )
    created_at: datetime = Field(..., description="Timestamp of creation")


class FIBOAPIResponse(BaseModel):
    """Response from FIBO API
    
    Used internally to parse BRIA API responses
    """
    result: Optional[dict] = Field(default=None, description="Result object from API")
    request_id: str = Field(..., description="BRIA API request ID")
    status_url: Optional[str] = Field(
        default=None,
        description="URL to poll for async generation status"
    )
    warning: Optional[str] = Field(default=None, description="Warning message from API")
    error: Optional[dict] = Field(default=None, description="Error details from API")
