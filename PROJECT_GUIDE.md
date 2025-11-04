# 📋 **Flashcard Generator - Complete Implementation Guide**

## 🎯 **Project Overview**
A web-to-Anki flashcard generator that allows users to select text on any webpage, generate flashcards using AI, and automatically sync them to Anki Desktop through a streamlined cloud-based architecture.

---

## 🏗️ **System Architecture**

### **High-Level Flow**
1. **User selects text** on any webpage
2. **Chrome Extension** captures text and sends to cloud API
3. **FastAPI backend** processes text with OpenRouter LLM
4. **Generated flashcards** saved to PostgreSQL database with user_id
5. **Custom Anki Addon** fetches pending flashcards from API
6. **Direct Anki integration** adds cards using internal APIs (no AnkiConnect)
7. **Sync confirmation** marks cards as processed in database

### **Key Design Decisions**
- **No AnkiConnect required** - Custom addon uses Anki's internal APIs directly
- **Cloud-first storage** - PostgreSQL database for persistence and multi-device sync
- **User isolation** - Simple user_id system for data separation without complex auth
- **Free tier focused** - All components use free/freemium services
- **Pull-based sync** - Local addon pulls from cloud (solves localhost/NAT issues)

---

## 🛠️ **Technology Stack**

### **Backend Services**
| Component          | Technology       | Service           | Cost      | Notes                    |
| ------------------ | ---------------- | ----------------- | --------- | ------------------------ |
| **API Framework**  | FastAPI          | Self-hosted       | Free      | Python web framework     |
| **Database**       | PostgreSQL       | Supabase/Railway  | Free tier | 500MB free on Supabase   |
| **LLM Processing** | OpenRouter API   | Various providers | Free tier | qwen/qwen3-4b:free model |
| **Hosting**        | Docker Container | Railway.app       | Free tier | 512MB RAM, 1GB storage   |

### **Client Applications**
| Component            | Technology         | Platform       | Distribution       |
| -------------------- | ------------------ | -------------- | ------------------ |
| **Web Extension**    | Vanilla JavaScript | Chrome/Firefox | Chrome Web Store   |
| **Anki Integration** | Python             | Anki Desktop   | .ankiaddon package |

---

## 📁 **Current Project Structure**

```
flashcardgen/
├── fcg/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── models.py                 # Original Pydantic models
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py           # Environment configuration
│   │   └── container.py          # Service container
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── flashcard.py          # SQLAlchemy models
│   │   └── api.py                # API request/response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database.py           # Database connection & operations
│   │   ├── anki_export_service.py
│   │   └── openrouter_flashcard_service.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── flashcard_api.py      # CRUD endpoints
│   │   └── flashcard_generation.py # LLM generation endpoints
│   ├── interfaces/               # Abstract interfaces
│   ├── repositories/             # Data access layer
│   ├── use_cases/               # Business logic
│   └── tests/                   # Test suite
│       ├── test_database_service.py
│       ├── test_flashcard_api.py
│       └── test_integration.py
├── Dockerfile                   # Container configuration
├── docker-compose.yml          # Local development
├── pyproject.toml              # Python dependencies
├── SUPABASE_SETUP.md          # Database setup guide
└── simple_db_test.py          # Standalone test script
```

---

## 🚀 **Implementation Status**

### **✅ Phase 1: Database & API Foundation (COMPLETED)**
- [x] SQLAlchemy models for Flashcard and FlashcardBatch
- [x] DatabaseService with auto-detection (SQLite/PostgreSQL)
- [x] FlashcardService for all CRUD operations
- [x] User isolation system with user_id
- [x] Comprehensive API endpoints:
  - `POST /api/v1/flashcards/` - Create single flashcard
  - `POST /api/v1/flashcards/batch` - Create multiple flashcards
  - `GET /api/v1/flashcards/pending/{user_id}` - Get pending flashcards
  - `POST /api/v1/flashcards/sync` - Mark flashcards as synced
  - `GET /api/v1/flashcards/stats/{user_id}` - Get user statistics
  - `DELETE /api/v1/flashcards/failed/{id}` - Mark flashcard as failed
- [x] Full test suite (unit, API, integration tests)
- [x] Supabase PostgreSQL configuration
- [x] Docker containerization

### **🚧 Phase 2: Cloud Deployment (IN PROGRESS)**
- [x] Dockerfile created
- [x] Environment configuration
- [ ] Railway.app deployment setup
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Production environment variables
- [ ] SSL/HTTPS configuration

