import json
import logging
from flask import current_app
from openai import OpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI business operations assistant. Analyze the provided content and return a JSON object with these fields:

{
  "summary": "A concise 2-3 sentence summary of the content",
  "category": "One of: invoice, receipt, note, task, contract, report, other",
  "extracted_data": {
    "dates": ["list of important dates found"],
    "costs": [{"description": "what the cost is for", "amount": 0.00}],
    "tasks": ["list of tasks or action items found"],
    "deadlines": ["list of deadlines found"],
    "people": ["names of people mentioned"],
    "key_terms": ["important terms or references"]
  },
  "action_items": [
    {"action": "Specific action to take", "priority": "high|medium|low", "due": "date or null"}
  ],
  "total_cost": 0.00,
  "due_date": "earliest deadline in ISO format or null"
}

Return ONLY valid JSON. No markdown, no explanation."""


class AIAnalysisError(Exception):
    """Raised when AI analysis fails."""
    pass


def analyze_content(content: str) -> dict:
    """Send content to OpenAI for analysis and return structured data."""
    api_key = current_app.config["OPENAI_API_KEY"]
    if not api_key:
        logger.warning("OpenAI API key not configured – returning mock analysis")
        return _mock_analysis(content)

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content[:15000]},  # limit token usage
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
            timeout=30,
        )
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        logger.error("OpenAI API error: %s", e)
        raise AIAnalysisError(f"AI analysis failed: {type(e).__name__}") from e


def _mock_analysis(content: str) -> dict:
    """Fallback mock analysis when OpenAI is unavailable."""
    word_count = len(content.split())
    return {
        "summary": f"Document contains {word_count} words. AI analysis unavailable – configure OPENAI_API_KEY for full analysis.",
        "category": "other",
        "extracted_data": {
            "dates": [],
            "costs": [],
            "tasks": [],
            "deadlines": [],
            "people": [],
            "key_terms": [],
        },
        "action_items": [
            {
                "action": "Review this document manually",
                "priority": "medium",
                "due": None,
            }
        ],
        "total_cost": None,
        "due_date": None,
    }
