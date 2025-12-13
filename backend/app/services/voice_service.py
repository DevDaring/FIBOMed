"""Voice Service for Speech-to-Text and Text-to-Speech using Google Cloud APIs"""
import os
import uuid
from typing import Optional
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech_v1 as texttospeech
from ..config import settings
from ..core.exceptions import VoiceProcessingError


class VoiceService:
    """Service for handling voice input and output"""

    def __init__(self):
        """Initialize Google Cloud clients"""
        try:
            self.speech_client = speech.SpeechClient()
            self.tts_client = texttospeech.TextToSpeechClient()
        except Exception as e:
            raise VoiceProcessingError(f"Failed to initialize voice service: {str(e)}")

    async def speech_to_text(
        self, audio_content: bytes, language_code: Optional[str] = None
    ) -> str:
        """
        Convert speech audio to text using Google Speech-to-Text API

        Args:
            audio_content: Audio file content in bytes
            language_code: Language code (e.g., 'en-US', 'hi-IN', 'es-ES')

        Returns:
            Transcribed text
        """
        try:
            # Determine language code
            lang_code = language_code or settings.GOOGLE_SPEECH_LANGUAGE_CODE

            # Configure audio and recognition
            audio = speech.RecognitionAudio(content=audio_content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code=lang_code,
                enable_automatic_punctuation=True,
                model="default",
                # Enable alternative languages for multilingual support
                alternative_language_codes=[
                    "hi-IN",  # Hindi
                    "es-ES",  # Spanish
                    "fr-FR",  # French
                    "de-DE",  # German
                    "ja-JP",  # Japanese
                    "zh-CN",  # Chinese (Simplified)
                ],
            )

            # Perform speech recognition
            response = self.speech_client.recognize(config=config, audio=audio)

            # Extract transcription
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript

            if not transcript:
                raise VoiceProcessingError("No speech detected in audio")

            return transcript.strip()

        except Exception as e:
            raise VoiceProcessingError(f"Speech-to-text failed: {str(e)}")

    async def text_to_speech(
        self,
        text: str,
        language_code: Optional[str] = None,
        voice_name: Optional[str] = None,
    ) -> tuple[bytes, str]:
        """
        Convert text to speech using Google Text-to-Speech API

        Args:
            text: Text to convert to speech
            language_code: Language code (e.g., 'en-US', 'hi-IN')
            voice_name: Specific voice name (e.g., 'en-US-Neural2-F')

        Returns:
            Tuple of (audio_content bytes, file_path)
        """
        try:
            # Determine language and voice
            lang_code = language_code or settings.GOOGLE_TTS_LANGUAGE_CODE
            voice = voice_name or settings.GOOGLE_TTS_VOICE_NAME

            # Google TTS has a 5000 byte limit - truncate if needed
            MAX_TTS_BYTES = 4800  # Leave some buffer
            text_bytes = text.encode('utf-8')
            if len(text_bytes) > MAX_TTS_BYTES:
                # Truncate to fit within limit, try to end at a sentence
                truncated = text_bytes[:MAX_TTS_BYTES].decode('utf-8', errors='ignore')
                # Try to end at last complete sentence
                last_period = truncated.rfind('.')
                last_question = truncated.rfind('?')
                last_exclaim = truncated.rfind('!')
                last_sentence_end = max(last_period, last_question, last_exclaim)
                if last_sentence_end > len(truncated) // 2:
                    text = truncated[:last_sentence_end + 1]
                else:
                    text = truncated + "..."

            # Configure synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Configure voice parameters
            voice_params = texttospeech.VoiceSelectionParams(
                language_code=lang_code,
                name=voice,
            )

            # Configure audio output
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0,
            )

            # Perform text-to-speech
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config,
            )

            # Save audio file
            audio_filename = f"{uuid.uuid4()}.mp3"
            audio_path = os.path.join(settings.GENERATED_PATH, "audio", audio_filename)

            with open(audio_path, "wb") as out:
                out.write(response.audio_content)

            return response.audio_content, audio_path

        except Exception as e:
            raise VoiceProcessingError(f"Text-to-speech failed: {str(e)}")

    def detect_language(self, text: str) -> str:
        """
        Simple language detection based on character sets
        Returns language code for TTS

        Args:
            text: Text to analyze

        Returns:
            Language code (e.g., 'en-US', 'hi-IN')
        """
        # Check for Hindi/Devanagari script
        if any("\u0900" <= char <= "\u097F" for char in text):
            return "hi-IN"

        # Check for Chinese characters
        if any("\u4e00" <= char <= "\u9fff" for char in text):
            return "zh-CN"

        # Check for Japanese characters
        if any("\u3040" <= char <= "\u30ff" for char in text):
            return "ja-JP"

        # Check for Arabic characters
        if any("\u0600" <= char <= "\u06ff" for char in text):
            return "ar-XA"

        # Default to English
        return "en-US"

    def get_voice_for_language(self, language_code: str) -> str:
        """
        Get appropriate neural voice for language

        Args:
            language_code: Language code

        Returns:
            Voice name
        """
        voice_map = {
            "en-US": "en-US-Neural2-F",
            "hi-IN": "hi-IN-Neural2-A",
            "es-ES": "es-ES-Neural2-A",
            "fr-FR": "fr-FR-Neural2-A",
            "de-DE": "de-DE-Neural2-F",
            "ja-JP": "ja-JP-Neural2-B",
            "zh-CN": "cmn-CN-Standard-A",
            "ar-XA": "ar-XA-Standard-A",
        }
        return voice_map.get(language_code, "en-US-Neural2-F")


# Singleton instance
voice_service = VoiceService()
