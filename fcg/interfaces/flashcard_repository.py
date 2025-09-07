from abc import ABC, abstractmethod
from typing import Any, Dict, List


class FlashcardRepository(ABC):
    """Abstract interface for flashcard storage systems"""

    @abstractmethod
    async def save_flashcards(self, flashcards: List[Dict[str, Any]]) -> bool:
        """Save flashcards to the storage system"""
        pass

    @abstractmethod
    async def get_flashcards(
        self, filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve flashcards from the storage system"""
        pass
