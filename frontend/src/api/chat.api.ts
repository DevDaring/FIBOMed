/**
 * Chat API integration
 */
import apiClient from './client';
import { ChatMessageRequest, ChatResponse, ChatMessage } from '../types/chat.types';

export const chatApi = {
  /**
   * Send a text message
   */
  sendTextMessage: async (request: ChatMessageRequest): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/chat/text', request);
    return response.data;
  },

  /**
   * Send a voice message
   */
  sendVoiceMessage: async (
    audioFile: File,
    sessionId?: string,
    enableTts: boolean = true,
    medicalContext?: string,
    languageCode?: string
  ): Promise<ChatResponse> => {
    const formData = new FormData();
    formData.append('audio', audioFile);
    if (sessionId) formData.append('session_id', sessionId);
    formData.append('enable_tts', String(enableTts));
    if (medicalContext) formData.append('medical_context', medicalContext);
    if (languageCode) formData.append('language_code', languageCode);

    const response = await apiClient.post<ChatResponse>('/chat/voice', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Clear a chat session
   */
  clearSession: async (sessionId: string): Promise<void> => {
    await apiClient.post('/chat/session/clear', { session_id: sessionId });
  },

  /**
   * Get chat history
   */
  getChatHistory: async (
    sessionId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<{ messages: ChatMessage[]; count: number }> => {
    const response = await apiClient.get(`/chat/session/${sessionId}/history`, {
      params: { limit, offset },
    });
    return response.data;
  },
};

export default chatApi;
