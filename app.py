from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from typing import Dict

import streamlit as st

from services.fact_checker import FactCheckError, evaluate_claim


st.set_page_config(page_title="Rumor-Stop", page_icon="🛑", layout="centered")

st.markdown(
    """
    <style>
    :root {
        --bg: #f5f7fb;
        --panel: #ffffff;
        --bubble-user: #d9fdd3;
        --bubble-ai: #ffffff;
        --text: #1f2937;
        --muted: #6b7280;
        --line: #e5e7eb;
        --red-bg: #ffe5e5;
        --red-fg: #9f1239;
        --yellow-bg: #fff7d6;
        --yellow-fg: #8a6d1d;
        --green-bg: #e6ffed;
        --green-fg: #166534;
        --shadow: rgba(17, 24, 39, 0.08);
    }

    [data-testid="stAppViewContainer"] {
        background: var(--bg);
        color: var(--text);
        font-family: "Segoe UI", Arial, sans-serif;
    }

    .stApp {
        max-width: 760px;
        margin: 0 auto;
        padding-bottom: 2rem;
    }

    .rumor-header {
        padding: 0.8rem 0 0.2rem;
    }

    .header-row {
        display: flex;
        align-items: center;
        gap: 0.65rem;
    }

    .logo-chip {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: linear-gradient(135deg, #e0f2fe, #dcfce7);
        border: 1px solid #d1d5db;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 1px 2px var(--shadow);
        font-size: 1.15rem;
        flex-shrink: 0;
    }

    .rumor-header h1 {
        font-size: clamp(2rem, 5vw, 2.6rem);
        line-height: 1.15;
        margin: 0;
        color: #111827;
        letter-spacing: -0.03em;
    }

    .rumor-subtitle {
        margin-top: 0.35rem;
        font-size: 0.95rem;
        color: #4b5563;
        font-weight: 600;
    }

    [data-testid="stChatMessage"] {
        padding: 0.2rem 0;
    }

    [data-testid="stChatMessageContent"] {
        border-radius: 16px;
        padding: 0.5rem 0.75rem;
        border: 1px solid var(--line);
        box-shadow: 0 1px 2px var(--shadow);
    }

    .verdict-card {
        padding: 0.85rem 0.9rem 0.7rem;
        border-radius: 14px;
        border-left: 5px solid transparent;
        margin-bottom: 0.9rem;
        box-shadow: inset 0 0 0 1px rgba(17, 24, 39, 0.04);
    }

    .verdict-badge {
        display: inline-block;
        padding: 0.5rem 0.8rem;
        border-radius: 999px;
        font-weight: 800;
        letter-spacing: 0.02em;
        margin-bottom: 0.8rem;
        font-size: 0.9rem;
        line-height: 1.2;
    }

    .verdict-summary {
        font-size: 1.02rem;
        line-height: 1.6;
        color: var(--text);
        margin: 0 0 0.75rem 0;
        font-weight: 500;
    }

    .citation-link {
        display: inline-block;
        font-size: 0.97rem;
        line-height: 1.5;
        margin-top: 0.2rem;
        word-break: break-word;
    }

    .welcome-panel {
        margin: 0.35rem 0 1rem;
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid var(--line);
        background: #ffffff;
        box-shadow: 0 1px 2px var(--shadow);
    }

    .welcome-icon {
        font-size: 1.5rem;
        margin-bottom: 0.35rem;
    }

    .welcome-title {
        font-size: 1.05rem;
        margin: 0 0 0.35rem;
        color: #111827;
        font-weight: 800;
    }

    .welcome-steps {
        margin: 0;
        padding-left: 1.15rem;
        color: #374151;
        line-height: 1.55;
        font-size: 0.96rem;
    }

    .welcome-steps li {
        margin-bottom: 0.28rem;
    }

    .stChatInput {
        border-top: 1px solid var(--line);
        padding-top: 0.8rem;
    }

    .stChatInput textarea {
        min-height: 54px;
        font-size: 1rem;
    }

    .stInfo {
        border-radius: 14px;
        border: 1px solid var(--line);
        background: #ffffff;
        box-shadow: none;
    }

    @media (max-width: 600px) {
        .header-row {
            gap: 0.5rem;
        }
        .logo-chip {
            width: 34px;
            height: 34px;
            border-radius: 10px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    (
        '<div class="rumor-header">'
        '<div class="header-row"><div class="logo-chip" aria-hidden="true">🛡️</div><h1>Rumor-Stop</h1></div>'
        '<div class="rumor-subtitle">WhatsApp &amp; Social Media Scam &amp; Health Fact-Checker</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []


def cleaned_claim_input(raw_claim: str | None) -> str:
    return (raw_claim or "").strip()


def append_user_message(content: str) -> None:
    st.session_state.messages.append({"role": "user", "content": content})


def append_assistant_result(result: Dict[str, str]) -> None:
    st.session_state.messages.append({"role": "assistant", **result, "content": result["summary"]})


def append_assistant_error() -> None:
    msg = "I could not verify this claim right now. Please try again in a moment."
    st.session_state.messages.append({"role": "assistant", "content": msg})


init_session_state()


def render_verdict_card(result: Dict[str, str]) -> None:
    palette = {
        "RED": {"bg": "var(--red-bg)", "fg": "var(--red-fg)", "emoji": "🔴", "label": "RED / FAKE"},
        "YELLOW": {"bg": "var(--yellow-bg)", "fg": "var(--yellow-fg)", "emoji": "🟡", "label": "YELLOW / UNVERIFIED"},
        "GREEN": {"bg": "var(--green-bg)", "fg": "var(--green-fg)", "emoji": "🟢", "label": "GREEN / SAFE"},
    }
    style = palette[result["verdict"]]
    badge = f"{style['emoji']} {style['label']}"

    st.markdown(
        (
            "<div class='verdict-card' style='background: {bg}; color: {fg}; border-left-color: {fg};'>"
            "<div class='verdict-badge' style='background: rgba(255,255,255,0.45); color: {fg};'>{badge}</div>"
            "<div class='verdict-summary'>{summary}</div>"
            "<div class='citation-link'>Source: <a href='{url}' target='_blank' rel='noopener noreferrer' style='color: {fg}; text-decoration: underline; font-weight: 700;'>{title}</a></div>"
            "</div>"
        ).format(
            bg=style["bg"],
            fg=style["fg"],
            badge=badge,
            summary=result["summary"],
            url=result["citation_url"],
            title=result["citation_title"],
        ),
        unsafe_allow_html=True,
    )


def process_claim(claim_text: str) -> None:
    append_user_message(claim_text)
    with st.chat_message("user"):
        st.write(claim_text)

    with st.chat_message("assistant"):
        with st.spinner("Checking the message..."):
            try:
                result = evaluate_claim(claim_text)
                render_verdict_card(result)
                append_assistant_result(result)
            except FactCheckError:
                msg = "I could not verify this claim right now. Please try again in a moment."
                st.error(msg)
                append_assistant_error()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "verdict" in message:
            render_verdict_card(message)
        else:
            st.write(message["content"])

if not st.session_state.messages:
    st.markdown(
        (
            "<div class='welcome-panel'>"
            "<div class='welcome-icon'>🔎</div>"
            "<div class='welcome-title'>Welcome to Rumor-Stop! 👋 Let's fact-check those WhatsApp forwards together.</div>"
            "<ol class='welcome-steps'>"
            "<li>Paste any forwarded message or rumor into the chat.</li>"
            "<li>We'll tell you if it's true (🟢), unverified (🟡), or a scam (🔴).</li>"
            "<li>You'll get a quick, easy-to-read summary with a real source.</li>"
            "</ol>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

claim = st.chat_input("Paste a forwarded WhatsApp message or health claim...")
if claim is not None:
    claim_text = cleaned_claim_input(claim)
    if not claim_text:
        st.warning("Please paste a message or health claim before submitting.")
    else:
        process_claim(claim_text)
