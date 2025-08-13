import os
import uuid
from typing import List
import httpx
from dotenv import load_dotenv
import json

import re

json.dumps(["foo", {"bar": ("baz", None, 1.0, 2)}])
from fcg.models import ChatMessage

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = os.getenv("OPENROUTER_URL")


def clean_json_string(text):
    """Clean common JSON formatting issues"""

    # 1. Remove markdown code block markers (```json and ```)
    text = re.sub(r"^```(?:json)?\n|```$", "", text, flags=re.MULTILINE)

    # 2. Remove backticks from start and end
    text = re.sub(r"^`+|`+$", "", text)

    # 3. Remove leading/trailing whitespace and newlines
    text = text.strip()

    # 4. Remove explanation text before JSON (anything before first [ or {)
    text = re.sub(r"^.*?(?=[\[\{])", "", text, flags=re.DOTALL)

    # 5. Remove trailing commas
    text = re.sub(r",\s*(?=[\}\]])", "", text)

    # 6. Fix single quotes to double quotes (but not escaped ones)
    text = re.sub(r"(?<!\\)'", '"', text)

    return text


def create_flashcard_prompt(content: str) -> str:
    return """Return ONLY a JSON array of flashcard objects.
    Create flashcards from the following content.
    Each object in the array must have these exact fields:
    {{
        "question": "string with the question",
        "answer": "string with the answer",
        "topic": "string indicating the general subject area"
    }}
    
    Content to process: {content}
    
    Technical requirements:
    1. Response must be parseable by json.loads()
    2. No markdown formatting
    3. No explanation text
    4. No backticks
    5. No code block markers
    6. Just the raw JSON array
    7. Topic should be a single word or short phrase
    
    Example format:
    [
        {{
            "question": "What is the capital of France?",
            "answer": "Paris",
            "topic": "Geography"
        }}
    ]""".format(
        content=content
    )


async def generate_flashcards(conversation: List[ChatMessage]) -> List[dict]:
    """
    Generate flashcards from the conversation using an LLM through OpenRouter
    """
    # Combine all messages into one content string
    content = "\n".join([msg.content for msg in conversation])

    # Prepare the API request
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = json.dumps(
        {
            "model": "mistralai/mistral-small-3.2-24b-instruct:free",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates flashcards from content.",
                },
                {"role": "user", "content": create_flashcard_prompt(content)},
            ],
        }
    )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OPENROUTER_URL, headers=headers, data=data)
            response.raise_for_status()

            # Parse the LLM response
            llm_response = response.json()
            flashcards_content = llm_response["choices"][0]["message"]["content"]

            cleaned_json = clean_json_string(flashcards_content)
            generated_cards = json.loads(cleaned_json)

            # Add UUIDs to the flashcards
            for card in generated_cards:
                card["id"] = str(uuid.uuid4())

            return generated_cards

    except Exception as e:
        raise RuntimeError(f"Error generating flashcards: {e}") from e
