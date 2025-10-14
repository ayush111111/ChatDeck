from typing import Any, Dict, List

from fcg.config.container import ServiceContainer
from fcg.interfaces.export_service import ExportService
from fcg.interfaces.flashcard_generator_service import FlashcardGeneratorService
from fcg.interfaces.flashcard_repository import FlashcardRepository
from fcg.models import (
    ChatMessage,
    ChatRole,
    DestinationType,
    FlashcardRequest,
    FlashcardResponse,
    TextFlashcardRequest,
)


class FlashcardUseCase:
    """Use case for flashcard operations"""

    def __init__(self, container: ServiceContainer):
        self.container = container

    async def generate_and_save_flashcards(self, request: FlashcardRequest) -> FlashcardResponse:
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
            return FlashcardResponse(status="error", message=f"Failed to process flashcards: {str(e)}")

    async def generate_flashcards_from_text(self, request: TextFlashcardRequest) -> FlashcardResponse:
        """Generate flashcards from raw text input"""
        try:
            # Convert text to conversation format for existing generator
            # This approach allows reuse of existing LLM service
            system_prompt = f"""Create {request.card_count} concise, simple, straightforward and distinct Anki cards to study the following text, each with a front and back.
Avoid repeating the content in the front on the back of the card. In particular, if the front is a question and the back an answer, avoid repeating the phrasing of the question as the initial part of the answer.
Avoid explicitly referring to the author or the article in the cards, and instead treat the content as factual and independent of the author.
{f'Focus on the topic: {request.topic}' if request.topic else ''}

Format each card as:
Q: [question]
A: [answer]

Text to study:"""

            # Create a conversation with system message and user text
            conversation = [
                ChatMessage(role=ChatRole.SYSTEM, content=system_prompt),
                ChatMessage(role=ChatRole.USER, content=request.text),
            ]

            # Generate flashcards using existing service
            generator = self.container.get(FlashcardGeneratorService)
            flashcards = await generator.generate_flashcards(conversation)

            if not flashcards:
                return FlashcardResponse(
                    status="error",
                    message="No flashcards could be generated from the provided text",
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
            return FlashcardResponse(status="error", message=f"Failed to process text flashcards: {str(e)}")

    async def _save_to_notion(self, flashcards: List[Dict[str, Any]]) -> FlashcardResponse:
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
                return FlashcardResponse(status="error", message="Failed to save flashcards to Notion")
        except Exception as e:
            return FlashcardResponse(status="error", message=f"Error saving to Notion: {str(e)}")

    async def _export_to_anki(self, flashcards: List[Dict[str, Any]]) -> FlashcardResponse:
        """Export flashcards to Anki format"""
        try:
            export_service = self.container.get(ExportService)
            # TODO: verify connxn
            file_path = export_service.export_flashcards(flashcards)

            return FlashcardResponse(
                status="success",
                message="Flashcards exported to Anki format successfully",
                data={"file_path": file_path, "count": len(flashcards)},
            )
        except Exception as e:
            return FlashcardResponse(status="error", message=f"Error exporting to Anki: {str(e)}")

    async def get_flashcards(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve flashcards with optional filtering"""
        try:
            if filters is None:
                filters = {}
            repository = self.container.get(FlashcardRepository)
            return await repository.get_flashcards(filters)
        except Exception as e:
            # Log error in production
            print(f"Error retrieving flashcards: {e}")
            return []
