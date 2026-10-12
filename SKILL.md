---
name: book-to-learning-roadmap
description: Turn a book, course, documentation set or syllabus into a session-by-session study roadmap, with an evidence-based lesson template (retrieval practice, worked examples, scaffolding ladder, spaced review) so the learner masters topics and does not forget them. Use whenever the user wants to convert a book, online course, tutorial series, docs or table of contents into a learning plan, study schedule, lesson plan or curriculum, asks what one study session per chapter should contain, or wants to learn programming, data science or another technical skill from a specific resource, even if they never say "roadmap". Also use when they ask how to study so that knowledge sticks.
---

# Book to Learning Roadmap: Empirical Mastery Protocol

Turn a source (book, course, docs, syllabus) into a realistic study plan and self-contained, interactive lessons. The plan fits the learner's goal, available time, and own dataset rather than passively mirroring the source's length and order.

---

## 1. Intake (Ask little, assume the rest)

Collect from the conversation:
- **Source**: URL, file, or title.
- **Goal**: What the learner will build or get hired for (this determines what to skip and what to expand).
- **Dataset**: The learner's own project or domain dataset. A real domain dataset always beats toy examples.
- **Level & Tooling**: What they already know; preferred editor, package runner, and runtime.
- **Budget**: Hours per week, session length (default 75–90 mins), deadline.

State reasonable assumptions in one line if unanswered, and allow defaults to be adapted.

---

## 2. Read the Source Before Planning

Review the table of contents and chapter intros. Editions change, APIs evolve, and features get deprecated: verify current library compatibility.

**Copyright Rule:** If the source prohibits copying, **never copy text, tables, or code verbatim**. Paraphrase concepts in your own words, design novel domain-relevant code examples, and provide chapter/section pointers for optional reading.

---

## 3. Triage by the Learner's Goal

Label every chapter against the learner's goal:
- **Core**: Directly needed for the goal. Receives dedicated, full sessions.
- **Quick**: Useful but foundational or lighter. Condensed into 1 session or a focused survey.
- **Skip / On demand**: Appendices, niche internals, or tangential topics. Omit from the primary calendar and note when to revisit.

Calculate calendar fit: `Total Sessions ÷ (Sessions/Week) = Total Weeks`. Compare against the learner's schedule budget.

---

## 4. Single-File Architecture & Naming Standard

1. **Single Source of Truth**: Each session lives as **exactly one self-contained Jupyter Notebook** (`notebooks/session_XX_<topic_slug>.ipynb`). Theory, runnable code, and exercise cells live together in one place without external website dependencies.
2. **Sequential Numbering**: Use zero-padded two-digit session numbers (`session_01`, `session_02`, ..., `session_XX`) to ensure clean chronological sorting. Do not label sessions with source book chapter numbers, as roadmap session groupings often differ from source chapter numbers.
3. **Internal Navigation**: Every notebook begins with relative breadcrumb links:
   `[<< Course Roadmap](./00_roadmap_and_orientation.ipynb) | [<< Previous] | Current | [Next >>]`

---

## 5. The Scaffolding Ladder

To eliminate cognitive leap ("How am I supposed to know this?"), never ask the learner to write code they haven't seen demonstrated in the same session. Every new skill or concept must advance through progressive scaffolding steps:

| Rung | Learner Activity | Pedagogical Objective |
|---|---|---|
| **1. Predict** | Inspect working code and predict output before running the cell. | Understand syntax and execution mechanics without the cognitive load of code generation. |
| **2. Modify** | Change a parameter, operator, or value in working demonstration code. | Observe cause-and-effect relationships between arguments and outcomes. |
| **3. Faded Example** | Complete missing blanks (`___`) in a code skeleton with clear reference to preceding examples. | Practice syntax retrieval with low cognitive load. |
| **4. Apply with Auto-Check** | Solve a problem on fresh data with an automated `assert` validation check. | Facilitate near-transfer of skills to a new scenario. |
| **5. Blank-Page Practice** | Synthesize end-of-session challenge starting from an empty cell (~30% duration). | Build independent problem-solving fluency. |

> **Invisible Scaffolding Rule:** The ladder is an **authoring discipline**, NOT a table of contents or heading template. **Never expose labels like `5-Rung`, `Rung 1: Predict`, `Rung 2: Modify`, `Faded Example`, or pedagogical meta-jargon in notebook titles or markdown headers.** Frame every step using natural, conversational prose (e.g., *"A Quick Mental Check"*, *"Hands-on: Adapting the Formula"*, *"Guided Exercise"*, *"Hands-On Challenge"*). Keep all text strictly in clear, professional English.

---

## 6. Structure of a Self-Contained Session (75 – 90 Minutes)

Scale minutes to the agreed session duration:

1. **Warm-up & Retrieval (~10% / ~10m):**
   - Active recall of 2–3 questions from previous sessions.
   - **Whole Game:** Run a top-down complete pipeline on real domain data before analyzing syntax minutiae (fast.ai approach).
2. **Concept & Scaffolding Cycles (~55% / ~45-50m):**
   - 2 to 3 micro-cycles. Each cycle explains the core concept, walks through a runnable code example, and climbs through the scaffolding ladder (Predict ➔ Modify ➔ Faded ➔ Apply).
   - Deliberate debugging clinic: intentionally trigger authentic runtime errors, analyze exact tracebacks, and fix them.
3. **Blank-Page Domain Practice (~30% / ~25m):**
   - Multi-step problem on domain data starting from a blank cell without AI assistance.
4. **Close & Spaced Retrieval (~5% / ~5m):**
   - 3 active flashcards formatted as **Task ➔ Write Code** prompts.

---

## 7. Retention System

- **Task-to-Code Flashcards:** Prompts describe a concrete programming task; answers are the exact code solution.
- **Spaced Review Schedule:** Review active cards at expanding gaps: Day 1, 3, 7, 14, 30 (*heuristic convention for retention*).
- **Weekly Interleaving (30 mins):** Solve mixed problems drawn across past sessions with topic titles hidden.
- **Monthly Blank-Page Rebuild (60 mins):** Rebuild a complete data pipeline from a clean notebook.

---

## 8. AI Assistant Safeguards

A trial of 52 developers (*Anthropic*) observed that participants delegating code creation to AI scored lower on post-task skill assessments (50% vs. 67% for manual coders).
- **Rule:** Do not allow AI to write code during Faded, Apply, and Blank-Page practice cells.
- AI is permitted strictly for conceptual questions and explaining code written by the learner.

---

## 9. Honesty About Evidence

- Cite only literature directly verified. Key references:
  - *Atkinson et al. (2000)*: Worked examples and fading in cognitive skill acquisition.
  - *fast.ai Teaching Philosophy (Jeremy Howard)*: Top-down, whole-game learning.
  - *Dunlosky et al. (2013)*: Review of retrieval practice and distributed learning.
  - *Anthropic*: Research on AI assistance and coding skills.
- Distinguish empirical research findings from practical heuristics (session durations, phase percentages, and 1-3-7-14-30 review spacing are conventions, not natural laws).