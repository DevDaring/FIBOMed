/**
 * FIBO API integration for medical visualization generation
 * Requirements: 2.1, 3.1, 4.3
 */
import apiClient from './client';
import {
  GenerateRequest,
  RefineRequest,
  VisualizationResult,
  FIBOError,
  FIBOErrorCode,
} from '../types/fibo.types';

/**
 * Backend response format for visualization endpoints
 */
interface VisualizationResponse {
  visualization_id: string;
  image_url: string;
  structured_prompt: Record<string, unknown>;
  seed: number;
  parent_id?: string;
  created_at: string;
}

/**
 * Backend error response format
 */
interface BackendErrorDetail {
  code: string;
  message: string;
  details?: string;
}

/**
 * Backend base URL for static files (images)
 */
const BACKEND_BASE_URL = 'http://localhost:8000';

/**
 * Transform snake_case backend response to camelCase frontend type
 * Converts relative image URLs to absolute URLs pointing to backend
 */
function transformResponse(response: VisualizationResponse): VisualizationResult {
  // Convert relative image URL to absolute URL pointing to backend
  let imageUrl = response.image_url;
  if (imageUrl && imageUrl.startsWith('/')) {
    imageUrl = `${BACKEND_BASE_URL}${imageUrl}`;
  }
  
  return {
    visualizationId: response.visualization_id,
    imageUrl: imageUrl,
    structuredPrompt: response.structured_prompt,
    seed: response.seed,
    parentId: response.parent_id,
    createdAt: response.created_at,
  };
}

/**
 * Transform camelCase frontend request to snake_case backend format
 */
function transformGenerateRequest(request: GenerateRequest): Record<string, unknown> {
  return {
    prompt: request.prompt,
    aspect_ratio: request.aspectRatio,
    negative_prompt: request.negativePrompt,
    session_id: request.sessionId,
  };
}

/**
 * Create a FIBOError from backend error response
 */
function createFIBOError(error: unknown): FIBOError {
  // Handle axios error response
  if (error && typeof error === 'object' && 'response' in error) {
    const axiosError = error as { response?: { data?: { detail?: BackendErrorDetail } } };
    const detail = axiosError.response?.data?.detail;
    
    if (detail) {
      return {
        message: detail.message,
        code: detail.code as FIBOErrorCode,
        details: detail.details,
      };
    }
  }
  
  // Handle generic errors
  const message = error instanceof Error ? error.message : 'An unknown error occurred';
  return {
    message,
    code: 'GENERATION_FAILED',
    details: undefined,
  };
}

export const fiboApi = {
  /**
   * Generate a new visualization from text prompt
   * Requirements: 2.1
   */
  generateVisualization: async (request: GenerateRequest): Promise<VisualizationResult> => {
    try {
      const response = await apiClient.post<VisualizationResponse>(
        '/fibo/generate',
        transformGenerateRequest(request)
      );
      return transformResponse(response.data);
    } catch (error) {
      throw createFIBOError(error);
    }
  },

  /**
   * Refine an existing visualization with additional instructions
   * Requirements: 3.1
   */
  refineVisualization: async (
    visualizationId: string,
    request: RefineRequest
  ): Promise<VisualizationResult> => {
    try {
      const response = await apiClient.post<VisualizationResponse>(
        `/fibo/refine/${visualizationId}`,
        request
      );
      return transformResponse(response.data);
    } catch (error) {
      throw createFIBOError(error);
    }
  },

  /**
   * Get visualization details by ID
   * Requirements: 4.3
   */
  getVisualization: async (visualizationId: string): Promise<VisualizationResult> => {
    try {
      const response = await apiClient.get<VisualizationResponse>(
        `/fibo/${visualizationId}`
      );
      return transformResponse(response.data);
    } catch (error) {
      throw createFIBOError(error);
    }
  },
};

export default fiboApi;
