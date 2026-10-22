---
doc: scope
status: approved
---

# Rumor-Stop

A lightweight, family-focused web app that fact-checks viral health claims and home-remedy messages from social media chat forwards.

## The Unique Kernel
Rumor-Stop translates noisy viral health text into a simple traffic-light safety verdict (`RED`, `YELLOW`, `GREEN`) with plain-language explanation and medical-source citation, so non-technical family users can decide quickly what to trust.

## Who It's For
A non-technical parent or elder who frequently uses WhatsApp or Facebook and receives forwarded health claims they are unsure about.

They are trying to decide, fast, whether a forwarded claim is safe to trust, dangerous, or uncertain. Today they often rely on guesswork, family opinions, or repeated forwards.

## The Core Loop
The user receives a suspicious health forward, copies the message text, opens Rumor-Stop in a browser, pastes the claim into a chat-style input, and gets:
1. A prominent traffic-light verdict badge.
2. A two-sentence summary in plain English.
3. A citation/link to a reputable medical source.

They come back whenever a new forwarded claim appears.

## Inspiration & Identity
Interface identity: familiar WhatsApp-style chat interaction, but purpose-built for health rumor checking.

Mood and tone: calm, clear, reassuring, and non-judgmental for family use.

## Why This Matters to the Learner
The project addresses a practical family safety problem: rapid spread of misinformation around remedies and health warnings. The learner wants a small, useful tool that helps non-technical relatives make safer decisions quickly.

## What "Working" Looks Like
A user can paste a forwarded health claim into the chat input and consistently receive a correct category-style outcome:
- `GREEN` when claim is supported by consensus reputable sources.
- `RED` when claim is debunked/scam/harmful.
- `YELLOW` when evidence is mixed, weak, or insufficient.

The result is immediately understandable in under a minute and demoable on screen.

## The POC Boundary
In scope for MVP:
- Text-input fact-checking only.
- Streamlit chat interface (`st.chat_message`, `st.chat_input`).
- Traffic-light verdict badge + two-sentence summary + reputable citation.
- Free-tier LLM inference only (Groq default, Gemini fallback).
- Session-only chat memory (`st.session_state`) cleared on page refresh/reload.

## Out of Scope / v2 Roadmap
- Voice Note Input (accessibility): allow users who struggle with typing to submit health claims via short recorded voice notes with transcription.
- Multi-language support.
- Multiple citations and source-ranking UI.
- Shareable result cards for messaging apps.
- Longitudinal misinformation tracking/reporting.

## Explicitly Cut
- User accounts/authentication: cut to keep setup and privacy handling simple for a fast PoC.
- Persistent database/history across reloads: cut to reduce infrastructure and privacy complexity.
- Paid APIs or paid model tokens: cut due to zero-cost constraint.
- Voice note/audio input in v1: cut to keep the MVP focused on the core text-checking loop and to avoid adding transcription complexity in the first release.
