# Anki Addon Publishing Guide

This guide covers how to publish your Flashcard Sync addon to AnkiWeb and distribute it to users.

## 📋 Pre-Publishing Checklist

### 1. Complete Your Addon Metadata

Update `anki-addon/manifest.json`:
```json
{
    "name": "Flashcard Sync",
    "package": "flashcard_sync",
    "author": "Your Name", // ← UPDATE THIS
    "version": "1.0.0",
    "ankiweb_id": "", // ← Will be filled after AnkiWeb approval
    "min_point_version": 50,
    "max_point_version": 0,
    "homepage": "https://github.com/ayush111111/flashcardgen",
    "conflicts": [],
    "mod": 0
}
```

**Required Updates:**
- [ ] Change `author` to your real name or username
- [ ] Verify `version` number follows semantic versioning
- [ ] Update `homepage` URL if needed
- [ ] `ankiweb_id` will be provided by AnkiWeb after approval (leave empty for now)

### 2. Test Your Addon Thoroughly

- [ ] Test on Anki 2.1.50+
- [ ] Test on Windows, macOS, and Linux (if possible)
- [ ] Verify all features work as expected
- [ ] Check for error handling
- [ ] Test with different Anki profiles
- [ ] Ensure no conflicts with popular addons

### 3. Prepare Documentation

- [ ] Clear installation instructions
- [ ] Configuration guide
- [ ] Troubleshooting section
- [ ] Screenshots or GIFs showing usage
- [ ] API requirements documented

---

## 🚀 Publishing Methods

### Method 1: AnkiWeb (Official - Recommended)

AnkiWeb is the official Anki addon repository. This is the best way to reach users.

#### Step 1: Create AnkiWeb Account
1. Go to https://ankiweb.net/
2. Click "Sign Up" and create a free account
3. Verify your email address

#### Step 2: Share Your Addon

**For Initial Sharing (Before AnkiWeb ID):**
1. Login to https://ankiweb.net/
2. Go to "Add-ons" → "Share" or visit https://ankiweb.net/shared/upload
3. You'll need to:
   - Upload your addon package
   - Provide a description
   - Add screenshots
   - Specify compatibility information

**Important Notes:**
- First-time submissions may take 1-2 weeks for review
- AnkiWeb moderators check for code quality and security
- You'll receive an addon ID after approval
- Updates are typically reviewed faster

#### Step 3: Prepare Your Submission

**Required Information:**
- **Title**: "Flashcard Sync"
- **Short Description** (80 chars): "Sync flashcards from Chrome extension to Anki automatically"
- **Long Description**: Include features, installation, usage instructions
- **Category**: Select appropriate category (e.g., "Web Tools" or "Synchronization")
- **Tags**: flashcard, sync, chrome, automation
- **Minimum Anki Version**: 2.1.50
- **Screenshot**: Show the sync dialog and settings

**Example Long Description:**
```markdown
Flashcard Sync connects your Chrome extension flashcard collection directly to Anki Desktop.

FEATURES:
• One-click sync from cloud database
• Automatic deck creation
• Tag preservation
• User-friendly settings dialog
• Connection testing

REQUIREMENTS:
• Anki 2.1.50 or higher
• FlashcardGen backend service
• Chrome extension (optional)

INSTALLATION:
Install through Anki's addon manager or visit the homepage for manual installation.

CONFIGURATION:
Tools → Add-ons → Flashcard Sync → Config
Set your User ID and API endpoint.

See the homepage for complete documentation and troubleshooting.
```

#### Step 4: Package Your Addon

Use the provided packaging script:
```powershell
powershell -ExecutionPolicy Bypass -File package-addon.ps1
```

This creates:
- `flashcard-sync.ankiaddon` - Upload this to AnkiWeb
- `flashcard-sync.zip` - Backup/alternative distribution

#### Step 5: Submit for Review

1. Go to https://ankiweb.net/shared/upload
2. Fill out the addon information form
3. Upload `flashcard-sync.ankiaddon`
4. Submit for review
5. Wait for approval (check email for updates)

#### Step 6: After Approval

Once approved, you'll receive:
- **Addon ID**: A unique number (e.g., 123456789)
- **Addon URL**: https://ankiweb.net/shared/info/123456789

Update your `manifest.json`:
```json
{
    "ankiweb_id": "123456789"
}
```

Update your documentation with installation instructions:
```markdown
### Installation from AnkiWeb
1. Open Anki
2. Go to Tools → Add-ons → Get Add-ons
3. Enter code: 123456789
4. Click OK and restart Anki
```

---

### Method 2: GitHub Releases (Immediate Distribution)

While waiting for AnkiWeb approval, distribute via GitHub.

#### Step 1: Package Your Addon
```powershell
.\package-addon.ps1
```

#### Step 2: Create GitHub Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Fill out the release form:
   - **Tag**: `anki-addon-v1.0.0`
   - **Title**: "Flashcard Sync Anki Addon v1.0.0"
   - **Description**: Use content from RELEASE_NOTES.md
4. Upload both files:
   - `flashcard-sync.ankiaddon`
   - `flashcard-sync.zip`
5. Mark as "pre-release" if still in alpha/beta
6. Publish release

#### Step 3: Update README

Add installation instructions pointing to GitHub releases:
```markdown
## Installation

### From GitHub Releases
1. Download `flashcard-sync.ankiaddon` from [latest release](https://github.com/ayush111111/ChatDeck-/releases)
2. Open Anki → Tools → Add-ons → Install from file
3. Select the downloaded `.ankiaddon` file
4. Restart Anki
```

---

### Method 3: Direct Distribution

For testing or limited distribution.

#### Package the Addon
```powershell
.\package-addon.ps1
```

