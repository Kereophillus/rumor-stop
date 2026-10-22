from typing import Dict, List

import streamlit as st

from services.fact_checker import FactCheckError, evaluate_claim


st.set_page_config(page_title="Rumor-Stop", page_icon="🛑", layout="centered")
st.title("Rumor-Stop")
st.caption("Paste a forwarded health claim to check if it is safe, fake, or unverified.")

if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, str]] = []


def render_verdict_card(result: Dict[str, str]) -> None:
    palette = {
        "RED": {"bg": "#ffe5e5", "fg": "#9f1239", "emoji": "🔴"},
        "YELLOW": {"bg": "#fff9db", "fg": "#8a6d1d", "emoji": "🟡"},
        "GREEN": {"bg": "#e6ffed", "fg": "#166534", "emoji": "🟢"},
    }
    style = palette[result["verdict"]]
    badge = f"{style['emoji']} {result['verdict']} / {result['label']}"

    st.markdown(
        (
            "<div style='padding: 0.65rem 0.85rem; border-radius: 0.6rem; "
            f"background:{style['bg']}; color:{style['fg']}; font-weight:700; margin-bottom:0.55rem;'>"
            f"{badge}</div>"
        ),
        unsafe_allow_html=True,
    )
    st.write(result["summary"])
    st.markdown(f"Source: [{result['citation_title']}]({result['citation_url']})")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "verdict" in message:
            render_verdict_card(message)
        else:
            st.write(message["content"])

claim = st.chat_input("Paste a suspicious health message here...")
if claim is not None:
    if not claim.strip():
        st.warning("Please paste a health claim before submitting.")
    else:
        st.session_state.messages.append({"role": "user", "content": claim})
        with st.chat_message("user"):
            st.write(claim)

        with st.chat_message("assistant"):
            with st.spinner("Checking medical evidence..."):
                try:
                    result = evaluate_claim(claim)
                    render_verdict_card(result)
                    st.session_state.messages.append({"role": "assistant", **result, "content": result["summary"]})
                except FactCheckError as exc:
                    msg = (
                        "I could not verify this claim right now. "
                        "Please try again in a moment with a little more detail."
                    )
                    st.error(msg)
                    st.caption(str(exc))
                    st.session_state.messages.append({"role": "assistant", "content": msg})
