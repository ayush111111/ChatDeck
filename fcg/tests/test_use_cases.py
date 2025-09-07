import pytest

from fcg.models import ChatMessage, ChatRole, DestinationType, FlashcardRequest
from fcg.use_cases.flashcard_use_case import FlashcardUseCase


@pytest.mark.asyncio
async def test_generate_and_save_flashcards_to_notion(container_with_mocks):
    """Test successful flashcard generation and saving to Notion"""
    # Arrange
    use_case = FlashcardUseCase(container_with_mocks)
    request = FlashcardRequest(
        conversation=[
            ChatMessage(role=ChatRole.USER, content="What is the capital of France?"),
            ChatMessage(
                role=ChatRole.ASSISTANT, content="The capital of France is Paris."
            ),
        ],
        destination=DestinationType.NOTION,
    )

    # Act
    response = await use_case.generate_and_save_flashcards(request)

    # Assert
    assert response.status == "success"
    assert "Notion" in response.message
    assert response.data["count"] == 2


@pytest.mark.asyncio
async def test_generate_and_export_flashcards_to_anki(container_with_mocks):
    """Test successful flashcard generation and export to Anki"""
    # Arrange
    use_case = FlashcardUseCase(container_with_mocks)
    request = FlashcardRequest(
        conversation=[
            ChatMessage(role=ChatRole.USER, content="What is the capital of France?"),
            ChatMessage(
                role=ChatRole.ASSISTANT, content="The capital of France is Paris."
            ),
        ],
        destination=DestinationType.ANKI,
    )

    # Act
    response = await use_case.generate_and_save_flashcards(request)

    # Assert
    assert response.status == "success"
    assert "Anki" in response.message
    assert response.data["file_path"] == "/tmp/test_flashcards.apkg"
    assert response.data["count"] == 2


@pytest.mark.asyncio
async def test_generate_flashcards_with_empty_conversation(
    container_with_mocks, mock_flashcard_generator
):
    """Test handling of empty flashcard generation"""
    # Arrange
    mock_flashcard_generator.generate_flashcards.return_value = []
    use_case = FlashcardUseCase(container_with_mocks)
    request = FlashcardRequest(
        conversation=[ChatMessage(role=ChatRole.USER, content="Hello")],
        destination=DestinationType.NOTION,
    )

    # Act
    response = await use_case.generate_and_save_flashcards(request)

    # Assert
    assert response.status == "error"
    assert "No flashcards could be generated" in response.message


@pytest.mark.asyncio
async def test_notion_save_failure(container_with_mocks, mock_repository):
    """Test handling of Notion save failure"""
    # Arrange
    mock_repository.save_flashcards.return_value = False
    use_case = FlashcardUseCase(container_with_mocks)
    request = FlashcardRequest(
        conversation=[ChatMessage(role=ChatRole.USER, content="Test content")],
        destination=DestinationType.NOTION,
    )

    # Act
    response = await use_case.generate_and_save_flashcards(request)

    # Assert
    assert response.status == "error"
    assert "Failed to save flashcards to Notion" in response.message
