---
name: hackerrank-resume-scorer
description: Score a tailored resume against HackerRank's open-source LLM resume-screener rubric (Open Source / Self-Projects / Production / Technical Skills + bonus − deductions, 0–120) using only truth-DB-grounded facts, and surface the ranked TRUTHFUL fixes that would raise the score. Runs on every tailoring run after resume-auditor. Use when the user says "score this against HackerRank", "run the LLM screener check", or as the standing post-audit step.
---

# hackerrank-resume-scorer

## Purpose

The rest of the pipeline optimizes for **keyword-matching ATS** (Workday / Greenhouse / Taleo — string scanners).
This skill optimizes for the other, growing threat model: an **LLM resume-scorer with GitHub awareness**, modeled on
HackerRank's open-sourced `hiring-agent`. It simulates that agent's grading on the tailored resume and reports:

1. a **0–120 score** broken into the agent's four axes + bonus − deductions, each line **cited to the truth DB**, and
2. a **ranked list of truthful fixes** — points currently left on the table that can be recovered **without fabrication**.

This skill is **advisory, not a blocking gate.** A low Open Source score is an honest structural fact about a solo
builder, not a failure. Blocking stays with `resume-auditor`. This skill tells the tailor where the cheap truthful wins are.

**Posture (durable, user-stated):** the candidate has no open-source contributions (every repo is solo)
and explicitly does **not** want that fabricated around. The job of this skill is to
**make the best of what genuinely exists, without hallucinating.** So the centre of gravity is the **"Truthful fixes"**
section: extract every real point currently being left on the table (unlinked live demos, missing header URLs, a complex
project under-framed, a production role under-credited). The "Honest gaps" section is **short, non-demoralizing, and factual** —
state the OSS ceiling once, name the only legitimate long-game path, and move on. Never pad the report with lectures about
what the candidate lacks; spend the words on what they can truthfully improve today.

## When it runs

**Every tailoring run**, after `resume-auditor`, before `output-packager`. The packager refuses to mark "packaged"
without `hackerrank_score.md` (same contract as `workday_skills.md`).

## Inputs

1. `outputs/<company>_<role>_<date>/tailored_resume.tex` — plain-text it via
   `python3 scripts/strip_latex.py outputs/<slug>/tailored_resume.tex` (same tool the auditor uses;
   it preserves `%% TAILOR: %%` markers so unfilled placeholders are visible).
2. The skill's rubric reference (a faithful transcription of HackerRank's open-source `hiring-agent` scoring rubric) —
   the **scoring contract**. Apply it faithfully; do not soften or reweight it.
3. `career_truth/sections/*` — read only what you need (`04_projects.md` for per-project links + solo/team status + tech;
   the experience section files for production; `01_personal.md` for header URLs; `06_skills.md` for technical breadth).
4. (Optional) `job_postings/<slug>.analysis.md` **§11 Screener type** — if it flags `LLM-resume-scorer` or `GitHub-aware`,
   note in the report that this rubric is the *primary* screen for this posting, not a secondary check.

**Truth-DB grounded — no network calls.** Do NOT hit the live GitHub API. The truth DB already records, per project,
whether it is solo vs. multi-contributor and whether it has a live URL. (This also avoids racing any concurrent session
that may be updating GitHub.)

## Scoring procedure

1. Plain-text the resume. Enumerate **every project, work/volunteer entry, skill row, and header URL** actually on it.
2. For each of the four axes, apply the rubric against **what the resume shows** (not what the truth DB could
   support but the resume omitted — the agent only sees the resume + GitHub, so an unlisted live demo earns nothing).
3. Apply the **link multipliers and deductions** per project: no link → 30–50% lower + −3..−5; GitHub-only → −2..−3;
   live demo → +10–20%. Check each project on the resume for an actual surfaced URL.
4. Apply the **Open Source hard cap**: if every repo the candidate has is solo (`self_project`, per truth DB), Open Source
   is **≤10/35** — state this plainly. Do not inflate it.
5. Apply **bonus** truthfully: +2 portfolio URL in header, +1 LinkedIn, founder/early-engineer/GSoC **only if the truth DB
   supports them**. Never invent a bonus trigger.
6. Flag any **named zero-score project pattern** present on the resume (weather/todo/calculator/CRUD/recipe/note-taking/
   basic-sentiment) — these actively *cost* points; they should be removed from an LLM-screened resume.
7. Compute the total: Σ(min(axis, max)) + min(bonus, 20) − deductions, floor 0.

## Output

`outputs/<company>_<role>_<date>/hackerrank_score.md`:

```markdown
# HackerRank LLM-Screener Score — <Company> <Role>

**Generated:** <date>
**Screener relevance:** PRIMARY (posting flagged LLM/GitHub-aware) / SECONDARY (keyword-ATS posting — scored as a hardening check)
**Total: <N> / 120**

## Score breakdown
| Axis | Score | Max | Evidence (truth-DB cited) |
| --- | --- | --- | --- |
| Open Source | <s> | 35 | <e.g. "All repos solo (self_project) per 04_projects.md → hard-capped ≤10"> |
| Self Projects | <s> | 30 | <projects listed, complexity band, link status per project> |
| Production | <s> | 25 | <production role(s), cited to the truth-DB experience sections> |
| Technical Skills | <s> | 10 | <breadth from 06_skills.md> |
| Bonus | +<b> | 20 | <+2 portfolio URL, +1 LinkedIn, ... — each trigger cited> |
| Deductions | −<d> | — | <which projects/links triggered them> |

## Truthful fixes — points left on the table (ranked by leverage)
1. **[+X–Y]** <fix, with the exact truthful change>. Evidence: <truth-DB pointer>.
   e.g. "The trade simulator has a live demo (trade-sim-demo.example.com, 04_projects.md) not linked on the resume →
   add it as an inline Live link to recover the +10–20% live-demo multiplier."
2. ...

## Honest gaps (cannot be fixed by wording — stated, never faked)
- **Open Source ceiling:** every project is solo, so this axis is structurally capped at ≤10/35. The only legitimate way
  to raise it is real contributions to others' projects (a long game) — never claim OSS contribution that didn't happen.
- <any other structural gap>

## Net read
<one paragraph: where this resume realistically lands against an LLM screener, the 2–3 highest-value truthful moves,
and the honest ceiling.>
```

## Hard rules (honesty firewall — inherited from the pipeline)

- **Never recommend fabrication.** Every fix must be a truthful surfacing/reframing backed by a `career_truth/` pointer.
  Surfacing a real-but-omitted live-demo link is a fix; inventing a contributor, a user count, GSoC, or a founder title is not.
- **No new metrics.** Same rule as the tailor and auditor.
- **Honesty over score.** If the honest score is low on an axis, report it low. The OSS cap is reported, never engineered away.
- **Score the resume, not the truth DB.** The agent grades what's on the page (+ GitHub). Credit a lever only if it is
  actually surfaced on `tailored_resume.tex`; if a truthful lever exists in the truth DB but is missing from the resume,
  that belongs in "Truthful fixes", not in the score.
- **Advisory only.** This skill never blocks packaging and never edits the resume — it reports. Cheap fixes (missing link,
  missing LinkedIn, a blocklist project present) should be handed back to `resume-tailor-no-hallucination` to apply.

## Done when

- `hackerrank_score.md` exists in the run folder with a total, the 6-row breakdown, ranked truthful fixes, and the honest-gaps section.
- Print to the user: `"hackerrank score: <N>/120 (OSS <s>/35, Projects <s>/30, Production <s>/25, Skills <s>/10, bonus +<b>, −<d>); top truthful fix: <one-liner>"`.
