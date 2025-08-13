
from pydantic import BaseModel

from typing import List

class ChatMessage(BaseModel):
    role: str
    content: str

class FlashcardRequest(BaseModel):
    conversation: List[ChatMessage]
    destination: str  # "notion" or "anki"
