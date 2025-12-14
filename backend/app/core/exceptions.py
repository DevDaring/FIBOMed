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


class FIBOError(FIBOMedException):
    """Base exception for FIBO operations"""

    def __init__(self, message: str, code: str, details: str = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


class FIBOAPIError(FIBOError):
    """Error from FIBO API"""

    pass


class FIBOStorageError(FIBOError):
    """Error storing visualization"""

    pass


class FIBOValidationError(FIBOError):
    """Validation error for FIBO requests"""

    pass


class ReportProcessingError(FIBOMedException):
    """Error processing medical report"""

    def __init__(self, message: str, code: str, details: str = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


class UserNotFoundError(FIBOMedException):
    """User not found"""

    pass


class UnauthorizedError(FIBOMedException):
    """Unauthorized access"""

    pass
