# File Mapping and Purpose Analysis

## Root Level Files

### Essential Configuration
- **pyproject.toml** - Python project configuration, dependencies, build settings
- **docker-compose.yml** - Docker orchestration for local development
- **Dockerfile** - Container configuration for deployment
- **railway.toml** - Railway platform deployment configuration  
- **.gitignore** - Git ignore patterns
- **.flake8** - Python linting configuration
- **.pre-commit-config.yaml** - Git pre-commit hooks configuration
- **readme.md** - Main project documentation

### Documentation
- **PROJECT_GUIDE.md** - Project overview and guide
- **SUPABASE_SETUP.md** - Supabase integration documentation
- **TECHNICAL_DECISIONS.md** - Architecture and design decisions
- **ANKI_ADDON_PUBLISHING_GUIDE.md** - Guide for publishing Anki addon
- **DEPLOY.md** - Deployment instructions
- **todo.md** - Task tracking

### Scripts
- **package-addon.ps1** - PowerShell script to package Anki addon
- **__init__.py** - Root package initialization (POTENTIALLY UNUSED - needs review)

### Test Files (Root Level)
- **test_db_standalone.py** - Standalone database testing (DUPLICATE - redundant with fcg/tests/test_database_service.py)
- **simple_db_test.py** - Simple database test (MARKED FOR DELETION in git status)

### Deployment Scripts (DEPRECATED - deleted in working tree)
- **deploy-azure-free.sh** - Azure deployment script (UNUSED - modern deployment via Railway/Docker)
- **deploy-railway.sh** - Railway deployment script (UNUSED - Railway uses railway.toml)
- **deploy-supabase.sh** - Supabase deployment script (UNUSED - platform handles deployment)

