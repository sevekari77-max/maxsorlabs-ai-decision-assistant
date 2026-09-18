import json
import time

from google import genai
from google.genai import types

from src.config import settings
from src.rag.retriever import retrieve


MODEL_NAME = "gemini-2.5-flash"


ALLOWED_ACTIONS = {
    "REQUEST_PHOTOS",
    "APPROVE_RETURN",
    "OPEN_SHIPPING_INVESTIGATION",
    "REPLACE_CORRECT_ITEM",
    "NEEDS_MORE_INFORMATION",
    "APPROVE_REFUND_OR_REPLACEMENT",
    "REQUEST_DEFECT_EVIDENCE",
    "APPROVE_REPLACEMENT",
    "REJECT_OUTSIDE_WINDOW",
    "WAIT_AND_TRACK",
    "OFFER_REPLACEMENT_OR_REFUND",
    "CANCEL_AND_REFUND",
    "CANNOT_CANCEL_AFTER_DISPATCH",
    "REJECT_OPENED_ITEM",
    "REJECT_FOOD_RETURN",
}


def _get_client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured in the environment."
        )

    return genai.Client(api_key=settings.gemini_api_key)


def _build_prompt(
    ticket_message: str,
    evidence: list[dict[str, str]],
) -> str:
    evidence_text = "\n\n".join(
        f"Source: {item['source']}\n"
        f"Evidence: {item['text']}"
        for item in evidence
    )

    return f"""
You are an AI customer-support decision assistant.

Use ONLY the supplied policy evidence to make the decision.
Do not invent policy rules.

Customer ticket:
{ticket_message}

Retrieved policy evidence:
{evidence_text}

Return ONLY valid JSON with exactly these fields:

{{
  "action": "one allowed action",
  "confidence": 0.0,
  "reason": "short explanation based on the evidence",
  "sources": ["source filename"]
}}

Allowed actions:
{sorted(ALLOWED_ACTIONS)}

Rules:
- confidence must be between 0 and 1.
- sources must contain the policy filenames actually used.
- If the ticket does not contain enough information to determine the correct action, use:
  NEEDS_MORE_INFORMATION
- Keep the reason concise and evidence-based.
"""


def _validate_decision(decision: dict) -> dict:
    required_fields = {
        "action",
        "confidence",
        "reason",
        "sources",
    }

    missing = required_fields - decision.keys()

    if missing:
        raise ValueError(
            f"Gemini response is missing fields: {sorted(missing)}"
        )

    if decision["action"] not in ALLOWED_ACTIONS:
        raise ValueError(
            f"Invalid action returned by Gemini: {decision['action']}"
        )

    confidence = float(decision["confidence"])

    if not 0 <= confidence <= 1:
        raise ValueError("Confidence must be between 0 and 1.")

    if not isinstance(decision["reason"], str) or not decision["reason"].strip():
        raise ValueError("Decision reason cannot be empty.")

    if not isinstance(decision["sources"], list):
        raise ValueError("Decision sources must be a list.")

    return {
        "action": decision["action"],
        "confidence": confidence,
        "reason": decision["reason"].strip(),
        "sources": [str(source) for source in decision["sources"]],
    }


def make_decision(ticket_message: str) -> dict:
    """
    Retrieve relevant policies and ask Gemini for a structured decision.
    """
    evidence = retrieve(ticket_message, top_k=3)

    if not evidence:
        return {
            "action": "NEEDS_MORE_INFORMATION",
            "confidence": 0.95,
            "reason": "No relevant policy evidence was retrieved.",
            "sources": [],
        }

    prompt = _build_prompt(ticket_message, evidence)

    client = _get_client()

    response = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                ),
            )
            break

        except Exception as exc:
            if attempt == 2:
                raise

            print(
                f"Gemini request failed "
                f"(attempt {attempt + 1}/3): {exc}"
            )

            time.sleep(2 * (attempt + 1))

    if response is None or not response.text:
        raise ValueError("Gemini returned an empty response.")

    try:
        decision = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Gemini returned invalid JSON."
        ) from exc

    return _validate_decision(decision)