"""FIBO Service for Medical Visualization Generation"""
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, Set

from ..config import settings
from ..core.exceptions import FIBOValidationError, FIBOStorageError, FIBOAPIError
from ..integrations.bria_fibo.client import FIBOClient, get_fibo_client, VALID_ASPECT_RATIOS
from .storage_service import StorageService, storage_service


# Medical/anatomical keywords that trigger background enhancement
MEDICAL_KEYWORDS: Set[str] = {
    # Organs
    "heart", "lung", "lungs", "liver", "kidney", "kidneys", "brain", "stomach",
    "intestine", "intestines", "colon", "pancreas", "spleen", "bladder", "uterus",
    "ovary", "ovaries", "prostate", "thyroid", "gallbladder", "appendix",
    # Body systems
    "artery", "arteries", "vein", "veins", "blood vessel", "blood vessels",
    "capillary", "capillaries", "aorta", "cardiac", "cardiovascular",
    "respiratory", "digestive", "nervous", "circulatory",
    # Anatomy terms
    "organ", "organs", "tissue", "muscle", "muscles", "bone", "bones",
    "skeleton", "spine", "vertebra", "vertebrae", "rib", "ribs",
    "chest", "abdomen", "abdominal", "thorax", "thoracic", "pelvis", "pelvic",
    # Medical conditions
    "tumor", "cancer", "blockage", "blocked", "clot", "inflammation",
    "infection", "disease", "lesion", "cyst", "polyp",
    # Anatomical structures
    "bronchi", "bronchus", "alveoli", "trachea", "esophagus", "larynx",
    "pharynx", "diaphragm", "tendon", "ligament", "cartilage",
}

# Background enhancement suffix for medical prompts
MEDICAL_BACKGROUND_SUFFIX = (
    ", set against a softly blurred interior of the human body cavity, "
    "with subtle anatomical context visible in the background, "
    "professional medical illustration style with depth of field effect"
)


def _is_medical_prompt(prompt: str) -> bool:
    """
    Check if the prompt contains medical/anatomical keywords.
    
    Args:
        prompt: The user's prompt text
        
    Returns:
        True if medical keywords are detected
    """
    prompt_lower = prompt.lower()
    for keyword in MEDICAL_KEYWORDS:
        # Use word boundary matching to avoid partial matches
        if re.search(r'\b' + re.escape(keyword) + r'\b', prompt_lower):
            return True
    return False


def _enhance_medical_prompt(prompt: str) -> str:
    """
    Enhance a medical prompt with blurred body interior background context.
    
    Args:
        prompt: The original user prompt
        
    Returns:
        Enhanced prompt with medical background context
    """
    if _is_medical_prompt(prompt):
        # Check if prompt already mentions background
        if "background" not in prompt.lower():
            return prompt + MEDICAL_BACKGROUND_SUFFIX
    return prompt


@dataclass
class VisualizationResult:
    """Result from visualization generation or retrieval"""
    visualization_id: str
    image_url: str
    structured_prompt: Dict[str, Any]
    seed: int
    parent_id: Optional[str] = None
    created_at: Optional[str] = None
    aspect_ratio: str = "1:1"
    original_prompt: Optional[str] = None


