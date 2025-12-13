/**
 * ImageViewer Component - Displays generated visualizations with refinement support
 * Requirements: 4.1, 4.2, 4.4, 4.5
 */
import React, { useState } from 'react';

export interface ImageViewerProps {
  imageUrl: string;
  visualizationId: string;
  onRefine?: (prompt: string) => void;
  allowFullscreen?: boolean;
  isLoading?: boolean;
  loadingText?: string;
}

export const ImageViewer: React.FC<ImageViewerProps> = ({
  imageUrl,
  visualizationId,
  onRefine,
  allowFullscreen = true,
  isLoading = false,
  loadingText = 'Generating visualization...',
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [refinementPrompt, setRefinementPrompt] = useState('');
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  const handleImageClick = () => {
    if (allowFullscreen && !isLoading && imageLoaded) {
      setIsFullscreen(true);
    }
  };

  const handleCloseFullscreen = () => {
    setIsFullscreen(false);
  };

  const handleRefineSubmit = () => {
    if (refinementPrompt.trim() && onRefine) {
      onRefine(refinementPrompt.trim());
      setRefinementPrompt('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleRefineSubmit();
    }
  };

  const handleImageLoad = () => {
    setImageLoaded(true);
    setImageError(false);
  };

  const handleImageError = () => {
    setImageError(true);
    setImageLoaded(false);
  };

  // Handle escape key to close fullscreen
  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };

    if (isFullscreen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isFullscreen]);

  return (
    <div className="image-viewer" data-visualization-id={visualizationId}>
      {/* Loading State */}
      {isLoading && (
        <div className="image-viewer-loading">
          <div className="image-loading-spinner"></div>
          <span className="image-loading-text">{loadingText}</span>
        </div>
      )}

      {/* Image Display */}
      {!isLoading && !imageError && (
        <div className="image-viewer-container">
          <div
            className={`image-wrapper ${allowFullscreen ? 'clickable' : ''}`}
            onClick={handleImageClick}
            role={allowFullscreen ? 'button' : undefined}
            tabIndex={allowFullscreen ? 0 : undefined}
            onKeyPress={(e) => e.key === 'Enter' && handleImageClick()}
            aria-label={allowFullscreen ? 'Click to view fullscreen' : undefined}
          >
            {!imageLoaded && (
              <div className="image-placeholder">
                <div className="image-loading-spinner small"></div>
              </div>
            )}
            <img
              src={imageUrl}
              alt="Generated visualization"
              onLoad={handleImageLoad}
              onError={handleImageError}
              style={{ display: imageLoaded ? 'block' : 'none' }}
            />
            {allowFullscreen && imageLoaded && (
              <div className="fullscreen-hint">
                <span>🔍 Click to enlarge</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error State */}
      {imageError && (
        <div className="image-viewer-error">
          <span>❌ Failed to load image</span>
        </div>
      )}

      {/* Refinement Input - Requirements 4.5 */}
      {onRefine && !isLoading && imageLoaded && (
        <div className="image-refinement">
          <input
            type="text"
            value={refinementPrompt}
            onChange={(e) => setRefinementPrompt(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe refinements..."
            className="refinement-input"
            aria-label="Refinement prompt"
          />
          <button
            onClick={handleRefineSubmit}
            disabled={!refinementPrompt.trim()}
            className="refinement-button"
            aria-label="Refine visualization"
          >
            ✨ Refine
          </button>
        </div>
      )}

      {/* Fullscreen Modal - Requirements 4.4 */}
      {isFullscreen && (
        <div
          className="image-fullscreen-modal"
          onClick={handleCloseFullscreen}
          role="dialog"
          aria-modal="true"
          aria-label="Fullscreen image viewer"
        >
          <div className="fullscreen-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="fullscreen-close"
              onClick={handleCloseFullscreen}
              aria-label="Close fullscreen"
            >
              ✕
            </button>
            <img src={imageUrl} alt="Generated visualization (fullscreen)" />
          </div>
          <div className="fullscreen-backdrop-hint">
            Click outside or press ESC to close
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageViewer;