### **🔄 Phase 3: Chrome Extension (NEXT)**
**Goal**: Browser extension for text selection and flashcard generation

**Planned Features**:
- Text selection on any webpage
- Floating "Create Flashcards" button
- User ID generation and persistence
- Integration with FastAPI endpoints
- OpenRouter LLM integration for flashcard generation
- Success/error notifications

**Estimated Files**:
```
chrome-extension/
├── manifest.json          # Extension configuration
├── content-script.js      # Page interaction logic
├── popup.html            # Extension popup UI
├── popup.js              # Popup functionality
├── background.js         # Background processing
└── icons/               # Extension icons
    ├── icon-16.png
    ├── icon-48.png
    └── icon-128.png
```

### **🔄 Phase 4: Custom Anki Addon (NEXT)**
**Goal**: Replace AnkiConnect dependency with direct Anki integration

**Planned Features**:
- Direct Anki API integration (no HTTP calls)
- User configuration for user_id and API URL
- Manual and automatic sync options
- Deck management and card creation
- Status feedback and error handling

**Estimated Files**:
```
anki-addon/
├── __init__.py           # Main addon logic
├── manifest.json         # Addon metadata
├── config.json          # Default configuration
├── config.md            # User setup instructions
├── sync_service.py      # API communication
├── anki_integration.py  # Direct Anki operations
└── gui/
    ├── sync_dialog.py   # Sync interface
    └── settings_dialog.py # Configuration UI
```

---

## 🔧 **API Endpoints Reference**

### **Flashcard Management**
```http
# Create single flashcard
POST /api/v1/flashcards/
Content-Type: application/json
{
    "user_id": "user_12345",
    "front": "What is FastAPI?",
    "back": "A modern Python web framework",
    "deck_name": "Programming",
    "tags": "python,web",
    "difficulty": "medium"
}

# Create multiple flashcards
POST /api/v1/flashcards/batch
Content-Type: application/json
{
    "user_id": "user_12345",
    "source_url": "https://example.com",
    "flashcards": [...]
}

# Get pending flashcards for sync
GET /api/v1/flashcards/pending/{user_id}

# Mark flashcards as synced
POST /api/v1/flashcards/sync
Content-Type: application/json
{
    "user_id": "user_12345",
    "flashcard_ids": [1, 2, 3]
}

# Get user statistics
GET /api/v1/flashcards/stats/{user_id}
```

### **LLM Generation** (Planned)
```http
# Generate flashcards from text
POST /api/v1/flashcards/generate
Content-Type: application/json
{
    "user_id": "user_12345",
    "text": "Selected webpage content...",
    "source_url": "https://example.com",
    "deck_name": "Web Learning",
    "card_count": 5
}
```

---

## 🗄️ **Database Schema**

### **Flashcard Table**
```sql
CREATE TABLE flashcards (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    source_url VARCHAR(500),
    source_text TEXT,
    deck_name VARCHAR(255) DEFAULT 'Default',
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    synced_at TIMESTAMP,
    tags VARCHAR(500),
    difficulty VARCHAR(20),
    INDEX idx_user_status (user_id, status),
    INDEX idx_created_at (created_at)
);
```

### **FlashcardBatch Table**
```sql
CREATE TABLE flashcard_batches (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    batch_id VARCHAR(100) NOT NULL UNIQUE,
    source_url VARCHAR(500),
    total_cards INTEGER DEFAULT 0,
    processed_cards INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'processing',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    INDEX idx_user_batch (user_id, batch_id)
);
```

---

## ⚙️ **Configuration & Environment**

### **Environment Variables**
```bash
# Database Configuration
DATABASE_URL=sqlite:///./flashcards.db  # Local development
POSTGRES_HOST=db.abc123.supabase.co     # Production
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=postgres

# OpenRouter LLM
OPENROUTER_API_KEY=your-api-key
OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions
OPENROUTER_MODEL=qwen/qwen3-4b:free

# Application Settings
CORS_ORIGINS=*
HOST=0.0.0.0
PORT=8000
```

