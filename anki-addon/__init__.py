"""
Flashcard Sync Addon for Anki
Syncs flashcards from cloud database to Anki Desktop
"""

from aqt import gui_hooks, mw
from aqt.qt import QAction
from aqt.utils import showInfo, tooltip

from .gui import show_settings_dialog
from .sync_service import sync_flashcards


def on_sync_flashcards():
    """
    Main sync action - called when user clicks sync button
    """
    try:
        config = mw.addonManager.getConfig(__name__)

        # Validate config
        user_id = config.get("user_id")
        if not user_id:
            showInfo(
                "Please configure your User ID first!\n\n"
                "Go to: Tools → Add-ons → Flashcard Sync → Config\n\n"
                "Copy your User ID from the Chrome extension settings."
            )
            return

        # Show progress
        tooltip("Syncing flashcards...", parent=mw)

        # Perform sync
        result = sync_flashcards(user_id, config.get("api_url"), config.get("deck_name"))

        # Show result
        if result["success"]:
            count = result["synced_count"]
            if count > 0:
                tooltip(f"✅ Synced {count} flashcard{'s' if count != 1 else ''}!", parent=mw)
            else:
                tooltip("No new flashcards to sync.", parent=mw)
        else:
            showInfo(f"❌ Sync failed:\n\n{result['error']}")

    except Exception as e:
        showInfo(f"❌ Error during sync:\n\n{str(e)}")


def on_show_settings():
    """
    Show settings dialog
    """
    show_settings_dialog()


def setup_menu():
    """
    Add menu items to Anki
    """
    # Add to Tools menu
    sync_action = QAction("🔄 Sync Flashcards", mw)
    sync_action.triggered.connect(on_sync_flashcards)
    mw.form.menuTools.addAction(sync_action)

    settings_action = QAction("⚙️ Flashcard Sync Settings", mw)
    settings_action.triggered.connect(on_show_settings)
    mw.form.menuTools.addAction(settings_action)


# Initialize addon when Anki starts
gui_hooks.main_window_did_init.append(setup_menu)
