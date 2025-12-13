# Implementation Plan

This plan modifies the existing FIBOMed project to add FIBO integration and fix environment loading.
Target deployment: GCP Cloud Run with Docker (no database, CSV/file-based storage).

- [x] 1. Fix configuration to load environment from secrets/.env





  - [x] 1.1 Modify backend/app/config.py to use secrets/.env path


    - Change env_file from ".env" to "secrets/.env"
    - Add FIBO_PROD_API_KEY field
    - Add GOOGLE_API_KEY field  
    - Add FIBO API configuration fields (base URL, timeout, default aspect ratio)
    - Update GEMINI_MODEL to use GEMINI_MODEL_NAME from env
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Create data directory structure and CSV for visualizations






  - [x] 2.1 Update scripts/init_csv.py to create visualization directories

    - Add data/generated/visualizations/ directory creation
    - Add data/generated/prompts/ directory creation
    - Add visualizations.csv with columns: id, prompt, structured_prompt, image_path, seed, parent_id, aspect_ratio, created_at
    - _Requirements: 2.3, 7.1, 7.2_

- [x] 3. Add FIBO exception classes to existing exceptions






  - [x] 3.1 Modify backend/app/core/exceptions.py

    - Add FIBOError base class
    - Add FIBOAPIError for API failures
    - Add FIBOStorageError for storage failures
    - Add FIBOValidationError for validation failures
    - _Requirements: 5.3_

- [x] 4. Create FIBO API client integration





  - [x] 4.1 Create backend/app/integrations/bria_fibo/__init__.py


    - Create directory structure and init file
    - _Requirements: 2.1_

  - [x] 4.2 Create backend/app/integrations/bria_fibo/client.py

    - Implement FIBOClient class with httpx async client
    - Implement generate_image method calling BRIA API at https://engine.prod.bria-api.com/v2/image/generate
    - Implement poll_status method for async responses (202 status)
    - Handle all API response codes (200, 202, 400, 401, 422, 429, 5XX)
    - Add retry logic for timeouts
    - _Requirements: 2.1, 5.1, 5.2, 5.3, 5.4_

- [x] 5. Create storage service for visualizations (CSV-based)






  - [x] 5.1 Create backend/app/services/storage_service.py

    - Implement save_visualization method to download image from URL and store locally
    - Implement save_prompt method to store structured prompts as JSON files
    - Implement save_to_csv method to record visualization metadata in visualizations.csv
    - Implement get_visualization method to retrieve from CSV
    - Implement get_prompt method to retrieve stored JSON prompts
    - Ensure directories exist on startup (Docker-compatible)
    - _Requirements: 2.3, 7.1, 7.2_

- [x] 6. Create FIBO service business logic






  - [x] 6.1 Create backend/app/services/fibo_service.py

    - Implement generate_visualization method (calls FIBO API, saves image, records in CSV)
    - Implement refine_visualization method with parent_id linking
    - Implement get_visualization method
    - Add aspect ratio validation with valid options: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 6.1, 6.2, 6.3_


- [x] 7. Create FIBO API schemas





  - [x] 7.1 Create backend/app/schemas/fibo_schemas.py

    - Define GenerateRequest schema with prompt, aspect_ratio, negative_prompt, session_id
    - Define RefineRequest schema with prompt and seed
    - Define VisualizationResponse schema with visualization_id, image_url, structured_prompt, seed, parent_id, created_at
    - Add AspectRatio enum with valid values
    - _Requirements: 2.1, 3.1, 6.2, 6.3_


- [x] 8. Create FIBO API endpoints





  - [x] 8.1 Create backend/app/api/v1/fibo.py

    - Implement POST /fibo/generate endpoint
    - Implement POST /fibo/refine/{visualization_id} endpoint
    - Implement GET /fibo/{visualization_id} endpoint
    - Add error handling and response formatting
    - _Requirements: 2.1, 2.4, 3.1, 3.2_

  - [x] 8.2 Modify backend/main.py to register FIBO router

    - Import fibo router
    - Include fibo router with /api/v1 prefix
    - Mount visualizations directory for static file serving at /visualizations
    - _Requirements: 2.4_


- [x] 9. Add frontend TypeScript types for FIBO




  - [x] 9.1 Create frontend/src/types/fibo.types.ts


    - Define GenerateRequest, RefineRequest, VisualizationResult interfaces
    - Define AspectRatio type union
    - Define FIBOError interface
    - _Requirements: 2.1, 3.1, 4.1_

  - [x] 9.2 Modify frontend/src/types/chat.types.ts

    - Add visualization fields to ChatMessage type (imageUrl, visualizationId, structuredPrompt)
    - _Requirements: 4.1_

- [x] 10. Create frontend FIBO API client






  - [x] 10.1 Create frontend/src/api/fibo.api.ts

    - Implement generateVisualization function
    - Implement refineVisualization function
    - Implement getVisualization function
    - Add error handling
    - _Requirements: 2.1, 3.1, 4.3_


- [x] 11. Create ImageViewer component






  - [ ] 11.1 Create frontend/src/components/chat/ImageViewer.tsx
    - Implement image display with loading state
    - Add fullscreen modal functionality
    - Add refinement input and button
    - _Requirements: 4.1, 4.2, 4.4, 4.5_


- [x] 12. Create ImageGenerator component






  - [ ] 12.1 Create frontend/src/components/chat/ImageGenerator.tsx
    - Implement prompt input field
    - Add aspect ratio selector dropdown
    - Add generate button with loading state
    - Handle generation errors with display
    - _Requirements: 2.1, 4.2, 4.3, 6.2_


- [x] 13. Integrate FIBO into ChatInterface






  - [ ] 13.1 Modify frontend/src/components/chat/ChatInterface.tsx
    - Import and integrate ImageGenerator component
    - Import and integrate ImageViewer component
    - Add visualization messages to chat history
    - Handle image generation and refinement flows
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_



- [-] 14. Update frontend styles



  - [ ] 14.1 Modify frontend/src/App.css
    - Add styles for ImageViewer component
    - Add styles for ImageGenerator component
    - Add fullscreen modal styles
    - Add loading indicator styles for image generation
    - _Requirements: 4.1, 4.2, 4.4_


- [x] 15. Create Dockerfile for GCP Cloud Run deployment






  - [ ] 15.1 Create Dockerfile in project root
    - Multi-stage build: Node.js for frontend, Python for backend
    - Copy secrets/.env and handle environment variables
    - Create data directories in container
    - Expose port 8000
    - Set up health check endpoint
    - _Requirements: 1.1_


- [x] 16. Create run script for local development






  - [ ] 16.1 Create run.bat in project root
    - Load environment variables from secrets/.env
    - Create data directories if not exist
    - Start backend server
    - Start frontend development server
    - Display service URLs
    - _Requirements: 1.1_


- [x] 17. Final verification and testing









  - [x] 17.1 Verify all services start correctly




    - Test backend starts and loads env from secrets/.env
    - Test frontend starts and connects to backend
    - Test FIBO image generation endpoint
    - Test image display in chat interface
    - Verify CSV records are created correctly
    - _Requirements: All_
