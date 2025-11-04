"""
OpenRouter Flashcard Generation Service

This service provides flashcard generation powered by DSPy.
"""

from typing import List

from fcg.config.settings import Settings
from fcg.interfaces.flashcard_generator_service import FlashcardGeneratorService
from fcg.schemas import ChatMessage
from fcg.utils.flashcard_generator import generate_flashcards as dspy_generate_flashcards


class OpenRouterFlashcardService(FlashcardGeneratorService):
    """
    OpenRouter implementation of flashcard generation service.
    Now powered by DSPy for better quality and maintainability.
    """

    def __init__(self, settings: Settings):
        if not settings.openrouter_api_key:
            raise ValueError("OpenRouter API key is required")

        self.api_key = settings.openrouter_api_key
        self.api_url = settings.openrouter_url
        self.model = settings.openrouter_model
        self.max_tokens = settings.openrouter_max_tokens

    async def generate_flashcards(self, conversation: List[ChatMessage]) -> List[dict]:
        """
        Generate flashcards from conversation using DSPy-powered generation.

        This delegates to the improved DSPy implementation which provides:
        - Simple card count calculation (~1 card per 100 words)
        - 3-stage pipeline: text analysis → concept prioritization → card generation
        - Structured output with question, answer, explanation, and topic
        - No manual JSON parsing or prompt engineering

        Args:
            conversation: List of ChatMessage objects to generate flashcards from

        Returns:
            List of flashcard dictionaries with id, question, answer, explanation, and topic

        Raises:
            RuntimeError: If flashcard generation fails
        """
        return await dspy_generate_flashcards(conversation)

