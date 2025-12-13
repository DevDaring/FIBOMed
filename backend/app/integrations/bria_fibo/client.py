"""BRIA FIBO API Client for Image Generation"""
import asyncio
import json
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

import httpx

from ...config import settings
from ...core.exceptions import FIBOAPIError, FIBOValidationError


# Valid aspect ratios supported by FIBO API
VALID_ASPECT_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9"]


@dataclass
class FIBOGenerationResult:
    """Result from FIBO image generation"""
    image_url: str
    seed: int
    structured_prompt: Dict[str, Any]
    request_id: str
    warning: Optional[str] = None


class FIBOClient:
    """Client for BRIA FIBO API"""

    BASE_URL = "https://engine.prod.bria-api.com/v2"
    GENERATE_ENDPOINT = "/image/generate"
    MAX_POLL_ATTEMPTS = 60  # Max polling attempts for async mode
    POLL_INTERVAL = 2  # Seconds between polls

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FIBO client.
        
        Args:
            api_key: FIBO API key. If not provided, uses settings.FIBO_PROD_API_KEY
        """
        self.api_key = api_key or settings.FIBO_PROD_API_KEY
        self.timeout = settings.FIBO_TIMEOUT
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers={
                    "api_token": self.api_key,
                    "Content-Type": "application/json"
                }
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

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

    def _handle_error_response(
        self, 
        status_code: int, 
        response_data: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> None:
        """
        Handle error responses from FIBO API.
        
        Args:
            status_code: HTTP status code
            response_data: Response JSON data
            request_id: Request ID from response
            
        Raises:
            FIBOAPIError: With appropriate error details
        """
        error = response_data.get("error", {})
        error_code = error.get("code", status_code)
        error_message = error.get("message", "Unknown error")
        error_details = error.get("details")
        req_id = request_id or response_data.get("request_id", "unknown")

        if status_code == 400:
            raise FIBOAPIError(
                message=f"Bad request: {error_message}",
                code=f"BAD_REQUEST_{error_code}",
                details=f"Request ID: {req_id}. {error_details or ''}"
            )
        elif status_code == 401:
            raise FIBOAPIError(
                message="Authentication failed",
                code="AUTH_FAILED",
                details=f"Request ID: {req_id}. Check your API key."
            )
        elif status_code == 403:
            raise FIBOAPIError(
                message="Permission denied",
                code="PERMISSION_DENIED",
                details=f"Request ID: {req_id}. {error_details or ''}"
            )
        elif status_code == 422:
            raise FIBOAPIError(
                message=f"Content moderation failure: {error_message}",
                code="CONTENT_MODERATION",
                details=f"Request ID: {req_id}. {error_details or ''}"
            )
        elif status_code == 429:
            raise FIBOAPIError(
                message="Rate limit exceeded",
                code="RATE_LIMITED",
                details=f"Request ID: {req_id}. Please retry later."
            )
        elif status_code >= 500:
            raise FIBOAPIError(
                message=f"Server error: {error_message}",
                code=f"SERVER_ERROR_{status_code}",
                details=f"Request ID: {req_id}. {error_details or ''}"
            )
        else:
            raise FIBOAPIError(
                message=f"API error: {error_message}",
                code=f"API_ERROR_{status_code}",
                details=f"Request ID: {req_id}. {error_details or ''}"
            )


    async def poll_status(self, status_url: str) -> FIBOGenerationResult:
        """
        Poll the status URL until generation is complete.
        
        Args:
            status_url: URL to poll for generation status
            
        Returns:
            FIBOGenerationResult with the generated image details
            
        Raises:
            FIBOAPIError: If polling fails or times out
        """
        for attempt in range(self.MAX_POLL_ATTEMPTS):
            try:
                response = await self.client.get(status_url)
                response_data = response.json()
                
                if response.status_code == 200:
                    # Generation complete
                    result = response_data.get("result", {})
                    structured_prompt = result.get("structured_prompt", "{}")
                    
                    # Parse structured_prompt if it's a string
                    if isinstance(structured_prompt, str):
                        try:
                            structured_prompt = json.loads(structured_prompt)
                        except json.JSONDecodeError:
                            structured_prompt = {"raw": structured_prompt}
                    
                    return FIBOGenerationResult(
                        image_url=result.get("image_url", ""),
                        seed=result.get("seed", 0),
                        structured_prompt=structured_prompt,
                        request_id=response_data.get("request_id", ""),
                        warning=response_data.get("warning")
                    )
                elif response.status_code == 202:
                    # Still processing, continue polling
                    await asyncio.sleep(self.POLL_INTERVAL)
                    continue
                else:
                    # Error response
                    self._handle_error_response(
                        response.status_code,
                        response_data,
                        response_data.get("request_id")
                    )
                    
            except httpx.TimeoutException:
                if attempt < self.MAX_POLL_ATTEMPTS - 1:
                    await asyncio.sleep(self.POLL_INTERVAL)
                    continue
                raise FIBOAPIError(
                    message="Polling timed out",
                    code="POLL_TIMEOUT",
                    details=f"Status URL: {status_url}"
                )
            except httpx.RequestError as e:
                raise FIBOAPIError(
                    message=f"Network error during polling: {str(e)}",
                    code="NETWORK_ERROR",
                    details=f"Status URL: {status_url}"
                )
        
        raise FIBOAPIError(
            message="Max polling attempts exceeded",
            code="POLL_TIMEOUT",
            details=f"Exceeded {self.MAX_POLL_ATTEMPTS} attempts"
        )


    async def generate_image(
        self,
        prompt: Optional[str] = None,
        images: Optional[List[str]] = None,
        structured_prompt: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "1:1",
        seed: Optional[int] = None,
        sync: bool = True,
        retry_on_timeout: bool = True
    ) -> FIBOGenerationResult:
        """
        Generate an image using FIBO API.
        
        Args:
            prompt: Text prompt for image generation
            images: List of image URLs for inspiration
            structured_prompt: JSON string of structured prompt for refinement
            negative_prompt: Text describing what to exclude
            aspect_ratio: Image aspect ratio (default: "1:1")
            seed: Seed for deterministic generation
            sync: If True, wait for result; if False, return status URL
            retry_on_timeout: If True, retry once on timeout
            
        Returns:
            FIBOGenerationResult with generated image details
            
        Raises:
            FIBOValidationError: If inputs are invalid
            FIBOAPIError: If API call fails
        """
        # Validate aspect ratio
        self._validate_aspect_ratio(aspect_ratio)
        
        # Build request payload
        payload: Dict[str, Any] = {
            "aspect_ratio": aspect_ratio,
            "sync": sync
        }
        
        if prompt is not None:
            payload["prompt"] = prompt
        if images is not None:
            payload["images"] = images
        if structured_prompt is not None:
            payload["structured_prompt"] = structured_prompt
        if negative_prompt is not None:
            payload["negative_prompt"] = negative_prompt
        if seed is not None:
            payload["seed"] = seed
        
        url = f"{self.BASE_URL}{self.GENERATE_ENDPOINT}"
        
        async def make_request() -> httpx.Response:
            return await self.client.post(url, json=payload)
        
        try:
            response = await make_request()
        except httpx.TimeoutException:
            if retry_on_timeout:
                # Retry once on timeout (Requirement 5.4)
                try:
                    response = await make_request()
                except httpx.TimeoutException:
                    raise FIBOAPIError(
                        message="Request timed out after retry",
                        code="API_TIMEOUT",
                        details=f"Timeout after {self.timeout}s (retried once)"
                    )
            else:
                raise FIBOAPIError(
                    message="Request timed out",
                    code="API_TIMEOUT",
                    details=f"Timeout after {self.timeout}s"
                )
        except httpx.RequestError as e:
            raise FIBOAPIError(
                message=f"Network error: {str(e)}",
                code="NETWORK_ERROR",
                details=str(e)
            )
        
        response_data = response.json()
        request_id = response_data.get("request_id", "")
        
        # Handle response based on status code
        if response.status_code == 200:
            # Synchronous success - result is ready
            result = response_data.get("result", {})
            structured_prompt_result = result.get("structured_prompt", "{}")
            
            # Parse structured_prompt if it's a string
            if isinstance(structured_prompt_result, str):
                try:
                    structured_prompt_result = json.loads(structured_prompt_result)
                except json.JSONDecodeError:
                    structured_prompt_result = {"raw": structured_prompt_result}
            
            return FIBOGenerationResult(
                image_url=result.get("image_url", ""),
                seed=result.get("seed", 0),
                structured_prompt=structured_prompt_result,
                request_id=request_id,
                warning=response_data.get("warning")
            )
            
        elif response.status_code == 202:
            # Asynchronous - need to poll status URL
            status_url = response_data.get("status_url")
            if not status_url:
                raise FIBOAPIError(
                    message="No status URL in async response",
                    code="MISSING_STATUS_URL",
                    details=f"Request ID: {request_id}"
                )
            return await self.poll_status(status_url)
            
        else:
            # Error response
            self._handle_error_response(
                response.status_code,
                response_data,
                request_id
            )
            # This line won't be reached but satisfies type checker
            raise FIBOAPIError(
                message="Unexpected error",
                code="UNEXPECTED",
                details=f"Status: {response.status_code}"
            )


# Singleton instance for convenience
fibo_client: Optional[FIBOClient] = None


def get_fibo_client() -> FIBOClient:
    """Get or create the singleton FIBO client instance."""
    global fibo_client
    if fibo_client is None:
        fibo_client = FIBOClient()
    return fibo_client
