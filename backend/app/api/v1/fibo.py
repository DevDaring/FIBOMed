"""FIBO API endpoints for medical visualization generation"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

from ...schemas.fibo_schemas import (
    GenerateRequest,
    RefineRequest,
    VisualizationResponse,
    VALID_ASPECT_RATIOS,
)
from ...services.fibo_service import get_fibo_service
from ...core.exceptions import FIBOError, FIBOAPIError, FIBOValidationError, FIBOStorageError

router = APIRouter(prefix="/fibo", tags=["fibo"])


@router.post("/generate", response_model=VisualizationResponse)
async def generate_visualization(request: GenerateRequest):
    """
    Generate a new visualization from text prompt.
    
    - Calls FIBO API with the provided prompt
    - Downloads and saves the generated image locally
    - Records visualization metadata in CSV storage
    - Returns the visualization details with local image URL
    
    Requirements: 2.1, 2.4
    """
    try:
        fibo_service = get_fibo_service()
        
        result = await fibo_service.generate_visualization(
            prompt=request.prompt,
            aspect_ratio=request.aspect_ratio,
            negative_prompt=request.negative_prompt,
            session_id=request.session_id
        )
        
        return VisualizationResponse(
            visualization_id=result.visualization_id,
            image_url=result.image_url,
            structured_prompt=result.structured_prompt,
            seed=result.seed,
            parent_id=result.parent_id,
            created_at=datetime.fromisoformat(result.created_at.replace("Z", "+00:00"))
        )
        
    except FIBOValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    except FIBOAPIError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    except FIBOStorageError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    except FIBOError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "GENERATION_FAILED",
                "message": f"Visualization generation failed: {str(e)}",
                "details": None
            }
        )


@router.post("/refine/{visualization_id}", response_model=VisualizationResponse)
async def refine_visualization(visualization_id: str, request: RefineRequest):
    """
    Refine an existing visualization with additional instructions.
    
    - Retrieves the original visualization's structured prompt and seed
    - Calls FIBO API with refinement prompt and original structured prompt
    - Saves the refined image with parent_id linking to original
    - Returns the refined visualization details
    
    Requirements: 3.1, 3.2
    """
    try:
        fibo_service = get_fibo_service()
        
        result = await fibo_service.refine_visualization(
            visualization_id=visualization_id,
            refinement_prompt=request.prompt
        )
        
        return VisualizationResponse(
            visualization_id=result.visualization_id,
            image_url=result.image_url,
            structured_prompt=result.structured_prompt,
            seed=result.seed,
            parent_id=result.parent_id,
            created_at=datetime.fromisoformat(result.created_at.replace("Z", "+00:00"))
        )
        
    except FIBOValidationError as e:
        # Handle visualization not found
        if e.code == "VISUALIZATION_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={
                    "code": e.code,
                    "message": e.message,
                    "details": e.details
                }
            )
        raise HTTPException(
            status_code=400,
            detail={
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    except FIBOAPIError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    except FIBOStorageError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    except FIBOError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "REFINEMENT_FAILED",
                "message": f"Visualization refinement failed: {str(e)}",
                "details": None
            }
        )


@router.get("/{visualization_id}", response_model=VisualizationResponse)
async def get_visualization(visualization_id: str):
    """
    Get visualization details by ID.
    
    - Retrieves visualization metadata from CSV storage
    - Returns the visualization details with local image URL
    
    Requirements: 2.4
    """
    try:
        fibo_service = get_fibo_service()
        
        result = await fibo_service.get_visualization(visualization_id)
        
        # Handle created_at which might be None or already a string
        created_at = result.created_at
        if created_at is None:
            created_at = datetime.utcnow()
        elif isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return VisualizationResponse(
            visualization_id=result.visualization_id,
            image_url=result.image_url,
            structured_prompt=result.structured_prompt,
            seed=result.seed,
            parent_id=result.parent_id,
            created_at=created_at
        )
        
    except FIBOValidationError as e:
        if e.code == "VISUALIZATION_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={
                    "code": e.code,
                    "message": e.message,
                    "details": e.details
                }
            )
        raise HTTPException(
            status_code=400,
            detail={
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    except FIBOStorageError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    except FIBOError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "RETRIEVAL_FAILED",
                "message": f"Failed to retrieve visualization: {str(e)}",
                "details": None
            }
        )
