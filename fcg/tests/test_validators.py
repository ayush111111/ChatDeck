from pydantic import ValidationError

from fcg.models import (
    ChatMessage,
    ChatRole,
    DestinationType,
    Flashcard,
    TextFlashcardRequest,
)

# Test valid case
try:
    msg = ChatMessage(role=ChatRole.USER, content="Hello world")
    print("✓ Valid message created successfully")
except Exception as e:
    print(f"✗ Error creating valid message: {e}")

# Test whitespace-only content
try:
    msg = ChatMessage(role=ChatRole.USER, content="   ")
    print("✗ ERROR: Whitespace message should have failed")
except ValidationError:
    print("✓ Whitespace validation working correctly")

# Test flashcard validators
try:
    card = Flashcard(question="What is Python?", answer="A programming language")
    print("✓ Valid flashcard created successfully")
except Exception as e:
    print(f"✗ Error creating valid flashcard: {e}")

# Test flashcard with whitespace-only answer
try:
    card = Flashcard(question="What is Python?", answer="   ")
    print("✗ ERROR: Whitespace answer should have failed")
except ValidationError:
    print("✓ Flashcard whitespace validation working correctly")

# Test TextFlashcardRequest validation
try:
    text_request = TextFlashcardRequest(
        text="This is a sample text with more than 10 characters for testing",
        destination=DestinationType.ANKI,
        card_count=5,
        topic="Testing",
    )
    print("✓ Valid TextFlashcardRequest created successfully")
except Exception as e:
    print(f"✗ Error creating valid TextFlashcardRequest: {e}")

# Test TextFlashcardRequest with text too short
try:
    text_request = TextFlashcardRequest(text="Short", destination=DestinationType.ANKI)
    print("✗ ERROR: Short text should have failed")
except ValidationError:
    print("✓ TextFlashcardRequest text length validation working correctly")

# Test TextFlashcardRequest with whitespace-only text
try:
    text_request = TextFlashcardRequest(text="                    ", destination=DestinationType.ANKI)
    print("✗ ERROR: Whitespace text should have failed")
except ValidationError:
    print("✓ TextFlashcardRequest whitespace validation working correctly")

# Test TextFlashcardRequest with invalid card count
try:
    text_request = TextFlashcardRequest(
        text="This is a valid text with more than 10 characters",
        destination=DestinationType.ANKI,
        card_count=100,  # Exceeds maximum of 50
    )
    print("✗ ERROR: Card count too high should have failed")
except ValidationError:
    print("✓ TextFlashcardRequest card count validation working correctly")

# Test TextFlashcardRequest with default values
try:
    text_request = TextFlashcardRequest(
        text="This is a valid text with more than 10 characters", destination=DestinationType.ANKI
    )
    assert text_request.card_count == 5  # Default value
    assert text_request.topic is None  # Default value
    print("✓ TextFlashcardRequest default values working correctly")
except Exception as e:
    print(f"✗ Error with TextFlashcardRequest defaults: {e}")

print("All validator tests completed!")
