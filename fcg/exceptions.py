from typing import Any, Dict, Optional


class FlashcardGeneratorException(Exception):
    """Base exception for flashcard generator application"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(FlashcardGeneratorException):
    """Raised when there's a configuration issue"""

    pass


class FlashcardGenerationError(FlashcardGeneratorException):
    """Raised when flashcard generation fails"""

    pass


class RepositoryError(FlashcardGeneratorException):
    """Raised when repository operations fail"""

    pass


class ExportError(FlashcardGeneratorException):
    """Raised when export operations fail"""

    pass


class ValidationError(FlashcardGeneratorException):
    """Raised when data validation fails"""

    pass