#### Share the File
- Email the `.ankiaddon` file
- Share via cloud storage (Google Drive, Dropbox)
- Host on your website

#### Installation Instructions for Users
```
1. Download flashcard-sync.ankiaddon
2. Open Anki
3. Tools → Add-ons → Install from file
4. Select the .ankiaddon file
5. Restart Anki
```

---

## 📦 Package Validation

Before publishing, verify your package:

### Check Package Contents
```powershell
# Extract and inspect
Expand-Archive flashcard-sync.ankiaddon -DestinationPath temp_check
dir temp_check
```

**Should contain:**
- `__init__.py`
- `manifest.json`
- `config.json`
- `config.md`
- `sync_service.py`
- `gui.py`

**Should NOT contain:**
- `__pycache__/` directories
- `.pyc` files
- `.DS_Store` or system files
- Test files
- Sensitive data or API keys

### Test Installation Locally
1. Install the packaged addon in fresh Anki profile
2. Verify all features work
3. Check for error messages in console
4. Test configuration dialog

---

## 🔄 Updating Your Addon

### Version Updates

Follow semantic versioning:
- **Major** (1.0.0 → 2.0.0): Breaking changes
- **Minor** (1.0.0 → 1.1.0): New features, backward compatible
- **Patch** (1.0.0 → 1.0.1): Bug fixes

### Update Process

1. **Update Version Number**
   ```json
   // manifest.json
   "version": "1.1.0"
   ```

2. **Update Release Notes**
   - Document changes
   - List new features
   - Note bug fixes
   - Mention any migration steps

3. **Test Thoroughly**
   - Test upgrade from previous version
   - Verify existing configurations still work
   - Test new features

4. **Package New Version**
   ```powershell
   .\package-addon.ps1
   ```

5. **Submit Update**
   - **AnkiWeb**: Upload new version through your account
   - **GitHub**: Create new release with updated tag
   - **Users**: Will be notified through Anki's addon manager

---

## 🎯 Marketing Your Addon

### AnkiWeb Listing Optimization

- Write clear, concise description
- Use bullet points for features
- Add quality screenshots
- Include usage examples
- Mention compatibility clearly
- Respond to user reviews promptly

### Promote Your Addon

- Share on Reddit r/Anki
- Post on Anki forums
- Twitter/X announcement
- Blog post with tutorial
- Video demo on YouTube
- Add badge to your README

### README Badge Example
```markdown
[![AnkiWeb](https://img.shields.io/badge/AnkiWeb-123456789-blue)](https://ankiweb.net/shared/info/123456789)
```

---

## 📊 Post-Publishing Tasks

### Monitor Usage
- Check download statistics on AnkiWeb
- Monitor GitHub stars/forks
- Watch for issues and bug reports

### User Support
- Respond to AnkiWeb reviews
- Answer GitHub issues promptly
- Update FAQ based on common questions
- Consider creating a support channel (Discord, GitHub Discussions)

### Maintenance
- Keep addon compatible with new Anki versions
- Fix reported bugs promptly
- Consider user feature requests
- Regular security updates if needed

---

## 🔒 Security Best Practices

### Before Publishing

- [ ] Remove any hardcoded API keys or secrets
- [ ] Validate all user inputs
- [ ] Use HTTPS for API connections
- [ ] Don't store sensitive data in plain text
- [ ] Add proper error handling
- [ ] Log errors safely (no sensitive data in logs)

### Code Review Checklist

- [ ] No obvious security vulnerabilities
- [ ] Proper exception handling
- [ ] Safe file operations
- [ ] Secure network requests
- [ ] No eval() or exec() on user input
- [ ] Sanitize configuration inputs

---

## 📝 Common Issues & Solutions

### "Addon doesn't appear in Anki"
- Check `__init__.py` is present
- Verify manifest.json syntax
- Look for Python errors in Anki console (Ctrl+Shift+;)

### "Config won't save"
- Ensure config.json has valid JSON syntax
- Check file permissions
- Verify config structure matches documentation

### "AnkiWeb submission rejected"
Common reasons:
- Code quality issues
- Security concerns
- Incomplete documentation
- Name conflict with existing addon
- Malformed package

### "Users can't install"
- Verify .ankiaddon file isn't corrupted
- Check minimum Anki version requirement
- Ensure all dependencies are listed
- Test installation on clean Anki install

---

## 📚 Additional Resources

### Official Documentation
- [Anki Add-on Development](https://addon-docs.ankiweb.net/)
- [AnkiWeb Shared Decks](https://ankiweb.net/shared/addons/)
- [Anki Manual](https://docs.ankiweb.net/)

### Community
- [Anki Forums](https://forums.ankiweb.net/)
- [Reddit r/Anki](https://www.reddit.com/r/Anki/)
- [Anki Discord Server](https://discord.gg/qjzcRTx)

### Development Tools
- [Anki PyQt Toolkit](https://github.com/ankitects/anki)
- [Addon Development Guide](https://addon-docs.ankiweb.net/intro.html)

---

## ✅ Quick Publishing Checklist

- [ ] Update author name in manifest.json
- [ ] Update version number
- [ ] Write clear documentation
- [ ] Test on multiple platforms
- [ ] Remove debug code and test files
- [ ] Create AnkiWeb account
- [ ] Package addon using script
- [ ] Prepare screenshots
- [ ] Write addon description
- [ ] Submit to AnkiWeb
- [ ] Create GitHub release
- [ ] Update README with installation instructions
- [ ] Announce on social media/forums

---

## 🎉 You're Ready to Publish!

Follow the steps above, and your addon will be available to the Anki community. Good luck! 🚀

**Questions?** Open an issue on GitHub or reach out to the Anki community forums.
