/**
 * Document Upload API - Agentic Document Processing
 */
import axios from 'axios';

// Use relative URL in production (same origin), localhost in development
const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
const API_BASE = isProduction ? '/api/v1' : 'http://localhost:8000/api/v1';

export interface AgentStep {
  step: string;
  model: string;
  timestamp: string;
}

export interface DocumentUploadResult {
  doc_id: string;
  filename: string;
  file_type: string;
  document_type: 'text_report' | 'medical_image';
  extracted_text: string;
  explanation: string;
  fibo_prompt: string;
  is_medical_image: boolean;
  session_id: string;
  timestamp: string;
  agent_steps: AgentStep[];
  visualization?: {
    image_url: string;
    visualization_id: string;
    prompt_used: string;
  };
  visualization_error?: string;
}

export const documentApi = {
  /**
   * Upload a document (PDF or image) for agentic processing
   * 
   * Pipeline:
   * 1. CLASSIFY: Determine if text report or medical image
   * 2. ANALYZE: Extract content and understand the document
   * 3. GENERATE: Create BOTH explanation AND FIBO visualization
   */
  uploadDocument: async (
    file: File,
    userId: string,
    sessionId?: string
  ): Promise<DocumentUploadResult> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    const response = await axios.post<DocumentUploadResult>(
      `${API_BASE}/documents/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minute timeout for AI processing
      }
    );
    return response.data;
  },

  /**
   * Get documents for a session
   */
  getSessionDocuments: async (sessionId: string) => {
    const response = await axios.get(`${API_BASE}/documents/session/${sessionId}`);
    return response.data;
  },
};

export default documentApi;
