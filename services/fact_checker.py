import json
import re
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

from services.providers.gemini_client import GeminiClientError, create_completion as create_gemini_completion
from services.providers.groq_client import GroqClientError, create_completion as create_groq_completion


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "fact_check_prompt.txt"
ALLOWED_VERDICTS = {"RED": "FAKE", "YELLOW": "UNVERIFIED", "GREEN": "SAFE"}
REQUIRED_KEYS = {"verdict", "summary", "citation"}


class FactCheckError(RuntimeError):
    """Raised when a claim cannot be evaluated into the required output contract."""


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _extract_json(text: str) -> Dict[str, str]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise FactCheckError("Model response did not include JSON.")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise FactCheckError("Model JSON could not be parsed.") from exc


def _validate_two_sentences(summary: str) -> bool:
    segments = [s.strip() for s in re.split(r"(?<=[.!?])\s+", summary.strip()) if s.strip()]
    return len(segments) == 2


def _extract_url(citation: str) -> str:
    match = re.search(r"https?://\S+", citation)
    if match:
        return match.group(0).rstrip(").,;\"'")
    return ""


def _citation_title_from_url(url: str) -> str:
    host = urlparse(url).netloc.replace("www.", "").strip()
    if not host:
        return "Reputable Medical Source"
    return host


def evaluate_claim(claim_text: str) -> Dict[str, str]:
    if not claim_text.strip():
        raise FactCheckError("Claim text is empty.")

    prompt = _load_prompt()
    raw = ""
    try:
        raw = create_groq_completion(prompt, claim_text)
    except GroqClientError as groq_error:
        try:
            raw = create_gemini_completion(prompt, claim_text)
        except GeminiClientError as gemini_error:
            raise FactCheckError(
                f"Groq and Gemini failed: {groq_error} | {gemini_error}"
            ) from gemini_error

    parsed = _extract_json(raw)
    if set(parsed.keys()) != REQUIRED_KEYS:
        raise FactCheckError("Model JSON must contain exactly: verdict, summary, citation.")

    verdict = str(parsed.get("verdict", "")).upper().strip()
    if verdict not in ALLOWED_VERDICTS:
        raise FactCheckError("Verdict was missing or invalid.")

    label = ALLOWED_VERDICTS[verdict]
    summary = str(parsed.get("summary", "")).strip()
    if not summary or not _validate_two_sentences(summary):
        raise FactCheckError("Summary must be exactly two sentences.")

    citation_raw = str(parsed.get("citation", "")).strip()
    citation_url = _extract_url(citation_raw)
    if not citation_url.startswith("http"):
        raise FactCheckError("Citation URL is missing or invalid.")
    citation_title = _citation_title_from_url(citation_url)

    return {
        "verdict": verdict,
        "label": label,
        "summary": summary,
        "citation_title": citation_title,
        "citation_url": citation_url,
    }
