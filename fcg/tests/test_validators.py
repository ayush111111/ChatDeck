from pydantic import ValidationError

from fcg.models import ChatMessage, ChatRole, Flashcard

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

print("All validator tests completed!")