### Build Artifacts
- **flashcard-sync.ankiaddon** - Packaged Anki addon (BUILD ARTIFACT - should be in .gitignore)
- **fcg.egg-info/** - Python package metadata (BUILD ARTIFACT - should be in .gitignore)
- **__pycache__/** - Python bytecode cache (BUILD ARTIFACT - should be in .gitignore)
- **htmlcov/** - Test coverage HTML reports (BUILD ARTIFACT - should be in .gitignore)

## FCG Package (fcg/)

### Core Application
- **fcg/main.py** - FastAPI application entry point, routes setup
- **fcg/schemas.py** - Pydantic models for API request/response
- **fcg/exceptions.py** - Custom exception definitions
- **fcg/__init__.py** - Package initialization

### Configuration (fcg/config/)
- **fcg/config/settings.py** - Application settings and environment variables
- **fcg/config/container.py** - Dependency injection container

### Interfaces (fcg/interfaces/)
- **fcg/interfaces/export_service.py** - Export service interface
- **fcg/interfaces/flashcard_generator_service.py** - Flashcard generator interface
- **fcg/interfaces/flashcard_repository.py** - Repository interface

### Models (fcg/models/)
- **fcg/models/__init__.py** - Models package initialization
- **fcg/models/api.py** - API models
- **fcg/models/flashcard.py** - Flashcard data models

### Repositories (fcg/repositories/)
- **fcg/repositories/notion_repository.py** - Notion API integration repository

### Routes (fcg/routes/)
- **fcg/routes/__init__.py** - Routes package initialization
- **fcg/routes/flashcard_api.py** - Database-backed flashcard API endpoints
- **fcg/routes/flashcard_generation.py** - Flashcard generation endpoints

### Services (fcg/services/)
- **fcg/services/anki_export_service.py** - Anki export functionality
- **fcg/services/database.py** - Database service and ORM models
- **fcg/services/openrouter_flashcard_service.py** - OpenRouter LLM integration

### Use Cases (fcg/use_cases/)
- **fcg/use_cases/flashcard_use_case.py** - Business logic orchestration

### Utilities (fcg/utils/)
- **fcg/utils/__init__.py** - Utils package initialization
- **fcg/utils/anki.py** - Anki-related utilities
- **fcg/utils/dspy_flashcard_generator.py** - DSPy-based flashcard generation
- **fcg/utils/flashcard_generator.py** - Flashcard generation utilities
- **fcg/utils/flashcard_count.py** - Flashcard counting utilities (NEW, untracked)
- **fcg/utils/logging.py** - Logging configuration
- **fcg/utils/notion.py** - Notion utilities

### Tests (fcg/tests/)
- **fcg/tests/__init__.py** - Tests package initialization
- **fcg/tests/conftest.py** - Pytest fixtures and configuration
- **fcg/tests/test_anki_connection.py** - Anki connection tests
- **fcg/tests/test_anki_export_service.py** - Anki export service tests
- **fcg/tests/test_database_service.py** - Database service tests
- **fcg/tests/test_flashcard_api.py** - API endpoint tests
- **fcg/tests/test_flashcard_generator.py** - Flashcard generator tests
- **fcg/tests/test_integration.py** - Integration tests
- **fcg/tests/test_use_cases.py** - Use case tests
- **fcg/tests/test_validators.py** - Validator tests

### Development (fcg/development/)
**STATUS: DEVELOPMENT/POC FILES - Consider moving to separate directory or removing**
- **fcg/development/conversation.pkl** - Pickled conversation data (POC artifact - BINARY FILE, should not be in git)
- **fcg/development/dspy_anki.ipynb** - Jupyter notebook for DSPy experimentation
- **fcg/development/dspy_poc.py** - DSPy proof of concept
- **fcg/development/format.html** - HTML format template
- **fcg/development/notion_poc.py** - Notion API proof of concept
- **fcg/development/notion_PoC/** - Notion POC directory

## Anki Addon (anki-addon/)
- **anki-addon/__init__.py** - Addon initialization and entry point
- **anki-addon/config.json** - Addon configuration defaults
- **anki-addon/config.md** - Configuration documentation
- **anki-addon/gui.py** - Anki addon GUI implementation
- **anki-addon/manifest.json** - Addon metadata
- **anki-addon/README.md** - Addon documentation
- **anki-addon/sync_service.py** - Sync service for pulling flashcards from API

## Chrome Extension (flash-card-extension/)
- **flash-card-extension/content_listener.js** - Listens for page content changes
- **flash-card-extension/content_script.js** - Content script for capturing conversations
- **flash-card-extension/manifest.json** - Extension manifest

## Static Files (static/)
- **static/text-flashcard-generator.html** - Standalone HTML for text-based flashcard generation

## GitHub Workflows (.github/workflows/)
- **.github/workflows/copilot-instructions.md** - GitHub Copilot instructions
- **.github/workflows/python-app.yml** - CI/CD workflow for Python app

## Data Directory (data/)
- **data/** - Runtime data directory for SQLite database (should be in .gitignore)

---

## Files to Remove

### 1. Deprecated Deployment Scripts
- ❌ **deploy-azure-free.sh** - Already deleted, Azure deployment deprecated
- ❌ **deploy-railway.sh** - Already deleted, replaced by railway.toml
- ❌ **deploy-supabase.sh** - Already deleted, Supabase deployment deprecated
- ❌ **simple_db_test.py** - Already deleted, redundant test file

### 2. Build Artifacts (should be in .gitignore)
- ❌ **flashcard-sync.ankiaddon** - Generated file, should not be tracked
- ❌ **fcg.egg-info/** - Generated package metadata
- ❌ **htmlcov/** - Generated coverage reports
- ❌ **__pycache__/** directories - Python bytecode

### 3. Development/POC Files
- ❌ **fcg/development/conversation.pkl** - Binary POC artifact
- ⚠️ **fcg/development/notion_poc.py** - Consider removing if Notion integration is complete
- ⚠️ **fcg/development/dspy_poc.py** - Consider removing if DSPy integration is complete
- ⚠️ **fcg/development/notion_PoC/** - Review and potentially remove

### 4. Potentially Redundant Files
- ⚠️ **test_db_standalone.py** - Appears to duplicate functionality in fcg/tests/test_database_service.py
- ⚠️ **__init__.py** (root level) - Likely unnecessary, review usage

### 5. Untracked Files to Review
- ⚠️ **fcg/utils/flashcard_count.py** - New file, needs to be added or removed
- ⚠️ **ANKI_ADDON_PUBLISHING_GUIDE.md** - New file, needs to be added
- ⚠️ **DEPLOY.md** - New file, needs to be added
- ⚠️ **railway.toml** - New file, needs to be added

## Recommended Actions

1. **Update .gitignore** to exclude:
   - `*.ankiaddon`
   - `*.egg-info/`
   - `htmlcov/`
   - `__pycache__/`
   - `data/`
   - `*.pkl`
   - `fcg/development/`

2. **Remove deprecated deployment scripts** (already marked for deletion)

3. **Clean up development directory**:
   - Remove `.pkl` files
   - Move POC scripts to a separate `examples/` or `docs/` directory if needed for reference
   - Or remove entirely if no longer needed

4. **Add untracked files** that should be in the repo:
   - Add `ANKI_ADDON_PUBLISHING_GUIDE.md`
   - Add `DEPLOY.md`
   - Add `railway.toml`
   - Add `fcg/utils/flashcard_count.py`

5. **Review and consolidate test files**:
   - Compare `test_db_standalone.py` with `fcg/tests/test_database_service.py`
   - Remove redundant test file

6. **Check root `__init__.py`** - verify if it's needed or can be removed
