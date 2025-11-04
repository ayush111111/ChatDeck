#!/usr/bin/env python3
"""
Test script to verify AnkiExportService works with real Anki
Requires Anki desktop running with AnkiConnect addon installed
"""

import pytest

from fcg.services.anki_export_service import AnkiExportService


@pytest.mark.anki
@pytest.mark.network
def test_anki_export_success():
    """Test AnkiExportService exports flashcards successfully"""
    # Sample flashcards
    sample_cards = [
        {
            "id": "test-1",
            "question": "What is the capital of France?",
            "answer": "Paris",
            "topic": "Geography",
        },
        {"id": "test-2", "question": "What is 2 + 2?", "answer": "4", "topic": "Math"},
    ]

    # Create service and export
    anki_service = AnkiExportService()
    result = anki_service.export_flashcards(sample_cards)

    # Assert export was successful
    assert result is not None, "Export result should not be None"
    assert result.get("success") is True, f"Export should succeed but got: {result}"
    assert "added" in result or "notes_added" in result, "Result should contain added notes count"


@pytest.mark.anki
@pytest.mark.network
def test_anki_export_empty_list():
    """Test AnkiExportService handles empty flashcard list"""
    anki_service = AnkiExportService()
    result = anki_service.export_flashcards([])

    # Should handle empty list gracefully
    assert result is not None, "Export result should not be None even for empty list"


@pytest.mark.anki
@pytest.mark.network
def test_anki_export_invalid_card():
    """Test AnkiExportService handles invalid flashcard data"""
    invalid_cards = [{"id": "test-invalid"}]  # Missing required fields

    anki_service = AnkiExportService()

    # Should either raise exception or return error result
    with pytest.raises(Exception):
        anki_service.export_flashcards(invalid_cards)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "anki"])
