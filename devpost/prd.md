---
doc: prd
status: approved
---

# Rumor-Stop - Product Requirements

Rumor-Stop is a family-focused health rumor checker for non-technical WhatsApp/Facebook users who need a fast, understandable safety verdict for forwarded health claims.
Source: `scope.md > Who It's For`, `scope.md > The Core Loop`, `scope.md > The Unique Kernel`.

## The Core Journey
1. User receives a suspicious health forward (remedy claim, warning, or fake health news) in WhatsApp/Facebook.
2. User opens Rumor-Stop in mobile or desktop browser.
3. User sees a WhatsApp-inspired chat interface with a clear text input prompt.
4. User pastes the forwarded claim into the chat input and submits.
5. App shows loading state while evaluating the claim.
6. App returns a prominent traffic-light verdict badge:
   - `RED / FAKE`
   - `YELLOW / UNVERIFIED`
   - `GREEN / SAFE`
7. App displays a two-sentence plain-English explanation immediately below the badge.
8. App displays at least one citation/link to a reputable medical source.
9. User decides whether to trust, ignore, or warn others about the forwarded claim.
10. User may submit another claim in the same session and see prior checks in chat history.

## Screens and Layout
Single-surface app.

- **Main Chat Screen (only screen)**
  - Header/title area communicating app purpose (health rumor checking).
  - Scrollable chat history area showing prior user inputs and assistant responses for current session.
  - Input area at bottom for text paste/submit.
  - Verdict block in each assistant response with visual priority:
    1. Traffic-light badge.
    2. Two-sentence summary.
    3. Citation link.

Navigation is implicit through conversation flow; no multi-page routing.
Source: `scope.md > The Core Loop`, `scope.md > The POC Boundary`.

## Look and Feel
Source: `scope.md > Inspiration & Identity`.

- WhatsApp-inspired conversational layout and message rhythm.
- Visual tone should feel trustworthy, simple, and family-friendly, not technical.
- Verdict badge must be the dominant visual element in each result.
- Copy style: short, plain, non-alarmist, and easy for non-technical users.

## Features and Behavior

### Claim Input and Submission
Source: `scope.md > The Core Loop`, `scope.md > The POC Boundary`.

- User can paste any health-related forwarded text into chat input.
- Submitted text is shown back in chat as user message.
- Empty or whitespace-only submission is rejected with a clear prompt to paste a claim.

Acceptance criteria:
- [ ] If user submits non-empty text, it appears in chat as a user bubble.
- [ ] If user submits empty text, app does not call model and shows an inline guidance message.

### Health Claim Evaluation and Verdict
Source: `scope.md > The Unique Kernel`, `scope.md > What "Working" Looks Like`.

- App evaluates claim and assigns one verdict category:
  - `GREEN (Safe/True)` when explicitly supported by consensus reputable organizations (WHO/CDC/Mayo Clinic class sources).
  - `RED (Fake/Dangerous)` when debunked, scam-like, or potentially harmful.
  - `YELLOW (Unverified/Mixed)` when harmless but unproven, mixed truth/exaggeration, or insufficient evidence.
- Verdict appears as prominent badge before explanation text.

Acceptance criteria:
- [ ] Every successful evaluation includes exactly one of the three verdict categories.
- [ ] Verdict label is visually obvious before explanatory text.
- [ ] Verdict logic aligns with the learner-provided definitions above.

### Explanation and Citation Output
Source: `scope.md > The Core Loop`, `scope.md > What "Working" Looks Like`.

- Output includes a two-sentence plain-English summary.
- Output includes at least one citation/link to a reputable medical source.

Acceptance criteria:
- [ ] Summary is always two sentences.
- [ ] Citation appears for every successful evaluation.
- [ ] Citation is presented as a clickable link when possible.

### Session Chat Memory (Non-Persistent)
Source: `scope.md > The POC Boundary`.

- During active app session, recent checks remain visible in chat.
- On browser refresh/reload, chat history resets fully.

Acceptance criteria:
- [ ] Multiple checks in one open session remain visible in chronological order.
- [ ] Refreshing page clears prior chat history.

### Model Routing (Free-Tier Only)
Source: `scope.md > The POC Boundary`.

- Default path uses Groq free API with `openai/gpt-oss-20b`.
- Fallback path uses Google Gemini free API with `gemini-1.5-flash` if default path is unavailable.
- No paid-token path is used in MVP.

Acceptance criteria:
- [ ] App attempts Groq path first.
- [ ] If Groq path fails/unavailable, app can use Gemini fallback path.
- [ ] Product behavior never requires paid API usage.

## States and Boundaries
- **First use** - Empty chat with guidance text explaining that user should paste a forwarded health claim.
- **Normal use** - User submits claim and receives verdict + summary + citation.
- **Loading state** - App shows clear in-progress indicator while model evaluates claim.
- **Invalid input state** - Empty submission returns guidance, no model call.
- **API failure state** - If both model paths fail, app returns a safe fallback message: unable to verify now, ask user to retry later.
- **Success state** - Completed response with all required output elements.
- **Persistence boundary** - Session-only memory; no account-based or cross-session history.

## Product Decisions
- Chat-first interface (not form/report UI) to mirror user familiarity from WhatsApp/Facebook.
- Traffic-light verdict as primary output to reduce interpretation burden for non-technical users.
- Two-sentence summary constraint to force concise, digestible explanations.
- Reputable medical citation required for every successful output to improve trust and traceability.
- Free APIs only (Groq default, Gemini fallback) due zero-cost requirement.
- Session-only memory to keep privacy handling and system complexity minimal in MVP.

## What We're Building
- Single-page Streamlit chat app for health-claim fact checking.
- Text claim input, model-based classification, and structured output (badge + 2 sentences + citation).
- Three-category verdict behavior using the agreed evidence standards.
- Groq-first, Gemini-fallback routing on free keys.
- Session-only chat history via in-memory session state.

## Out of Scope / v2 Roadmap
- Voice Note Input (accessibility): optional short voice-note submission with transcription for users who cannot type comfortably.
- Audio input and speech transcription beyond text paste.
- Accounts and saved claim history.
- Advanced evidence reconciliation across many links.
- Social sharing export cards.
- Multi-language claim support.
- Confidence indicator and rationale transparency panel.
- Multiple source citations ranked by authority and recency.
- Optional persistent encrypted local history.

## Non-Goals
- Replacing professional medical diagnosis.
- Offering treatment prescriptions.
- Building a comprehensive medical knowledge graph.
- Moderating social media directly inside WhatsApp/Facebook platforms.

## Open Questions
- Should v1 require one citation minimum or support up to three citations when available without harming readability? (Can wait until `4-spec`; does not block current PRD.)
- What exact wording style should be used for harmful-claim warnings to avoid panic while staying clear? (Can wait until `4-spec`/build copy pass.)
