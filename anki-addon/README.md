# Flashcard Sync - Anki Addon

Sync flashcards from your Chrome extension to Anki Desktop automatically!

## 📦 Installation

### Method 1: Manual Installation (Development)
1. Locate your Anki addons folder:
   - **Windows**: `C:\Users\[YourUsername]\AppData\Roaming\Anki2\addons21\`
   - **Mac**: `~/Library/Application Support/Anki2/addons21/`
   - **Linux**: `~/.local/share/Anki2/addons21/`

2. Create a new folder named `flashcard_sync`

3. Copy all files from this `anki-addon` directory into that folder:
   ```
   addons21/flashcard_sync/
   ├── __init__.py
   ├── manifest.json
   ├── config.json
   ├── config.md
   ├── sync_service.py
   └── gui.py
   ```

4. Restart Anki

### Method 2: ZIP Installation (Future)
1. Create a `.ankiaddon` file (it's just a renamed .zip)
2. In Anki: **Tools → Add-ons → Install from file**
3. Select the `.ankiaddon` file

## 🚀 Quick Start

1. **Get your User ID** from Chrome extension settings
2. **Configure addon**: Tools → Add-ons → Flashcard Sync → Config
3. **Sync flashcards**: Tools → 🔄 Sync Flashcards

See [config.md](config.md) for detailed setup instructions.

## ✨ Features

- ✅ One-click sync from cloud database
- ✅ Automatic deck creation
- ✅ Tag preservation
- ✅ Connection testing
- ✅ User-friendly settings dialog
- 🔄 Auto-sync (coming soon)

## 🏗️ Architecture

```
Chrome Extension → FastAPI (Cloud) → PostgreSQL Database
                                          ↓
                                    This Anki Addon
                                          ↓
                                    Anki Desktop
```

**Pull-based sync**: The addon fetches flashcards from the cloud, no localhost/NAT issues!

## 🛠️ Development

### Requirements
- Anki 2.1.50+
- Python 3.9+ (bundled with Anki)
- `requests` library (should be available in Anki)

### File Structure
```python
__init__.py         # Entry point, menu registration
manifest.json       # Addon metadata
config.json         # Default configuration
config.md          # User documentation
sync_service.py    # API communication
gui.py             # Settings dialog UI
```

### Key Components

**Sync Logic** (`sync_service.py`):
- Fetches pending flashcards via API
- Creates Anki notes using `mw.col.newNote()`
- Marks flashcards as synced

**UI** (`gui.py`):
- Settings dialog with Qt
- User ID configuration
- Connection testing

## 📝 API Endpoints Used

- `GET /api/v1/flashcards/pending/{user_id}` - Fetch pending flashcards
- `POST /api/v1/flashcards/sync` - Mark flashcards as synced
- `GET /health` - Test API connection

## 🐛 Debugging

Check Anki's debug console:
```python
# In Anki's debug console (Ctrl+Shift+;)
from flashcard_sync import sync_service
result = sync_service.test_connection("http://localhost:8000")
print(result)
```

## 📄 License

MIT License - feel free to modify and distribute!

## 🤝 Contributing

This is part of the larger Flashcard Generator project. See the main repo for contribution guidelines.
