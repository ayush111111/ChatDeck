import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from fcg.main import create_app
from fcg.models.flashcard import Base


@pytest.fixture
def temp_db_url():
    """Create temporary database URL for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        db_path = temp_file.name

    db_url = f"sqlite:///{db_path}"

    yield db_url

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def test_app(temp_db_url, monkeypatch):
    """Create FastAPI test client with temporary database"""
    # Override database URL in settings
    monkeypatch.setenv("DATABASE_URL", temp_db_url)

    # Create app
    app = create_app()

    # Initialize database
    engine = create_engine(temp_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    return app


@pytest.fixture
def client(test_app):
    """Create test client"""
    return TestClient(test_app)


class TestFlashcardAPI:
    """Test flashcard API endpoints"""

    def test_create_single_flashcard(self, client):
        """Test creating a single flashcard"""
        flashcard_data = {
            "user_id": "test_user_123",
            "front": "What is FastAPI?",
            "back": "A modern Python web framework",
            "deck_name": "Web Development",
            "tags": "python,fastapi,web",
            "difficulty": "medium",
        }

        response = client.post("/api/v1/flashcards/", json=flashcard_data)

        assert response.status_code == 200
        data = response.json()

        assert data["user_id"] == "test_user_123"
        assert data["front"] == "What is FastAPI?"
        assert data["back"] == "A modern Python web framework"
        assert data["deck_name"] == "Web Development"
        assert data["tags"] == "python,fastapi,web"
        assert data["difficulty"] == "medium"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

    def test_create_flashcard_batch(self, client):
        """Test creating multiple flashcards in a batch"""
        batch_data = {
            "user_id": "test_user_123",
            "source_url": "https://example.com/tutorial",
            "flashcards": [
                {"user_id": "test_user_123", "front": "What is Python?", "back": "A programming language"},
                {"user_id": "test_user_123", "front": "What is Django?", "back": "A Python web framework"},
            ],
        }

        response = client.post("/api/v1/flashcards/batch", json=batch_data)

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2
        assert data[0]["user_id"] == "test_user_123"
        assert data[1]["user_id"] == "test_user_123"
        assert data[0]["front"] == "What is Python?"
        assert data[1]["front"] == "What is Django?"

    def test_get_pending_flashcards(self, client):
        """Test retrieving pending flashcards for a user"""
        user_id = "test_user_456"

        # Create some flashcards first
        flashcard1 = {"user_id": user_id, "front": "Question 1", "back": "Answer 1"}
        flashcard2 = {"user_id": user_id, "front": "Question 2", "back": "Answer 2"}

        # Create flashcards
        client.post("/api/v1/flashcards/", json=flashcard1)
        client.post("/api/v1/flashcards/", json=flashcard2)

        # Get pending flashcards
        response = client.get(f"/api/v1/flashcards/pending/{user_id}")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2
        assert all(fc["status"] == "pending" for fc in data)
        assert all(fc["user_id"] == user_id for fc in data)

    def test_sync_flashcards(self, client):
        """Test syncing flashcards"""
        user_id = "test_user_sync"

        # Create flashcards
        flashcard1_response = client.post(
            "/api/v1/flashcards/", json={"user_id": user_id, "front": "Sync Question 1", "back": "Sync Answer 1"}
        )
        flashcard2_response = client.post(
            "/api/v1/flashcards/", json={"user_id": user_id, "front": "Sync Question 2", "back": "Sync Answer 2"}
        )

        flashcard1_id = flashcard1_response.json()["id"]
        flashcard2_id = flashcard2_response.json()["id"]

        # Sync flashcards
        sync_data = {"user_id": user_id, "flashcard_ids": [flashcard1_id, flashcard2_id]}

        response = client.post("/api/v1/flashcards/sync", json=sync_data)

        assert response.status_code == 200
        data = response.json()

        assert data["synced_count"] == 2
        assert data["user_id"] == user_id
        assert "Successfully synced 2 flashcards" in data["message"]

        # Verify no pending flashcards remain
        pending_response = client.get(f"/api/v1/flashcards/pending/{user_id}")
        pending_data = pending_response.json()
        assert len(pending_data) == 0

    def test_get_user_stats(self, client):
        """Test getting user statistics"""
        user_id = "test_user_stats"

        # Create flashcards
        flashcard1_response = client.post(
            "/api/v1/flashcards/", json={"user_id": user_id, "front": "Stats Question 1", "back": "Stats Answer 1"}
        )
        flashcard2_response = client.post(
            "/api/v1/flashcards/", json={"user_id": user_id, "front": "Stats Question 2", "back": "Stats Answer 2"}
        )
        flashcard3_response = client.post(
            "/api/v1/flashcards/", json={"user_id": user_id, "front": "Stats Question 3", "back": "Stats Answer 3"}
        )

        # Sync one flashcard
        sync_data = {"user_id": user_id, "flashcard_ids": [flashcard1_response.json()["id"]]}
        client.post("/api/v1/flashcards/sync", json=sync_data)

        # Mark one as failed
        failed_id = flashcard2_response.json()["id"]
        client.delete(f"/api/v1/flashcards/failed/{failed_id}")

        # Get stats
        response = client.get(f"/api/v1/flashcards/stats/{user_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["user_id"] == user_id
        assert data["pending"] == 1
        assert data["synced"] == 1
        assert data["failed"] == 1
        assert data["total"] == 3

    def test_mark_flashcard_failed(self, client):
        """Test marking a flashcard as failed"""
        user_id = "test_user_failed"

        # Create flashcard
        flashcard_response = client.post(
            "/api/v1/flashcards/", json={"user_id": user_id, "front": "Failed Question", "back": "Failed Answer"}
        )

        flashcard_id = flashcard_response.json()["id"]

        # Mark as failed
        response = client.delete(f"/api/v1/flashcards/failed/{flashcard_id}")

        assert response.status_code == 200
        data = response.json()

        assert f"Flashcard {flashcard_id} marked as failed" in data["message"]

    def test_mark_nonexistent_flashcard_failed(self, client):
        """Test marking non-existent flashcard as failed"""
        response = client.delete("/api/v1/flashcards/failed/99999")

        assert response.status_code == 404
        data = response.json()
        assert "Flashcard not found" in data["detail"]

    def test_get_pending_flashcards_empty(self, client):
        """Test getting pending flashcards for user with no flashcards"""
        response = client.get("/api/v1/flashcards/pending/nonexistent_user")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_stats_for_nonexistent_user(self, client):
        """Test getting stats for user with no flashcards"""
        response = client.get("/api/v1/flashcards/stats/nonexistent_user")

        assert response.status_code == 200
        data = response.json()

        assert data["user_id"] == "nonexistent_user"
        assert data["pending"] == 0
        assert data["synced"] == 0
        assert data["failed"] == 0
        assert data["total"] == 0

    def test_invalid_flashcard_data(self, client):
        """Test creating flashcard with invalid data"""
        invalid_data = {"user_id": "", "front": "", "back": ""}  # Empty user_id  # Empty front  # Empty back

        response = client.post("/api/v1/flashcards/", json=invalid_data)

        # Should succeed but with empty strings (validation can be added later)
        assert response.status_code == 200

    def test_user_isolation(self, client):
        """Test that users can only see their own flashcards"""
        user1 = "user_1"
        user2 = "user_2"

        # Create flashcards for different users
        client.post("/api/v1/flashcards/", json={"user_id": user1, "front": "User 1 Question", "back": "User 1 Answer"})
        client.post("/api/v1/flashcards/", json={"user_id": user2, "front": "User 2 Question", "back": "User 2 Answer"})

        # Get flashcards for each user
        user1_response = client.get(f"/api/v1/flashcards/pending/{user1}")
        user2_response = client.get(f"/api/v1/flashcards/pending/{user2}")

        user1_data = user1_response.json()
        user2_data = user2_response.json()

        assert len(user1_data) == 1
        assert len(user2_data) == 1
        assert user1_data[0]["user_id"] == user1
        assert user2_data[0]["user_id"] == user2
        assert user1_data[0]["front"] == "User 1 Question"
        assert user2_data[0]["front"] == "User 2 Question"


class TestAPIModels:
    """Test API model validation"""

    def test_flashcard_create_model(self, client):
        """Test FlashcardCreate model validation"""
        # Test with minimal required fields
        minimal_data = {"user_id": "test_user", "front": "Test front", "back": "Test back"}

        response = client.post("/api/v1/flashcards/", json=minimal_data)
        assert response.status_code == 200

        data = response.json()
        assert data["deck_name"] == "Default"  # Should use default value

    def test_flashcard_create_with_all_fields(self, client):
        """Test FlashcardCreate with all optional fields"""
        complete_data = {
            "user_id": "test_user",
            "front": "Complete front",
            "back": "Complete back",
            "source_url": "https://example.com",
            "source_text": "Original source text",
            "deck_name": "Custom Deck",
            "tags": "tag1,tag2,tag3",
            "difficulty": "hard",
        }

        response = client.post("/api/v1/flashcards/", json=complete_data)
        assert response.status_code == 200

        data = response.json()
        assert data["source_url"] == "https://example.com"
        assert data["source_text"] == "Original source text"
        assert data["deck_name"] == "Custom Deck"
        assert data["tags"] == "tag1,tag2,tag3"
        assert data["difficulty"] == "hard"
