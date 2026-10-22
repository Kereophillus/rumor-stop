import os
from typing import Any, Dict

import requests


GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


class GroqClientError(RuntimeError):
    """Raised when the Groq request cannot be completed."""


def create_completion(system_prompt: str, claim_text: str, model: str = "openai/gpt-oss-20b") -> str:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise GroqClientError("Missing GROQ_API_KEY environment variable.")

    payload: Dict[str, Any] = {
        "model": model,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": claim_text},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise GroqClientError(f"Groq API request failed: {exc}") from exc

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise GroqClientError("Unexpected Groq response format.") from exc
