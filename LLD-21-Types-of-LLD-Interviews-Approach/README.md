# LLD-21 &mdash; Types of LLD Interviews & How to Approach LLD Problems

> The methodology class. Eight classes of patterns and SOLID, now turned into a 90-minute playbook for the interview room.

This class is **not about new patterns.** Every senior engineer who's flunked an LLD round did so because they knew the patterns but missed the process. LLD-21 gives you that process.

---

## What this class covers

1. **The five (really six) shapes of an LLD interview** — machine coding, design discussion, take-home, system+LLD hybrid, code review, live screen-share design.
2. **The 7-step approach** — a repeatable timeline from minute 0 to minute 90.
3. **The seven mistakes** that tank LLD interviews — and the audible fix for each.
4. **A worked example** — Parking Lot, solved on the clock with the playbook.
5. **A cheat sheet** — taped to your desk, glanced at before every interview.
6. **Resources** — where to practice without burning out.

---

## The 7-step approach (memorise this)

| #  | Time     | Step                         | What you do                                                |
|----|----------|------------------------------|------------------------------------------------------------|
| 1  | 0–5      | **Clarify**                  | Ask 3–5 questions. Scope, scale, out-of-scope.             |
| 2  | 5–10     | **Requirements**             | Functional + non-functional. Pin them to the board.        |
| 3  | 10–18    | **Entities & relationships** | Circle nouns, underline verbs. Sketch the UML.             |
| 4  | 18–25    | **APIs**                     | Method signatures only. No bodies yet.                     |
| 5  | 25–65    | **Code (happy path first)**  | Simplest case end-to-end. Then edges.                      |
| 6  | 65–80    | **Demo**                     | Run it live. Walk one happy path, one edge case.           |
| 7  | 80–90    | **Trade-offs**               | Persistence, concurrency, extension. "If I had 10 more…"   |

The first three steps look slow. They're what makes the last four fast.

---

## Five interview formats — pick the right playbook

| Format                  | Time         | Common at                      | What's judged                                |
|-------------------------|--------------|--------------------------------|----------------------------------------------|
| **Machine coding**      | 90 min       | Flipkart, Razorpay, Swiggy, PhonePe, Cred | Working demo + clean class design     |
| **Design discussion**   | 45–60 min    | Google, Meta, Atlassian        | UML class diagram, APIs, trade-offs          |
| **Take-home**           | 24–72 hours  | Stripe, GitLab, remote-first   | Repo with tests, README, polish              |
| **System + LLD hybrid** | 60 min       | FAANG senior+, Atlassian, Uber | Switching altitude on demand                 |
| **Code review**         | 45–60 min    | Stripe, Atlassian, Twilio      | What you notice, how you frame, what you fix |
| **Live design talk**    | 30 min       | Phone screens, recruiter calls | Structured thinking without visuals          |

Misreading the format costs you the round. Confirm with the recruiter.

---

## Seven mistakes (and the audible fix)

1. **Diving into code without clarifying** → ask 3–5 questions, write FRs/NFRs on the board.
2. **Building all 47 features instead of MVP** → pick the top 3 with the interviewer, in writing.
3. **Inheritance for everything** → prefer composition; reach for Strategy / Decorator before subclasses.
4. **Singleton-for-everything** → constructor injection; reserve Singleton for true process-wide resources.
5. **Weak naming** → verb + domain noun. `add_expense`, not `doStuff`.
6. **Skipping the live demo** → run the code on screen, even if it crashes. Live debugging is a strength signal.
7. **No trade-offs at the end** → have 3 ready: persistence, concurrency, extension.

---

## Worked example — Parking Lot, the 90-minute version

The class works through this on the clock. The full code is in `code/01_parking_lot_walkthrough.py` and the playbook in `code/02_seven_step_template.py` is a copy-paste skeleton you can use on any new problem.

The Parking Lot demo uses **two Strategy patterns** (where to put a car, how to charge) and zero inheritance trees. Adding "reserved EV slots" becomes one new strategy class — that's what you say in Step 7.

---

## The code in this class

| File                                | What it shows                                                      |
|-------------------------------------|--------------------------------------------------------------------|
| `code/01_parking_lot_walkthrough.py`| The Parking Lot end-to-end &mdash; happy path + 3 edge cases       |
| `code/02_seven_step_template.py`    | A blank 7-step template you fill in for any new problem            |
| `code/03_splitwise_skeleton.py`     | Splitwise skeleton with `SplitStrategy` (Equal / Percent / Share)  |
| `code/04_code_review_target.py`     | Deliberately-messy code for code-review-interview practice         |
| `code/05_interview_clock.py`        | A tiny CLI that runs the 7-step clock and prompts you each phase   |

Run any of them with plain `python3` — no pip installs needed.

---

## How to use this class to actually pass interviews

1. **Read** the `index.html` once start to finish. Don't skim the mistakes section.
2. **Do** the 30 quizzes inside `index.html`. The correct answer is randomly distributed across A/B/C/D — there's no "default to B" shortcut.
3. **Practise** the 7-step playbook on 5 problems: Splitwise, Parking Lot, Tic-Tac-Toe, BookMyShow, an in-memory cache. Each problem twice — once untimed, once strict 90-minute clock.
4. **Watch yourself** in mock interviews. The single most useful drill is recording yourself running step 1 (clarifying) and step 7 (trade-offs). If they sound shaky, every other step also will.

---

## Sanity-check questions for yourself before any LLD interview

- Can I name 5 design patterns and where I'd reach for each one in <60 seconds?
- Can I draw the 6 UML relationship arrows (Inheritance / Realisation / Composition / Aggregation / Association / Dependency) without looking?
- Can I write a Strategy + Protocol skeleton in <2 minutes?
- Do I have 3 trade-off bullets memorised (persistence, concurrency, extension)?
- Do I have 3 clarifying questions memorised (scope, scale, out-of-scope)?

If yes to all five — you've got the toolkit. The interview is now about discipline, not knowledge.

---

## Where this class sits

Module 3 of the LLD batch:

- LLD-13 / 14 — SOLID
- LLD-15 — Singleton
- LLD-16 — Builder
- LLD-17 — Factory family
- LLD-18 — Prototype + Adapter
- LLD-19 — Strategy + Observer
- LLD-20 — Decorator + UML
- **LLD-21 — Types of LLD interviews + how to approach (you are here)**
- LLD-22 / 23 — Tic-Tac-Toe (the first end-to-end LLD problem we code together)
- LLD-24+ — Parking Lot, BookMyShow, Splitwise, Google Calendar

Everything from LLD-13 onward shows up in the cheat sheet. The next 8 classes are this class applied to a real problem each.
