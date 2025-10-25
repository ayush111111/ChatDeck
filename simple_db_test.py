#!/usr/bin/env python3
"""Simple test script to verify database functionality"""

import os
import sys
import tempfile

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("🔄 Importing database models...")
    from fcg.models.flashcard import Flashcard, FlashcardBatch

    print("✅ Database models imported")

    print("🔄 Importing database services...")
    from fcg.services.database import DatabaseService, FlashcardService

    print("✅ Successfully imported database modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)


def test_database():
    """Test database functionality"""
    print("🧪 Testing database functionality...")

    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        db_path = temp_file.name

    try:
        db_url = f"sqlite:///{db_path}"
        print(f"📁 Using database: {db_url}")

        # Create database service
        db_service = DatabaseService(db_url)
        db_service.init_database()
        print("✅ Database initialized")

        # Get session
        session = next(db_service.get_db())
        flashcard_service = FlashcardService(session)
        print("✅ Database session created")

        # Create flashcard
        user_id = "test_user_123"
        flashcard = flashcard_service.add_flashcard(
            user_id=user_id, front="What is Python?", back="A programming language", deck_name="Programming"
        )
        print(f"✅ Created flashcard with ID: {flashcard.id}")

        # Get pending flashcards
        pending = flashcard_service.get_pending_flashcards(user_id)
        print(f"✅ Found {len(pending)} pending flashcards")

        # Test stats
        stats = flashcard_service.get_flashcard_stats(user_id)
        print(f"✅ Stats: {stats}")

        session.close()
        print("✅ All database tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
            print("🧹 Cleaned up test database")


if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
