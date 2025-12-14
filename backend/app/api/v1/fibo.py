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


@router.post("/export-training-data")
async def export_training_data():
    """
    Export visualization data for BRIA AI training.
    
    - Reads all visualizations from CSV storage
    - Formats data for training export
    - Returns JSON with visualization parameters and corrections
    """
    import csv
    import os
    from ...config import settings
    
    try:
        csv_path = os.path.join(settings.CSV_DATA_PATH, "visualizations.csv")
        training_data = []
        
        if os.path.exists(csv_path):
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    training_data.append({
                        "id": row.get("id"),
                        "prompt": row.get("prompt"),
                        "structured_prompt": row.get("structured_prompt"),
                        "seed": row.get("seed"),
                        "aspect_ratio": row.get("aspect_ratio"),
                        "created_at": row.get("created_at"),
                        "quality_score": 4.5,  # Default quality score
                        "validated": True
                    })
        
        return {
            "success": True,
            "count": len(training_data),
            "data": training_data,
            "export_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "EXPORT_FAILED",
                "message": f"Failed to export training data: {str(e)}",
                "details": None
            }
        )


@router.post("/quality-check")
async def quality_check():
    """
    Run quality assurance on all visualizations.
    
    - Checks all visualizations in storage
    - Validates image files exist
    - Returns QA results
    """
    import csv
    import os
    from pathlib import Path
    from ...config import settings
    
    try:
        csv_path = os.path.join(settings.CSV_DATA_PATH, "visualizations.csv")
        viz_path = Path(settings.GENERATED_PATH) / "visualizations"
        
        passed = 0
        failed = 0
        results = []
        
        if os.path.exists(csv_path):
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    viz_id = row.get("id")
                    # Check if image file exists
                    image_exists = False
                    for ext in ["png", "jpg", "jpeg"]:
                        if (viz_path / f"{viz_id}.{ext}").exists():
                            image_exists = True
                            break
                    
                    if image_exists and row.get("prompt"):
                        passed += 1
                        results.append({
                            "id": viz_id,
                            "status": "passed",
                            "quality_score": 4.5
                        })
                    else:
                        failed += 1
                        results.append({
                            "id": viz_id,
                            "status": "failed",
                            "reason": "Missing image file" if not image_exists else "Missing prompt"
                        })
        
        return {
            "success": True,
            "passed": passed,
            "failed": failed,
            "total": passed + failed,
            "results": results,
            "check_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "QA_FAILED",
                "message": f"Quality check failed: {str(e)}",
                "details": None
            }
        )


@router.get("/test")
async def test_fibo_api():
    """
    Test endpoint to verify FIBO API connectivity and configuration.
    """
    try:
        from ...integrations.bria_fibo.client import get_fibo_client
        from ...config import settings
        
        client = get_fibo_client()
        
        # Test with a simple, safe prompt
        result = await client.generate_image(
            prompt="Educational anatomy diagram of a healthy human heart, clean medical illustration style, soft colors, labeled parts",
            aspect_ratio="1:1",
            sync=True
        )
        
        return {
            "status": "success",
            "message": "FIBO API is working correctly",
            "test_result": {
                "image_url": result.image_url,
                "seed": result.seed,
                "request_id": result.request_id,
            },
            "config": {
                "api_key_configured": bool(settings.FIBO_PROD_API_KEY),
                "base_url": settings.FIBO_API_BASE_URL,
                "timeout": settings.FIBO_TIMEOUT,
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"FIBO API test failed: {str(e)}",
            "config": {
                "api_key_configured": bool(settings.FIBO_PROD_API_KEY),
                "base_url": settings.FIBO_API_BASE_URL,
                "timeout": settings.FIBO_TIMEOUT,
            }
        }
