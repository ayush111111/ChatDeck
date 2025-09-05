#!/usr/bin/env python3
"""
Quick test script to verify AnkiExportService works with real Anki
"""

from fcg.services.anki_export_service import AnkiExportService


def test_anki_export():
    """Test AnkiExportService with sample flashcards"""

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

    try:
        result = anki_service.export_flashcards(sample_cards)
        print(f"✅ Success: {result}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("Testing AnkiExportService with real Anki...")
    success = test_anki_export()

    if success:
        print("\n🎉 AnkiConnect integration is working!")
        print("Check your Anki desktop - you should see a new deck with test cards.")
    else:
        print("\n❌ Something went wrong. Check that Anki is running with AnkiConnect.")
