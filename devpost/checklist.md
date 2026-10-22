---
doc: checklist
status: approved
---

# Build Checklist

Build mode: learn

## Slices

- [ ] **1. Paste a claim and get a Groq verdict in chat**
  Becomes usable: A running Streamlit chat app where a pasted health claim returns `RED|YELLOW|GREEN` plus a two-sentence summary and one citation from the primary Groq path.
  Why now: Proves the unique kernel end-to-end immediately, including UI, prompt path, and structured output.
  PRD ref: `prd.md > The Core Journey`, `prd.md > Claim Input and Submission`, `prd.md > Health Claim Evaluation and Verdict`, `prd.md > Explanation and Citation Output`
  Spec ref: `spec.md > Streamlit UI Shell (\`app.py\`)`, `spec.md > Claim Evaluation Orchestrator (\`services/fact_checker.py\`)`, `spec.md > Prompt Templates (\`prompts/fact_check_prompt.txt\`)`, `spec.md > Where It Runs and How Someone Tries It`
  Build: Create the file structure, install dependencies, implement chat UI with `st.chat_message`/`st.chat_input`, add Groq client call, and render verdict badge + summary + citation in assistant responses.
  Verify (mechanical): Run `streamlit run app.py`, submit a non-empty test claim, and confirm a response renders with one valid verdict label, two-sentence summary, and citation link.
  Learner check: Paste one forwarded health claim and confirm the output is understandable at a glance, with verdict first.
  Commit: `Build end-to-end Groq fact-check chat slice`

- [ ] **2. Add session chat memory and input/error guards**
  Becomes usable: Users can run multiple checks in one session with visible history, while empty input and obvious failures show clear guidance.
  Why now: Stabilizes core day-to-day use and aligns behavior with PRD boundary states before adding multi-provider complexity.
  PRD ref: `prd.md > Session Chat Memory (Non-Persistent)`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Session State Manager (\`app.py\` helper functions)`, `spec.md > Data Model`, `spec.md > Important Failure Modes`
  Build: Implement `st.session_state` message history, whitespace-input validation, loading state, and fallback user-facing message when primary call fails.
  Verify (mechanical): Submit two claims in one session and confirm both remain visible in order; refresh browser and confirm history resets; submit whitespace-only input and confirm no model call occurs.
  Learner check: Try two real claims, then refresh and verify the privacy-preserving reset behavior matches expectation.
  Commit: `Add session memory and robust input/error states`

- [ ] **3. Implement Gemini fallback and provider routing**
  Becomes usable: If Groq is unavailable, the app still produces usable fact-check output through Gemini free-tier fallback.
  Why now: Reduces external-service risk early and enforces the zero-paid-token reliability strategy.
  PRD ref: `prd.md > Model Routing (Free-Tier Only)`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Provider Clients (\`services/providers/groq_client.py\`, \`services/providers/gemini_client.py\`)`, `spec.md > External Services and Dependencies`, `spec.md > Important Failure Modes`
  Build: Add Gemini provider client, route Groq-first then Gemini fallback in orchestrator, and keep one normalized output contract across both providers.
  Verify (mechanical): Temporarily force Groq failure path and confirm Gemini fallback returns a valid verdict/summary/citation response without crashing.
  Learner check: Trigger the fallback demo path and confirm the UX still feels consistent and trustworthy.
  Commit: `Add Gemini fallback routing for resilient free-tier inference`

- [ ] **4. Enforce output contract and polish verdict presentation**
  Becomes usable: Responses consistently match the product contract and the verdict badge is visually prominent and readable on mobile/desktop.
  Why now: Locks product quality and demo consistency after behavior is complete.
  PRD ref: `prd.md > Explanation and Citation Output`, `prd.md > Look and Feel`, `prd.md > Screens and Layout`
  Spec ref: `spec.md > Output Validator (\`services/validator.py\`)`, `spec.md > Look and Feel`, `spec.md > Important Failure Modes`
  Build: Add output validator for verdict label/two-sentence summary/citation checks, add one retry path for malformed output, and refine chat response styling with clear traffic-light hierarchy.
  Verify (mechanical): Run app and submit test claims that produce normal and malformed-like outputs; confirm validator enforces contract and UI consistently displays badge first with stable color mapping.
  Learner check: Open on mobile-width and desktop-width views and confirm readability, badge prominence, and citation clarity.
  Commit: `Validate output contract and finalize verdict-first UI polish`

- [ ] **5. Prepare demo-ready run flow and docs**
  Becomes usable: Project is easy to run, test, and record for hackathon submission with reproducible setup instructions.
  Why now: Converts working code into a reliable handoff artifact for final review and shipping.
  PRD ref: `prd.md > What We're Building`, `prd.md > Non-Goals`
  Spec ref: `spec.md > Where It Runs and How Someone Tries It`, `spec.md > File Structure`, `spec.md > Decisions and Open Issues`
  Build: Add/finish `.env.example`, write README quickstart and demo script steps, verify required dependencies and commands align with actual implementation.
  Verify (mechanical): In a clean shell, follow README steps to start app and run one full claim-check flow successfully.
  Learner check: Follow README yourself and confirm no missing setup assumptions.
  Commit: `Finalize runbook and demo-ready documentation`

## Hands-on Checkpoints

- [ ] Early usable behavior explored - after Slice 2 (core flow + session behavior)
- [ ] Final kick-the-tires exploration and feedback completed

## Final Review

- [ ] Final review complete - feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [ ] Learning activity complete - guided route, focused alternative, prior practice connected, or brief recap
- [ ] Optional edit and transfer reflection addressed - offered/declined/already covered/not applicable as appropriate
- [ ] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: [what actually happened; real document/test/code references; unfinished work if interrupted]
Route and stops: [actual paths and symbols; guided stops completed, or reference-only route]
Edit outcome: [tried/kept/reverted/declined/not applicable; verification if changed]
Reflection: [offered/answered/declined/already covered - personal answer belongs only in the ignored profile]
Activity mode: [live app and editor, explicit static fallback, focused alternative, prior practice, or recap]

## Revisions
- Groq default model updated from `llama-3.1-8b-instant` to `openai/gpt-oss-20b` - learner check found the previous free-tier model was deprecated and returning 404.
- Groq response contract tightened to JSON-object mode with exactly `verdict`, `summary`, and `citation` - learner test failure showed free-form model output caused parse errors.
