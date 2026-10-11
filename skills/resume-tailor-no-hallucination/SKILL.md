---
name: resume-tailor-no-hallucination
description: Produce a tailored resume for a specific posting using only verified facts from the truth database. Use when the user says "tailor resume for <posting>", "write a tailored resume", or "apply this posting".
---

# resume-tailor-no-hallucination

## Purpose

Generate a tailored, ATS-friendly resume for one posting, drawing **only** from `career_truth/source_of_truth.json` and the posting analysis.

## Inputs

1. `career_truth/source_of_truth.json` (run `resume-source-truth` first if missing or stale).
2. A `*.analysis.md` from `job_postings/` (run `job-posting-analyzer` first).
3. `templates/resume_template.tex` — the LaTeX scaffold to fill in (required).

## Hard rules

- **No fact appears in the tailored resume unless it appears in `source_of_truth.json` with confidence `high` or `medium`.** `low`-confidence items are forbidden in the resume body.
- **No new metrics.** If the posting says "scaled to 1M users", the tailored resume does NOT claim a user count unless the truth database already has one.
- **Action verbs only on actions in evidence.** Don't write "Led a team" if no source says the candidate led a team.
- **Tech stack per bullet must be a subset of that project's `technologies` array** in the truth database.
- Coursework appears only if (a) the posting cares about coursework AND (b) the truth database has it with `high` confidence.
- Preserve chronology — most recent first within each section.
- **Hard rule: 1 page maximum, always.** Durable style rule. Even when a posting permits 2+ pages, the tailored resume MUST fit on 1 page. Trim aggressively — drop the weakest project, cut secondary bullets, and tighten language before ever spilling to a second page. Switching to 2 pages requires the user to explicitly override the preference in the current session; do not infer permission from a posting's stated page allowance.

## Leading-project rule

On any posting whose primary domain is AI, automation, agentic, orchestration, RAG, pipeline, workflow, or data (including analyst/analytics/ML/data-engineering roles), the truth DB's flagship **AI-automation portfolio entry MUST appear as the first project** in the Projects section. This is a hard ordering rule — do not place another project above it regardless of keyword overlap score.

## Google XYZ bullet formula

Every bullet MUST map to the structure: **"Accomplished [X] as measured by [Y] by doing [Z]."**
X = the outcome (what changed or was achieved). Y = how it is measured or evidenced (metric, status, artifact). Z = the method or action.

**Before (BAD):** "Built defense-in-depth middleware with rate limits and TTL pruning."
**After (XYZ):** "Passed 76 tests across 4 suites [Y] and hardened the API [X] with per-IP rate limits (120 req/min), a 64 KB body cap, security headers and a daily cron for price refresh and 30-day TTL cleanup [Z]."

**Before (BAD):** "Added authentication to the ordering platform using HMAC-SHA256."
**After (XYZ):** "Hardened session handling [X] on a production ordering platform [Y] with HMAC-SHA256 signed, HttpOnly, SameSite, Secure session cookies checked in constant time [Z]."

Not every bullet yields a clean Y measurement. When there is no numeric metric, use a status anchor ("since launch", "production", "zero reported issues") or a scope anchor ("across 8 REST routes", "across all 12 tracked securities"). Never invent a number.

## AI-orchestration voice rule

The **user is always the actor; AI is always the tool.** Bullets that mention AI usage must frame the user as the decision-maker and orchestrator.

**Forbidden pattern:** "AI-assisted development of X" / "leveraged AI to write Y" / "used Claude to generate Z" — these make AI the subject and the user a passive beneficiary.

**Required pattern:** "Orchestrated [Claude Code / MCP agents / multi-agent pipeline] to [outcome]" — user is the subject, AI is the instrument.

