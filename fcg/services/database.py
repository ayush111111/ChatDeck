import uuid
from pathlib import Path
from typing import Generator, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fcg.config.settings import Settings
from fcg.models.flashcard import Base, Flashcard, FlashcardBatch


class DatabaseService:
    """Database service for managing SQLite/PostgreSQL connections"""

    def __init__(self, database_url: Optional[str] = None):
        settings = Settings()

        # Build database URL based on configuration
        if database_url:
            # Explicit database URL provided
            self.database_url = database_url
        elif settings.postgres_enabled and settings.postgres_host:
            # Use PostgreSQL when enabled and host is configured
            self.database_url = (
                f"postgresql://{settings.postgres_user}:{settings.postgres_password}@"
                f"{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db or 'postgres'}"
            )
        elif settings.postgres_enabled and not settings.postgres_host:
            # PostgreSQL enabled but no manual config - use DATABASE_URL environment variable
            self.database_url = settings.database_url
        else:
            # Use SQLite (default for local development)
            self.database_url = settings.database_url
            # Ensure SQLite directory exists
            self._ensure_sqlite_directory()

        # Create engine with appropriate settings
        if self.database_url.startswith("postgresql"):
            # PostgreSQL settings
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=300,  # Recycle connections every 5 minutes
            )
        else:
            # SQLite settings
            self.engine = create_engine(self.database_url, connect_args={"check_same_thread": False})

        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def _ensure_sqlite_directory(self):
        """Ensure the directory for SQLite database exists"""
        if self.database_url and self.database_url.startswith("sqlite:///"):
            # Extract path from SQLite URL (e.g., sqlite:///./data/flashcards.db)
            db_path = self.database_url.replace("sqlite:///", "")
            db_dir = Path(db_path).parent
            # Create directory if it doesn't exist
            db_dir.mkdir(parents=True, exist_ok=True)

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
        batch = FlashcardBatch(user_id=user_id, batch_id=batch_id, source_url=source_url)
        self.db.add(batch)
        self.db.commit()
        return batch_id

    def add_flashcard(
        self,
        user_id: str,
        front: str,
        back: str,
        batch_id: Optional[str] = None,
        source_url: Optional[str] = None,
        source_text: Optional[str] = None,
        deck_name: str = "Default",
        tags: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> Flashcard:
        """Add a new flashcard to the database"""
        flashcard = Flashcard(
            user_id=user_id,
            front=front,
            back=back,
            source_url=source_url,
            source_text=source_text,
            deck_name=deck_name,
            tags=tags,
            difficulty=difficulty,
        )
        self.db.add(flashcard)
        self.db.commit()
        self.db.refresh(flashcard)
        return flashcard

    def get_pending_flashcards(self, user_id: str) -> List[Flashcard]:
        """Get all pending flashcards for a user"""
        return (
            self.db.query(Flashcard)
            .filter(Flashcard.user_id == user_id, Flashcard.status == "pending")
            .order_by(Flashcard.created_at.desc())
            .all()
        )

    def mark_flashcards_synced(self, flashcard_ids: List[int]) -> int:
        """Mark multiple flashcards as synced"""
        from datetime import datetime

        updated_count = (
            self.db.query(Flashcard)
            .filter(Flashcard.id.in_(flashcard_ids))
            .update({"status": "synced", "synced_at": datetime.utcnow()}, synchronize_session=False)
        )

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

        stats = (
            self.db.query(Flashcard.status, func.count(Flashcard.id))
            .filter(Flashcard.user_id == user_id)
            .group_by(Flashcard.status)
            .all()
        )

        result = {"pending": 0, "synced": 0, "failed": 0}
        for status, count in stats:
            result[status] = count

        return result


# Global database service instance
db_service = DatabaseService()
