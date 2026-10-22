---
doc: spec
status: approved
---

# Rumor-Stop - Technical Spec

## How This Works, In Plain Language
Rumor-Stop is a single-page Streamlit chat app. A user pastes a forwarded health claim, the app sends that text to a free LLM API, and the model returns a structured decision with three parts: a traffic-light verdict, a two-sentence explanation, and a citation link.

The app is intentionally small: one interface, one core loop, no accounts, no database, and no paid services. During one open session, previous checks stay visible so the user can compare results. When the page reloads, session memory clears, which keeps the MVP simple and privacy-friendly.

This shape was chosen because it proves the core idea quickly for a hackathon demo while staying within zero-cost API constraints.

## The Core Journey Through the System
PRD ref: `prd.md > The Core Journey`.

1. User enters claim text in Streamlit chat input.
2. App validates input (non-empty text required).
3. App appends user message to in-memory session chat history.
4. App builds a classifier prompt with strict output format requirements.
5. App calls Groq (`openai/gpt-oss-20b`) as primary model path.
6. If Groq call fails, app attempts Gemini (`gemini-1.5-flash`) fallback path.
7. App parses/normalizes model output into required fields:
   - verdict (`RED|YELLOW|GREEN`)
   - summary (exactly 2 sentences)
   - citation URL + source label
8. App renders assistant response block with prominent traffic-light badge first, then summary, then citation.
9. User can repeat the process for another forwarded claim in the same session.
10. On reload, session history is reset.

## Stack
- **Python 3.10+**
  - Docs: `https://docs.python.org/3/`
  - Rationale: learner-specified baseline and broad compatibility.

- **Streamlit**
  - Docs: `https://docs.streamlit.io/`
  - Rationale: fastest path to a browser chat UI with `st.chat_message` and `st.chat_input`.

- **Pandas**
  - Docs: `https://pandas.pydata.org/docs/`
  - Rationale: included by learner constraint; useful for optional lightweight tabular logging/normalization in-session.

- **Groq API (OpenAI-compatible) with `openai/gpt-oss-20b`**
  - Docs: `https://console.groq.com/docs`
  - Rationale: primary free path chosen for speed and zero paid tokens.

- **Google Gemini API with `gemini-1.5-flash` (fallback)**
  - Docs: `https://ai.google.dev/gemini-api/docs`
  - Rationale: free fallback if Groq path is unavailable.

Accepted tradeoff: free-tier APIs may have stricter rate limits and occasional downtime; fallback routing reduces but does not eliminate this risk.

## Where It Runs and How Someone Tries It
- **Runtime**: local Streamlit server in browser.
- **Requirements**:
  - Python 3.10+
  - `GROQ_API_KEY`
  - `GEMINI_API_KEY`
- **Start command**:
  - `streamlit run app.py`
- **What to open**:
  - local URL printed by Streamlit (typically `http://localhost:8501`)
- **Demo flow for recording**:
  1. Open app.
  2. Paste one suspicious claim.
  3. Show verdict badge + two-sentence summary + citation.
  4. Paste second claim to show same-session history.
  5. Refresh page to show history reset behavior.

Submission reminder: demo video and public GitHub repository are required. Deployment is optional.

## Look and Feel
Implements `prd.md > Look and Feel` and `prd.md > Screens and Layout`.

- WhatsApp-inspired chat rhythm and message structure.
- Visual hierarchy: verdict badge is most prominent element.
- Color mapping must be explicit and consistent:
  - `RED / FAKE`
  - `YELLOW / UNVERIFIED`
  - `GREEN / SAFE`
- Language tone: calm, direct, non-judgmental, family-friendly.
- Keep layout clean and legible on mobile and desktop.

## Components

### Streamlit UI Shell (`app.py`)
Implements `prd.md > Screens and Layout`.

- Renders page title/help text.
- Owns chat input and chat transcript rendering.
- Displays verdict badge, summary, and citation in assistant messages.

### Session State Manager (`app.py` helper functions)
Implements `prd.md > Session Chat Memory (Non-Persistent)`.

- Initializes and updates `st.session_state` message list.
- Ensures history persists only while app instance remains active.

### Claim Evaluation Orchestrator (`services/fact_checker.py`)
Implements `prd.md > Health Claim Evaluation and Verdict`.

- Builds prompt and schema expectations.
- Routes requests to primary/fallback providers.
- Normalizes provider response into common output contract.

### Provider Clients (`services/providers/groq_client.py`, `services/providers/gemini_client.py`)
Implements `prd.md > Model Routing (Free-Tier Only)`.

- Encapsulate API-specific request/response logic.
- Return structured result or typed failure.

### Output Validator (`services/validator.py`)
Implements `prd.md > Explanation and Citation Output`.

- Enforces allowed verdict labels.
- Enforces two-sentence summary constraint.
- Validates citation presence/URL shape.
- Applies safe fallback if model output is malformed.

### Prompt Templates (`prompts/fact_check_prompt.txt`)
Implements `prd.md > Health Claim Evaluation and Verdict`.

