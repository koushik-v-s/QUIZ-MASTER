import json
import time
import logging
import re
from groq import Groq
from django.conf import settings
from rest_framework.exceptions import ValidationError

from core.exceptions import AIGenerationError

logger = logging.getLogger(__name__)

QUIZ_GENERATION_PROMPT = """
You are a quiz generation expert. Generate exactly {question_count} multiple choice questions about "{topic}" at {difficulty} difficulty level.

Rules:
- Each question must have exactly 4 choices
- Exactly 1 choice must be correct
- Include a brief explanation for the correct answer
- Questions should be clear, unambiguous, and educational
- Vary question styles (definition, application, analysis)

Respond ONLY with valid JSON in this exact format, with no markdown codeblocks, just the raw JSON:
{{
  "questions": [
    {{
      "question_text": "...",
      "explanation": "...",
      "points": 1,
      "choices": [
        {{"choice_text": "...", "is_correct": true}},
        {{"choice_text": "...", "is_correct": false}},
        {{"choice_text": "...", "is_correct": false}},
        {{"choice_text": "...", "is_correct": false}}
      ]
    }}
  ]
}}
"""

class GroqQuizGenerator:
    """Service class to handle AI quiz generation using Groq API."""

    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.error("GROQ_API_KEY is not set.")
            raise ValueError("GROQ_API_KEY is not configured.")

        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def generate(self, topic: str, question_count: int, difficulty: str) -> dict:
        """
        Generates quiz questions with retries and exponential backoff.
        """
        prompt = self._build_prompt(topic, question_count, difficulty)

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a quiz API that strictly returns pure JSON objects matching the requested schema."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=4000,
                    response_format={"type": "json_object"}
                )

                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Empty response from Grok AI API.")

                return self._parse_response(content, question_count)

            except Exception as e:
                logger.warning(f"AI Generation attempt {attempt + 1} failed: {str(e)}")
                if attempt == 2:
                    logger.error(f"All 3 AI generation attempts failed for topic '{topic}'.")
                    raise AIGenerationError(f"Failed to generate quiz via Grok: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff (1s, 2s)

    def _build_prompt(self, topic, count, difficulty) -> str:
        """Format the prompt template with arguments."""
        return QUIZ_GENERATION_PROMPT.format(
            question_count=count,
            topic=topic,
            difficulty=difficulty
        )

    def _parse_response(self, text: str, expected_count: int) -> dict:
        """Parse the JSON response and validate its structure."""
        # Strip markdown formatting if present (```json ... ```)
        cleaned_text = re.sub(r'```json\s*|\s*```', '', text, flags=re.IGNORECASE).strip()

        try:
            data = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {e}")

        # Sometimes the LLM wraps it in an outer object, sometimes not. Ensure `questions` exists.
        if 'questions' not in data or not isinstance(data['questions'], list):
            raise ValueError("Invalid JSON structure: missing 'questions' array.")

        questions = data['questions']
        if len(questions) != expected_count:
            logger.warning(f"AI returned {len(questions)} questions instead of expected {expected_count}.")

        # Deep validate questions
        for idx, q in enumerate(questions):
            if 'question_text' not in q or 'choices' not in q or 'explanation' not in q:
                raise ValueError(f"Question {idx+1} is missing required fields.")

            choices = q.get('choices', [])
            if len(choices) != 4:
                raise ValueError(f"Question {idx+1} does not have exactly 4 choices.")

            correct_count = sum(1 for c in choices if c.get('is_correct') is True)
            if correct_count != 1:
                raise ValueError(f"Question {idx+1} must have exactly 1 correct choice (found {correct_count}).")

        return data

