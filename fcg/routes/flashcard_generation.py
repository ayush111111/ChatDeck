from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from fcg.config.settings import Settings
from fcg.models.api import FlashcardResponse
from fcg.schemas import ChatMessage, ChatRole
from fcg.services.database import FlashcardService, db_service
from fcg.services.openrouter_flashcard_service import OpenRouterFlashcardService

router = APIRouter(prefix="/api/v1/flashcards", tags=["Flashcard Generation (LLM)"])


class GenerateFlashcardsRequest(BaseModel):
    """Request to generate flashcards from text"""

    user_id: str
    text: str
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    deck_name: str = "Web Learning"
    card_count: Optional[int] = 5


def get_db():
    """Dependency to get database session"""
    return next(db_service.get_db())


@router.post("/generate", response_model=List[FlashcardResponse])
async def generate_flashcards(request: GenerateFlashcardsRequest, db: Session = Depends(get_db)):
    """
    Generate flashcards from text using LLM and save to database

    This is where the magic happens:
    1. Text comes from Chrome extension
    2. LLM generates flashcards
    3. Flashcards saved with user_id for routing
    4. User can later sync to Anki via addon
    """
    try:
        # Initialize OpenRouter service
        settings = Settings()
        llm_service = OpenRouterFlashcardService(settings)

        # Create a conversation-style prompt for the LLM
        system_prompt = f"""Create {request.card_count} concise, simple, straightforward and distinct Anki cards to study the following text.
Each card should have a question, answer, and topic.
Avoid repeating the content in the question as part of the answer.
Avoid explicitly referring to the author or article in the cards."""

        conversation = [
            ChatMessage(role=ChatRole.SYSTEM, content=system_prompt),
            ChatMessage(role=ChatRole.USER, content=request.text),
        ]

        # Generate flashcards using LLM
        generated_cards = await llm_service.generate_flashcards(conversation)

        if not generated_cards:
            raise HTTPException(status_code=400, detail="No flashcards could be generated from the provided text")

        # Save all flashcards to database
        service = FlashcardService(db)
        results = []

        # TODO: batch it
        for card in generated_cards:
            flashcard = service.add_flashcard(
                user_id=request.user_id,
                front=card.get("question", ""),
                back=card.get("answer", ""),
                deck_name=request.deck_name,
                source_url=request.source_url,
                source_text=request.text[:500] + "..." if len(request.text) > 500 else request.text,
                tags=f"web-learning,{card.get('topic', 'general').lower().replace(' ', '-')}",
            )
            results.append(FlashcardResponse.model_validate(flashcard))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcards: {str(e)}")


@router.get("/user/{user_id}/stats")
async def get_user_dashboard(user_id: str, db: Session = Depends(get_db)):
    """Get user's flashcard dashboard stats"""
    service = FlashcardService(db)
    stats = service.get_flashcard_stats(user_id)
    pending = service.get_pending_flashcards(user_id)

    return {
        "user_id": user_id,
        "stats": stats,
        "pending_count": len(pending),
        "latest_pending": [
            {
                "id": fc.id,
                "front": fc.front[:100] + "..." if len(fc.front) > 100 else fc.front,
                "created_at": fc.created_at,
                "source_url": fc.source_url,
            }
            for fc in pending[:5]  # Latest 5 pending cards
        ],
    }
