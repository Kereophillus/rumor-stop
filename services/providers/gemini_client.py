import os
from typing import Any, Dict

import requests


GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"


class GeminiClientError(RuntimeError):
    """Raised when the Gemini request cannot be completed."""


def create_completion(system_prompt: str, claim_text: str, model: str = "gemini-3.8-flash") -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise GeminiClientError("Missing GEMINI_API_KEY environment variable.")

    payload: Dict[str, Any] = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_prompt}\n\nUser claim: {claim_text}"},
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }
    headers = {"X-goog-api-key": api_key}

    try:
        response = requests.post(
            f"{GEMINI_ENDPOINT}?key={api_key}",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise GeminiClientError(f"Gemini API request failed: {exc}") from exc

    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise GeminiClientError("Unexpected Gemini response format.") from exc
