"""
Highlight-to-flashcard generation module.

Implements the Memory Machines approach: given a reader's highlight and its
surrounding source context, generate a single high-quality spaced repetition
memory prompt that preserves the novelty of the passage.

Key principles from the research:
- Source context is required — the model needs the full passage, not just the highlight
- Good prompts re-encounter the novelty that made the detail worth marking
- Cloze-deletion beats Q&A for striking specific facts
- T0 (off-target) prompts are cheap to filter; T1/T2 boundary requires careful instructions
- Generating candidates and picking the best outperforms single-shot generation
"""

import os
import uuid
from typing import List

import dspy
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class HighlightCard(BaseModel):
    question: str
    answer: str
    topic: str


class HighlightIntent(dspy.Signature):
    """Identify what a reader wants to remember from a highlighted passage.

    Focus on the specific detail, fact, or insight that is most likely to be
    the reason the reader highlighted this text — not what the passage is
    generally about.
    """

    highlight: str = dspy.InputField(desc="The exact text the reader highlighted")
    source_context: str = dspy.InputField(desc="The surrounding passage providing context for the highlight")

    core_detail: str = dspy.OutputField(
        desc="The single most specific fact, number, mechanism, or insight the reader likely wants to retain"
    )
    novelty: str = dspy.OutputField(
        desc="What makes this detail surprising, counterintuitive, or striking — why did the reader stop here?"
    )


class HighlightCandidates(dspy.Signature):
    """Generate 3 candidate spaced repetition memory prompts for a highlight.

    GOOD prompts:
    - Re-encounter the novelty or specific detail (not generic summaries)
    - Are precise: only one answer is clearly correct months from now
    - Prefer cloze-deletion for striking specific facts:
        Q: "On Titan, gravity is so low that humans could fly simply by..."
        A: "...flapping their arms (in winged space suits)"
    - Are concise — readable in under 5 seconds

    BAD prompts:
    - Vague questions that accept many valid answers ("What is special about X?")
    - Generic trivia that strips away the novelty ("What planet has low gravity?")
    - Wordy phrasing with long formal qualifiers
    - Questions that give away the answer
    - Questions asking for a list when only one insight matters
    """

    highlight: str = dspy.InputField(desc="The exact text the reader highlighted")
    source_context: str = dspy.InputField(desc="The surrounding passage for context")
    core_detail: str = dspy.InputField(desc="The specific detail worth reinforcing")
    novelty: str = dspy.InputField(desc="What makes this detail striking or worth remembering")

    candidate_1_question: str = dspy.OutputField(desc="First candidate prompt question or cloze stem")
    candidate_1_answer: str = dspy.OutputField(desc="First candidate answer")
    candidate_2_question: str = dspy.OutputField(desc="Second candidate prompt question or cloze stem")
    candidate_2_answer: str = dspy.OutputField(desc="Second candidate answer")
    candidate_3_question: str = dspy.OutputField(desc="Third candidate prompt question or cloze stem")
    candidate_3_answer: str = dspy.OutputField(desc="Third candidate answer")
    topic: str = dspy.OutputField(desc="Single word or short phrase for the subject area")


class BestCandidate(dspy.Signature):
    """Select the best memory prompt from candidates.

    Choose the prompt most likely to reliably cue the same specific memory
    months from now. Prefer:
    1. Precise over vague (unique answer vs. multiple valid answers)
    2. Specific over generic (preserves novelty vs. strips it away)
    3. Concise over wordy

    Reject any prompt that:
    - Could be answered multiple ways
    - Asks about the wrong detail
    - Gives away the answer in the question
    """

    highlight: str = dspy.InputField(desc="The original highlight")
    candidate_1_question: str = dspy.InputField(desc="First candidate question")
    candidate_1_answer: str = dspy.InputField(desc="First candidate answer")
    candidate_2_question: str = dspy.InputField(desc="Second candidate question")
    candidate_2_answer: str = dspy.InputField(desc="Second candidate answer")
    candidate_3_question: str = dspy.InputField(desc="Third candidate question")
    candidate_3_answer: str = dspy.InputField(desc="Third candidate answer")

    best_number: str = dspy.OutputField(desc="Which candidate is best: '1', '2', or '3'")
    reasoning: str = dspy.OutputField(desc="One sentence explaining why this candidate will survive long-horizon review")


class HighlightToFlashcard(dspy.Module):
    """
    Three-stage pipeline: identify intent → generate candidates → pick best.

    Stage 1 — Intent: understand what specific detail the reader wants to retain
    Stage 2 — Candidates: generate 3 prompts with quality constraints
    Stage 3 — Selection: pick the one most likely to survive months of review
    """

    def __init__(self):
        super().__init__()
        self.identify_intent = dspy.ChainOfThought(HighlightIntent)
        self.generate_candidates = dspy.ChainOfThought(HighlightCandidates)
        self.select_best = dspy.ChainOfThought(BestCandidate)

    def forward(self, highlight: str, source_context: str) -> HighlightCard:
        intent = self.identify_intent(highlight=highlight, source_context=source_context)

        candidates = self.generate_candidates(
            highlight=highlight,
            source_context=source_context,
            core_detail=intent.core_detail,
            novelty=intent.novelty,
        )

        best = self.select_best(
            highlight=highlight,
            candidate_1_question=candidates.candidate_1_question,
            candidate_1_answer=candidates.candidate_1_answer,
            candidate_2_question=candidates.candidate_2_question,
            candidate_2_answer=candidates.candidate_2_answer,
            candidate_3_question=candidates.candidate_3_question,
            candidate_3_answer=candidates.candidate_3_answer,
        )

        # Map best_number back to the winning candidate
        num = best.best_number.strip()
        if num == "2":
            question = candidates.candidate_2_question
            answer = candidates.candidate_2_answer
        elif num == "3":
            question = candidates.candidate_3_question
            answer = candidates.candidate_3_answer
        else:
            question = candidates.candidate_1_question
            answer = candidates.candidate_1_answer

        return HighlightCard(question=question, answer=answer, topic=candidates.topic)


def _get_lm():
    return dspy.LM(
        model=f"openrouter/{os.getenv('OPENROUTER_MODEL', 'qwen/qwen3-4b:free')}",
        api_base="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        max_tokens=int(os.getenv("OPENROUTER_MAX_TOKENS", "4096")),
    )


async def generate_from_highlight(highlight: str, source_context: str) -> dict:
    """
    Generate a single high-quality memory prompt from a highlight + source context.

    Returns a flashcard dict with id, question, answer, and topic.
    """
    lm = _get_lm()
    with dspy.context(lm=lm):
        generator = HighlightToFlashcard()
        card = generator(highlight=highlight, source_context=source_context)

    return {
        "id": str(uuid.uuid4()),
        "question": card.question,
        "answer": card.answer,
        "topic": card.topic,
    }
