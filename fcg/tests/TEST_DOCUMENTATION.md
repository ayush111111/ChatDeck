# Test Documentation

## test_anki_connection.py

### Tests
- **test_anki_export_success** - Export flashcards to Anki successfully → Creates sample cards, calls export_flashcards(), asserts result is successful and contains added notes count
- **test_anki_export_empty_list** - Handle empty flashcard list → Calls export_flashcards([]), asserts result handles empty list gracefully
- **test_anki_export_invalid_card** - Reject invalid flashcard data → Sends card with missing required fields, asserts exception is raised

## test_anki_export_service.py
Tests the Anki export service functionality and flashcard export operations

## test_database_service.py

### TestDatabaseService
- **test_database_initialization** - Verify database tables are created → Checks table names in inspector
- **test_get_db_session** - Test database session creation → Creates session and verifies it's not None

### TestFlashcardService
- **test_create_batch** - Create flashcard batch with user_id and source_url → Calls create_batch(), verifies UUID returned, queries database for batch
- **test_add_flashcard** - Add flashcard with all fields → Calls add_flashcard() with full data, asserts all fields match
- **test_get_pending_flashcards** - Get pending flashcards for user → Creates 3 flashcards (2 for user, 1 synced), calls get_pending(), asserts only 1 returned
- **test_get_pending_flashcards_empty** - Get pending flashcards when none exist → Calls get_pending() for user with no data, asserts empty list
- **test_mark_flashcards_synced** - Mark flashcards as synced → Creates 3 flashcards, syncs 2 by ID, verifies status updated and synced_at set
- **test_mark_flashcard_failed** - Mark flashcard as failed → Creates flashcard, calls mark_flashcard_failed(), verifies status is 'failed'
- **test_get_flashcard_stats** - Get user flashcard statistics → Creates flashcards with different statuses, calls get_flashcard_stats(), asserts counts
- **test_get_flashcard_stats_empty** - Get stats for user with no flashcards → Calls get_flashcard_stats() for empty user, asserts all counts are 0
- **test_multiple_users_isolation** - Users' flashcards are isolated → Creates flashcards for 2 users, verifies each query returns only their data

## test_flashcard_api.py

### TestFlashcardAPI
- **test_create_flashcard** - POST /api/v1/flashcards/ creates single flashcard → Sends POST with flashcard data, asserts 200 response and correct data returned
- **test_create_flashcard_batch** - POST /api/v1/flashcards/batch creates multiple → Sends POST with array of flashcards, asserts all created with correct data
- **test_get_pending_flashcards** - GET /api/v1/flashcards/pending/{user_id} retrieves pending → Creates 2 flashcards, sends GET, asserts 2 returned with status='pending'
- **test_get_pending_flashcards_empty** - GET pending for user with none → Sends GET for user with no flashcards, asserts empty array
- **test_sync_flashcards** - POST /api/v1/flashcards/sync marks as synced → Creates flashcards, sends POST with IDs, asserts synced_count correct and pending is empty
- **test_sync_nonexistent_flashcards** - Sync with invalid IDs → Sends sync request with non-existent IDs, asserts synced_count=0
- **test_get_user_stats** - GET /api/v1/flashcards/stats/{user_id} returns stats → Creates 3 flashcards, syncs 1, fails 1, asserts correct counts
- **test_get_user_stats_empty** - GET stats for user with no data → Sends GET for empty user, asserts all counts are 0
- **test_mark_flashcard_failed** - DELETE /api/v1/flashcards/failed/{id} marks failed → Creates flashcard, sends DELETE, asserts status changed
- **test_mark_nonexistent_flashcard_failed** - Mark non-existent flashcard → Sends DELETE for invalid ID, asserts 404 response
- **test_user_isolation** - Users only see their own flashcards → Creates data for 2 users, queries each, asserts no data leakage
- **test_batch_with_source_url** - Batch creation tracks source URL → Creates batch with source_url, verifies it's stored
- **test_flashcard_with_optional_fields** - Create with difficulty and tags → Creates flashcard with optional fields, asserts they're saved

## test_flashcard_generator.py
Tests LLM-based flashcard generation using OpenRouter API

## test_integration.py

### TestCompleteFlashcardFlow
- **test_complete_user_workflow** - Full lifecycle: create→view→sync→fail→stats → Creates batch, checks pending, syncs some, marks one failed, verifies stats at each step
- **test_multi_user_isolation** - Multiple users don't see each other's data → Alice creates 1 flashcard, Bob creates 2, each queries pending, asserts only their own returned
- **test_error_handling_in_workflow** - Invalid requests handled gracefully → Syncs non-existent IDs (expects 0 synced), marks non-existent as failed (expects 404), checks empty user stats
- **test_health_endpoint** - GET /health returns correct status → Sends GET to /health, asserts 200 and status='healthy'
- **test_large_batch_creation** - Create and manage 50 flashcards → Creates batch of 50, verifies all pending, syncs 25, checks stats show 25 pending/25 synced

## test_use_cases.py
Tests business logic layer and use case orchestration

## test_validators.py

### TestChatMessageValidation
- **test_valid_message** - Create valid ChatMessage → Creates message with role and content, asserts fields match
- **test_whitespace_only_content** - Reject whitespace-only content → Attempts to create message with "   ", asserts ValidationError raised
- **test_empty_content** - Reject empty content → Attempts to create message with "", asserts ValidationError raised

### TestFlashcardValidation
- **test_valid_flashcard** - Create valid flashcard → Creates flashcard with question and answer, asserts fields match
- **test_whitespace_only_question** - Reject whitespace-only question → Attempts flashcard with "   " question, asserts ValidationError
- **test_whitespace_only_answer** - Reject whitespace-only answer → Attempts flashcard with "   " answer, asserts ValidationError
- **test_empty_question** - Reject empty question → Attempts flashcard with "" question, asserts ValidationError
- **test_empty_answer** - Reject empty answer → Attempts flashcard with "" answer, asserts ValidationError

### TestTextFlashcardRequestValidation
- **test_valid_request** - Create valid TextFlashcardRequest → Creates request with all fields, asserts values match
- **test_text_too_short** - Reject text shorter than 10 characters → Attempts request with "Short", asserts ValidationError
- **test_whitespace_only_text** - Reject whitespace-only text → Attempts request with whitespace text, asserts ValidationError
- **test_card_count_too_high** - Reject card count above 50 → Attempts request with card_count=100, asserts ValidationError
- **test_card_count_too_low** - Reject card count below 1 → Attempts request with card_count=0, asserts ValidationError
- **test_default_values** - Apply default values correctly → Creates request without optional fields, asserts card_count=5 and topic=None
- **test_notion_destination** - Create request with Notion destination → Creates request with DestinationType.NOTION, asserts destination set correctly
