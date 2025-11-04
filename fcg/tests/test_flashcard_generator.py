import pytest

from fcg.schemas import ChatMessage
from fcg.utils.flashcard_generator import generate_flashcards


@pytest.mark.llm
@pytest.mark.asyncio
async def test_flashcard_generation():
    # Arrange
    test_conversation = [
        ChatMessage(
            role="user",
            content="The earth revolves around the sun in an elliptical orbit.",
        ),
        ChatMessage(
            role="assistant",
            content="This is called the heliocentric model, proposed by Copernicus.",
        ),
    ]

    # Act
    flashcards = await generate_flashcards(test_conversation)

    # Assert
    assert isinstance(flashcards, list)
    assert len(flashcards) > 0

    for card in flashcards:
        assert "id" in card
        assert "question" in card
        assert "answer" in card
        assert isinstance(card["id"], str)
        assert isinstance(card["question"], str)
        assert isinstance(card["answer"], str)
        assert len(card["id"]) > 0
        assert len(card["question"]) > 0
        assert len(card["answer"]) > 0
