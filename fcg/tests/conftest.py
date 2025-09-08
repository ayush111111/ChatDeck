from unittest.mock import AsyncMock, Mock

import pytest

from fcg.config.container import ServiceContainer
from fcg.config.settings import Settings
from fcg.interfaces.export_service import ExportService
from fcg.interfaces.flashcard_generator_service import FlashcardGeneratorService
from fcg.interfaces.flashcard_repository import FlashcardRepository


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    return Settings(
        openrouter_api_key="test_key",
        openrouter_url="https://test.api.com",
        notion_api_key="test_notion_key",
        notion_page_id="test_page_id",
    )


@pytest.fixture
def mock_flashcard_generator():
    """Mock flashcard generator service"""
    mock = AsyncMock(spec=FlashcardGeneratorService)
    mock.generate_flashcards.return_value = [
        {
            "id": "test-id-1",
            "question": "Test question 1?",
            "answer": "Test answer 1",
            "topic": "Test",
        },
        {
            "id": "test-id-2",
            "question": "Test question 2?",
            "answer": "Test answer 2",
            "topic": "Test",
        },
    ]
    return mock


@pytest.fixture
def mock_repository():
    """Mock flashcard repository"""
    mock = AsyncMock(spec=FlashcardRepository)
    mock.save_flashcards.return_value = True
    mock.get_flashcards.return_value = []
    return mock


@pytest.fixture
def mock_export_service():
    """Mock export service"""
    mock = Mock(spec=ExportService)
    mock.export_flashcards.return_value = "/tmp/test_flashcards.apkg"
    return mock


@pytest.fixture
def container_with_mocks(mock_settings, mock_flashcard_generator, mock_repository, mock_export_service):
    """Service container with mocked dependencies"""
    container = ServiceContainer(mock_settings)
    container.register_instance(FlashcardGeneratorService, mock_flashcard_generator)
    container.register_instance(FlashcardRepository, mock_repository)
    container.register_instance(ExportService, mock_export_service)
    return container
