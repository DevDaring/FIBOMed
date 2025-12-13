/**
 * ImageGenerator Component - Generates medical visualizations from text prompts
 * Requirements: 2.1, 4.2, 4.3, 6.2
 */
import React, { useState } from 'react';
import { fiboApi } from '../../api/fibo.api';
import { AspectRatio, VisualizationResult, FIBOError } from '../../types/fibo.types';

/**
 * Valid aspect ratio options for the dropdown
 */
const ASPECT_RATIO_OPTIONS: { value: AspectRatio; label: string }[] = [
  { value: '1:1', label: '1:1 (Square)' },
  { value: '2:3', label: '2:3 (Portrait)' },
  { value: '3:2', label: '3:2 (Landscape)' },
  { value: '3:4', label: '3:4 (Portrait)' },
  { value: '4:3', label: '4:3 (Landscape)' },
  { value: '4:5', label: '4:5 (Portrait)' },
  { value: '5:4', label: '5:4 (Landscape)' },
  { value: '9:16', label: '9:16 (Vertical)' },
  { value: '16:9', label: '16:9 (Widescreen)' },
];

export interface ImageGeneratorProps {
  onImageGenerated: (result: VisualizationResult) => void;
  onError: (error: string) => void;
  disabled?: boolean;
  sessionId?: string;
}

export const ImageGenerator: React.FC<ImageGeneratorProps> = ({
  onImageGenerated,
  onError,
  disabled = false,
  sessionId,
}) => {
  const [prompt, setPrompt] = useState('');
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>('1:1');
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  /**
   * Handle form submission to generate visualization
   * Requirements: 2.1 - Submit text prompt for image generation
   */
  const handleGenerate = async () => {
    if (!prompt.trim() || isGenerating || disabled) return;

    setIsGenerating(true);
    setErrorMessage(null);

    try {
      const result = await fiboApi.generateVisualization({
        prompt: prompt.trim(),
        aspectRatio,
        sessionId,
      });

      // Clear prompt on success
      setPrompt('');
      onImageGenerated(result);
    } catch (error) {
      // Requirements: 4.3 - Display error message with API error details
      const fiboError = error as FIBOError;
      const message = fiboError.details
        ? `${fiboError.message}: ${fiboError.details}`
        : fiboError.message || 'Failed to generate visualization';
      
      setErrorMessage(message);
      onError(message);
    } finally {
      setIsGenerating(false);
    }
  };

  /**
   * Handle Enter key press to submit
   */
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleGenerate();
    }
  };

  /**
   * Clear error message when user starts typing
   */
  const handlePromptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPrompt(e.target.value);
    if (errorMessage) {
      setErrorMessage(null);
    }
  };

  return (
    <div className="image-generator">
      <div className="image-generator-header">
        <span className="image-generator-icon">🎨</span>
        <span className="image-generator-title">Generate Visualization</span>
      </div>

      <div className="image-generator-form">
        {/* Prompt Input - Requirements: 2.1 */}
        <div className="prompt-input-container">
          <textarea
            value={prompt}
            onChange={handlePromptChange}
            onKeyPress={handleKeyPress}
            placeholder="Describe the medical visualization you want to generate..."
            className="prompt-input"
            disabled={isGenerating || disabled}
            rows={3}
            aria-label="Visualization prompt"
          />
        </div>

        <div className="image-generator-controls">
          {/* Aspect Ratio Selector - Requirements: 6.2 */}
          <div className="aspect-ratio-selector">
            <label htmlFor="aspect-ratio-select" className="aspect-ratio-label">
              Aspect Ratio:
            </label>
            <select
              id="aspect-ratio-select"
              value={aspectRatio}
              onChange={(e) => setAspectRatio(e.target.value as AspectRatio)}
              className="aspect-ratio-dropdown"
              disabled={isGenerating || disabled}
              aria-label="Select aspect ratio"
            >
              {ASPECT_RATIO_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Generate Button - Requirements: 4.2 */}
          <button
            onClick={handleGenerate}
            disabled={!prompt.trim() || isGenerating || disabled}
            className={`generate-button ${isGenerating ? 'generating' : ''}`}
            aria-label={isGenerating ? 'Generating visualization' : 'Generate visualization'}
          >
            {isGenerating ? (
              <>
                <span className="generate-spinner"></span>
                <span>Generating...</span>
              </>
            ) : (
              <>
                <span>✨</span>
                <span>Generate</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Display - Requirements: 4.3 */}
      {errorMessage && (
        <div className="image-generator-error" role="alert">
          <span className="error-icon">❌</span>
          <span className="error-text">{errorMessage}</span>
          <button
            onClick={() => setErrorMessage(null)}
            className="error-dismiss"
            aria-label="Dismiss error"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
};

export default ImageGenerator;
