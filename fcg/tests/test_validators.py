import pytest
from pydantic import ValidationError

from fcg.schemas import ChatMessage, ChatRole, DestinationType, Flashcard, TextFlashcardRequest


class TestChatMessageValidation:
    """Test ChatMessage validation"""

    def test_valid_message(self):
        """Test creating valid ChatMessage"""
        msg = ChatMessage(role=ChatRole.USER, content="Hello world")
        assert msg.role == ChatRole.USER
        assert msg.content == "Hello world"

    def test_whitespace_only_content(self):
        """Test that whitespace-only content is rejected"""
        with pytest.raises(ValidationError):
            ChatMessage(role=ChatRole.USER, content="   ")

    def test_empty_content(self):
        """Test that empty content is rejected"""
        with pytest.raises(ValidationError):
            ChatMessage(role=ChatRole.USER, content="")


class TestFlashcardValidation:
    """Test Flashcard validation"""

    def test_valid_flashcard(self):
        """Test creating valid flashcard"""
        card = Flashcard(question="What is Python?", answer="A programming language")
        assert card.question == "What is Python?"
        assert card.answer == "A programming language"

    def test_whitespace_only_question(self):
        """Test that whitespace-only question is rejected"""
        with pytest.raises(ValidationError):
            Flashcard(question="   ", answer="Some answer")

    def test_whitespace_only_answer(self):
        """Test that whitespace-only answer is rejected"""
        with pytest.raises(ValidationError):
            Flashcard(question="What is Python?", answer="   ")

    def test_empty_question(self):
        """Test that empty question is rejected"""
        with pytest.raises(ValidationError):
            Flashcard(question="", answer="Some answer")

    def test_empty_answer(self):
        """Test that empty answer is rejected"""
        with pytest.raises(ValidationError):
            Flashcard(question="What is Python?", answer="")


class TestTextFlashcardRequestValidation:
    """Test TextFlashcardRequest validation"""

    def test_valid_request(self):
        """Test creating valid TextFlashcardRequest"""
        text_request = TextFlashcardRequest(
            text="This is a sample text with more than 10 characters for testing",
            destination=DestinationType.ANKI,
            card_count=5,
            topic="Testing",
        )
        assert text_request.text == "This is a sample text with more than 10 characters for testing"
        assert text_request.destination == DestinationType.ANKI
        assert text_request.card_count == 5
        assert text_request.topic == "Testing"

    def test_text_too_short(self):
        """Test that text shorter than 10 characters is rejected"""
        with pytest.raises(ValidationError):
            TextFlashcardRequest(text="Short", destination=DestinationType.ANKI)

    def test_whitespace_only_text(self):
        """Test that whitespace-only text is rejected"""
        with pytest.raises(ValidationError):
            TextFlashcardRequest(text="                    ", destination=DestinationType.ANKI)

    def test_card_count_too_high(self):
        """Test that card count above 50 is rejected"""
        with pytest.raises(ValidationError):
            TextFlashcardRequest(
                text="This is a valid text with more than 10 characters",
                destination=DestinationType.ANKI,
                card_count=100,
            )

    def test_card_count_too_low(self):
        """Test that card count below 1 is rejected"""
        with pytest.raises(ValidationError):
            TextFlashcardRequest(
                text="This is a valid text with more than 10 characters",
                destination=DestinationType.ANKI,
                card_count=0,
            )

    def test_default_values(self):
        """Test that default values are applied correctly"""
        text_request = TextFlashcardRequest(
            text="This is a valid text with more than 10 characters", destination=DestinationType.ANKI
        )
        assert text_request.card_count == 5  # Default value
        assert text_request.topic is None  # Default value

    def test_notion_destination(self):
        """Test creating request with Notion destination"""
        text_request = TextFlashcardRequest(
            text="This is a valid text with more than 10 characters",
            destination=DestinationType.NOTION,
            card_count=3,
        )
        assert text_request.destination == DestinationType.NOTION
        assert text_request.card_count == 3
