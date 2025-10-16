from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Flashcard(Base):
    """Model for individual flashcards"""
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True)
    source_text = Column(Text, nullable=True)
    deck_name = Column(String(255), default="Default")
    
    # Status tracking
    status = Column(String(50), default="pending")  # pending, synced, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    synced_at = Column(DateTime, nullable=True)
    
    # Metadata
    tags = Column(String(500), nullable=True)  # comma-separated
    difficulty = Column(String(20), nullable=True)  # easy, medium, hard


class FlashcardBatch(Base):
    """Model for tracking batches of flashcards"""
    __tablename__ = "flashcard_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)
    batch_id = Column(String(100), nullable=False)  # UUID for grouping
    source_url = Column(String(500), nullable=True)
    total_cards = Column(Integer, default=0)
    processed_cards = Column(Integer, default=0)
    status = Column(String(50), default="processing")  # processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)