"""Chat Service combining Voice and Gemini services"""
import uuid
from typing import Optional, Dict
from .voice_service import voice_service
from ..integrations.google_gemini.client import gemini_client
from ..core.exceptions import VoiceProcessingError, GeminiError


class ChatService:
    """Service for handling chat conversations with voice support"""

    def __init__(self):
        """Initialize chat service"""
        self.voice_service = voice_service
        self.gemini_client = gemini_client

    async def process_voice_message(
        self,
        audio_content: bytes,
        session_id: Optional[str] = None,
        language_code: Optional[str] = None,
        enable_tts: bool = True,
        medical_context: Optional[str] = None,
    ) -> Dict:
        """
        Process a voice message: STT -> Gemini -> TTS

        Args:
            audio_content: Audio file content in bytes
            session_id: Session ID for conversation continuity
            language_code: Language code for STT
            enable_tts: Whether to generate speech response
            medical_context: Additional medical context

        Returns:
            Dict with transcription, response text, and optional audio path
        """
        try:
            # Step 1: Speech to Text
            transcription = await self.voice_service.speech_to_text(
                audio_content, language_code
            )

            # Step 2: Generate response with Gemini
            if medical_context:
                response_text = await self.gemini_client.generate_medical_response(
                    transcription, session_id, medical_context
                )
            else:
                response_text = await self.gemini_client.generate_response(
                    transcription, session_id
                )

            # Step 3: Text to Speech (if enabled)
            audio_path = None
            audio_url = None
            if enable_tts:
                # Detect language from response for appropriate TTS voice
                detected_lang = self.voice_service.detect_language(response_text)
                voice_name = self.voice_service.get_voice_for_language(detected_lang)

                audio_content_bytes, audio_path = await self.voice_service.text_to_speech(
                    response_text, detected_lang, voice_name
                )

                # Generate URL for frontend
                audio_filename = audio_path.split("/")[-1]
                audio_url = f"/generated/audio/{audio_filename}"

            return {
                "transcription": transcription,
                "response": response_text,
                "audio_url": audio_url,
                "audio_path": audio_path,
                "session_id": session_id or str(uuid.uuid4()),
            }

        except VoiceProcessingError as e:
            raise VoiceProcessingError(f"Voice processing failed: {str(e)}")
        except GeminiError as e:
            raise GeminiError(f"Response generation failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Chat processing failed: {str(e)}")

    async def process_text_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        enable_tts: bool = True,
        medical_context: Optional[str] = None,
    ) -> Dict:
        """
        Process a text message: Gemini -> TTS

        Args:
            message: User's text message
            session_id: Session ID for conversation continuity
            enable_tts: Whether to generate speech response
            medical_context: Additional medical context

        Returns:
            Dict with response text and optional audio path
        """
        try:
            # Step 1: Generate response with Gemini
            if medical_context:
                response_text = await self.gemini_client.generate_medical_response(
                    message, session_id, medical_context
                )
            else:
                response_text = await self.gemini_client.generate_response(
                    message, session_id
                )

            # Step 2: Text to Speech (if enabled)
            audio_path = None
            audio_url = None
            if enable_tts:
                # Detect language from response for appropriate TTS voice
                detected_lang = self.voice_service.detect_language(response_text)
                voice_name = self.voice_service.get_voice_for_language(detected_lang)

                audio_content_bytes, audio_path = await self.voice_service.text_to_speech(
                    response_text, detected_lang, voice_name
                )

                # Generate URL for frontend
                audio_filename = audio_path.split("/")[-1]
                audio_url = f"/generated/audio/{audio_filename}"

            return {
                "response": response_text,
                "audio_url": audio_url,
                "audio_path": audio_path,
                "session_id": session_id or str(uuid.uuid4()),
            }

        except GeminiError as e:
            raise GeminiError(f"Response generation failed: {str(e)}")
        except VoiceProcessingError as e:
            raise VoiceProcessingError(f"TTS processing failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Chat processing failed: {str(e)}")

    def clear_session(self, session_id: str):
        """Clear a chat session"""
        self.gemini_client.clear_session(session_id)


# Singleton instance
chat_service = ChatService()
