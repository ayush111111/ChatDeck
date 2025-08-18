from typing import List, Dict, Any
from fcg.models import FlashcardRequest, FlashcardResponse, DestinationType
from fcg.interfaces.flashcard_generator_service import FlashcardGeneratorService
from fcg.interfaces.flashcard_repository import FlashcardRepository
from fcg.interfaces.export_service import ExportService
from fcg.config.container import ServiceContainer


class FlashcardUseCase:
    """Use case for flashcard operations"""

    def __init__(self, container: ServiceContainer):
        self.container = container

    async def generate_and_save_flashcards(
        self, request: FlashcardRequest
    ) -> FlashcardResponse:
        """Generate flashcards and save/export them based on destination"""
        try:
            # Generate flashcards
            generator = self.container.get(FlashcardGeneratorService)
            flashcards = await generator.generate_flashcards(request.conversation)

            if not flashcards:
                return FlashcardResponse(
                    status="error",
                    message="No flashcards could be generated from the provided conversation",
                )

            # Process based on destination
            if request.destination == DestinationType.NOTION:
                return await self._save_to_notion(flashcards)
            elif request.destination == DestinationType.ANKI:
                return await self._export_to_anki(flashcards)
            else:
                return FlashcardResponse(
                    status="error",
                    message=f"Unsupported destination: {request.destination}",
                )

        except Exception as e:
            return FlashcardResponse(
                status="error", message=f"Failed to process flashcards: {str(e)}"
            )

    async def _save_to_notion(
        self, flashcards: List[Dict[str, Any]]
    ) -> FlashcardResponse:
        """Save flashcards to Notion"""
        try:
            repository = self.container.get(FlashcardRepository)
            success = await repository.save_flashcards(flashcards)

            if success:
                return FlashcardResponse(
                    status="success",
                    message="Flashcards saved to Notion successfully",
                    data={"count": len(flashcards)},
                )
            else:
                return FlashcardResponse(
                    status="error", message="Failed to save flashcards to Notion"
                )
        except Exception as e:
            return FlashcardResponse(
                status="error", message=f"Error saving to Notion: {str(e)}"
            )

    async def _export_to_anki(
        self, flashcards: List[Dict[str, Any]]
    ) -> FlashcardResponse:
        """Export flashcards to Anki format"""
        try:
            export_service = self.container.get(ExportService)
            file_path = export_service.export_flashcards(flashcards)

            return FlashcardResponse(
                status="success",
                message="Flashcards exported to Anki format successfully",
                data={"file_path": file_path, "count": len(flashcards)},
            )
        except Exception as e:
            return FlashcardResponse(
                status="error", message=f"Error exporting to Anki: {str(e)}"
            )

    async def get_flashcards(
        self, filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve flashcards with optional filtering"""
        try:
            repository = self.container.get(FlashcardRepository)
            return await repository.get_flashcards(filters)
        except Exception as e:
            # Log error in production
            print(f"Error retrieving flashcards: {e}")
            return []
