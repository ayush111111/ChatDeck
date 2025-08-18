from abc import ABC, abstractmethod
from typing import List
from fcg.models import ChatMessage


class FlashcardGeneratorService(ABC):
    """Abstract interface for flashcard generation"""

    @abstractmethod
    async def generate_flashcards(self, conversation: List[ChatMessage]) -> List[dict]:
        """Generate flashcards from conversation"""
        pass
