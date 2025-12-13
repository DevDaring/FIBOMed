"""Storage Service for FIBO Visualizations"""
import csv
import json
import os
import uuid
import httpx
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from threading import Lock

from ..config import settings
from ..core.exceptions import FIBOStorageError


class StorageService:
    """Service for storing generated visualizations and prompts"""

    def __init__(self):
        """Initialize storage service with paths and ensure directories exist"""
        self.viz_path = Path(settings.GENERATED_PATH) / "visualizations"
        self.prompt_path = Path(settings.GENERATED_PATH) / "prompts"
        self.csv_path = Path(settings.CSV_DATA_PATH) / "visualizations.csv"
        self.lock = Lock()
        
        # Ensure directories exist on startup (Docker-compatible)
        self._ensure_directories()
        self._ensure_csv_exists()

    def _ensure_directories(self):
        """Ensure all required directories exist"""
        self.viz_path.mkdir(parents=True, exist_ok=True)
        self.prompt_path.mkdir(parents=True, exist_ok=True)

    def _ensure_csv_exists(self):
        """Ensure visualizations CSV exists with headers"""
        if not self.csv_path.exists():
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "id", "prompt", "structured_prompt", "image_path",
                    "seed", "parent_id", "aspect_ratio", "created_at"
                ])

    async def save_visualization(
        self,
        image_url: str,
        structured_prompt: dict,
        seed: int,
        original_prompt: str,
        aspect_ratio: str = "1:1",
        parent_id: Optional[str] = None,
        api_request_id: Optional[str] = None
    ) -> str:
        """
        Download and save visualization with metadata.
        
        Args:
            image_url: URL to download the image from
            structured_prompt: The structured prompt object from FIBO API
            seed: The seed value used for generation
            original_prompt: The user's original text prompt
            aspect_ratio: The aspect ratio used
            parent_id: Optional parent visualization ID for refinements
            api_request_id: Optional BRIA API request ID
            
        Returns:
            visualization_id: The unique ID for this visualization
            
        Raises:
            FIBOStorageError: If storage operation fails
        """
        visualization_id = str(uuid.uuid4())
        
        try:
            # Download and save image
            image_path = await self._download_image(image_url, visualization_id)
            
            # Save structured prompt as JSON
            await self.save_prompt(
                visualization_id=visualization_id,
                structured_prompt=structured_prompt,
                seed=seed,
                original_prompt=original_prompt,
                aspect_ratio=aspect_ratio,
                parent_id=parent_id,
                api_request_id=api_request_id
            )
            
            # Record in CSV
            await self.save_to_csv(
                visualization_id=visualization_id,
                prompt=original_prompt,
                structured_prompt=structured_prompt,
                image_path=str(image_path),
                seed=seed,
                parent_id=parent_id,
                aspect_ratio=aspect_ratio
            )
            
            return visualization_id
            
        except Exception as e:
            raise FIBOStorageError(
                message=f"Failed to save visualization: {str(e)}",
                code="STORAGE_ERROR",
                details=str(e)
            )

    async def _download_image(self, image_url: str, visualization_id: str) -> Path:
        """
        Download image from URL and save locally.
        
        Args:
            image_url: URL to download from
            visualization_id: ID to use for filename
            
        Returns:
            Path to saved image file
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                
                # Determine file extension from content type or URL
                content_type = response.headers.get("content-type", "")
                if "png" in content_type or image_url.endswith(".png"):
                    extension = "png"
                elif "jpeg" in content_type or "jpg" in content_type or image_url.endswith(".jpg"):
                    extension = "jpg"
                else:
                    extension = "png"  # Default to PNG
                
                image_path = self.viz_path / f"{visualization_id}.{extension}"
                
                with open(image_path, "wb") as f:
                    f.write(response.content)
                
                return image_path
                
        except httpx.HTTPError as e:
            raise FIBOStorageError(
                message=f"Failed to download image: {str(e)}",
                code="DOWNLOAD_ERROR",
                details=str(e)
            )

    async def save_prompt(
        self,
        visualization_id: str,
        structured_prompt: dict,
        seed: int,
        original_prompt: str,
        aspect_ratio: str,
        parent_id: Optional[str] = None,
        api_request_id: Optional[str] = None
    ) -> Path:
        """
        Store structured prompt as JSON file.
        
        Args:
            visualization_id: Unique ID for the visualization
            structured_prompt: The structured prompt object
            seed: Seed value used for generation
            original_prompt: User's original text prompt
            aspect_ratio: Aspect ratio used
            parent_id: Optional parent ID for refinements
            api_request_id: Optional BRIA API request ID
            
        Returns:
            Path to saved JSON file
        """
        prompt_data = {
            "visualization_id": visualization_id,
            "structured_prompt": structured_prompt,
            "seed": seed,
            "parent_id": parent_id,
            "original_prompt": original_prompt,
            "aspect_ratio": aspect_ratio,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "api_request_id": api_request_id
        }
        
        prompt_file = self.prompt_path / f"{visualization_id}.json"
        
        try:
            with open(prompt_file, "w", encoding="utf-8") as f:
                json.dump(prompt_data, f, indent=2)
            return prompt_file
        except Exception as e:
            raise FIBOStorageError(
                message=f"Failed to save prompt: {str(e)}",
                code="PROMPT_SAVE_ERROR",
                details=str(e)
            )

    async def save_to_csv(
        self,
        visualization_id: str,
        prompt: str,
        structured_prompt: dict,
        image_path: str,
        seed: int,
        parent_id: Optional[str],
        aspect_ratio: str
    ) -> bool:
        """
        Record visualization metadata in visualizations.csv.
        
        Args:
            visualization_id: Unique ID
            prompt: Original user prompt
            structured_prompt: Structured prompt object
            image_path: Path to saved image
            seed: Seed value
            parent_id: Optional parent ID
            aspect_ratio: Aspect ratio used
            
        Returns:
            True if successful
        """
        try:
            with self.lock:
                with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        visualization_id,
                        prompt,
                        json.dumps(structured_prompt),
                        image_path,
                        seed,
                        parent_id or "",
                        aspect_ratio,
                        datetime.utcnow().isoformat()
                    ])
            return True
        except Exception as e:
            raise FIBOStorageError(
                message=f"Failed to save to CSV: {str(e)}",
                code="CSV_SAVE_ERROR",
                details=str(e)
            )

    async def get_visualization(self, visualization_id: str) -> Optional[Dict]:
        """
        Retrieve visualization metadata from CSV.
        
        Args:
            visualization_id: The visualization ID to look up
            
        Returns:
            Dict with visualization metadata or None if not found
        """
        try:
            with self.lock:
                if not self.csv_path.exists():
                    return None
                    
                with open(self.csv_path, "r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row["id"] == visualization_id:
                            return {
                                "visualization_id": row["id"],
                                "prompt": row["prompt"],
                                "structured_prompt": json.loads(row["structured_prompt"]) if row["structured_prompt"] else {},
                                "image_path": row["image_path"],
                                "seed": int(row["seed"]) if row["seed"] else None,
                                "parent_id": row["parent_id"] if row["parent_id"] else None,
                                "aspect_ratio": row["aspect_ratio"],
                                "created_at": row["created_at"]
                            }
            return None
        except Exception as e:
            raise FIBOStorageError(
                message=f"Failed to retrieve visualization: {str(e)}",
                code="RETRIEVAL_ERROR",
                details=str(e)
            )

    async def get_prompt(self, visualization_id: str) -> Optional[Dict]:
        """
        Retrieve stored JSON prompt for a visualization.
        
        Args:
            visualization_id: The visualization ID
            
        Returns:
            Dict with prompt data or None if not found
        """
        prompt_file = self.prompt_path / f"{visualization_id}.json"
        
        try:
            if not prompt_file.exists():
                return None
                
            with open(prompt_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise FIBOStorageError(
                message=f"Failed to retrieve prompt: {str(e)}",
                code="PROMPT_RETRIEVAL_ERROR",
                details=str(e)
            )

    async def get_image_url(self, visualization_id: str) -> Optional[str]:
        """
        Get the local URL for a visualization image.
        
        Args:
            visualization_id: The visualization ID
            
        Returns:
            Local URL path or None if not found
        """
        # Check for common extensions
        for ext in ["png", "jpg", "jpeg"]:
            image_path = self.viz_path / f"{visualization_id}.{ext}"
            if image_path.exists():
                return f"/visualizations/{visualization_id}.{ext}"
        return None


# Singleton instance
storage_service = StorageService()
