"""
fcg.services.anki_export_service
================================
Module that provides AnkiExportService, an implementation of the ExportService
interface that exports flashcards to Anki using the AnkiConnect HTTP API.
Summary
-------
This module wraps calls to AnkiConnect (default at http://127.0.0.1:8765) to:
- create a uniquely named deck,
- add flashcards as Anki notes using the built-in "Basic" model,
- surface clear, high-level success/failure information to callers.
Public classes and functions
----------------------------
AnkiExportService(anki_connect_url: str = "http://127.0.0.1:8765")
    ExportService implementation that sends requests to AnkiConnect.
    - export_flashcards(flashcards: List[Dict[str, Any]]) -> str
        Export a list of flashcards to Anki. Each flashcard is a dict with at
        least "question" and "answer" keys. If "topic" is present, it is added
        as a tag (spaces replaced with underscores). Returns a human-readable
        summary string of how many cards were added and the deck name.
    - _create_anki_note(deck_name: str, card: Dict[str, Any])
        Internal helper that formats and sends a single addNote request.
    - _request(action, **params)
        Build the JSON payload including the AnkiConnect API version.
    - _invoke(action, **params)
        Send the JSON request to AnkiConnect, parse and validate the response,
        and return the "result" field or raise an appropriate exception.
Behavior and error handling
---------------------------
- A unique deck name is generated for each export using a short UUID prefix.
- Notes use the "Basic" model with fields "Front" and "Back".
- Tags: the provided topic (spaces -> underscores) and a constant "FlashcardGen"
  tag are attached to each note.
- Network errors or inability to reach Anki raise AnkiConnectionError.
- Unexpected or error-containing responses from AnkiConnect raise
  AnkiResponseError.
- Any other failures during export are wrapped and re-raised as ExportError.
Dependencies and requirements
-----------------------------
- Requires Anki to be running with the AnkiConnect plugin installed and enabled.
- Uses AnkiConnect API version 6 when building requests.
- Relies on exceptions and interfaces from the fcg package:
  AnkiConnectionError, AnkiResponseError, ExportError, and ExportService.
Example
-------
Basic usage:
    service = AnkiExportService()  # or provide a custom anki_connect_url
    flashcards = [
        {"question": "What is the capital of France?", "answer": "Paris", "topic": "Geography"},
        {"question": "2+2", "answer": "4"}
    ]
    result_summary = service.export_flashcards(flashcards)
    print(result_summary)
Notes
-----
- The module intentionally keeps network and response parsing logic internal
  and presents a simple, high-level interface to callers.
- The default AnkiConnect URL and API version can be adjusted if needed by
  modifying the constructor and _request implementation respectively.
"""

import json
import urllib.error
import urllib.request
import uuid
from typing import Any, Dict, List

from fcg.exceptions import AnkiConnectionError, AnkiResponseError, ExportError
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
                except (AnkiConnectionError, AnkiResponseError) as e:
                    logger.error(
                        "Failed to add card: %s, Error: %s",
                        card.get("question", "Unknown"),
                        e,
                    )

            return f"Successfully exported {cards_added}/{len(flashcards)}  \
        cards to Anki deck: {deck_name}"

        except Exception as e:
            raise ExportError(f"Failed to export to Anki: {e}") from e

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
        except urllib.error.URLError as e:
            raise AnkiConnectionError(
                "Cannot connect to Anki. Make sure Anki is running with AnkiConnect installed."
            ) from e

        if len(response) != 2:
            raise AnkiResponseError("Response has an unexpected number of fields")
        if "error" not in response:
            raise AnkiResponseError("Response is missing required error field")
        if "result" not in response:
            raise AnkiResponseError("Response is missing required result field")
        if response["error"] is not None:
            raise AnkiResponseError(response["error"])

        return response["result"]