class FIBOService:
    """Service for FIBO image generation operations"""

    def __init__(
        self,
        client: Optional[FIBOClient] = None,
        storage: Optional[StorageService] = None
    ):
        """
        Initialize FIBO service.
        
        Args:
            client: Optional FIBOClient instance. Uses singleton if not provided.
            storage: Optional StorageService instance. Uses singleton if not provided.
        """
        self._client = client
        self._storage = storage

    @property
    def client(self) -> FIBOClient:
        """Get the FIBO client instance."""
        if self._client is None:
            self._client = get_fibo_client()
        return self._client

    @property
    def storage(self) -> StorageService:
        """Get the storage service instance."""
        if self._storage is None:
            self._storage = storage_service
        return self._storage

    def _validate_aspect_ratio(self, aspect_ratio: str) -> None:
        """
        Validate aspect ratio is in the allowed set.
        
        Args:
            aspect_ratio: Aspect ratio string to validate
            
        Raises:
            FIBOValidationError: If aspect ratio is invalid
        """
        if aspect_ratio not in VALID_ASPECT_RATIOS:
            raise FIBOValidationError(
                message=f"Invalid aspect ratio: {aspect_ratio}",
                code="INVALID_ASPECT_RATIO",
                details=f"Valid options are: {', '.join(VALID_ASPECT_RATIOS)}"
            )

    async def generate_visualization(
        self,
        prompt: str,
        aspect_ratio: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> VisualizationResult:
        """
        Generate a new visualization from text prompt.
        
        Calls the FIBO API with the prompt, downloads and saves the generated
        image, and records the visualization metadata in CSV storage.
        
        Args:
            prompt: Text prompt describing the visualization to generate
            aspect_ratio: Image aspect ratio (default: "1:1")
            negative_prompt: Optional text describing what to exclude
            session_id: Optional session identifier for tracking
            
        Returns:
            VisualizationResult with the generated visualization details
            
        Raises:
            FIBOValidationError: If inputs are invalid
            FIBOAPIError: If API call fails
            FIBOStorageError: If storage operation fails
        """
        # Use default aspect ratio if not specified (Requirement 6.1)
        if aspect_ratio is None:
            aspect_ratio = settings.FIBO_DEFAULT_ASPECT_RATIO
        
        # Validate aspect ratio (Requirement 6.3)
        self._validate_aspect_ratio(aspect_ratio)
        
        # Enhance medical prompts with blurred body interior background
        enhanced_prompt = _enhance_medical_prompt(prompt)
        
        # Call FIBO API (Requirements 2.1, 5.1)
        api_result = await self.client.generate_image(
            prompt=enhanced_prompt,
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt,
            sync=settings.FIBO_SYNC_MODE
        )
        
        # Save visualization (Requirements 2.2, 2.3, 7.1, 7.2)
        visualization_id = await self.storage.save_visualization(
            image_url=api_result.image_url,
            structured_prompt=api_result.structured_prompt,
            seed=api_result.seed,
            original_prompt=prompt,
            aspect_ratio=aspect_ratio,
            parent_id=None,
            api_request_id=api_result.request_id
        )
        
        # Get local image URL (Requirement 2.4)
        local_image_url = await self.storage.get_image_url(visualization_id)
        if local_image_url is None:
            local_image_url = api_result.image_url  # Fallback to remote URL
        
        return VisualizationResult(
            visualization_id=visualization_id,
            image_url=local_image_url,
            structured_prompt=api_result.structured_prompt,
            seed=api_result.seed,
            parent_id=None,
            created_at=datetime.utcnow().isoformat() + "Z",
            aspect_ratio=aspect_ratio,
            original_prompt=prompt
        )

    async def refine_visualization(
        self,
        visualization_id: str,
        refinement_prompt: str
    ) -> VisualizationResult:
        """
        Refine an existing visualization with additional instructions.
        
        Retrieves the original visualization's structured prompt and seed,
        then calls the FIBO API with both the refinement prompt and original
        structured prompt for deterministic refinement.
        
        Args:
            visualization_id: ID of the visualization to refine
            refinement_prompt: Additional instructions for refinement
            
        Returns:
            VisualizationResult with the refined visualization details
            
        Raises:
            FIBOValidationError: If visualization not found
            FIBOAPIError: If API call fails
            FIBOStorageError: If storage operation fails
        """
        # Get original visualization data (Requirement 3.3)
        original_prompt_data = await self.storage.get_prompt(visualization_id)
        if original_prompt_data is None:
            raise FIBOValidationError(
                message=f"Visualization not found: {visualization_id}",
                code="VISUALIZATION_NOT_FOUND",
                details=f"No visualization exists with ID: {visualization_id}"
            )
        
        # Extract original structured prompt and seed (Requirements 3.1, 3.4)
        original_structured_prompt = original_prompt_data.get("structured_prompt", {})
        original_seed = original_prompt_data.get("seed")
        original_aspect_ratio = original_prompt_data.get("aspect_ratio", "1:1")
        
        # Convert structured prompt to JSON string for API
        structured_prompt_str = json.dumps(original_structured_prompt)
        
        # Call FIBO API with refinement (Requirements 3.1, 3.4)
        api_result = await self.client.generate_image(
            prompt=refinement_prompt,
            structured_prompt=structured_prompt_str,
            seed=original_seed,
            aspect_ratio=original_aspect_ratio,
            sync=settings.FIBO_SYNC_MODE
        )
        
        # Save refined visualization with parent_id linking (Requirements 3.2, 3.3, 7.3)
        new_visualization_id = await self.storage.save_visualization(
            image_url=api_result.image_url,
            structured_prompt=api_result.structured_prompt,
            seed=api_result.seed,
            original_prompt=refinement_prompt,
            aspect_ratio=original_aspect_ratio,
            parent_id=visualization_id,
            api_request_id=api_result.request_id
        )
        
        # Get local image URL
        local_image_url = await self.storage.get_image_url(new_visualization_id)
        if local_image_url is None:
            local_image_url = api_result.image_url
        
        return VisualizationResult(
            visualization_id=new_visualization_id,
            image_url=local_image_url,
            structured_prompt=api_result.structured_prompt,
            seed=api_result.seed,
            parent_id=visualization_id,
            created_at=datetime.utcnow().isoformat() + "Z",
            aspect_ratio=original_aspect_ratio,
            original_prompt=refinement_prompt
        )

    async def get_visualization(
        self,
        visualization_id: str
    ) -> VisualizationResult:
        """
        Retrieve a stored visualization by ID.
        
        Args:
            visualization_id: The visualization ID to retrieve
            
        Returns:
            VisualizationResult with the visualization details
            
        Raises:
            FIBOValidationError: If visualization not found
            FIBOStorageError: If retrieval fails
        """
        # Get visualization from CSV
        viz_data = await self.storage.get_visualization(visualization_id)
        if viz_data is None:
            raise FIBOValidationError(
                message=f"Visualization not found: {visualization_id}",
                code="VISUALIZATION_NOT_FOUND",
                details=f"No visualization exists with ID: {visualization_id}"
            )
        
        # Get local image URL
        local_image_url = await self.storage.get_image_url(visualization_id)
        if local_image_url is None:
            # Fallback to image_path from CSV
            local_image_url = viz_data.get("image_path", "")
        
        return VisualizationResult(
            visualization_id=viz_data["visualization_id"],
            image_url=local_image_url,
            structured_prompt=viz_data.get("structured_prompt", {}),
            seed=viz_data.get("seed", 0),
            parent_id=viz_data.get("parent_id"),
            created_at=viz_data.get("created_at"),
            aspect_ratio=viz_data.get("aspect_ratio", "1:1"),
            original_prompt=viz_data.get("prompt")
        )


# Singleton instance for convenience
fibo_service: Optional[FIBOService] = None


def get_fibo_service() -> FIBOService:
    """Get or create the singleton FIBO service instance."""
    global fibo_service
    if fibo_service is None:
        fibo_service = FIBOService()
    return fibo_service
