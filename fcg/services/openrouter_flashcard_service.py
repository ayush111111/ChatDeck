import json
import re
import uuid
from typing import Any, Dict, List

import httpx

from fcg.config.settings import Settings
from fcg.interfaces.flashcard_generator_service import FlashcardGeneratorService
from fcg.models import ChatMessage


class OpenRouterFlashcardService(FlashcardGeneratorService):
    """OpenRouter implementation of flashcard generation service"""

    def __init__(self, settings: Settings):
        if not settings.openrouter_api_key:
            raise ValueError("OpenRouter API key is required")

        self.api_key = settings.openrouter_api_key
        self.api_url = settings.openrouter_url
        self.model = settings.openrouter_model

    async def generate_flashcards(self, conversation: List[ChatMessage]) -> List[dict]:
        """Generate flashcards from conversation using OpenRouter API"""
        try:
            content = self._combine_conversation(conversation)
            prompt = self._create_flashcard_prompt(content)

            llm_response = await self._call_llm_api(prompt)
            flashcards_content = self._extract_content_from_response(llm_response)

            # TODO: fix or remove
            # cleaned_json = self._clean_json_string(flashcards_content)
            parsed_json = json.loads(flashcards_content)

            # Ensure the JSON contains the "flashcards" field
            if "flashcards" not in parsed_json or not isinstance(parsed_json["flashcards"], list):
                raise ValueError("Invalid response format: 'flashcards' field is missing or not a list")

            generated_cards = parsed_json["flashcards"]

            # Add UUIDs and validate structure
            validated_cards = []
            for card in generated_cards:
                if self._validate_flashcard(card):
                    card["id"] = str(uuid.uuid4())
                    validated_cards.append(card)

            return validated_cards

        except Exception as e:
            raise RuntimeError(f"Error generating flashcards: {e}") from e

    def _combine_conversation(self, conversation: List[ChatMessage]) -> str:
        """Combine all conversation messages into a single content string"""
        return "\n".join([msg.content for msg in conversation])

    def _create_flashcard_prompt(self, content: str) -> str:
        """Create the prompt for flashcard generation"""
        return (
            f"""Return ONLY a JSON object with a single field called "flashcards" """
            f"""that contains a JSON array of flashcard objects.
Create flashcards from the following content.
Each object in the array must have these exact fields:
{{
    "question": "string with the question",
    "answer": "string with the answer"
    "topic": "string indicating the general subject area"
}}

Content to process: {content}

Technical requirements:
1. Response must be parseable by json.loads()
2. No markdown formatting
3. No explanation text
4. No backticks
5. No code block markers
6. Just the raw JSON object
7. The JSON object must have a single field called "flashcards"
8. Topic should be a single word or short phrase

Example format:
{{
    "flashcards": [
        {{
            "question": "What is the capital of France?",
            "answer": "Paris",
            "topic": "Geography"
        }}
    ]
}}"""
        )

    async def _call_llm_api(self, prompt: str) -> Dict[str, Any]:
        """Make API call to OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates flashcards from content.",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()

    def _extract_content_from_response(self, llm_response: Dict[str, Any]) -> str:
        """Extract content from LLM API response"""
        return llm_response["choices"][0]["message"]["content"]

    def _clean_json_string(self, text: str) -> str:
        """Clean common JSON formatting issues"""
        # Remove markdown code block markers
        text = re.sub(r"^```(?:json)?\n|```$", "", text, flags=re.MULTILINE)

        # Remove backticks from start and end
        text = re.sub(r"^`+|`+$", "", text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Remove explanation text before JSON
        text = re.sub(r"^.*?(?=[\[\{])", "", text, flags=re.DOTALL)

        # Remove trailing commas
        text = re.sub(r",\s*(?=[\}\]])", "", text)

        # Fix single quotes to double quotes
        text = re.sub(r"(?<!\\)'", '"', text)

        return text

    def _validate_flashcard(self, card: Dict[str, Any]) -> bool:
        """Validate that a flashcard has required fields"""
        required_fields = ["question", "answer", "topic"]
        return all(
            field in card and isinstance(card[field], str) and len(card[field].strip()) > 0 for field in required_fields
        )
