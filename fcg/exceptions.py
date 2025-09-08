"""
fcg.exceptions
~~~~~~~~~~~~~~
Exception hierarchy used by the flashcard generator application.
This module defines application-specific exceptions that provide a consistent,
typed way to signal and handle error conditions across configuration parsing,
repository operations, validation, flashcard generation, and exporting (for
example to Anki via AnkiConnect).
Classes
- FlashcardGeneratorException: Base class for all custom exceptions. It stores
    a human-readable message and an optional `details` dict for structured
    diagnostic information.
- ConfigurationError: Raised for configuration-related problems.
- FlashcardGenerationError: Raised when flashcard creation or transformation
    fails.
- RepositoryError: Raised for errors interacting with storage/repositories.
- ExportError: Raised for export-related failures (e.g., file output, network).
- ValidationError: Raised when input data fails validation checks.
- AnkiConnectionError: Raised when a connection to Anki / AnkiConnect cannot be
    established (subclass of ExportError).
- AnkiResponseError: Raised when Anki returns an error or an unexpected
    response (subclass of ExportError).
Usage examples
- Raising an error:
        raise ConfigurationError("Missing API key", details={"env_var": "API_KEY"})
- Catching and inspecting:
        try:
                generate_flashcards(...)
        except FlashcardGeneratorException as exc:
                logger.error("Generation failed: %s", exc.message)
                if exc.details:
                        logger.debug("Failure details: %s", exc.details)
Notes
- The `details` attribute is intended for machine-consumable information that
    can help with diagnostics and debugging (e.g., invalid field names,
    underlying exception data, HTTP status codes).
- The base exception captures a `message` attribute in addition to the native
    Exception message to make structured handling easier.
"""

from typing import Any, Dict, Optional


class FlashcardGeneratorException(Exception):
    """Base exception for flashcard generator application"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(FlashcardGeneratorException):
    """Raised when there's a configuration issue"""


class FlashcardGenerationError(FlashcardGeneratorException):
    """Raised when flashcard generation fails"""


class RepositoryError(FlashcardGeneratorException):
    """Raised when repository operations fail"""


class ExportError(FlashcardGeneratorException):
    """Raised when export operations fail"""


class ValidationError(FlashcardGeneratorException):
    """Raised when data validation fails"""


class AnkiConnectionError(ExportError):
    """Raised when cannot connect to Anki or AnkiConnect"""


class AnkiResponseError(ExportError):
    """Raised when Anki returns an invalid or error response"""