### **Docker Configuration**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .
COPY . .
EXPOSE 8000
CMD ["uvicorn", "fcg.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 💰 **Cost Analysis**

### **Free Tier Limits**
| Service        | Resource         | Free Limit      | Usage Estimate             |
| -------------- | ---------------- | --------------- | -------------------------- |
| **Supabase**   | Database storage | 500MB           | ~1M flashcards             |
| **Supabase**   | API requests     | 50,000/month    | ~1,600/day                 |
| **Railway**    | Build time       | 500 hours/month | Sufficient                 |
| **Railway**    | RAM              | 512MB           | Adequate for FastAPI       |
| **OpenRouter** | API calls        | Model-dependent | Some free models available |

### **Scaling Thresholds**
- **10,000+ users**: Consider paid PostgreSQL plan
- **100,000+ API calls/month**: Consider Redis caching
- **Heavy LLM usage**: Evaluate OpenRouter pricing tiers

---

## 🧪 **Testing Strategy**

### **Implemented Tests**
```python
# Unit Tests
test_database_service.py     # Database operations
test_flashcard_service.py    # Business logic
test_models.py              # Data model validation

# API Tests
test_flashcard_api.py       # HTTP endpoint testing
test_authentication.py      # User isolation testing

# Integration Tests
test_integration.py         # End-to-end workflows
test_user_scenarios.py      # Multi-user scenarios
```

### **Test Coverage Areas**
- ✅ Database CRUD operations
- ✅ User isolation and data privacy
- ✅ API request/response validation
- ✅ Error handling and edge cases
- ✅ Bulk operations and performance
- 🔄 LLM integration (planned)
- 🔄 Chrome extension (planned)
- 🔄 Anki addon integration (planned)

---

## 🚀 **Deployment Guide**

### **Local Development**
```bash
# Setup
git clone https://github.com/yourusername/flashcardgen
cd flashcardgen
pip install -e .

# Database setup
python simple_db_test.py

# Run server
uvicorn fcg.main:app --reload

# Run tests
python -m pytest fcg/tests/ -v
```

### **Production Deployment** (Planned)
```bash
# Railway.app deployment
railway login
railway init
railway add postgresql
railway deploy

# Environment variables
railway variables set POSTGRES_HOST=xxx
railway variables set OPENROUTER_API_KEY=xxx
```

---

## 📋 **Development Roadmap**

### **Immediate Priorities**
1. **Complete cloud deployment** - Railway.app setup with PostgreSQL
2. **Integrate LLM generation** - Connect OpenRouter to /generate endpoint
3. **Build Chrome extension MVP** - Basic text selection and API integration
4. **Create Anki addon foundation** - Direct Anki API integration

### **Next Phase**
1. **End-to-end testing** - Complete user workflow validation
2. **Error handling improvements** - Robust failure scenarios
3. **Performance optimization** - API response times and caching
4. **User documentation** - Installation and usage guides

### **Future Enhancements**
1. **Advanced flashcard templates** - Cloze deletion, image cards
2. **Batch processing with Celery** - If performance issues arise
3. **Mobile app integration** - Cross-platform synchronization
4. **Advanced analytics** - User learning statistics

---

## 🔒 **Security & Privacy**

### **Current Approach**
- **No authentication required** - Simple user_id system
- **Data isolation** - Users can only access their own flashcards
- **No sensitive data storage** - Only flashcard content and metadata
- **HTTPS enforcement** - All API communication encrypted

### **Privacy Considerations**
- **User data** limited to flashcard content and usage patterns
- **No personal information** collected beyond user-generated content
- **Local storage** of user_id in browser/Anki addon
- **Cloud storage** minimal and purpose-specific

---

## 📚 **Documentation Status**

### **Completed Documentation**
- ✅ This implementation guide
- ✅ Database setup guide (SUPABASE_SETUP.md)
- ✅ API endpoint documentation
- ✅ Test case explanations
- ✅ Architecture decisions

### **Pending Documentation**
- 🔄 Chrome extension installation guide
- 🔄 Anki addon installation guide
- 🔄 User troubleshooting guide
- 🔄 Developer contribution guide
- 🔄 API rate limiting and usage policies

---

## 🎯 **Success Metrics**

### **Technical Milestones**
- [ ] API deployed and accessible via HTTPS
- [ ] Database storing and retrieving flashcards correctly
- [ ] Chrome extension generating flashcards from selected text
- [ ] Anki addon successfully syncing cards to Anki Desktop
- [ ] Complete end-to-end user workflow functional

### **User Experience Goals**
- [ ] < 5 second flashcard generation time
- [ ] One-click installation for all components
- [ ] Reliable sync with < 1% failure rate
- [ ] Clear error messages and recovery options
- [ ] Seamless cross-device synchronization

---

This comprehensive guide reflects the current state of the project and provides a clear roadmap for completing the flashcard generator system. The foundation is solid with a robust database layer and API structure - now ready for cloud deployment and client application development.
