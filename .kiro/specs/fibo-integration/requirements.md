# Requirements Document

## Introduction

This document specifies the requirements for integrating BRIA FIBO cloud API into the FIBOMed medical visualization platform. The integration enables the system to generate medical visualizations from text prompts using FIBO's cloud-based image generation API (`https://engine.prod.bria-api.com/v2/image/generate`), with proper environment configuration loading from the `secrets/` folder, and seamless rendering in the React frontend. This is a CPU-only deployment using BRIA's hosted API service.

## Glossary

- **FIBO**: BRIA's controllable image generation model accessible via cloud API
- **FIBO API**: BRIA's hosted API endpoint at `https://engine.prod.bria-api.com/v2/image/generate`
- **Structured Prompt**: A detailed JSON object describing the image to generate, including objects, lighting, aesthetics, and style
- **FIBOMed**: The medical visual storytelling platform being developed
- **STT**: Speech-to-Text conversion service using Google Cloud
- **TTS**: Text-to-Speech conversion service using Google Cloud
- **Gemini**: Google's AI model used for chat responses and medical context analysis

## Requirements

### Requirement 1

**User Story:** As a developer, I want the application to load environment variables from the `secrets/.env` file, so that API keys and credentials are properly configured.

#### Acceptance Criteria

1. WHEN the backend application starts THEN the System SHALL load environment variables from `secrets/.env` file path using python-dotenv
2. WHEN the `FIBO_PROD_API_KEY` environment variable is required for FIBO API THEN the System SHALL read it from the loaded environment configuration
3. WHEN the `GEMINI_API_KEY` environment variable is required THEN the System SHALL read it from the loaded environment configuration
4. WHEN the `GOOGLE_API_KEY` environment variable is required THEN the System SHALL read it from the loaded environment configuration
5. IF a required environment variable is missing THEN the System SHALL raise a descriptive error indicating which variable is missing

### Requirement 2

**User Story:** As a user, I want to generate medical visualizations from text descriptions, so that I can better understand medical concepts visually.

#### Acceptance Criteria

1. WHEN a user submits a text prompt for image generation THEN the System SHALL call the FIBO API with the prompt parameter
2. WHEN the FIBO API returns a response THEN the System SHALL extract the image_url and structured_prompt from the result
3. WHEN an image URL is received THEN the System SHALL download and save the image to the `data/generated/visualizations/` directory
4. WHEN an image is saved THEN the System SHALL return the local image URL to the frontend for display
5. WHEN the prompt contains medical terminology THEN the System SHALL preserve the medical context in the API request

### Requirement 3

**User Story:** As a user, I want to refine generated images with additional instructions, so that I can iteratively improve the visualization.

#### Acceptance Criteria

1. WHEN a user provides a refinement instruction with an existing structured_prompt THEN the System SHALL call the FIBO API with both prompt and structured_prompt parameters
2. WHEN the FIBO API returns a refined image THEN the System SHALL save the new image and updated structured_prompt
3. WHEN a refinement is applied THEN the System SHALL store both the original and refined structured_prompts for reference
4. WHEN refining an image THEN the System SHALL include the original seed value for deterministic refinement

### Requirement 4

**User Story:** As a user, I want to view generated medical visualizations in the chat interface, so that I can see visual explanations alongside text responses.

#### Acceptance Criteria

1. WHEN an image is generated THEN the Frontend SHALL render the image inline within the chat message
2. WHEN an image generation is in progress THEN the Frontend SHALL show a loading indicator with status text
3. WHEN an image fails to generate THEN the Frontend SHALL display an error message with the API error details
4. WHEN an image is displayed THEN the Frontend SHALL allow the user to click for full-screen viewing
5. WHEN displaying an image THEN the Frontend SHALL show a button to request refinement

### Requirement 5

**User Story:** As a developer, I want the FIBO API calls to handle synchronous and asynchronous modes properly, so that the system provides responsive feedback.

#### Acceptance Criteria

1. WHEN calling the FIBO API THEN the System SHALL use sync=true mode for immediate response
2. WHEN the API returns a 202 status THEN the System SHALL poll the status_url until completion
3. WHEN the API returns an error status THEN the System SHALL return a descriptive error message to the user
4. IF the API request times out THEN the System SHALL retry once before returning an error

### Requirement 6

**User Story:** As a user, I want the system to support different aspect ratios for generated images, so that I can get visualizations suitable for different display contexts.

#### Acceptance Criteria

1. WHEN generating an image THEN the System SHALL default to 1:1 aspect ratio
2. WHEN a user specifies an aspect ratio THEN the System SHALL pass the aspect_ratio parameter to the FIBO API
3. WHEN an invalid aspect ratio is specified THEN the System SHALL return an error listing valid options

### Requirement 7

**User Story:** As a developer, I want the FIBO structured prompts to be stored alongside generated images, so that visualizations can be reproduced or refined later.

#### Acceptance Criteria

1. WHEN an image is generated THEN the System SHALL save the structured_prompt JSON to a file with matching filename
2. WHEN storing structured prompts THEN the System SHALL include the seed value and generation timestamp
3. WHEN a refinement is performed THEN the System SHALL link the refined prompt to the original prompt via a parent_id field
