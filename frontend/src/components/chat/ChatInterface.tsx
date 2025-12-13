/**
 * Chat Interface Component - Main chat UI with voice support and FIBO visualization
 * Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
 */
import React, { useState, useRef, useEffect } from 'react';
import VoiceInput from './VoiceInput';
import ImageGenerator from './ImageGenerator';
import ImageViewer from './ImageViewer';
import chatApi from '../../api/chat.api';
import { fiboApi } from '../../api/fibo.api';
import { ChatResponse, ChatMessage } from '../../types/chat.types';
import { VisualizationResult } from '../../types/fibo.types';

/**
 * Simple markdown to HTML converter for chat messages
 * Handles: **bold**, *italic*, bullet points, numbered lists
 */
const formatMarkdown = (text: string): string => {
  if (!text) return '';
  
  let formatted = text
    // Escape HTML first
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Bold: **text** or __text__
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    // Italic: *text* or _text_
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/_(.+?)_/g, '<em>$1</em>')
    // Line breaks
    .replace(/\n/g, '<br/>');
  
  return formatted;
};

/**
 * Component to render formatted markdown text
 */
const FormattedText: React.FC<{ text: string }> = ({ text }) => {
  return (
    <span 
      dangerouslySetInnerHTML={{ __html: formatMarkdown(text) }}
      className="formatted-text"
    />
  );
};

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [speakerEnabled, setSpeakerEnabled] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [languageCode, setLanguageCode] = useState('en-US');
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [generatingVisualizationId, setGeneratingVisualizationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Play audio response
  const playAudio = (audioUrl: string) => {
    if (speakerEnabled && audioUrl) {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      audioRef.current = new Audio(audioUrl);
      audioRef.current.play().catch((error) => {
        console.error('Error playing audio:', error);
      });
    }
  };

  // Handle text message send
  const handleSendTextMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setError(null);
    setIsLoading(true);

    try {
      const response: ChatResponse = await chatApi.sendTextMessage({
        message: userMessage,
        sessionId: sessionId || undefined,
        enableTts: speakerEnabled,
        languageCode,
      });

      // Update session ID
      if (!sessionId) {
        setSessionId(response.sessionId);
      }

      // Add message to chat
      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        sessionId: response.sessionId,
        userMessage: userMessage,
        botResponse: response.response,
        audioUrl: response.audioUrl,
        timestamp: response.timestamp,
        languageCode,
      };

      setMessages((prev) => [...prev, newMessage]);

      // Play audio if available
      if (response.audioUrl) {
        playAudio(response.audioUrl);
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      setError(error.response?.data?.detail || 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle voice message
  const handleVoiceRecordingComplete = async (audioBlob: Blob) => {
    setError(null);
    setIsLoading(true);

    try {
      // Convert blob to file
      const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm;codecs=opus' });

      const response: ChatResponse = await chatApi.sendVoiceMessage(
        audioFile,
        sessionId || undefined,
        speakerEnabled,
        undefined,
        languageCode
      );

      // Update session ID
      if (!sessionId) {
        setSessionId(response.sessionId);
      }

      // Add message to chat
      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        sessionId: response.sessionId,
        userMessage: response.transcription || '[Voice message]',
        botResponse: response.response,
        transcription: response.transcription,
        audioUrl: response.audioUrl,
        timestamp: response.timestamp,
        languageCode,
      };

      setMessages((prev) => [...prev, newMessage]);

      // Play audio if available
      if (response.audioUrl) {
        playAudio(response.audioUrl);
      }
    } catch (error: any) {
      console.error('Error sending voice message:', error);
      setError(error.response?.data?.detail || 'Failed to send voice message');
    } finally {
      setIsLoading(false);
    }
  };

  // Clear chat session
  const handleClearChat = async () => {
    if (sessionId && window.confirm('Are you sure you want to clear this chat?')) {
      try {
        await chatApi.clearSession(sessionId);
        setMessages([]);
        setSessionId('');
      } catch (error) {
        console.error('Error clearing chat:', error);
      }
    } else {
      setMessages([]);
    }
  };

  // Handle key press in input
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendTextMessage();
    }
  };

  /**
   * Handle successful image generation
   * Requirements: 4.1 - Render image inline within chat message
   */
  const handleImageGenerated = (result: VisualizationResult) => {
    const visualizationMessage: ChatMessage = {
      id: `viz-${Date.now()}`,
      sessionId: sessionId || 'default',
      userMessage: `🎨 Generated visualization`,
      botResponse: 'Here is your generated medical visualization:',
      imageUrl: result.imageUrl,
      visualizationId: result.visualizationId,
      structuredPrompt: result.structuredPrompt,
      timestamp: result.createdAt,
    };

    setMessages((prev) => [...prev, visualizationMessage]);
    setIsGeneratingImage(false);
    setGeneratingVisualizationId(null);
  };

  /**
   * Handle image generation error
   * Requirements: 4.3 - Display error message with API error details
   */
  const handleImageError = (errorMessage: string) => {
    setError(errorMessage);
    setIsGeneratingImage(false);
    setGeneratingVisualizationId(null);
  };

  /**
   * Handle image refinement request
   * Requirements: 4.5 - Show button to request refinement
   */
  const handleRefineImage = async (visualizationId: string, refinementPrompt: string) => {
    setIsGeneratingImage(true);
    setGeneratingVisualizationId(visualizationId);
    setError(null);

    try {
      const result = await fiboApi.refineVisualization(visualizationId, {
        prompt: refinementPrompt,
      });

      // Add refined visualization as a new message
      const refinedMessage: ChatMessage = {
        id: `viz-refined-${Date.now()}`,
        sessionId: sessionId || 'default',
        userMessage: `✨ Refined: "${refinementPrompt}"`,
        botResponse: 'Here is your refined visualization:',
        imageUrl: result.imageUrl,
        visualizationId: result.visualizationId,
        structuredPrompt: result.structuredPrompt,
        timestamp: result.createdAt,
      };

      setMessages((prev) => [...prev, refinedMessage]);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to refine visualization';
      setError(errorMsg);
    } finally {
      setIsGeneratingImage(false);
      setGeneratingVisualizationId(null);
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h1>FIBOMed Voice Chat</h1>
        <div className="chat-controls">
          <label className="speaker-toggle">
            <input
              type="checkbox"
              checked={speakerEnabled}
              onChange={(e) => setSpeakerEnabled(e.target.checked)}
            />
            <span>{speakerEnabled ? '🔊 Speaker On' : '🔇 Speaker Off'}</span>
          </label>
          <select
            value={languageCode}
            onChange={(e) => setLanguageCode(e.target.value)}
            className="language-selector"
          >
            <option value="en-US">English (US)</option>
            <option value="hi-IN">Hindi</option>
            <option value="es-ES">Spanish</option>
            <option value="fr-FR">French</option>
            <option value="de-DE">German</option>
            <option value="ja-JP">Japanese</option>
            <option value="zh-CN">Chinese</option>
          </select>
          <button onClick={handleClearChat} className="clear-button" title="Clear chat">
            🗑️ Clear
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>👋 Welcome to FIBOMed Voice Chat!</h2>
            <p>
              Start a conversation by typing a message or recording your voice. The assistant
              supports multiple languages and can help you understand medical information.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className="message-group">
            <div className="message user-message">
              <div className="message-content">
                {msg.transcription && (
                  <div className="transcription-badge">🎤 Voice</div>
                )}
                <p>{msg.userMessage}</p>
              </div>
            </div>
            <div className="message bot-message">
              <div className="message-content">
                <div className="bot-response-text">
                  <FormattedText text={msg.botResponse} />
                </div>
                {/* Requirements: 4.1 - Render image inline within chat message */}
                {msg.imageUrl && msg.visualizationId && (
                  <ImageViewer
                    imageUrl={msg.imageUrl}
                    visualizationId={msg.visualizationId}
                    onRefine={(prompt) => handleRefineImage(msg.visualizationId!, prompt)}
                    allowFullscreen={true}
                    isLoading={generatingVisualizationId === msg.visualizationId}
                    loadingText="Refining visualization..."
                  />
                )}
                {msg.audioUrl && (
                  <button
                    onClick={() => playAudio(msg.audioUrl!)}
                    className="play-audio-button"
                    title="Play audio"
                  >
                    🔊 Play Audio
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message bot-message loading">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
            <p>❌ {error}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <div className="input-container">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading || isGeneratingImage}
            rows={2}
          />
          <button
            onClick={handleSendTextMessage}
            disabled={isLoading || isGeneratingImage || !inputMessage.trim()}
            className="send-button"
            title="Send message"
          >
            📤 Send
          </button>
        </div>

        <div className="voice-input-container">
          <VoiceInput
            onRecordingComplete={handleVoiceRecordingComplete}
            disabled={isLoading || isGeneratingImage}
          />
        </div>

        {/* Requirements: 4.2 - Image generation with loading state */}
        <div className="image-generator-container">
          <ImageGenerator
            onImageGenerated={handleImageGenerated}
            onError={handleImageError}
            disabled={isLoading || isGeneratingImage}
            sessionId={sessionId}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
