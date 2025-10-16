import pytest
import tempfile
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fcg.models.flashcard import Base, Flashcard, FlashcardBatch
from fcg.services.database import DatabaseService, FlashcardService


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
        db_path = temp_file.name
    
    db_url = f"sqlite:///{db_path}"
    
    # Create database service
    db_service = DatabaseService(db_url)
    db_service.init_database()
    
    yield db_service
    
    # Cleanup
    os.unlink(db_path)


@pytest.fixture
def db_session(temp_db):
    """Create a database session for testing"""
    session = next(temp_db.get_db())
    yield session
    session.close()


@pytest.fixture
def flashcard_service(db_session):
    """Create a FlashcardService instance for testing"""
    return FlashcardService(db_session)


class TestDatabaseService:
    """Test DatabaseService functionality"""
    
    def test_database_initialization(self, temp_db):
        """Test database tables are created correctly"""
        # Check that tables exist
        inspector = temp_db.engine.dialect.get_table_names(temp_db.engine.connect())
        assert 'flashcards' in inspector
        assert 'flashcard_batches' in inspector
    
    def test_get_db_session(self, temp_db):
        """Test database session creation"""
        session = next(temp_db.get_db())
        assert session is not None
        session.close()


class TestFlashcardService:
    """Test FlashcardService functionality"""
    
    def test_create_batch(self, flashcard_service, db_session):
        """Test creating a flashcard batch"""
        user_id = "test_user_123"
        source_url = "https://example.com"
        
        batch_id = flashcard_service.create_batch(user_id, source_url)
        
        assert batch_id is not None
        assert len(batch_id) == 36  # UUID length
        
        # Verify batch was created in database
        batch = db_session.query(FlashcardBatch).filter_by(batch_id=batch_id).first()
        assert batch is not None
        assert batch.user_id == user_id
        assert batch.source_url == source_url
        assert batch.status == "processing"
    
    def test_add_flashcard(self, flashcard_service, db_session):
        """Test adding a flashcard"""
        user_id = "test_user_123"
        front = "What is Python?"
        back = "A programming language"
        
        flashcard = flashcard_service.add_flashcard(
            user_id=user_id,
            front=front,
            back=back,
            deck_name="Programming",
            tags="python,programming",
            difficulty="easy"
        )
        
        assert flashcard.id is not None
        assert flashcard.user_id == user_id
        assert flashcard.front == front
        assert flashcard.back == back
        assert flashcard.deck_name == "Programming"
        assert flashcard.tags == "python,programming"
        assert flashcard.difficulty == "easy"
        assert flashcard.status == "pending"
        assert flashcard.created_at is not None
    
    def test_get_pending_flashcards(self, flashcard_service, db_session):
        """Test retrieving pending flashcards"""
        user_id = "test_user_123"
        
        # Create multiple flashcards
        flashcard1 = flashcard_service.add_flashcard(user_id, "Front 1", "Back 1")
        flashcard2 = flashcard_service.add_flashcard(user_id, "Front 2", "Back 2")
        flashcard3 = flashcard_service.add_flashcard("other_user", "Front 3", "Back 3")
        
        # Mark one as synced
        flashcard1.status = "synced"
        db_session.commit()
        
        pending = flashcard_service.get_pending_flashcards(user_id)
        
        assert len(pending) == 1
        assert pending[0].id == flashcard2.id
        assert pending[0].front == "Front 2"
    
    def test_mark_flashcards_synced(self, flashcard_service, db_session):
        """Test marking flashcards as synced"""
        user_id = "test_user_123"
        
        # Create flashcards
        flashcard1 = flashcard_service.add_flashcard(user_id, "Front 1", "Back 1")
        flashcard2 = flashcard_service.add_flashcard(user_id, "Front 2", "Back 2")
        flashcard3 = flashcard_service.add_flashcard(user_id, "Front 3", "Back 3")
        
        # Mark some as synced
        updated_count = flashcard_service.mark_flashcards_synced([flashcard1.id, flashcard2.id])
        
        assert updated_count == 2
        
        # Verify status changed
        db_session.refresh(flashcard1)
        db_session.refresh(flashcard2)
        db_session.refresh(flashcard3)
        
        assert flashcard1.status == "synced"
        assert flashcard2.status == "synced"
        assert flashcard3.status == "pending"
        assert flashcard1.synced_at is not None
        assert flashcard2.synced_at is not None
    
    def test_mark_flashcard_failed(self, flashcard_service, db_session):
        """Test marking a flashcard as failed"""
        user_id = "test_user_123"
        flashcard = flashcard_service.add_flashcard(user_id, "Front", "Back")
        
        success = flashcard_service.mark_flashcard_failed(flashcard.id)
        
        assert success is True
        
        # Verify status changed
        db_session.refresh(flashcard)
        assert flashcard.status == "failed"
    
    def test_mark_nonexistent_flashcard_failed(self, flashcard_service):
        """Test marking a non-existent flashcard as failed"""
        success = flashcard_service.mark_flashcard_failed(99999)
        assert success is False
    
    def test_get_flashcard_stats(self, flashcard_service, db_session):
        """Test getting user flashcard statistics"""
        user_id = "test_user_123"
        
        # Create flashcards with different statuses
        flashcard1 = flashcard_service.add_flashcard(user_id, "Front 1", "Back 1")
        flashcard2 = flashcard_service.add_flashcard(user_id, "Front 2", "Back 2")
        flashcard3 = flashcard_service.add_flashcard(user_id, "Front 3", "Back 3")
        flashcard4 = flashcard_service.add_flashcard("other_user", "Front 4", "Back 4")
        
        # Update statuses
        flashcard1.status = "synced"
        flashcard2.status = "failed"
        # flashcard3 remains "pending"
        db_session.commit()
        
        stats = flashcard_service.get_flashcard_stats(user_id)
        
        assert stats["pending"] == 1
        assert stats["synced"] == 1
        assert stats["failed"] == 1
    
    def test_get_flashcard_stats_empty(self, flashcard_service):
        """Test getting stats for user with no flashcards"""
        stats = flashcard_service.get_flashcard_stats("nonexistent_user")
        
        assert stats["pending"] == 0
        assert stats["synced"] == 0
        assert stats["failed"] == 0


