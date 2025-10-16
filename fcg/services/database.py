from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fcg.models.flashcard import Base, Flashcard, FlashcardBatch
from fcg.config.settings import Settings
from typing import List, Optional, Generator
import uuid


class DatabaseService:
    """Database service for managing SQLite connection and initialization"""
    
    def __init__(self, database_url: Optional[str] = None):
        settings = Settings()
        self.database_url = database_url or settings.database_url
        
        # Create engine with SQLite-specific settings
        self.engine = create_engine(
            self.database_url, 
            connect_args={"check_same_thread": False}
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )
    
    def init_database(self):
        """Initialize database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_db(self) -> Generator[Session, None, None]:
        """Dependency for getting database session"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


class FlashcardService:
    """Service for managing flashcard operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_batch(self, user_id: str, source_url: Optional[str] = None) -> str:
        """Create a new flashcard batch and return batch_id"""
        batch_id = str(uuid.uuid4())
        batch = FlashcardBatch(
            user_id=user_id,
            batch_id=batch_id,
            source_url=source_url
        )
        self.db.add(batch)
        self.db.commit()
        return batch_id
    
    def add_flashcard(self, 
                     user_id: str, 
                     front: str, 
                     back: str,
                     batch_id: Optional[str] = None,
                     source_url: Optional[str] = None,
                     source_text: Optional[str] = None,
                     deck_name: str = "Default",
                     tags: Optional[str] = None,
                     difficulty: Optional[str] = None) -> Flashcard:
        """Add a new flashcard to the database"""
        flashcard = Flashcard(
            user_id=user_id,
            front=front,
            back=back,
            source_url=source_url,
            source_text=source_text,
            deck_name=deck_name,
            tags=tags,
            difficulty=difficulty
        )
        self.db.add(flashcard)
        self.db.commit()
        self.db.refresh(flashcard)
        return flashcard
    
    def get_pending_flashcards(self, user_id: str) -> List[Flashcard]:
        """Get all pending flashcards for a user"""
        return self.db.query(Flashcard).filter(
            Flashcard.user_id == user_id,
            Flashcard.status == "pending"
        ).order_by(Flashcard.created_at.desc()).all()
    
    def mark_flashcards_synced(self, flashcard_ids: List[int]) -> int:
        """Mark multiple flashcards as synced"""
        from datetime import datetime
        
        updated_count = self.db.query(Flashcard).filter(
            Flashcard.id.in_(flashcard_ids)
        ).update({
            "status": "synced",
            "synced_at": datetime.utcnow()
        }, synchronize_session=False)
        
        self.db.commit()
        return updated_count
    
    def mark_flashcard_failed(self, flashcard_id: int, error_message: Optional[str] = None) -> bool:
        """Mark a flashcard as failed to sync"""
        flashcard = self.db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
        if flashcard:
            flashcard.status = "failed"
            # Could add error_message field to model later
            self.db.commit()
            return True
        return False
    
    def get_flashcard_stats(self, user_id: str) -> dict:
        """Get statistics for user's flashcards"""
        from sqlalchemy import func
        
        stats = self.db.query(
            Flashcard.status,
            func.count(Flashcard.id)
        ).filter(
            Flashcard.user_id == user_id
        ).group_by(Flashcard.status).all()
        
        result = {"pending": 0, "synced": 0, "failed": 0}
        for status, count in stats:
            result[status] = count
        
        return result


# Global database service instance
db_service = DatabaseService()