**Worked transformation (recipe-box context):**
- BAD: "AI-assisted scaffolding of a recipe-manager API using Claude."
- GOOD: "Orchestrated Claude Code agents to build a 12-endpoint Flask recipe API, verified by 34 passing pytest tests." (the demo persona's recipe-box — every number is in its truth DB)

Apply this rule consistently in both bullet drafting and `bullet-evidence-rewriter` output.

## Bullet quality rules (audit P1 — non-negotiable)

- **No README-as-bullet.** Never credit "documented architecture in a README" or "wrote a 200-line README" as a resume bullet. Documentation is process, not outcome. If the README demonstrates something verifiable (e.g., a live URL or architecture decision), surface THAT outcome instead.
- **Synthetic-metric ban.** A simulated dollar figure (e.g., a portfolio simulator's "$X million under management" — a random-walk constant) triggers credibility flinch in interviewers. Drop it — do not substitute another scale number (describe the simulated scope plainly, e.g. "sample portfolios over simulated securities"). Never use a simulated dollar figure anywhere in the resume or cover letter.
- **Role-differentiated bullet variants.** For a flagship project, maintain per-audience variants of one bullet and select exactly one based on posting type. Worked example — a family restaurant's ordering platform (live production site), bullet 3:
  - SWE / AI / security posting: "Hardened the platform with HMAC-SHA256 signed, HttpOnly session cookies, constant-time comparison and per-endpoint rate limits."
  - BA / product / ops posting: "Shipped owner-editable menu management (sold-out toggles, price overrides, photo uploads) so the non-technical owner can update the menu without a developer or redeploy."
  - Data / analytics posting: the data-model / analytics-schema variant, drawn from that project's truth-DB entry.
  Pick exactly one variant per run — never mix two in the same resume.

## LLM-screener optimization (truthful levers — additive, never override the rules above)

Modern screeners increasingly include an **LLM resume-scorer with GitHub awareness** (modeled on HackerRank's open-source
`hiring-agent` — see the rubric reference in `hackerrank-resume-scorer`). That scorer grades on
project complexity, **working links**, and real experience — NOT keyword density — and reads the candidate's GitHub. The
levers below recover real points for free. They are all **truthful surfacing** moves, never fabrication, and they yield to
every hard rule above (1-page ceiling, LOCKED spacing contract, XYZ, the audience-gated experience rule — surface a
non-technical role, e.g. a retail distribution centre role, only on postings where it is audience-relevant — the leading-project
rule, no-new-metrics).

1. **Surface a working link on every project that has one.** The scorer gives projects with **no link 30–50% lower** scores
   and **live demos +10–20%**. Render the live URL and/or repo inline in the project header (the template already supports
   left-side GitHub/Live links — layout section). Use the exact URLs from `career_truth/sections/04_projects.md`
   (e.g. `ordering-platform-demo.example.com`, `recipe-box-demo.example.com`, `trade-sim-demo.example.com`). A project
   with a real live demo that the resume fails to link is the most common point left on the table.
2. **Header always carries three literal URLs:** GitHub profile (`github.com/ada-nguyen-demo`), LinkedIn (`linkedin.com/in/ada-nguyen-demo`),
   and a portfolio URL — as real selectable text, not bare words. This (a) earns +2 (portfolio) +1 (LinkedIn) bonus and
   (b) is what lets a GitHub-aware screener find the profile at all. A missing literal GitHub URL collapses the entire
   35-pt Open Source axis to the floor.
3. **LLM-scorer project blocklist (on technical / `LLM-resume-scorer` / `GitHub-aware` postings — see analysis §11).** Never
   list a thin weather-app project — it is a *literally named zero-score pattern* in the rubric ("weather apps using public
   APIs") and *costs* points via deductions. Avoid the other named simple-project patterns as headline projects: todo,
   calculator, basic CRUD, note-taking, recipe, exercise, basic NLTK/scikit-learn sentiment, "Hello World", classroom
   assignments. If a thin project is the only way to fill the page, prefer a 4th bullet or a one-liner on an already-listed
   COMPLEX project instead. (On a non-technical / pure keyword-ATS posting the blocklist relaxes — a weather app can still
   carry a keyword — but never lead with it.)
4. **Frame complex projects with the rewarded vocabulary — only where the truth DB supports it.** The scorer rewards
   "full-stack with **authentication and databases**", "**real-time**", "**microservices**", "ML/AI", "advanced algorithms",
   "solves real-world problems". If the portfolio dashboard and trade simulator genuinely are full-stack + auth/DB +
   cron/real-data — say so plainly. Do NOT attach this vocabulary to a project whose `technologies`/`features` don't back it.
5. **Surface truthful production / startup signals.** The scorer gives extra Production points for **early-stage engineer
   (first 10–20 employees)** and founder roles, and credits real production work. Frame any genuinely early-stage or production role
   exactly as its truth-DB experience section records it — e.g., a family restaurant's ordering platform as a production
   role on a live business (pay is never a resume fact). Never invent a founder title or a headcount that isn't in evidence.

**Honest ceiling (do not engineer around it):** every workspace repo is solo, so an LLM scorer hard-caps Open Source at
≤10/35 and there is no GSoC to claim. That gap is real; the tailor's job is to **maximize the other three axes + bonus with
what genuinely exists**, not to manufacture open-source contributions. The `hackerrank-resume-scorer` reports the resulting
score and any remaining truthful fixes after the draft is built.

## Code-graph verification for numeric claims

Any numeric claim about an indexed project (route count, test count, endpoint count, table count, commit count, function count) **MUST be verified via the code graph (GitNexus) BEFORE the bullet is written.** Use:
- `mcp__gitnexus__route_map` → REST route counts and names
- `mcp__gitnexus__query` → symbol existence, test count, import lists
- `mcp__gitnexus__api_impact` → third-party integration counts

MCP tools are deferred — call `ToolSearch` with `select:<tool_name>` first to load the schema. Do NOT write a count from memory or truth-DB alone when the graph can confirm it in one query.

Before writing any bullet citing an indexed-project count, check the shared `indexed_projects.json` registry for the current `commits_behind` status. If the target project is marked `stale: true` or appears in `not_indexed`, EITHER call `mcp__gitnexus__list_repos` for fresh state OR document the staleness in `evidence_report.md`. The auditor enforces this same check at audit time (see `resume-auditor` SKILL.md).

## Selection logic

1. Read the posting analysis. Build a ranked keyword list (required > preferred > responsibilities > nice-to-have).
2. For each project in the truth database, score = sum of keyword hits across `technologies`, `features`, and existing bullets.
3. Pick **2–3 major projects** (highest scoring) for the Projects section — calibrated for 1-page fit. Each major project gets its own header + bullets block. Apply the leading-project rule: on AI/automation/agentic/orchestration/RAG/pipeline/workflow/data postings, the AI-automation portfolio entry is always first regardless of score.
4. For each picked major project, write **exactly 3 bullets** by default (4 only when the content is genuinely loaded AND there is page room). Target ~22 words per bullet so each wraps cleanly to ~2 lines without orphan stub words. Never split a substantial project into 2 long bullets; 3 medium bullets reads better (durable style rule). Apply the Google XYZ formula (X=outcome, Y=measure, Z=method) to every bullet where a Y anchor exists.
5. After the main projects, optional **one-liner projects** may surface keyword adjacencies. Format: single bold name + colon + one-sentence description, NO bullets. **Use only when at least 2 one-liners can be placed together** (a single isolated one-liner looks out of place against the bulleted projects above — durable style rule). Skip entirely if the keyword adjacency is already covered by the Technical Knowledge row or coursework.
6. **Invoke `bullet-evidence-rewriter` once per PROJECT (batched), not once per bullet.** All of a project's drafted bullets (1–4) go in a single invocation, since they share the same KEYWORDS and PROJECT TECH context; the 2–3 project batches are independent and may run as parallel Agent calls. Input contract per invocation:
   ```
   KEYWORDS: <ranked keyword list from posting analysis>
   PROJECT TECH: <technologies array for this project from source_of_truth.json>
   BULLET 1 ORIGINAL: <drafted bullet text>
   BULLET 1 EVIDENCE: <evidence pointer(s) from truth DB — path:line and quote>
   BULLET 2 ORIGINAL: ...
   BULLET 2 EVIDENCE: ...
   ```
   The skill returns one complete REWRITE / EVIDENCE / CHANGES / REJECTED ALTERNATIVES record **per bullet** — the per-bullet four-field contract is unchanged; only the invocation transport is batched. Each bullet's EVIDENCE must cite only its own input evidence (no borrowing across bullets in the batch — the auditor verifies each bullet independently and will catch cross-contamination). Use each REWRITE as the final bullet text. Append every four-field record to `evidence_report.md` using the format defined in `templates/evidence_report.md`. The `bullet-evidence-rewriter` enforces the Google XYZ formula and AI-orchestration voice rule automatically.
7. Education section: minimal — one two-line `\entry{School}{Location}{Degree}{Dates}` header, then 2 bullets at most (Relevant Courses, Certifications). Intersect coursework with posting keywords.
8. Technical Knowledge section: 4-bullet list at the bottom (Programming, Frameworks, Tools, Platforms). Put the items the current posting prioritizes first within each row (row labels are the only bold). Include an **AI Workflow** row on AI/automation postings listing: Claude Code, MCP agent integration, prompt engineering, AI skill authoring. (NEVER list consumed third-party tools such as code-graph indexers — the resume lists capabilities the candidate authored; durable style rule.)
9. Work Experience section: include only if the candidate has real-world experience that is itself high-signal. **Always position above Projects** (durable style rule).
10. Additional Information section: bulleted list with Languages always shown (the candidate's spoken languages, verbatim from the truth DB); optional second bullet for Concepts or Strengths if space permits.
11. After drafting, **compile with Tectonic for page-count verification ONLY** (this is NOT the final render — see note below). Check page count via the shared script:
    ```bash
    python3 scripts/page_metrics.py outputs/<slug>/tailored_resume.pdf
    ```
    Parse `page_count` from the JSON output. Do NOT use `mdls kMDItemNumberOfPages` — it lags ~2s after a fresh write and produces stale results. If `page_count > 1`, trim and recompile until 1. This compile step is for page-count verification only; the user-gated final render is done by `latex-to-pdf-renderer` after auditor passes.
12. **Page-fill check (durable style rule).** Both ends of the page are hard rules: never spill past 1 page, AND never leave the bottom half-empty. The `page_metrics.py` call from step 11 already returns `last_page_fill` (how far down the text area the last line sits) and `verdict` in the same JSON — re-use that output; no need to re-run. Fill replaced a line count on 2026-10-11 because two-line entry headers and entry gaps make line counts depend on how many entries a page has. Verdict mapping:
    - `PASS` (fill ≥ 0.93) — the page is full, no action.
    - `BORDERLINE` (0.85–0.93) — add one filler if you can.
    - `DEAD-SPACE` (< 0.85) — MUST add content.

    Fill order (stop at the first that produces a clean fill, truth-DB only):
    1. **Hobbies bullet** under Additional Information — pull verbatim from `career_truth/sections/01_personal.md` Hobbies field.
    2. **Strengths bullet** — only if verifiable in truth DB and posting-relevant.
    3. **Promote a 3-bullet project to 4 bullets** — only if truth DB has additional strong evidence; never pad an existing bullet.
    4. **Surface 2+ one-liner projects together** (a single isolated one-liner is forbidden — durable style rule).
    5. **Add a Concepts / Methodologies row** to Technical Knowledge from §6 unused entries.
    6. **Widen Technical Knowledge rows** with 2–3 more genuine items per row.
    7. **Add Certifications inline** in Education from §5 if not already listed.

    Forbidden fills: increasing font size or line spacing, padding bullets with adjectives, inventing hobbies/achievements, adding a redundant Summary/Objective block, repeating skills across sections. Recompile after filling and re-measure; iterate until the last page's fill is ≥ 0.93 — **capped at 3 fill/trim iterations total** (the trim→fill→trim oscillation between the 1-page ceiling and the fill floor is structurally possible and each lap costs model turns). After the 3rd iteration, stop and document the remaining gap in `run_summary.md` — that escape hatch is the designed exit, not a failure.

    **Spacing is NOT a fitting lever — in either direction (hard rule, regression-proofed).** The template carries a LOCKED SPACING CONTRACT (titlespacing 8/3pt, a 6pt gap before every entry, itemsep/topsep 1.5pt, margin 0.5in, 10pt font — revised 2026-10-11). To make content FIT one page you trim content (drop the weakest bullet/project, tighten wording toward ~22 words/bullet) — you do NOT shrink titlespacing/itemsep/topsep, push them negative or below 1pt, narrow the margin, or drop the font. Negative or sub-1pt spacing is what makes bullets collide and the page look squished; it is banned. Symmetrically, to FILL a page you add truthful content, never inflate spacing/font. Land between the fill floor (≥ 0.93) and the 1-page ceiling by adjusting CONTENT only; a full page holds roughly 43–50 lines under this layout.

## Layout

Use `templates/resume_template.tex` as the scaffold. The template implements a classic single-column serif layout (durable style rule):

- **Section order (top to bottom):** Header (name + contact + one-line italic tagline) → Education → Work Experience → Projects → Technical Knowledge → Additional Information. Experience always above Projects.
- **Header:** large bold black serif name, single-line contact with `|` separators, then a one-line *italic* professional tagline grounded in truth-DB evidence (no aspirational claims).
- **Section headers:** bold serif title case, thin rule beneath. NOT colored, NOT uppercase.
- **Entry headers (layout rule 2026-10-11 — entries must be easy to tell apart):** jobs and education use the two-line `\entry{Organisation}{Location}{Title}{Dates}` (bold organisation, plain location, then italic title + dates); links in the organisation field go inside `\textnormal{...}`. Projects use the one-line `\rolerow{\textbf{Name}, links}{Dates}`. Both put a 6pt gap before every entry. If a header line wraps, trim content — never widen the page.
- **No bold inside bullets** (same rule): bold appears only in the name, section titles, entry headers, project names and row labels, so the entry headers stand out.
- **Disallowed content (durable style rule):** internal-refactor war stories (e.g., a payment-provider removal) as bullets on the flagship production project — that work is interview-discussion material only.

Every `%% TAILOR: ... %%` marker in the template must be replaced or the placeholder block removed. Do NOT add new sections, new packages, or restyle the template — only fill content. The preamble's SPACING CONTRACT (titlespacing / itemsep / topsep / margin / font) is off-limits: never edit those values to hit a page target.

## Output files (in `outputs/<company>_<role>_<YYYY-MM-DD>/`)

- `tailored_resume.tex` — the filled LaTeX file (one page, ATS-friendly content).
- `evidence_report.md` — bullet-by-bullet justification (see `bullet-evidence-rewriter` and `templates/evidence_report.md`).
- `omissions.md` — list of posting keywords intentionally NOT claimed, with the reason ("no project evidence", "low confidence", etc.).

**Clarification on PDF compilation:** this skill compiles with Tectonic **once, for page-count verification only** (step 11). That intermediate PDF is a draft measurement artifact — do NOT hand it to the user as a deliverable. The final, user-visible PDF is produced by `latex-to-pdf-renderer` after:
1. The user reviews `tailored_resume.tex`.
2. `resume-auditor` returns `PASS` or `PASS-WITH-WARNINGS`.
3. The user explicitly says "render" / "compile" / "looks good — make the PDF."

Never skip this gate and never present the page-count-check PDF as the final output.

## Done when

- `tailored_resume.tex` exists, compiles cleanly in principle (no leftover `%% TAILOR:` markers), every project bullet traces to evidence.
- The draft is calibrated to fit **1 page** at the template's geometry. If the line count exceeds the budget, return to the selection step and cut before declaring done.
- `evidence_report.md` exists in the run directory AND contains a four-field record for every bullet (produced by `bullet-evidence-rewriter` in step 6). If `evidence_report.md` is missing or incomplete, the skill has NOT completed — produce it before returning.
- `omissions.md` lists all posting keywords intentionally not claimed.
- A summary is printed: "X projects selected, Y bullets, Z keywords claimed, W keywords intentionally omitted, page-count target: 1".
- **`resume-auditor` is invoked next**, then **`hackerrank-resume-scorer`** (the standing LLM-screener check — produces `hackerrank_score.md`, advisory; apply its cheap truthful fixes back into the draft if any). Then the user reviews the `.tex` and explicitly approves rendering via `latex-to-pdf-renderer`.
