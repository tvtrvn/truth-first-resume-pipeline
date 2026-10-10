# Workflow — How to Tailor a Resume Here

> Written for a beginner. The whole system is a sequence of small "skills" that each do one thing and write one file. Run them in order and you get a tailored resume + cover letter + audit trail in a single folder.

If you've never used this before, read the **TL;DR** first, then skim the **Step-by-step**. Come back to **Tips** when something breaks.

---

## TL;DR

1. Paste a job posting into `job_postings/<company>_<role>_<date>.md`.
2. In Claude Code, say: *"Tailor a resume for `job_postings/<filename>`."*
3. Claude runs the pipeline (analyze posting → map keywords → check skills gap → tailor resume → audit → **show you the `.tex` draft and wait** → render PDF on your OK → optional cover letter → package).
4. Open `outputs/<company>_<role>_<date>/` and read `run_summary.md` first. That folder has everything you need to send.

**Important:** The tailored resume comes out as `tailored_resume.tex` first. You review it, ask for edits if needed, and only then does Claude render `tailored_resume.pdf` via Tectonic. This is a deliberate gate — no PDF is generated without your explicit OK and without the audit passing.

If the audit says **FAIL**, fix the flagged bullets (or let Claude rewrite them) before sending. If it says **PASS-WITH-WARNINGS**, review the warnings — they're usually small ATS or vagueness issues, not lies.

---

## The Pipeline

```
            ┌─────────────────────────┐
            │ career_truth/           │  ← built once by resume-source-truth, refreshed when
            │   source_of_truth.md    │     your projects change. This is the truth DB.
            │   source_of_truth.json  │
            │   uncertain_items.md    │
            └────────────┬────────────┘
                         │
   ┌─────────────────────┼──────────────────────────────────────┐
   │                     │                                       │
   ▼                     ▼                                       ▼
[job-posting-      [resume-source-truth]                  [project-evidence-miner]
 analyzer]          → refresh truth DB                     → optional deep dive on
 → posting           when new projects                       a single project
 .analysis.md        get added
   │
   ▼
[skills-gap-analyzer] ────┐
   → skills_gap.md         │
[ats-keyword-mapper] ─────┤
   → keyword_map.md         │
                            ▼
                  [resume-tailor-no-hallucination]
                   → tailored_resume.tex   ← fills templates/resume_template.tex
                   → evidence_report.md
                            │
                            ▼
                     [resume-auditor]
                   → audit_report.md
                   verdict: PASS / PASS-WITH-WARNINGS / FAIL
                            │
                            ▼
                [hackerrank-resume-scorer]   (step 5b — advisory, never blocks)
                   → hackerrank_score.md   ← mandatory artifact on every run
                            │
                            ▼
                  *** USER REVIEWS .tex AND APPROVES ***
                            │
                            ▼
                  [latex-to-pdf-renderer]   ← Tectonic; only runs on PASS + approval
                   → tailored_resume.pdf
                            │
                            ▼
                  [cover-letter-grounded]   (optional, same gate)
                   → cover_letter.tex → cover_letter.pdf
                   → cover_letter_evidence.md
                            │
                            ▼
                    [output-packager]
                   → run_summary.md + bundled folder
```

Most boxes are skills in `skills/`; `resume-source-truth`, `project-evidence-miner` and `cover-letter-grounded` stay private. You don't have to call them by name — Claude will figure out which to run when you describe what you want.

---

## Step-by-step (the first time)

### One-time setup (already done)

The truth DB exists at `career_truth/`. It was built by reading every project in the workspace, every master resume in `career_source/resumes/` (if any), every source resume and cover letter PDF, and every certificate.

If you add a new project to the workspace or update a master resume, run:

> *"Refresh the truth database."*

Claude will rerun `resume-source-truth` and update the three files in `career_truth/`.

### For every new job posting

1. **Add the posting** to `job_postings/`. Naming convention: `<company-slug>_<role-slug>_<YYYY-MM-DD>.md`. Inside, paste the full posting text. Add any notes (e.g., "they emphasize teamwork", "saw this on LinkedIn") at the top.

2. **Ask Claude to analyze the posting**:
   > *"Analyze `job_postings/<filename>`."*

   This runs `job-posting-analyzer` and writes a `.analysis.md` next to the posting. It pulls out required skills, preferred skills, responsibilities, ATS keywords, and likely evaluation criteria.

3. **Check the skills gap (honesty mode)**:
   > *"Run the skills gap on this posting."*

   This runs `skills-gap-analyzer` and produces a `skills_gap.md` with an `APPLY` / `APPLY-IF-FLEXIBLE` / `SKIP` recommendation. **If the recommendation is `SKIP`, talk to Claude before tailoring** — you'd be claiming things you don't have to get through ATS.

