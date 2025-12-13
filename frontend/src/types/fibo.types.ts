/**
 * TypeScript type definitions for FIBO integration
 */

/**
 * Valid aspect ratios for FIBO image generation
 */
export type AspectRatio =
  | "1:1"
  | "2:3"
  | "3:2"
  | "3:4"
  | "4:3"
  | "4:5"
  | "5:4"
  | "9:16"
  | "16:9";

/**
 * Request to generate a new visualization
 */
export interface GenerateRequest {
  prompt: string;
  aspectRatio?: AspectRatio;
  negativePrompt?: string;
  sessionId?: string;
}

/**
 * Request to refine an existing visualization
 */
export interface RefineRequest {
  prompt: string;
  seed?: number;
}

/**
 * Response containing visualization details
 */
export interface VisualizationResult {
  visualizationId: string;
  imageUrl: string;
  structuredPrompt: Record<string, unknown>;
  seed: number;
  parentId?: string;
  createdAt: string;
}

/**
 * Error codes for FIBO operations
 */
export type FIBOErrorCode =
  | "GENERATION_FAILED"
  | "REFINEMENT_FAILED"
  | "INVALID_ASPECT_RATIO"
  | "API_TIMEOUT"
  | "STORAGE_ERROR"
  | "VISUALIZATION_NOT_FOUND";

/**
 * Error interface for FIBO operations
 */
export interface FIBOError {
  message: string;
  code: FIBOErrorCode;
  details?: string;
}
