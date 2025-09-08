import json
from unittest.mock import MagicMock, patch

import pytest

from fcg.services.anki_export_service import AnkiExportService


@pytest.fixture
def sample_flashcards():
    """Sample flashcards for testing"""
    return [
        {
            "id": "test-id-1",
            "question": "What is the capital of France?",
            "answer": "Paris",
            "topic": "Geography",
        },
        {
            "id": "test-id-2",
            "question": "What is 2 + 2?",
            "answer": "4",
            "topic": "Math",
        },
        {
            "id": "test-id-3",
            "question": "Who wrote Romeo and Juliet?",
            "answer": "William Shakespeare",
            # No topic provided
        },
    ]


@pytest.fixture
def anki_service():
    """AnkiExportService instance for testing"""
    return AnkiExportService()


class TestAnkiExportService:
    """Test cases for AnkiExportService"""

    @patch("urllib.request.urlopen")
    def test_export_flashcards_success(self, mock_urlopen, anki_service, sample_flashcards):
        """Test successful export of flashcards to Anki"""
        # Arrange
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"result": None, "error": None}).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Act
        result = anki_service.export_flashcards(sample_flashcards)

        # Assert
        assert "Successfully exported 3/3 cards" in result
        assert "FlashcardGen_" in result
        assert mock_urlopen.call_count == 4  # 1 createDeck + 3 addNote calls

    @patch("urllib.request.urlopen")
    def test_export_empty_flashcards(self, mock_urlopen, anki_service):
        """Test export with empty flashcard list"""
        # Act
        result = anki_service.export_flashcards([])

        # Assert
        assert result == "No flashcards to export"
        mock_urlopen.assert_not_called()

    @patch("urllib.request.urlopen")
    def test_anki_connection_error(self, mock_urlopen, anki_service, sample_flashcards):
        """Test handling of Anki connection errors"""
        # Arrange
        mock_urlopen.side_effect = Exception("Connection refused")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            anki_service.export_flashcards(sample_flashcards)

        assert "Failed to export to Anki" in str(exc_info.value)

    @patch("urllib.request.urlopen")
    def test_anki_api_error_response(self, mock_urlopen, anki_service, sample_flashcards):
        """Test handling of Anki API error responses"""
        # Arrange
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"result": None, "error": "Deck already exists"}).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            anki_service.export_flashcards(sample_flashcards)

        assert "Deck already exists" in str(exc_info.value)

    @patch("urllib.request.urlopen")
    def test_create_anki_note_with_topic(self, mock_urlopen, anki_service):
        """Test creating Anki note with topic tag"""
        # Arrange
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"result": None, "error": None}).encode("utf-8")
        mock_urlopen.return_value = mock_response

        card = {
            "question": "Test question?",
            "answer": "Test answer",
            "topic": "Test Topic",
        }

        # Act
        anki_service._create_anki_note("TestDeck", card)

        # Assert
        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args[0][0]
        request_data = json.loads(call_args.data.decode("utf-8"))

        assert request_data["action"] == "addNote"
        assert request_data["params"]["note"]["deckName"] == "TestDeck"
        assert request_data["params"]["note"]["fields"]["Front"] == "Test question?"
        assert request_data["params"]["note"]["fields"]["Back"] == "Test answer"
        assert "Test_Topic" in request_data["params"]["note"]["tags"]
        assert "FlashcardGen" in request_data["params"]["note"]["tags"]

    @patch("urllib.request.urlopen")
    def test_create_anki_note_without_topic(self, mock_urlopen, anki_service):
        """Test creating Anki note without topic tag"""
        # Arrange
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"result": None, "error": None}).encode("utf-8")
        mock_urlopen.return_value = mock_response

        card = {
            "question": "Test question?",
            "answer": "Test answer",
            # No topic
        }

        # Act
        anki_service._create_anki_note("TestDeck", card)

        # Assert
        call_args = mock_urlopen.call_args[0][0]
        request_data = json.loads(call_args.data.decode("utf-8"))

        # Should only have FlashcardGen tag
        assert request_data["params"]["note"]["tags"] == ["FlashcardGen"]

    def test_request_format(self, anki_service):
        """Test AnkiConnect request format"""
        # Act
        request = anki_service._request("testAction", param1="value1", param2="value2")

        # Assert
        assert request["action"] == "testAction"
        assert request["version"] == 6
        assert request["params"]["param1"] == "value1"
        assert request["params"]["param2"] == "value2"

    @patch("urllib.request.urlopen")
    def test_partial_failure_handling(self, mock_urlopen, anki_service, sample_flashcards):
        """Test handling when some cards fail to be added"""
        # Arrange - First call (createDeck) succeeds, second fails, third and fourth succeed
        responses = [
            json.dumps({"result": None, "error": None}),  # createDeck success
            json.dumps({"result": None, "error": "Invalid note"}),  # first card fails
            json.dumps({"result": None, "error": None}),  # second card success
            json.dumps({"result": None, "error": None}),  # third card success
        ]

        mock_response = MagicMock()
        mock_response.read.side_effect = [r.encode("utf-8") for r in responses]
        mock_urlopen.return_value = mock_response

        # Act
        with patch("builtins.print"):
            result = anki_service.export_flashcards(sample_flashcards)

        # Assert
        assert "Successfully exported 2/3 cards" in result


@pytest.mark.integration
class TestAnkiExportServiceIntegration:
    """Integration tests that require actual Anki running"""

    def test_real_anki_connection(self, anki_service):
        """Test actual connection to Anki (requires Anki + AnkiConnect running)"""
        pytest.skip("Integration test - requires Anki running with AnkiConnect")

        # Uncomment to test with real Anki:
        # try:
        #     version = anki_service._invoke("version")
        #     assert version == 6
        # except Exception as e:
        #     pytest.fail(f"Could not connect to Anki: {e}")
