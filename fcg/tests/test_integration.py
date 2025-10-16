import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from fcg.main import create_app
from fcg.models.flashcard import Base


@pytest.fixture
def integration_client():
    """Create test client for integration tests"""
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
        db_path = temp_file.name
    
    db_url = f"sqlite:///{db_path}"
    
    # Set environment variable for database URL
    os.environ["DATABASE_URL"] = db_url
    
    # Create app and initialize database
    app = create_app()
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    client = TestClient(app)
    
    yield client
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)
    
    # Clean up environment
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]


class TestCompleteFlashcardFlow:
    """Test complete flashcard workflow from creation to sync"""
    
    def test_complete_user_workflow(self, integration_client):
        """Test complete user workflow: create -> view -> sync -> stats"""
        user_id = "integration_user_123"
        
        # Step 1: Create flashcards via batch endpoint
        batch_data = {
            "user_id": user_id,
            "source_url": "https://example.com/learning-python",
            "flashcards": [
                {
                    "user_id": user_id,
                    "front": "What does 'def' keyword do in Python?",
                    "back": "Defines a function",
                    "deck_name": "Python Basics",
                    "difficulty": "easy"
                },
                {
                    "user_id": user_id,
                    "front": "What is a list comprehension?",
                    "back": "A concise way to create lists using a single line of code",
                    "deck_name": "Python Advanced",
                    "difficulty": "medium"
                },
                {
                    "user_id": user_id,
                    "front": "What is the difference between '==' and 'is'?",
                    "back": "'==' compares values, 'is' compares object identity",
                    "deck_name": "Python Advanced",
                    "difficulty": "hard"
                }
            ]
        }
        
        batch_response = integration_client.post("/api/v1/flashcards/batch", json=batch_data)
        assert batch_response.status_code == 200
        created_flashcards = batch_response.json()
        assert len(created_flashcards) == 3
        
        # Step 2: Verify all flashcards are pending
        pending_response = integration_client.get(f"/api/v1/flashcards/pending/{user_id}")
        assert pending_response.status_code == 200
        pending_flashcards = pending_response.json()
        assert len(pending_flashcards) == 3
        assert all(fc["status"] == "pending" for fc in pending_flashcards)
        
        # Step 3: Check initial stats
        stats_response = integration_client.get(f"/api/v1/flashcards/stats/{user_id}")
        assert stats_response.status_code == 200
        initial_stats = stats_response.json()
        assert initial_stats["pending"] == 3
        assert initial_stats["synced"] == 0
        assert initial_stats["failed"] == 0
        assert initial_stats["total"] == 3
        
        # Step 4: Sync 2 flashcards successfully
        flashcard_ids_to_sync = [created_flashcards[0]["id"], created_flashcards[1]["id"]]
        sync_data = {
            "user_id": user_id,
            "flashcard_ids": flashcard_ids_to_sync
        }
        
        sync_response = integration_client.post("/api/v1/flashcards/sync", json=sync_data)
        assert sync_response.status_code == 200
        sync_result = sync_response.json()
        assert sync_result["synced_count"] == 2
        
        # Step 5: Mark 1 flashcard as failed
        failed_id = created_flashcards[2]["id"]
        failed_response = integration_client.delete(f"/api/v1/flashcards/failed/{failed_id}")
        assert failed_response.status_code == 200
        
        # Step 6: Verify pending flashcards are now empty
        final_pending_response = integration_client.get(f"/api/v1/flashcards/pending/{user_id}")
        assert final_pending_response.status_code == 200
        final_pending = final_pending_response.json()
        assert len(final_pending) == 0
        
        # Step 7: Check final stats
        final_stats_response = integration_client.get(f"/api/v1/flashcards/stats/{user_id}")
        assert final_stats_response.status_code == 200
        final_stats = final_stats_response.json()
        assert final_stats["pending"] == 0
        assert final_stats["synced"] == 2
        assert final_stats["failed"] == 1
        assert final_stats["total"] == 3
    
    def test_multi_user_isolation(self, integration_client):
        """Test that multiple users' flashcards are properly isolated"""
        user_alice = "alice_123"
        user_bob = "bob_456"
        
        # Alice creates flashcards
        alice_flashcard = {
            "user_id": user_alice,
            "front": "Alice's question",
            "back": "Alice's answer",
            "deck_name": "Alice's Deck"
        }
        alice_response = integration_client.post("/api/v1/flashcards/", json=alice_flashcard)
        assert alice_response.status_code == 200
        alice_fc_id = alice_response.json()["id"]
        
        # Bob creates flashcards
        bob_flashcards = {
            "user_id": user_bob,
            "source_url": "https://bob-learning.com",
            "flashcards": [
                {
                    "user_id": user_bob,
                    "front": "Bob's question 1",
                    "back": "Bob's answer 1"
                },
                {
                    "user_id": user_bob,
                    "front": "Bob's question 2", 
                    "back": "Bob's answer 2"
                }
            ]
        }
        bob_response = integration_client.post("/api/v1/flashcards/batch", json=bob_flashcards)
        assert bob_response.status_code == 200
        bob_fcs = bob_response.json()
        
        # Verify Alice can only see her flashcards
        alice_pending = integration_client.get(f"/api/v1/flashcards/pending/{user_alice}")
        alice_data = alice_pending.json()
        assert len(alice_data) == 1
        assert alice_data[0]["front"] == "Alice's question"
        assert alice_data[0]["deck_name"] == "Alice's Deck"
        
        # Verify Bob can only see his flashcards
        bob_pending = integration_client.get(f"/api/v1/flashcards/pending/{user_bob}")
        bob_data = bob_pending.json()
        assert len(bob_data) == 2
        assert all("Bob's question" in fc["front"] for fc in bob_data)
        
        # Verify stats are separate
        alice_stats = integration_client.get(f"/api/v1/flashcards/stats/{user_alice}").json()
        bob_stats = integration_client.get(f"/api/v1/flashcards/stats/{user_bob}").json()
        
        assert alice_stats["total"] == 1
        assert bob_stats["total"] == 2
        
        # Alice syncs her flashcard
        alice_sync = integration_client.post("/api/v1/flashcards/sync", json={
            "user_id": user_alice,
            "flashcard_ids": [alice_fc_id]
        })
        assert alice_sync.status_code == 200
        
        # Bob's flashcards should still be pending
        bob_pending_after = integration_client.get(f"/api/v1/flashcards/pending/{user_bob}")
        assert len(bob_pending_after.json()) == 2
        
        # Alice should have no pending flashcards
        alice_pending_after = integration_client.get(f"/api/v1/flashcards/pending/{user_alice}")
        assert len(alice_pending_after.json()) == 0
    
    def test_error_handling_in_workflow(self, integration_client):
        """Test error handling throughout the workflow"""
        user_id = "error_test_user"
        
        # Test invalid sync request (non-existent flashcard IDs)
        invalid_sync = {
            "user_id": user_id,
            "flashcard_ids": [99999, 88888]  # Non-existent IDs
        }
        sync_response = integration_client.post("/api/v1/flashcards/sync", json=invalid_sync)
        assert sync_response.status_code == 200  # Should succeed but sync 0 cards
        assert sync_response.json()["synced_count"] == 0
        
        # Test marking non-existent flashcard as failed
        failed_response = integration_client.delete("/api/v1/flashcards/failed/99999")
        assert failed_response.status_code == 404
        
        # Test getting stats for user with no flashcards
        stats_response = integration_client.get(f"/api/v1/flashcards/stats/{user_id}")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["total"] == 0
        
        # Test getting pending flashcards for user with no flashcards
        pending_response = integration_client.get(f"/api/v1/flashcards/pending/{user_id}")
        assert pending_response.status_code == 200
        assert len(pending_response.json()) == 0
    
    def test_health_endpoint(self, integration_client):
        """Test health check endpoint"""
        response = integration_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "flashcard-generator"
    
    def test_large_batch_creation(self, integration_client):
        """Test creating a large batch of flashcards"""
        user_id = "batch_test_user"
        
        # Create a batch of 50 flashcards
        flashcards = []
        for i in range(50):
            flashcards.append({
                "user_id": user_id,
                "front": f"Question {i + 1}",
                "back": f"Answer {i + 1}",
                "deck_name": f"Deck {(i // 10) + 1}",  # 5 decks with 10 cards each
                "difficulty": ["easy", "medium", "hard"][i % 3]
            })
        
        batch_data = {
            "user_id": user_id,
            "source_url": "https://example.com/large-course",
            "flashcards": flashcards
        }
        
        # Create batch
        batch_response = integration_client.post("/api/v1/flashcards/batch", json=batch_data)
        assert batch_response.status_code == 200
        created_flashcards = batch_response.json()
        assert len(created_flashcards) == 50
        
        # Verify all are pending
        pending_response = integration_client.get(f"/api/v1/flashcards/pending/{user_id}")
        pending_flashcards = pending_response.json()
        assert len(pending_flashcards) == 50
        
        # Sync half of them
        ids_to_sync = [fc["id"] for fc in created_flashcards[:25]]
        sync_response = integration_client.post("/api/v1/flashcards/sync", json={
            "user_id": user_id,
            "flashcard_ids": ids_to_sync
        })
        assert sync_response.status_code == 200
        assert sync_response.json()["synced_count"] == 25
        
        # Check final stats
        stats_response = integration_client.get(f"/api/v1/flashcards/stats/{user_id}")
        stats = stats_response.json()
        assert stats["pending"] == 25
        assert stats["synced"] == 25
        assert stats["failed"] == 0
        assert stats["total"] == 50