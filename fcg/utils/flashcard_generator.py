import json
import os
import re
import uuid
from typing import List

import httpx
from dotenv import load_dotenv

from fcg.schemas import ChatMessage

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

    # 5. Extract only the JSON array/object part
    # Find the first [ or { and match until the corresponding closing bracket

    # Find the start of JSON
    start_match = re.search(r"[\[\{]", text)
    if not start_match:
        return text

    start_pos = start_match.start()
    bracket_count = 0
    brace_count = 0
    in_string = False
    escape_next = False
    end_pos = len(text)

    for i, char in enumerate(text[start_pos:], start_pos):
        if escape_next:
            escape_next = False
            continue

        if char == "\\":
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if not in_string:
            if char == "[":
                bracket_count += 1
            elif char == "]":
                bracket_count -= 1
            elif char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1

            # If we've closed all brackets and braces, we're done
            if bracket_count == 0 and brace_count == 0 and i > start_pos:
                end_pos = i + 1
                break

    text = text[start_pos:end_pos]

    # 6. Fix unescaped quotes in strings (like "Earth"s" -> "Earth's")
    # This is a complex fix - we need to find unescaped quotes within quoted strings
    def fix_quotes_in_strings(match):
        content = match.group(1)
        # Replace unescaped quotes with apostrophes
        content = re.sub(r'(?<!\\)"(?![\s]*[,}\]])', "'", content)
        return f'"{content}"'

    text = re.sub(r'"([^"]*?)"', fix_quotes_in_strings, text)

    # 7. Remove trailing commas
    text = re.sub(r",\s*(?=[\}\]])", "", text)

    # 8. Fix single quotes to double quotes (but not apostrophes within words)
    text = re.sub(r"(?<!\\)'(?=\s*[\{\[])", '"', text)

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
            "model": "qwen/qwen3-4b:free",
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

            # Ensure we have a list of dictionaries
            if isinstance(generated_cards, str):
                # Try to parse again if it's still a string
                generated_cards = json.loads(generated_cards)

            # If LLM returns a single object instead of array, wrap it in a list
            if isinstance(generated_cards, dict):
                generated_cards = [generated_cards]

            if not isinstance(generated_cards, list):
                raise ValueError(f"Expected a list of flashcards, got {type(generated_cards)}")

            # Add UUIDs to the flashcards
            for card in generated_cards:
                if not isinstance(card, dict):
                    raise ValueError(f"Expected flashcard to be a dict, got {type(card)}")
                card["id"] = str(uuid.uuid4())

            return generated_cards

    except Exception as e:
        raise RuntimeError(f"Error generating flashcards: {e}") from e
