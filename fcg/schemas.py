from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ChatRole(str, Enum):
    """Valid chat message roles"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Chat message with validation"""

    role: ChatRole
    content: str = Field(..., min_length=1, description="Message content cannot be empty")

    @field_validator("content")
    @classmethod
    def content_must_not_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError("Content cannot be only whitespace")
        return v.strip()


class DestinationType(str, Enum):
    """Valid destination types"""

    NOTION = "notion"
    ANKI = "anki"


class FlashcardRequest(BaseModel):
    """Request to generate flashcards"""

    conversation: List[ChatMessage] = Field(..., min_items=1, description="At least one message required")
    destination: DestinationType

    @field_validator("conversation")
    @classmethod
    def conversation_must_have_content(cls, v):
        if not any(msg.content.strip() for msg in v):
            raise ValueError("Conversation must contain at least one message with content")
        return v


class TextFlashcardRequest(BaseModel):
    """Request to generate flashcards from text input"""

    text: str = Field(..., min_length=10, description="Text content to convert to flashcards")
    destination: DestinationType
    card_count: Optional[int] = Field(default=5, ge=1, le=50, description="Number of flashcards to generate")
    topic: Optional[str] = Field(default=None, max_length=100, description="Optional topic for the flashcards")

    @field_validator("text")
    @classmethod
    def text_must_not_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError("Text content cannot be only whitespace")
        return v.strip()


class Flashcard(BaseModel):
    """Flashcard domain model"""

    id: Optional[str] = None
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    topic: Optional[str] = None

    @field_validator("question", "answer")
    @classmethod
    def text_fields_must_not_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be only whitespace")
        return v.strip()


class FlashcardResponse(BaseModel):
    """Response from flashcard operations"""

    status: str
    message: Optional[str] = None
    data: Optional[dict] = None