4. **Map the keywords**:
   > *"Map the ATS keywords."*

   `ats-keyword-mapper` produces `keyword_map.md` with three buckets: matched (safe), adjacent (use carefully), cannot-claim (forbidden).

5. **Tailor the resume**:
   > *"Tailor my resume for this posting."*

   `resume-tailor-no-hallucination` selects the strongest bullets per project, rewrites them to fit the posting's emphasis, and fills `templates/resume_template.tex` to produce `tailored_resume.tex` + `evidence_report.md`. **No PDF is generated yet.**

6. **Audit**:
   > *"Audit the resume."*

   `resume-auditor` checks every bullet in the `.tex` against the truth DB and produces `audit_report.md` with a `PASS` / `PASS-WITH-WARNINGS` / `FAIL` verdict.

7. **Review the .tex, then approve rendering**:

   Open `tailored_resume.tex`, read it, request edits if you want changes. When you're happy, say:
   > *"Looks good — render the PDF."*

   `latex-to-pdf-renderer` runs `tectonic tailored_resume.tex`. It refuses if the audit FAILed or if any `%% TAILOR: %%` markers are still present. Output: `tailored_resume.pdf` next to the `.tex`.

8. **(Optional) Cover letter**:
   > *"Add a cover letter."*

   `cover-letter-grounded` writes a 280–350 word cover letter as `cover_letter.tex`. Same gate as the resume: review, audit (light), then *"render the cover letter"* to produce `cover_letter.pdf`. If you have notes about why you want this specific company, drop them in `career_source/notes/<company>.md` before this step — otherwise the letter will defer the "why this company" paragraph to you.

9. **Package**:
   > *"Package the run."*

   `output-packager` writes `run_summary.md` and ensures everything (`.tex`, `.pdf`, evidence, audit, omissions) is in `outputs/<company>_<role>_<date>/`. **If the audit said FAIL or no PDF was rendered, packaging refuses** — fix the CRITICAL flags first, then re-render.

You can also skip the per-step prompts and say:

> *"Run the full pipeline for `job_postings/<filename>`."*

Claude will run analyze → gap → keyword map → tailor → audit, then **stop and show you the `.tex`** for review. After your OK it will render the PDF and continue with cover letter + package. Any decision points (e.g., gap-analyzer says SKIP, audit returns FAIL) are surfaced for you.

---

## What lives where

| Folder | What's in it | When to touch it |
|---|---|---|
| `career_source/` | Your raw inputs: resumes, project notes, education info, certifications | When you write a new project README, add a new course, or finish a cert |
| `career_truth/` | Generated truth DB | Don't edit by hand — rerun `resume-source-truth` |
| `job_postings/` | Postings you've pasted in + their analyses | Drop a new posting here before each application |
| `outputs/<run>/` | Final tailored bundle, one folder per application | Read `run_summary.md` first; send the resume from here |
| `templates/` | `resume_template.tex` — the LaTeX scaffold the tailor fills in | Edit only if you're changing the *visual style* across all future runs |
| `docs/` | This documentation | Update when the process changes |
| `skills/` | The skill files Claude uses | Read if you want to know exactly what each step does |

---

## Tips

- **The truth DB is built from your workspace, including sibling project folders.** When you add a new project (a new Expo app, a new Next.js side project), do `git init && git commit` so the README + manifest are visible, then say *"refresh truth"*. The project will show up in `source_of_truth.md` automatically.
- **Save company-specific notes** in `career_source/notes/<company-slug>.md` before generating cover letters. Without notes, the cover letter will defer the "why you" paragraph back to you — that's a feature, not a bug.
- **Read uncertain_items.md once a month.** As you finish more projects, items move from "uncertain" → "verified" → "on the resume".
- **The auditor is your friend.** A FAIL is not a problem; it's a save. Better to find an unsupported claim before you send than after the interviewer asks about it.

---

## Common pitfalls

- *"The skill said APPLY-IF-FLEXIBLE but I want to apply anyway."* — That's fine. The recommendation is informational. The audit gate is what actually blocks.
- *"The audit FAILed because I want to claim a number that's not in the truth DB."* — Either find a real number, omit the number, or — if it's real but undocumented — go back and add evidence for it to `career_source/` and re-refresh the truth DB.
- *"The keyword map shows 30% coverage."* — That's a posting-fit signal, not a tailor problem. If the gap-analyzer also said SKIP, listen.
- *"A project has two names — which is canonical?"* — Until you tell the system which name is canonical, it will follow the precedent on your most-recent tailored resume for the same role family. Decide once and update `source_of_truth.md`.

---

## When to ask for help

If you don't know what a section of `source_of_truth.md` is claiming or why, just ask Claude:
> *"Where does the truth DB get the claim that recipe-box has 12 endpoints?"*

Claude will look up the evidence pointer and show you the source file + line.
