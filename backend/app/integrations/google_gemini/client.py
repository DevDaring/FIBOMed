"""Gemini Flash API Client for Chat Responses"""
import google.generativeai as genai
from typing import Optional, List, Dict
from ...config import settings
from ...core.exceptions import GeminiError


class GeminiClient:
    """Client for interacting with Google Gemini Flash API"""

    def __init__(self):
        """Initialize Gemini client"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            self.chat_sessions: Dict[str, any] = {}
        except Exception as e:
            raise GeminiError(f"Failed to initialize Gemini client: {str(e)}")

    async def generate_response(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate a response using Gemini Flash

        Args:
            user_message: User's input message
            session_id: Optional session ID for conversation continuity
            system_prompt: Optional system prompt to set context

        Returns:
            Generated response text
        """
        try:
            # Build the prompt with system context
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
            else:
                full_prompt = user_message

            # Use existing chat session or create new one
            if session_id and session_id in self.chat_sessions:
                chat = self.chat_sessions[session_id]
                response = chat.send_message(user_message)
            else:
                # Create new chat session with history
                chat = self.model.start_chat(history=[])
                if session_id:
                    self.chat_sessions[session_id] = chat
                response = chat.send_message(full_prompt)

            return response.text

        except Exception as e:
            raise GeminiError(f"Failed to generate response: {str(e)}")

    async def generate_medical_response(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        context: Optional[str] = None,
    ) -> str:
        """
        Generate a medical-focused response with appropriate context

        Args:
            user_message: User's medical question or message
            session_id: Session ID for conversation continuity
            context: Additional medical context (reports, history, etc.)

        Returns:
            Generated medical response
        """
        # Medical assistant system prompt
        system_prompt = """You are FIBOMed Assistant, a helpful medical AI assistant that helps patients
understand their medical reports and conditions. You provide clear, compassionate, and accurate medical
information in patient-friendly language. You support multiple languages and adapt your explanations
to the patient's level of understanding.

Important guidelines:
- Use simple, understandable language
- Be empathetic and supportive
- Provide accurate medical information
- Encourage patients to consult their doctors for specific medical advice
- Break down complex medical terms into simple explanations
- Respond in the same language as the user's question
"""

        if context:
            system_prompt += f"\n\nMedical Context:\n{context}"

        return await self.generate_response(user_message, session_id, system_prompt)

    def clear_session(self, session_id: str):
        """Clear a chat session"""
        if session_id in self.chat_sessions:
            del self.chat_sessions[session_id]

    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session"""
        if session_id in self.chat_sessions:
            chat = self.chat_sessions[session_id]
            return chat.history
        return []


# Singleton instance
gemini_client = GeminiClient()
