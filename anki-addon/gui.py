"""
GUI components for settings dialog
"""

from aqt import mw
from aqt.qt import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)
from aqt.utils import showInfo

from .sync_service import test_connection


class SettingsDialog(QDialog):
    """
    Settings dialog for configuring the addon
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Flashcard Sync Settings")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout()

        # User ID section
        layout.addWidget(QLabel("<h3>User ID Configuration</h3>"))
        layout.addWidget(QLabel("Copy this from your Chrome extension settings:"))

        user_id_layout = QHBoxLayout()
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Paste your User ID here...")
        user_id_layout.addWidget(self.user_id_input)
        layout.addLayout(user_id_layout)

        # API URL section
        layout.addWidget(QLabel("<h3>API Configuration</h3>"))
        layout.addWidget(QLabel("API URL:"))

        api_layout = QHBoxLayout()
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("https://chatdeck-dev.up.railway.app")
        api_layout.addWidget(self.api_url_input)

        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self.on_test_connection)
        api_layout.addWidget(test_btn)
        layout.addLayout(api_layout)

        # Deck name section
        layout.addWidget(QLabel("<h3>Anki Configuration</h3>"))
        layout.addWidget(QLabel("Default Deck Name:"))
        self.deck_input = QLineEdit()
        self.deck_input.setPlaceholderText("Default")
        layout.addWidget(self.deck_input)

        # Auto-sync section (future feature)
        auto_sync_layout = QHBoxLayout()
        self.auto_sync_checkbox = QCheckBox("Enable auto-sync")
        self.auto_sync_checkbox.setEnabled(False)  # Disabled for now
        auto_sync_layout.addWidget(self.auto_sync_checkbox)

        auto_sync_layout.addWidget(QLabel("Interval (minutes):"))
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(60)
        self.interval_spinbox.setValue(5)
        self.interval_spinbox.setEnabled(False)  # Disabled for now
        auto_sync_layout.addWidget(self.interval_spinbox)
        auto_sync_layout.addStretch()
        layout.addLayout(auto_sync_layout)

        # Instructions
        layout.addWidget(QLabel("<hr>"))
        layout.addWidget(QLabel("<b>Setup Instructions:</b>"))
        instructions = QLabel(
            "1. Open your Chrome extension<br>"
            "2. Click ⚙️ Settings button<br>"
            "3. Copy your User ID<br>"
            "4. Paste it above and click Save<br>"
            "5. Use Tools → Sync Flashcards to sync!"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.on_save)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_config(self):
        """Load current configuration"""
        config = mw.addonManager.getConfig(__name__)

        self.user_id_input.setText(config.get("user_id", ""))
        self.api_url_input.setText(config.get("api_url", "https://chatdeck-dev.up.railway.app"))
        self.deck_input.setText(config.get("deck_name", "Default"))
        self.auto_sync_checkbox.setChecked(config.get("auto_sync", False))
        self.interval_spinbox.setValue(config.get("sync_interval_minutes", 5))

    def on_test_connection(self):
        """Test API connection"""
        api_url = self.api_url_input.text().strip()
        if not api_url:
            showInfo("Please enter an API URL first.")
            return

        result = test_connection(api_url)
        showInfo(result["message"])

    def on_save(self):
        """Save configuration"""
        user_id = self.user_id_input.text().strip()
        api_url = self.api_url_input.text().strip()
        deck_name = self.deck_input.text().strip()

        if not user_id:
            showInfo("Please enter your User ID.")
            return

        if not api_url:
            showInfo("Please enter an API URL.")
            return

        if not deck_name:
            deck_name = "Default"

        # Save config
        config = {
            "user_id": user_id,
            "api_url": api_url,
            "deck_name": deck_name,
            "auto_sync": self.auto_sync_checkbox.isChecked(),
            "sync_interval_minutes": self.interval_spinbox.value(),
        }

        mw.addonManager.writeConfig(__name__, config)
        showInfo("✅ Settings saved!")
        self.accept()


def show_settings_dialog():
    """Show the settings dialog"""
    dialog = SettingsDialog(mw)
    dialog.exec()
