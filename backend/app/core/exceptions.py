"""Custom exception classes"""


class FIBOMedException(Exception):
    """Base exception for FIBOMed"""

    pass


class AuthenticationError(FIBOMedException):
    """Authentication failed"""

    pass


class DatabaseError(FIBOMedException):
    """Database operation failed"""

    pass


class VoiceProcessingError(FIBOMedException):
    """Voice processing failed"""

    pass


class GeminiError(FIBOMedException):
    """Gemini API error"""

    pass
