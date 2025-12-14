/**
 * Chat Interface Component - Full height chat with 2x2 button grid
 * Supports chat history loading and document upload with preview
 */
import React, { useState, useRef, useEffect, useCallback } from 'react';
import ImageViewer from './ImageViewer';
import chatApi from '../../api/chat.api';
import { fiboApi } from '../../api/fibo.api';
import documentApi, { DocumentUploadResult } from '../../api/document.api';
import { ChatResponse, ChatMessage } from '../../types/chat.types';


const formatMarkdown = (text: string): string => {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>');
};

const FormattedText: React.FC<{ text: string }> = ({ text }) => (
  <span dangerouslySetInnerHTML={{ __html: formatMarkdown(text) }} className="formatted-text" />
);

interface ChatInterfaceProps {
  initialPrompt?: string;
  userId?: string;
  sessionId?: string; // Allow passing session ID to load history
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ initialPrompt, userId = 'DOC001', sessionId: initialSessionId }) => {
  // Get or create session ID from localStorage for persistence
  const getStoredSessionId = (key: string): string => {
    const stored = localStorage.getItem(`fibomed_session_${key}`);
    return stored || '';
  };
  
  const storeSessionId = (key: string, sid: string) => {
    localStorage.setItem(`fibomed_session_${key}`, sid);
  };

  // Use initialSessionId as the key for localStorage, but load the actual stored UUID
  const sessionKey = initialSessionId || `default_${userId}`;
  const storedSid = getStoredSessionId(sessionKey);
  
  // Determine which session ID to use:
  // 1. If initialSessionId is provided (e.g., viz-DOC001-RPT001), use it directly to load shared sessions
  // 2. Otherwise, use stored session from localStorage
  // CRITICAL: Always prioritize initialSessionId when provided - this is for shared doctor-patient sessions
  const effectiveSessionId = initialSessionId || storedSid;
  
  // Debug logging
  console.log('ChatInterface mounted with:', { initialSessionId, userId, effectiveSessionId, storedSid });
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState(initialPrompt || '');
  const [sessionId, setSessionId] = useState<string>(effectiveSessionId);
  const [isLoading, setIsLoading] = useState(false);
  const [speakerEnabled, setSpeakerEnabled] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [languageCode] = useState('en-US');
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [isUploadingDoc, setIsUploadingDoc] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [generatingVisualizationId, setGeneratingVisualizationId] = useState<string | null>(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Load chat history when session ID is available
  const loadChatHistory = useCallback(async (sid: string) => {
    if (!sid) {
      console.log('loadChatHistory called with empty session ID, skipping');
      return;
    }
    console.log('=== LOADING CHAT HISTORY ===');
    console.log('Session ID to load:', sid);
    setIsLoadingHistory(true);
    try {
      const result = await chatApi.getChatHistory(sid, 100, 0);
      console.log('Chat history API response:', result);
      console.log('Number of messages:', result.messages?.length || 0);
      if (result.messages && result.messages.length > 0) {
        // Convert backend messages to frontend format, parsing special message types
        const loadedMessages: ChatMessage[] = result.messages.map((msg: any) => {
          const userMsg = msg.user_message || msg.userMessage || '';
          const botResp = msg.bot_response || msg.botResponse || '';
          
          // Parse special message types
          let documentInfo: ChatMessage['documentInfo'] | undefined;
          let imageUrl: string | undefined;
          let visualizationId: string | undefined;
          let displayUserMsg = userMsg;
          
          // Check for document upload marker: [DOC_UPLOAD:filename.pdf]
          const docMatch = userMsg.match(/^\[DOC_UPLOAD:(.+)\]$/);
          if (docMatch) {
            const filename = docMatch[1];
            const isImage = /\.(png|jpg|jpeg|gif|webp)$/i.test(filename);
            documentInfo = {
              filename,
              fileType: isImage ? 'image' : 'pdf',
              isMedicalImage: isImage,
            };
            displayUserMsg = `Uploaded: ${filename}`;
          }
          
          // Check for AI analysis marker
          if (userMsg === '[AI_ANALYSIS]') {
            displayUserMsg = 'AI Analysis';
          }
          
          // Check for visualization marker: [VISUALIZATION:viz_id]
          const vizMatch = userMsg.match(/^\[VISUALIZATION:(.+)\]$/);
          if (vizMatch) {
            visualizationId = vizMatch[1];
            displayUserMsg = 'Medical Visualization';
            // Extract image URL from bot response
            const urlMatch = botResp.match(/Generated visualization: (.+)$/);
            if (urlMatch) {
              let extractedUrl = urlMatch[1];
              console.log('Found visualization URL:', extractedUrl);
              // Handle different URL types:
              // 1. BRIA API URLs (https://...) - use as-is
              // 2. Local paths (/visualizations/...) - skip in production (ephemeral containers)
              // 3. localhost URLs - convert to relative in production
              if (extractedUrl.startsWith('https://')) {
                // BRIA API URL - use directly
                imageUrl = extractedUrl;
                console.log('Using BRIA API URL:', imageUrl);
              } else if (extractedUrl.startsWith('/visualizations/')) {
                // Local path - only works in development
                const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
                if (!isProduction) {
                  imageUrl = `http://localhost:8000${extractedUrl}`;
                  console.log('Using local dev URL:', imageUrl);
                } else {
                  console.log('Skipping local path in production:', extractedUrl);
                }
                // In production, skip local paths (they don't exist in ephemeral containers)
              } else if (extractedUrl.includes('localhost:8000')) {
                // localhost URL - convert to relative in production
                const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
                if (isProduction) {
                  imageUrl = extractedUrl.replace('http://localhost:8000', '');
                  console.log('Converted to relative URL:', imageUrl);
                } else {
                  imageUrl = extractedUrl;
                  console.log('Using localhost URL:', imageUrl);
                }
              } else {
                // Other URLs - use as-is
                imageUrl = extractedUrl;
                console.log('Using URL as-is:', imageUrl);
              }
            }
          }
          
          return {
            id: msg.id || `hist-${Date.now()}-${Math.random()}`,
            sessionId: sid,
            userMessage: displayUserMsg,
            botResponse: vizMatch ? 'Generated visualization based on document analysis' : botResp,
            transcription: msg.transcription,
            audioUrl: msg.audio_url || msg.audioUrl,
            timestamp: msg.timestamp,
            languageCode: msg.language_code || msg.languageCode,
            documentInfo,
            imageUrl,
            visualizationId,
          };
        });
        setMessages(loadedMessages);
      }
    } catch (err) {
      console.error('Failed to load chat history:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  }, []);

  // Track if initial prompt has been sent
  const initialPromptSentRef = useRef(false);
  
  useEffect(() => { if (initialPrompt) setInputMessage(initialPrompt); }, [initialPrompt]);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);
  
  // Auto-send initial prompt when provided (for View Visual button)
  useEffect(() => {
    if (initialPrompt && !initialPromptSentRef.current && !isLoading && !isGeneratingImage) {
      initialPromptSentRef.current = true;
      // Small delay to ensure component is ready
      const timer = setTimeout(() => {
        handleAutoGenerateVisualization(initialPrompt);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [initialPrompt, isLoading, isGeneratingImage]);
  
  // Auto-generate visualization for initial prompt
  const handleAutoGenerateVisualization = async (prompt: string) => {
    if (!prompt.trim() || isGeneratingImage) return;
    setIsGeneratingImage(true);
    setError(null);
    setInputMessage('');
    try {
      const result = await fiboApi.generateVisualization({ prompt, aspectRatio: '1:1', sessionId });
      setMessages((prev) => [...prev, {
        id: `viz-${Date.now()}`, sessionId: sessionId || 'default', userMessage: prompt,
        botResponse: 'Here is your medical visualization:', imageUrl: result.imageUrl,
        visualizationId: result.visualizationId, structuredPrompt: result.structuredPrompt, timestamp: result.createdAt,
      }]);
    } catch (err: any) {
      setError(err instanceof Error ? err.message : 'Failed to generate visualization');
    } finally { setIsGeneratingImage(false); }
  };
  
  // Load history when component mounts or when initialSessionId changes
  useEffect(() => {
    console.log('=== HISTORY LOADING EFFECT ===');
    console.log('initialSessionId prop:', initialSessionId);
    console.log('effectiveSessionId:', effectiveSessionId);
    console.log('storedSid:', storedSid);
    
    // Clear existing messages when switching sessions
    setMessages([]);
    
    // CRITICAL: Use initialSessionId directly if provided (for shared doctor-patient sessions)
    // This ensures we load the exact session the doctor created
    const sidToLoad = initialSessionId || effectiveSessionId;
    console.log('Final session ID to load:', sidToLoad);
    
    if (sidToLoad) {
      // Always load history when we have a session ID
      loadChatHistory(sidToLoad);
    } else {
      console.log('No session ID available, showing empty chat');
    }
  }, [initialSessionId, loadChatHistory]); // Include loadChatHistory in deps
  
  // Also load history when effectiveSessionId changes (for localStorage-based sessions)
  useEffect(() => {
    if (!initialSessionId && effectiveSessionId) {
      console.log('Loading history for stored session (secondary effect):', effectiveSessionId);
      loadChatHistory(effectiveSessionId);
    }
  }, [effectiveSessionId, initialSessionId, loadChatHistory]);
  
  // Update session ID and store it
  const updateSessionId = useCallback((newSid: string) => {
    setSessionId(newSid);
    storeSessionId(sessionKey, newSid);
  }, [sessionKey]);

  const playAudio = (audioUrl: string) => {
    if (speakerEnabled && audioUrl) {
      audioRef.current?.pause();
      audioRef.current = new Audio(audioUrl);
      audioRef.current.play().catch(console.error);
    }
  };

  const handleSendTextMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;
    const userMessage = inputMessage.trim();
    setInputMessage('');
    setError(null);
    setIsLoading(true);
    try {
      const response: ChatResponse = await chatApi.sendTextMessage({
        message: userMessage, sessionId: sessionId || undefined, enableTts: speakerEnabled, languageCode,
      });
      if (!sessionId) updateSessionId(response.sessionId);
      setMessages((prev) => [...prev, {
        id: Date.now().toString(), sessionId: response.sessionId, userMessage,
        botResponse: response.response, audioUrl: response.audioUrl, timestamp: response.timestamp, languageCode,
      }]);
      if (response.audioUrl) playAudio(response.audioUrl);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send message');
    } finally { setIsLoading(false); }
  };

  // Voice Recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) audioChunksRef.current.push(e.data); };
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm;codecs=opus' });
        stream.getTracks().forEach((t) => t.stop());
        if (timerRef.current) clearInterval(timerRef.current);
        setRecordingTime(0);
        await handleVoiceMessage(audioBlob);
      };
      mediaRecorder.start();
      setIsRecording(true);
      timerRef.current = setInterval(() => setRecordingTime((p) => p + 1), 1000);
    } catch (err) { alert('Failed to access microphone'); }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleVoiceMessage = async (audioBlob: Blob) => {
    setError(null);
    setIsLoading(true);
    try {
      const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm;codecs=opus' });
      const response: ChatResponse = await chatApi.sendVoiceMessage(audioFile, sessionId || undefined, speakerEnabled, undefined, languageCode);
      if (!sessionId) updateSessionId(response.sessionId);
      setMessages((prev) => [...prev, {
        id: Date.now().toString(), sessionId: response.sessionId,
        userMessage: response.transcription || '[Voice]', botResponse: response.response,
        transcription: response.transcription, audioUrl: response.audioUrl, timestamp: response.timestamp, languageCode,
      }]);
      if (response.audioUrl) playAudio(response.audioUrl);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send voice');
    } finally { setIsLoading(false); }
  };

  const handleClearChat = async () => {
    if (window.confirm('Clear chat?')) {
      if (sessionId) { try { await chatApi.clearSession(sessionId); } catch (e) { console.error(e); } }
      setMessages([]);
      setSessionId('');
      localStorage.removeItem(`fibomed_session_${sessionKey}`);
    }
  };

  const handleGenerateVisualization = async () => {
    if (!inputMessage.trim() || isGeneratingImage) return;
    setIsGeneratingImage(true);
    setError(null);
    const prompt = inputMessage.trim();
    setInputMessage('');
    try {
      const result = await fiboApi.generateVisualization({ prompt, aspectRatio: '1:1', sessionId });
      setMessages((prev) => [...prev, {
        id: `viz-${Date.now()}`, sessionId: sessionId || 'default', userMessage: 'Generated visualization',
        botResponse: 'Here is your medical visualization:', imageUrl: result.imageUrl,
        visualizationId: result.visualizationId, structuredPrompt: result.structuredPrompt, timestamp: result.createdAt,
      }]);
    } catch (err: any) {
      setError(err instanceof Error ? err.message : 'Failed to generate');
    } finally { setIsGeneratingImage(false); setGeneratingVisualizationId(null); }
  };

  const handleRefineImage = async (visualizationId: string, refinementPrompt: string) => {
    setIsGeneratingImage(true);
    setGeneratingVisualizationId(visualizationId);
    try {
      const result = await fiboApi.refineVisualization(visualizationId, { prompt: refinementPrompt });
      setMessages((prev) => [...prev, {
        id: `viz-refined-${Date.now()}`, sessionId: sessionId || 'default',
        userMessage: `Refined: "${refinementPrompt}"`, botResponse: 'Refined visualization:',
        imageUrl: result.imageUrl, visualizationId: result.visualizationId, timestamp: result.createdAt,
      }]);
    } catch (err) { setError(err instanceof Error ? err.message : 'Failed to refine'); }
    finally { setIsGeneratingImage(false); setGeneratingVisualizationId(null); }
  };

  const handleDocumentUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploadingDoc(true);
    setError(null);
    
    // Create local preview URL for the uploaded file
    const localPreviewUrl = URL.createObjectURL(file);
    const isImage = file.type.startsWith('image/');
    
    try {
      const result: DocumentUploadResult = await documentApi.uploadDocument(file, userId, sessionId || undefined);
      if (!sessionId && result.session_id) updateSessionId(result.session_id);
      
      // Message 1: Show uploaded document with preview thumbnail
      setMessages((prev) => [...prev, {
        id: `doc-${Date.now()}`, sessionId: result.session_id, 
        userMessage: `Uploaded: ${result.filename}`,
        botResponse: `Document Type: ${result.document_type === 'medical_image' ? 'Medical Image' : 'Text Report'}\n\nExtracted Content:\n${result.extracted_text.substring(0, 300)}${result.extracted_text.length > 300 ? '...' : ''}`,
        timestamp: result.timestamp,
        documentInfo: { 
          filename: result.filename, 
          fileType: result.file_type, 
          isMedicalImage: result.is_medical_image,
          previewUrl: isImage ? localPreviewUrl : undefined,
        },
      }]);
      
      // Message 2: Show AI explanation (always generated)
      if (result.explanation) {
        setMessages((prev) => [...prev, {
          id: `explain-${Date.now()}`, sessionId: result.session_id,
          userMessage: 'AI Analysis', 
          botResponse: result.explanation, 
          timestamp: result.timestamp,
        }]);
      }
      
      // Message 3: Show FIBO visualization (always generated for both types)
      if (result.visualization && result.visualization.image_url) {
        const viz = result.visualization;
        setMessages((prev) => [...prev, {
          id: `viz-doc-${Date.now()}`, sessionId: result.session_id, 
          userMessage: 'Medical Visualization',
          botResponse: `Generated visualization based on: ${result.fibo_prompt.substring(0, 100)}...`,
          imageUrl: viz.image_url,
          visualizationId: viz.visualization_id, 
          timestamp: result.timestamp,
        }]);
      } else if (result.visualization_error) {
        setMessages((prev) => [...prev, {
          id: `viz-error-${Date.now()}`, sessionId: result.session_id,
          userMessage: 'Visualization', 
          botResponse: `Could not generate visualization: ${result.visualization_error}`,
          timestamp: result.timestamp,
        }]);
      }
    } catch (err: any) { 
      setError(err.response?.data?.detail || err.message || 'Failed to process document'); 
    }
    finally { setIsUploadingDoc(false); if (fileInputRef.current) fileInputRef.current.value = ''; }
  };

  const isDisabled = isLoading || isGeneratingImage || isUploadingDoc || isRecording;
  const formatTime = (s: number) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  return (
    <div className="chat-fullscreen">
      {/* Floating Clear Button */}
      <button onClick={handleClearChat} className="floating-clear-btn" title="Clear chat">X</button>
      
      {/* Speaker Toggle */}
      <div className="floating-speaker">
        <label>
          <input type="checkbox" checked={speakerEnabled} onChange={(e) => setSpeakerEnabled(e.target.checked)} />
          {speakerEnabled ? 'Sound On' : 'Sound Off'}
        </label>
      </div>

      {/* Messages Area */}
      <div className="chat-messages-full">
        {isLoadingHistory && (
          <div className="loading-history">
            <div className="typing-indicator"><span></span><span></span><span></span></div>
            <span>Loading chat history...</span>
          </div>
        )}
        
        {messages.length === 0 && !isLoadingHistory && (
          <div className="welcome-message">
            <h2>FIBOMed Voice Chat</h2>
            <p>Type a message, record voice, or upload a medical document (PDF/image).</p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className="message-group">
            <div className="message user-message">
              <div className="message-content">
                {msg.transcription && <span className="msg-badge">Voice</span>}
                {msg.documentInfo && (
                  <div className="uploaded-doc-preview">
                    {msg.documentInfo.previewUrl ? (
                      <img src={msg.documentInfo.previewUrl} alt="Uploaded" className="doc-thumbnail" />
                    ) : (
                      <div className="doc-icon-box">PDF</div>
                    )}
                    <span className="doc-name">{msg.documentInfo.filename}</span>
                  </div>
                )}
                {!msg.documentInfo && <p>{msg.userMessage}</p>}
              </div>
            </div>
            <div className="message bot-message">
              <div className="message-content">
                <div className="bot-response-text"><FormattedText text={msg.botResponse} /></div>
                {msg.imageUrl && (
                  msg.visualizationId ? (
                    <ImageViewer imageUrl={msg.imageUrl} visualizationId={msg.visualizationId}
                      onRefine={(p) => handleRefineImage(msg.visualizationId!, p)} allowFullscreen={true}
                      isLoading={generatingVisualizationId === msg.visualizationId} loadingText="Refining..." />
                  ) : (
                    <img 
                      src={msg.imageUrl} 
                      alt="Generated visualization" 
                      className="chat-generated-image" 
                      style={{ maxWidth: '100%', borderRadius: '8px', marginTop: '10px' }}
                      onError={(e) => {
                        console.error('Failed to load image:', msg.imageUrl);
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        const errorDiv = document.createElement('div');
                        errorDiv.className = 'image-error-placeholder';
                        errorDiv.innerHTML = '❌ Image not available in production deployment';
                        errorDiv.style.cssText = 'padding: 20px; background: #f5f5f5; border-radius: 8px; color: #666; text-align: center; margin-top: 10px;';
                        target.parentNode?.insertBefore(errorDiv, target.nextSibling);
                      }}
                    />
                  )
                )}
                {!msg.imageUrl && msg.visualizationId && (
                  <div className="image-error-placeholder" style={{
                    padding: '20px', 
                    background: '#f5f5f5', 
                    borderRadius: '8px', 
                    color: '#666', 
                    textAlign: 'center', 
                    marginTop: '10px'
                  }}>
                    🖼️ Visualization generated but image not available in current deployment
                  </div>
                )}
                {msg.audioUrl && (
                  <button onClick={() => playAudio(msg.audioUrl!)} className="play-audio-btn">Play Audio</button>
                )}
              </div>
            </div>
          </div>
        ))}

        {isDisabled && (
          <div className="message bot-message loading">
            <div className="message-content">
              <div className="typing-indicator"><span></span><span></span><span></span></div>
              <span>{isUploadingDoc ? 'Processing...' : isGeneratingImage ? 'Generating...' : isRecording ? 'Recording...' : 'Thinking...'}</span>
            </div>
          </div>
        )}

        {error && <div className="error-message"><p>{error}</p></div>}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area with 2x2 Grid */}
      <div className="chat-input-full">
        <textarea value={inputMessage} onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendTextMessage(); } }}
          placeholder="Type message or describe visualization..." disabled={isDisabled} rows={2} className="chat-textarea-full" />
        
        <div className="btn-grid-2x2">
          <button onClick={handleSendTextMessage} disabled={isDisabled || !inputMessage.trim()} className="grid-btn chat-btn">
            Chat
          </button>
          <button onClick={handleGenerateVisualization} disabled={isDisabled || !inputMessage.trim()} className="grid-btn generate-btn">
            {isGeneratingImage ? 'Wait...' : 'Generate'}
          </button>
          <button onClick={() => fileInputRef.current?.click()} disabled={isDisabled} className="grid-btn upload-btn">
            {isUploadingDoc ? 'Wait...' : 'Upload'}
          </button>
          {!isRecording ? (
            <button onClick={startRecording} disabled={isDisabled} className="grid-btn voice-btn">Voice</button>
          ) : (
            <button onClick={stopRecording} className="grid-btn voice-btn recording">
              <span className="rec-dot"></span> {formatTime(recordingTime)}
            </button>
          )}
        </div>
        
        <input ref={fileInputRef} type="file" accept=".pdf,image/*" onChange={handleDocumentUpload} style={{ display: 'none' }} />
      </div>
    </div>
  );
};

export default ChatInterface;
