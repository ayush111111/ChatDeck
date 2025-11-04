# Flashcard Sync Addon - Setup Instructions

## 🚀 Quick Setup

### Step 1: Get Your User ID
1. Open your Chrome browser with the Flashcard extension installed
2. Click the extension icon or find the flashcard buttons on any webpage
3. Click the **⚙️ Settings** button
4. Click **📋 Copy** to copy your User ID

### Step 2: Configure Anki Addon
1. Open Anki Desktop
2. Go to: **Tools → Add-ons**
3. Select **Flashcard Sync** in the list
4. Click **Config** button (or right-click → Config)
5. Paste your User ID in the `user_id` field
6. Set your `api_url`:
   - Local development: `http://localhost:8000`
   - Cloud deployment: `https://your-api-url.com`
7. Click **OK** to save

### Step 3: Sync Flashcards
1. Go to: **Tools → 🔄 Sync Flashcards**
2. Wait for confirmation message
3. Your flashcards will appear in the specified deck!

---

## ⚙️ Configuration Options

```json
{
  "user_id": "",                    // REQUIRED: Your unique user ID from Chrome extension
  "api_url": "http://localhost:8000", // API endpoint URL
  "deck_name": "Default",           // Deck to add flashcards to
  "auto_sync": false,               // Future: Enable automatic syncing
  "sync_interval_minutes": 5        // Future: How often to auto-sync
}
```

---

## 🔧 Menu Items

- **Tools → 🔄 Sync Flashcards**: Manually sync pending flashcards
- **Tools → ⚙️ Flashcard Sync Settings**: Open settings dialog

---

## ❓ Troubleshooting

### "Please configure your User ID first!"
- You haven't set your User ID yet
- Follow Step 1 and 2 above

### "Cannot connect to API"
- Make sure your FastAPI server is running
- Check that `api_url` in config matches your server
- Test connection in settings dialog

### "No new flashcards to sync"
- You don't have any pending flashcards
- Generate some flashcards using the Chrome extension first

### Cards not appearing in correct deck
- Change `deck_name` in addon config
- The deck will be created if it doesn't exist

---

## 🎯 How It Works

1. **Chrome Extension** generates flashcards from text → saves to database
2. **Database** stores flashcards with `status="pending"` and your `user_id`
3. **Anki Addon** fetches pending flashcards for your `user_id`
4. **Addon** adds cards to Anki and marks them as `status="synced"`

---

## 🆘 Support

If you encounter issues:
1. Check the Anki console: **Tools → Add-ons → [Flashcard Sync] → View Files** → check `stderr.txt`
2. Verify your User ID matches between extension and addon
3. Test API connection in addon settings
4. Ensure FastAPI server is running and accessible
