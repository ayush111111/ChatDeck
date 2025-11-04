from abc import ABC, abstractmethod
from typing import Any, Dict, List


class FlashcardGeneratorService(ABC):
    """Abstract interface for flashcard generation"""

    @abstractmethod
    async def generate_flashcards(self, conversation: List[Dict[str, Any]]) -> List[dict]:
        """Generate flashcards from conversation"""
        pass
