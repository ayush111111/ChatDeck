"""
API communication service for syncing flashcards
"""

from typing import Any, Dict

import requests
from aqt import mw


def sync_flashcards(user_id: str, api_url: str, deck_name: str) -> Dict[str, Any]:
    """
    Fetch pending flashcards from API and add them to Anki

    Args:
        user_id: User's unique identifier
        api_url: Base API URL (e.g., http://localhost:8000)
        deck_name: Name of deck to add cards to

    Returns:
        Dict with success status and count of synced cards
    """
    try:
        # 1. Fetch pending flashcards from API
        response = requests.get(f"{api_url}/api/v1/flashcards/pending/{user_id}", timeout=10)
        response.raise_for_status()
        flashcards = response.json()

        if not flashcards:
            return {"success": True, "synced_count": 0}

        # 2. Get the note type (Basic is default)
        model = mw.col.models.by_name("Basic")
        if not model:
            return {"success": False, "error": "Basic note type not found. Please ensure you have the default note types."}

        # 3. Add each flashcard to Anki
        synced_ids = []
        for card_data in flashcards:
            try:
                # Get deck name from flashcard data, fallback to config default
                card_deck_name = card_data.get("deck_name", deck_name)
                deck_id = mw.col.decks.id(card_deck_name)

                # Create new note
                note = mw.col.newNote(model)
                note.note_type()["did"] = deck_id

                # Set fields
                note.fields[0] = card_data.get("front", "")  # Front field
                note.fields[1] = card_data.get("back", "")  # Back field

                # Add tags
                tags = card_data.get("tags", "")
                if tags:
                    note.tags = tags.split(",")

                # Add note to collection
                mw.col.addNote(note)
                synced_ids.append(card_data["id"])

            except Exception as e:
                print(f"Failed to add card {card_data.get('id')}: {str(e)}")
                continue

        # 5. Save changes to collection
        mw.col.save()

        # 6. Mark flashcards as synced in database
        if synced_ids:
            try:
                sync_response = requests.post(
                    f"{api_url}/api/v1/flashcards/sync", json={"user_id": user_id, "flashcard_ids": synced_ids}, timeout=10
                )
                sync_response.raise_for_status()
            except Exception as e:
                print(f"Failed to mark cards as synced: {str(e)}")
                # Continue anyway - cards are already in Anki

        return {"success": True, "synced_count": len(synced_ids)}

    except requests.exceptions.ConnectionError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}\n\nMake sure the server is running."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. Server may be slow or unresponsive."}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"API error: {e.response.status_code}\n\n{e.response.text}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def test_connection(api_url: str) -> Dict[str, Any]:
    """
    Test connection to API

    Returns:
        Dict with success status and message
    """
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        response.raise_for_status()
        return {"success": True, "message": "✅ Connected successfully!"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "message": f"❌ Cannot connect to {api_url}"}
    except Exception as e:
        return {"success": False, "message": f"❌ Error: {str(e)}"}