- Defines verdict rules exactly as product decisions specify.
- Instructs model to prefer reputable medical-source grounding.

## Data Model
- **In-memory chat message list**
  - Shape: list of message objects `{role, content, verdict?, summary?, citation?}`.
  - Location: `st.session_state["messages"]`.
  - Update: append on each user submit and assistant response.
  - Persistence: lost on reload/refresh.

- **Evaluation result object**
  - Shape:
    - `verdict`: `RED|YELLOW|GREEN`
    - `label`: `FAKE|UNVERIFIED|SAFE`
    - `summary`: two-sentence plain text
    - `citation_title`: source name
    - `citation_url`: HTTPS link
  - Location: computed per request; then embedded in chat message.

No external database in MVP.

## File Structure

```text
rumor-stop/
├── app.py                              # Streamlit entrypoint and UI composition
├── requirements.txt                    # Python dependencies
├── .env.example                        # Example env vars only (no secrets)
├── README.md                           # Setup and demo instructions
├── prompts/
│   └── fact_check_prompt.txt           # Prompt template with verdict rules
├── services/
│   ├── fact_checker.py                 # Orchestration and provider routing
│   ├── validator.py                    # Output contract and fallback formatting
│   └── providers/
│       ├── groq_client.py              # Groq API integration
│       └── gemini_client.py            # Gemini API integration
└── devpost/
    ├── learner-profile.md              # Ignored by git by default
    ├── scope.md
    ├── prd.md
    └── spec.md
```

## External Services and Dependencies

### Groq API (Primary)
- Docs: `https://console.groq.com/docs`
- Endpoint (OpenAI-compatible): `POST https://api.groq.com/openai/v1/chat/completions`
- Auth: `Authorization: Bearer $GROQ_API_KEY`
- Request payload (core):
  - `model: "openai/gpt-oss-20b"`
  - `messages: [...]`
  - optional low-temperature settings for stable formatting
- Response used: assistant text content parsed into verdict/summary/citation fields.
- Cost target: free-tier only.
- Limits: rate limits depend on current free-tier policy; verify during build.

### Google Gemini API (Fallback)
- Docs: `https://ai.google.dev/gemini-api/docs`
- SDK path (recommended): official Gemini client library with `gemini-1.5-flash`.
- REST endpoint form (if direct HTTP used): `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent`
- Auth: API key via header/query per official docs (`$GEMINI_API_KEY`).
- Request payload (core): user claim + format instructions.
- Response used: generated text parsed into same common output contract.
- Cost target: free-tier only.
- Limits: free-tier quotas can vary; verify during build.

### Streamlit
- Docs: `https://docs.streamlit.io/`
- Used for local web hosting and chat UI controls.

## Important Failure Modes
- **Provider outage or timeout** -> Auto-attempt fallback provider; if both fail, show polite "unable to verify now" message and suggest retry.
- **Malformed model output** -> Validate and coerce to safe fallback response with `YELLOW` and explicit uncertainty language.
- **Missing/invalid citation in response** -> Mark as incomplete, retry once with stricter formatting prompt, else return fallback uncertainty message.

## What Was Simplified and Why
- **Session-only in-memory history** instead of persistent user history/database - preserves core usefulness while avoiding auth/storage/privacy complexity.
- **Single-screen chat app** instead of multi-page workflow - keeps focus on core paste-and-check loop and faster implementation.
- **One required citation per result** instead of multi-source evidence panel - enough to prove trust signal in PoC.
- **Text-only input** instead of audio capture/transcription - reduces integration risk and keeps MVP within time budget.

## Out of Scope / v2 Roadmap
- **Voice Note Input (accessibility)**: add optional voice-note capture plus speech-to-text so non-typing users can submit claims.
- **Broader audio pipeline**: extended speech transcription tuning and multilingual voice handling.
- **Persistent user memory**: optional saved history with secure storage once auth/privacy architecture is added.
- **Advanced evidence view**: ranked multi-citation evidence panel with recency/authority signals.

## Decisions and Open Issues
- Chosen: Groq `openai/gpt-oss-20b` as default, Gemini `gemini-1.5-flash` as fallback.
  - Why: fast, free-tier compatible, aligned with learner constraints.
  - Tradeoff: free-tier quotas/reliability can fluctuate.

- Chosen: `st.session_state` for chat memory with full reset on reload.
  - Why: simple privacy-friendly MVP behavior.
  - Tradeoff: no continuity after refresh.

- Chosen: strict output contract (badge + two-sentence summary + citation) for every successful result.
  - Why: improves readability and demo consistency.
  - Tradeoff: extra validation/parsing logic required.

- Learner uncertainty note: none surfaced as unresolved in interview; verdict definitions, target user, model routing, and memory boundary were explicitly specified.

- Open issues to verify early in build:
  - Confirm current free-tier quota/rate-limit details in Groq and Gemini docs at implementation time.
  - Decide whether one citation is always enough or whether optional second citation improves trust without clutter.
