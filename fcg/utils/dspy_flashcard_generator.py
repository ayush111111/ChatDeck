"""
DSPy-based flashcard generation module.

This module uses DSPy signatures to generate flashcards from text content,
adapted from the experimental dspy-poc branch but generalized for any text input.
"""

from typing import List

import dspy
from pydantic import BaseModel


class Flashcard(BaseModel):
    """Structure for a complete flashcard with three components"""

    question: str  # Front of the card (question or concept)
    answer: str  # Back of the card (direct answer)
    explanation: str  # Detailed explanation with examples
    topic: str  # General subject area


class TextAnalysis(dspy.Signature):
    """Analyze text to identify key concepts and learning priorities"""

    text_content = dspy.InputField(desc="The text to analyze for flashcard generation")
    key_concepts = dspy.OutputField(desc="main concepts and important details extracted from the text")
    concept_hierarchy = dspy.OutputField(desc="main concepts vs supporting details")
    learning_priorities = dspy.OutputField(desc="concepts that are most important to remember")


class ConceptPrioritization(dspy.Signature):
    """Rank concepts by learning importance based on text analysis"""

    concepts = dspy.InputField(desc="extracted concepts from text")
    hierarchy = dspy.InputField(desc="concept hierarchy information")
    prioritized_concepts = dspy.OutputField(desc="concepts ranked by learning priority")


class FlashcardGeneration(dspy.Signature):
    """Generate flashcards following spaced repetition best practices.

    Each flashcard should have:
    1. Question: A concise concept title or focused question
    2. Answer: A brief, direct answer that addresses the question
    3. Explanation: A detailed explanation with examples to deepen understanding (4-5 sentences)
    4. Topic: A single word or short phrase indicating the general subject area

    Guidelines:
    - Create concise, simple, straightforward and distinct flashcards
    - Avoid repeating the question content in the answer
    - Treat information as factual and independent
    - Ensure each card covers a different concept without overlap
    - Make cards atomic - one concept per card
    """

    prioritized_concepts = dspy.InputField(desc="concepts ranked by importance")
    original_text = dspy.InputField(desc="the original text for context")
    num_cards = dspy.InputField(desc="approximate number of flashcards to generate")
    flashcards: List[Flashcard] = dspy.OutputField(
        desc="List of Flashcard models, each with question (concise concept/question), "
        "answer (direct answer), explanation (detailed with examples), and topic (subject area)"
    )


class DistinctnessChecker(dspy.Signature):
    """Ensure flashcards cover different concepts without overlap"""

    flashcards = dspy.InputField(desc="generated flashcards")
    distinct_flashcards = dspy.OutputField(desc="flashcards with overlapping content merged or removed")


class TextToFlashcards(dspy.Module):
    """
    DSPy Module for converting text into high-quality flashcards.

    This module implements a pipeline:
    1. Analyze the text to extract key concepts
    2. Prioritize concepts by learning importance
    3. Generate flashcards with question, answer, explanation, and topic
    """

    def __init__(self):
        super().__init__()
        # Core pipeline
        self.analyze = dspy.ChainOfThought(TextAnalysis)
        self.prioritize = dspy.ChainOfThought(ConceptPrioritization)
        self.generate = dspy.ChainOfThought(FlashcardGeneration)

    def forward(self, text_content: str, num_cards: int = 5) -> List[Flashcard]:
        """
        Generate flashcards from text content.

        Args:
            text_content: The text to convert into flashcards
            num_cards: Approximate number of flashcards to generate (default: 5)

        Returns:
            List of Flashcard objects with question, answer, explanation, and topic
        """
        # 1. Analyze the text
        analysis = self.analyze(text_content=text_content)

        # 2. Rank/prioritize concepts
        priorities = self.prioritize(
            concepts=analysis.key_concepts,
            hierarchy=analysis.concept_hierarchy,
        )

        # 3. Generate the flashcards
        generated = self.generate(
            prioritized_concepts=priorities.prioritized_concepts,
            original_text=text_content,
            num_cards=str(num_cards),
        )

        return generated.flashcards
