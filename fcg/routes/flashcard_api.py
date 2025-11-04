from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fcg.models.api import (
    FlashcardBatchCreate,
    FlashcardCreate,
    FlashcardResponse,
    SyncRequest,
    UserStatsResponse,
)
from fcg.services.database import FlashcardService, db_service

router = APIRouter(prefix="/api/v1/flashcards", tags=["Flashcards API (Database)"])


def get_db():
    """Dependency to get database session"""
    return next(db_service.get_db())


@router.post("/", response_model=FlashcardResponse)
async def create_flashcard(flashcard: FlashcardCreate, db: Session = Depends(get_db)):
    """Create a single flashcard"""
    try:
        service = FlashcardService(db)
        result = service.add_flashcard(
            user_id=flashcard.user_id,
            front=flashcard.front,
            back=flashcard.back,
            source_url=flashcard.source_url,
            source_text=flashcard.source_text,
            deck_name=flashcard.deck_name,
            tags=flashcard.tags,
            difficulty=flashcard.difficulty,
        )
        return FlashcardResponse.model_validate(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create flashcard: {str(e)}")


@router.post("/batch", response_model=List[FlashcardResponse])
async def create_flashcard_batch(batch: FlashcardBatchCreate, db: Session = Depends(get_db)):
    """Create multiple flashcards in a batch"""
    try:
        service = FlashcardService(db)
        batch_id = service.create_batch(batch.user_id, batch.source_url)

        results = []
        for flashcard_data in batch.flashcards:
            result = service.add_flashcard(
                user_id=flashcard_data.user_id,
                front=flashcard_data.front,
                back=flashcard_data.back,
                source_url=flashcard_data.source_url,
                source_text=flashcard_data.source_text,
                deck_name=flashcard_data.deck_name,
                tags=flashcard_data.tags,
                difficulty=flashcard_data.difficulty,
            )
            results.append(FlashcardResponse.model_validate(result))

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create flashcard batch: {str(e)}")


@router.get("/pending/{user_id}", response_model=List[FlashcardResponse])
async def get_pending_flashcards(user_id: str, db: Session = Depends(get_db)):
    """Get all pending flashcards for a user"""
    try:
        service = FlashcardService(db)
        flashcards = service.get_pending_flashcards(user_id)
        print(f"[API] get_pending_flashcards: user_id={user_id}, found {len(flashcards)} pending cards")
        if flashcards:
            print(f"[API] Card IDs: {[fc.id for fc in flashcards]}")
        return [FlashcardResponse.model_validate(fc) for fc in flashcards]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending flashcards: {str(e)}")


@router.post("/sync")
async def sync_flashcards(sync_request: SyncRequest, db: Session = Depends(get_db)):
    """Mark flashcards as synced"""
    try:
        print(f"[API] sync_flashcards: user_id={sync_request.user_id}, flashcard_ids={sync_request.flashcard_ids}")
        print(f"[API] Number of cards to sync: {len(sync_request.flashcard_ids)}")

        service = FlashcardService(db)
        updated_count = service.mark_flashcards_synced(sync_request.flashcard_ids)

        print(f"[API] Successfully synced {updated_count} flashcards")

        return {
            "message": f"Successfully synced {updated_count} flashcards",
            "synced_count": updated_count,
            "user_id": sync_request.user_id,
        }
    except Exception as e:
        print(f"[API] Error syncing flashcards: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to sync flashcards: {str(e)}")


@router.get("/stats/{user_id}", response_model=UserStatsResponse)
async def get_user_stats(user_id: str, db: Session = Depends(get_db)):
    """Get flashcard statistics for a user"""
    try:
        service = FlashcardService(db)
        stats = service.get_flashcard_stats(user_id)
        total = sum(stats.values())

        return UserStatsResponse(
            user_id=user_id,
            pending=stats.get("pending", 0),
            synced=stats.get("synced", 0),
            failed=stats.get("failed", 0),
            total=total,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user stats: {str(e)}")


@router.delete("/failed/{flashcard_id}")
async def mark_flashcard_failed(flashcard_id: int, db: Session = Depends(get_db)):
    """Mark a flashcard as failed"""
    try:
        service = FlashcardService(db)
        success = service.mark_flashcard_failed(flashcard_id)

        if not success:
            raise HTTPException(status_code=404, detail="Flashcard not found")

        return {"message": f"Flashcard {flashcard_id} marked as failed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark flashcard as failed: {str(e)}")
