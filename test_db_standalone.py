import os
import tempfile

# Direct imports to avoid circular dependency
from fcg.services.database import DatabaseService, FlashcardService


def test_database_basic_functionality():
    """Basic test of database functionality without fixtures"""
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        db_path = temp_file.name

    try:
        db_url = f"sqlite:///{db_path}"

        # Create database service
        db_service = DatabaseService(db_url)
        db_service.init_database()

        # Test database session
        session = next(db_service.get_db())

        # Create FlashcardService
        flashcard_service = FlashcardService(session)

        # Test creating a flashcard
        user_id = "test_user_123"
        front = "What is Python?"
        back = "A programming language"

        flashcard = flashcard_service.add_flashcard(user_id=user_id, front=front, back=back, deck_name="Programming")

        # Verify flashcard was created
        assert flashcard.id is not None
        assert flashcard.user_id == user_id
        assert flashcard.front == front
        assert flashcard.back == back
        assert flashcard.deck_name == "Programming"
        assert flashcard.status == "pending"

        # Test getting pending flashcards
        pending = flashcard_service.get_pending_flashcards(user_id)
        assert len(pending) == 1
        assert pending[0].id == flashcard.id

        # Test marking as synced
        updated_count = flashcard_service.mark_flashcards_synced([flashcard.id])
        assert updated_count == 1

        # Verify no more pending flashcards
        pending_after_sync = flashcard_service.get_pending_flashcards(user_id)
        assert len(pending_after_sync) == 0

        # Test stats
        stats = flashcard_service.get_flashcard_stats(user_id)
        assert stats["pending"] == 0
        assert stats["synced"] == 1
        assert stats["failed"] == 0

        session.close()
        print("✅ All database tests passed!")

    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    test_database_basic_functionality()