class TestFlashcardModel:
    """Test Flashcard model directly"""
    
    def test_flashcard_model_defaults(self, db_session):
        """Test flashcard model default values"""
        flashcard = Flashcard(
            user_id="test_user",
            front="Test front",
            back="Test back"
        )
        
        db_session.add(flashcard)
        db_session.commit()
        db_session.refresh(flashcard)
        
        assert flashcard.deck_name == "Default"
        assert flashcard.status == "pending"
        assert flashcard.created_at is not None
        assert flashcard.synced_at is None
        assert isinstance(flashcard.created_at, datetime)
    
    def test_flashcard_model_custom_values(self, db_session):
        """Test flashcard model with custom values"""
        custom_time = datetime.now()
        
        flashcard = Flashcard(
            user_id="test_user",
            front="Custom front",
            back="Custom back",
            source_url="https://example.com",
            source_text="Original text here",
            deck_name="Custom Deck",
            status="synced",
            created_at=custom_time,
            synced_at=custom_time,
            tags="tag1,tag2,tag3",
            difficulty="hard"
        )
        
        db_session.add(flashcard)
        db_session.commit()
        db_session.refresh(flashcard)
        
        assert flashcard.source_url == "https://example.com"
        assert flashcard.source_text == "Original text here"
        assert flashcard.deck_name == "Custom Deck"
        assert flashcard.status == "synced"
        assert flashcard.tags == "tag1,tag2,tag3"
        assert flashcard.difficulty == "hard"


class TestFlashcardBatchModel:
    """Test FlashcardBatch model"""
    
    def test_batch_model_defaults(self, db_session):
        """Test batch model default values"""
        batch = FlashcardBatch(
            user_id="test_user",
            batch_id="test-batch-123"
        )
        
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        assert batch.total_cards == 0
        assert batch.processed_cards == 0
        assert batch.status == "processing"
        assert batch.created_at is not None
        assert batch.completed_at is None
        assert isinstance(batch.created_at, datetime)