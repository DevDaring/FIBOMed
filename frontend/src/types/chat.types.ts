/**
 * TypeScript type definitions for chat functionality
 */

export interface ChatMessage {
  id: string;
  sessionId: string;
  userMessage: string;
  botResponse: string;
  transcription?: string;
  audioUrl?: string;
  timestamp: string;
  languageCode?: string;
}

export interface ChatMessageRequest {
  message: string;
  sessionId?: string;
  enableTts: boolean;
  medicalContext?: string;
  languageCode?: string;
}

export interface VoiceChatRequest {
  audio: File;
  sessionId?: string;
  enableTts: boolean;
  medicalContext?: string;
  languageCode?: string;
}

export interface ChatResponse {
  transcription?: string;
  response: string;
  audioUrl?: string;
  sessionId: string;
  timestamp: string;
}

export interface ChatSession {
  sessionId: string;
  messages: ChatMessage[];
}
