from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ExportService(ABC):
    """Abstract interface for exporting flashcards"""

    @abstractmethod
    def export_flashcards(self, flashcards: List[Dict[str, Any]]) -> str:
        """Export flashcards and return file path or identifier"""
