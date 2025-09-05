import json
import urllib.request
import urllib.error
import uuid
from typing import List, Dict, Any
from fcg.interfaces.export_service import ExportService
from fcg.utils.logging import logger


class AnkiExportService(ExportService):
    """Anki implementation of export service using AnkiConnect"""

    def __init__(self, anki_connect_url: str = "http://127.0.0.1:8765"):
        self.anki_connect_url = anki_connect_url

    def export_flashcards(self, flashcards: List[Dict[str, Any]]) -> str:
        """Export flashcards to Anki via AnkiConnect"""
        if not flashcards:
            return "No flashcards to export"

        # Create a unique deck name
        deck_name = f"FlashcardGen_{uuid.uuid4().hex[:8]}"

        try:
            # Create deck
            self._invoke("createDeck", deck=deck_name)

            # Add each flashcard
            cards_added = 0
            for card in flashcards:
                try:
                    self._create_anki_note(deck_name, card)
                    cards_added += 1
                except Exception as e:
                    logger.error(
                        f"Failed to add card: {card.get('question', 'Unknown')}, Error: {e}"
                    )

            return f"Successfully exported {cards_added}/{len(flashcards)} cards to Anki deck: {deck_name}"

        except Exception as e:
            raise Exception(f"Failed to export to Anki: {str(e)}")

    def _create_anki_note(self, deck_name: str, card: Dict[str, Any]):
        """Create a single note in Anki"""
        note = {
            "deckName": deck_name,
            "modelName": "Basic",  # Using basic card type
            "fields": {
                "Front": card.get("question", ""),
                "Back": card.get("answer", ""),
            },
            "tags": [],
        }

        # Add topic as tag if provided
        topic = card.get("topic")
        if topic:
            note["tags"].append(topic.replace(" ", "_"))

        # Add general tag
        note["tags"].append("FlashcardGen")

        self._invoke("addNote", note=note)

    def _request(self, action, **params):
        """Create AnkiConnect request"""
        return {"action": action, "params": params, "version": 6}

    def _invoke(self, action, **params):
        """Send request to AnkiConnect and return response"""
        request_json = json.dumps(self._request(action, **params)).encode("utf-8")

        try:
            response = json.load(
                urllib.request.urlopen(
                    urllib.request.Request(self.anki_connect_url, request_json)
                )
            )
        except urllib.error.URLError:
            raise Exception(
                "Cannot connect to Anki. Make sure Anki is running with AnkiConnect installed."
            )

        if len(response) != 2:
            raise Exception("Response has an unexpected number of fields")
        if "error" not in response:
            raise Exception("Response is missing required error field")
        if "result" not in response:
            raise Exception("Response is missing required result field")
        if response["error"] is not None:
            raise Exception(response["error"])

        return response["result"]
