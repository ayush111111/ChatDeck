from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class FlashcardCreate(BaseModel):
    """Model for creating a new flashcard"""

    user_id: str
    front: str
    back: str
    source_url: Optional[str] = None
    source_text: Optional[str] = None
    deck_name: str = "Default"
    tags: Optional[str] = None
    difficulty: Optional[str] = None


class FlashcardResponse(BaseModel):
    """Model for flashcard response"""

    id: int
    user_id: str
    front: str
    back: str
    source_url: Optional[str] = None
    source_text: Optional[str] = None
    deck_name: str
    status: str
    created_at: datetime
    synced_at: Optional[datetime] = None
    tags: Optional[str] = None
    difficulty: Optional[str] = None

    class Config:
        from_attributes = True


class FlashcardBatchCreate(BaseModel):
    """Model for creating a flashcard batch"""

    user_id: str
    source_url: Optional[str] = None
    flashcards: List[FlashcardCreate]


class SyncRequest(BaseModel):
    """Model for syncing flashcards"""

    user_id: str
    flashcard_ids: List[int]


class UserStatsResponse(BaseModel):
    """Model for user flashcard statistics"""

    user_id: str
    pending: int
    synced: int
    failed: int
    total: int
