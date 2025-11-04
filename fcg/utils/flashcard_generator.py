import os
import uuid
from typing import List

import dspy
from dotenv import load_dotenv

from fcg.schemas import ChatMessage
from fcg.utils.dspy_flashcard_generator import Flashcard, TextToFlashcards

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Configure DSPy with OpenRouter
lm = dspy.LM(
    model=f"openrouter/{os.getenv('OPENROUTER_MODEL', 'qwen/qwen3-4b:free')}",
    api_base="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    max_tokens=int(os.getenv("OPENROUTER_MAX_TOKENS", "4096")),
)
dspy.configure(lm=lm)


async def generate_flashcards(conversation: List[ChatMessage]) -> List[dict]:
    """
    Generate flashcards from the conversation using DSPy
    """
    # Combine all messages into one content string
    content = "\n".join([msg.content for msg in conversation])

    try:
        # Initialize the DSPy flashcard generator
        flashcard_generator = TextToFlashcards()

        # Calculate approximate number of cards based on content length
        # Rule of thumb: ~1 card per 100 words
        word_count = len(content.split())
        num_cards = max(3, min(10, word_count // 100))  # Between 3-10 cards

        # Generate flashcards using DSPy
        generated_flashcards: List[Flashcard] = flashcard_generator(text_content=content, num_cards=num_cards)

        # Convert Pydantic models to dictionaries and add UUIDs
        flashcards_dict = []
        for card in generated_flashcards:
            card_dict = {
                "id": str(uuid.uuid4()),
                "question": card.question,
                "answer": card.answer,
                "explanation": card.explanation if hasattr(card, "explanation") else "",
                "topic": card.topic if hasattr(card, "topic") else "General",
            }
            flashcards_dict.append(card_dict)

        return flashcards_dict

    except Exception as e:
        raise RuntimeError(f"Error generating flashcards with DSPy: {e}") from e
