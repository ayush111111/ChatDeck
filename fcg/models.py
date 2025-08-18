from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum


class ChatRole(str, Enum):
    """Valid chat message roles"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Chat message with validation"""

    role: ChatRole
    content: str = Field(
        ..., min_length=1, description="Message content cannot be empty"
    )

    @validator("content")
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

    conversation: List[ChatMessage] = Field(
        ..., min_items=1, description="At least one message required"
    )
    destination: DestinationType

    @validator("conversation")
    def conversation_must_have_content(cls, v):
        if not any(msg.content.strip() for msg in v):
            raise ValueError(
                "Conversation must contain at least one message with content"
            )
        return v


class Flashcard(BaseModel):
    """Flashcard domain model"""

    id: Optional[str] = None
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    topic: Optional[str] = None

    @validator("question", "answer")
    def text_fields_must_not_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be only whitespace")
        return v.strip()


class FlashcardResponse(BaseModel):
    """Response from flashcard operations"""

    status: str
    message: Optional[str] = None
    data: Optional[dict] = None
