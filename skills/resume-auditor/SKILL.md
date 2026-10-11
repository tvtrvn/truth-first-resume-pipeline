---
name: resume-auditor
description: Final hallucination check on a tailored resume draft. Verifies every bullet against source_of_truth, surfaces unsupported claims, checks date/tech consistency, flags ATS issues, and refuses to bless a resume with any unresolved CRITICAL flag. Run as the last step before output-packager.
---

# resume-auditor

## Purpose

Be the truth firewall. Read a tailored resume draft and the truth DB, then produce an audit that says — for every claim — whether the resume is allowed to make it.

The auditor never modifies the resume. It only reports. If flags are CRITICAL, the tailor (or the user) must fix them before packaging.

## Inputs

1. `outputs/<company>_<role>_<date>/tailored_resume.tex` — the LaTeX draft to audit. Get the plain-text view via `python3 scripts/strip_latex.py outputs/<slug>/tailored_resume.tex` before comparing to the truth DB. The script preserves `%% TAILOR: ... %%` markers in the output so this skill can still detect unfilled placeholders — reject the run if any remain.
2. `career_truth/source_of_truth.md` and `.json`
3. `career_truth/uncertain_items.md`
4. `job_postings/<company>_<role>_<date>.analysis.md` — for ATS / posting-fit checks.
5. (Optional) `outputs/<company>_<role>_<date>/keyword_map.md` — for keyword-coverage cross-check.

## Output

`outputs/<company>_<role>_<date>/audit_report.md`:

```markdown
# Resume Audit — <Company> <Role>

**Verdict:** PASS / PASS-WITH-WARNINGS / FAIL
**Generated:** <date>

## Summary
- Bullets audited: N
- CRITICAL flags: A
- WARN flags: B
- INFO flags: C

## CRITICAL flags (must fix before packaging)
| Bullet (truncated) | Issue | Required action |
| --- | --- | --- |
| "Improved query performance by 47% via caching" | metric "47%" not in source_of_truth.json | Replace with verified metric or remove the number |
| ... | ... | ... |

## WARN flags (should fix; not strictly hallucination)
| Bullet | Issue | Suggested action |
| --- | --- | --- |
| "Led a team of 3 engineers" | source_of_truth marks only one course project as a team setting; this bullet is on a solo project | Restate as solo or remove |
| ... | ... | ... |

## INFO flags (cosmetic / ATS)
| Bullet / section | Note |
| --- | --- |
| Skills section | "JavaScript" appears as both "JS" and "JavaScript" — pick one for ATS consistency |
| ... | ... |

## Date sanity
- All experience dates parse cleanly: YES / NO
- No overlap conflicts: YES / NO
- No future dates beyond "expected_end": YES / NO

## Tech consistency
- Every tech in a project bullet appears in source_of_truth.json for that project: YES / NO (list mismatches)
- Framework claimed via certification? → cross-check the certification entry in the truth DB: present ✓

## ATS alignment (if keyword_map.md present)
- Bucket A keywords surfaced on resume: M / N
- Bucket A keywords missing from resume (but available): <list — recommend the tailor add>
- Bucket C keywords mistakenly on resume: <list — must remove>

## LLM-screener readiness (WARN-level — full score in hackerrank_score.md)
- Every listed project surfaces its live/repo link: YES / NO (list any unlinked-but-available)
- Header carries literal GitHub + LinkedIn + portfolio URLs: YES / NO (list missing)
- No named zero-score project pattern on a technical/LLM-screened posting: YES / NO (list offenders)

## Verdict explanation
<one paragraph: why PASS / PASS-WITH-WARNINGS / FAIL>
```

## Flag severity rules

**CRITICAL** (block packaging until resolved):
- Any metric / number / percent / dollar amount / count not in `source_of_truth.json`.
- Any technology claimed on a project bullet that's not in that project's `technologies` list in source_of_truth.
- Any claim of a skill in `uncertain_items.md` Bucket C (cannot-claim).
- Any "team" / "led" / "collaborated with N engineers" claim not backed by an evidence-cited team setup (the truth DB records which projects were genuinely multi-engineer settings). **Carveout:** client communication, stakeholder management, or owner-direction — for example, liaising with a small-business owner to gather requirements — is NOT a "led a team of N engineers" claim and must NOT trip this rule. Flag only explicit claims of leading / collaborating with other software engineers when unsupported.
- Any date that conflicts with source_of_truth (e.g., start of role before its evidenced start month).
- Any project that does not exist in source_of_truth being listed.
- **Page-count overflow.** The resume MUST fit on exactly 1 page (durable style rule). Estimate by counting content lines at the template's geometry — if the draft would spill past 1 page, flag CRITICAL and require the tailor to trim before packaging. Compiling and reading the rendered PDF is acceptable for verification, but tailor-time line-budget estimation should catch most overflows.
- **Mid-word line breaks on proper nouns.** No technology name, product name, framework, or other proper noun may be hyphenated across two lines in the rendered PDF (durable style rule — "MongoDB" once got cut into "Mon-goDB"; never again).

  **Detection procedure** (run AFTER the .tex compiles to PDF):
  ```bash
  python3 scripts/check_hyphen_breaks.py <file>.pdf
  ```
  The script returns JSON with `offenders` (joined proper-noun tokens that got hyphen-broken across lines) and a `verdict`. If `verdict` is `FAIL`, list each offender and apply the fix paths below.

  **Maintaining the watchlist:** the proper-noun list lives at `scripts/tech_watchlist.txt` — add new proper nouns there as the truth DB grows (one per line, bare alphanumeric tokens only; tokens with dots/slashes/spaces like `Node.js` or `Spring Boot` cannot be hyphen-broken at all because LaTeX breaks on those characters, not within them). Common English-word breaks like `demon-strating`, `informa-tion`, `imple-mented` are correctly ignored because they are not in the watchlist.

  **Fix paths** (tell the tailor, in this order of preference):
  1. Add the term to the `\hyphenation{...}` declaration at the top of the .tex (LaTeX accepts only plain letters there — tokens with dots, slashes, or embedded hyphens must use option 2 or 3).
  2. Wrap the offending occurrence in `\mbox{TermName}` so it can never break.
  3. Restructure the sentence so the term doesn't sit at a line boundary.

  If a proper-noun break is found and not yet fixed, flag CRITICAL.

**WARN** (fix recommended, not strictly hallucination):
- Surface form differs between resume and posting (resume says "React.js", posting says "React") — ATS scanners sometimes care.
- A bullet is technically true but vague ("worked on backend systems") where a more specific version exists in source_of_truth.
- Resume claims "production" but source's `deployment` field is `local-only`.
- Skills row imbalance — one technology dominates while a posting-required tech is absent.
- **Page-fill / dead space on the last page** (durable style rule). After compile, run the shared metrics script:
  ```bash
  python3 scripts/page_metrics.py <resume>.pdf
  ```
  Map `verdict` to flag severity: `PASS` = no flag, `BORDERLINE` = WARN (recommend one filler), `DEAD-SPACE` = WARN-STRONG (recommend tailor add content before final render). Suggested fill order (auditor reports as remediation guidance — tailor executes): Hobbies bullet (from `01_personal.md`) → Strengths bullet → promote 3-bullet project to 4 bullets → 2+ one-liner projects → Concepts row in Tech Knowledge → widen existing Tech Knowledge rows. Page-fill is a WARN (not CRITICAL) because the resume is still legitimate at fill < 0.85 — it just reads as sparse. The 1-page hard ceiling stays CRITICAL.

- **LLM-screener readiness** (cheap truthful fixes an AI resume-scorer rewards — full grading is owned by `hackerrank-resume-scorer`, this is just a gate-time catch). Each missing item below is a WARN, not CRITICAL (the resume is still truthful and valid without it):
  - A project that has a live demo and/or repo in `source_of_truth.json` is listed **without surfacing the link** on the resume. (Unlinked live demos are the most common point left on the table — an LLM scorer docks 30–50% for no link.)
  - The header is **missing any of** the literal GitHub profile URL, LinkedIn URL, or portfolio URL. A missing literal GitHub URL is the strongest WARN here — it blinds a GitHub-aware screener.
  - A **named zero-score project pattern** is present on a technical / `LLM-resume-scorer` / `GitHub-aware` posting (analysis §11): a weather app, or a todo/calculator/basic-CRUD/recipe/note-taking/basic-sentiment project listed as a headline project. Recommend the tailor swap it for a complex-project bullet.

**INFO** (cosmetic):
- Inconsistent bullet length, lazy verbs, double spaces, oxford comma usage. (Don't flood the report — at most 5 INFO flags.)

## Hard rules

- **Audit every bullet.** Do not sample.
- For each bullet, the audit must record the **specific evidence row** in source_of_truth that backs it — or the **specific reason** it is flagged.
- If `source_of_truth.json` lacks an evidence pointer for the bullet's claim, the bullet defaults to **CRITICAL**, even if the claim sounds reasonable.
- Verdicts: `PASS` only if zero CRITICAL and zero WARN. `PASS-WITH-WARNINGS` only if zero CRITICAL and ≥1 WARN. `FAIL` if any CRITICAL.
- The auditor does not auto-rewrite — it tells the tailor what to fix.
- **Code-graph (GitNexus) verification is REQUIRED (not optional) for any numeric claim on an indexed project.** For any bullet naming a specific count (N REST routes, N endpoints, N tests, N-table schema, N commits, N integrations), the auditor MUST verify via the code graph BEFORE accepting or flagging the bullet. Use `mcp__gitnexus__route_map` (route count), `mcp__gitnexus__query` (symbol existence, test count, import lists), or `mcp__gitnexus__api_impact` (third-party integration list). MCP tools are deferred — call ToolSearch with `select:<tool_name>` to load the schema first. DO NOT re-read the project's source files or full README to confirm counts when the graph has the answer in 10-20x fewer tokens. Indexed projects + stale flags + not-indexed list live in a shared `indexed_projects.json` registry (refresh via `mcp__gitnexus__list_repos`, then re-run the indexer and update the JSON). For any project listed under `not_indexed`, fall back to file inspection and note the un-indexed status. If the code graph disagrees with a bullet's count claim, flag CRITICAL (graph is authoritative over truth DB for code-level facts).

## Done when

- The `audit_report.md` file exists.
- Every bullet from the resume appears at least once in the report (either in a flag row or implicitly cleared in the summary count).
- A verdict line is printed exactly once and matches the flag counts.
- Print to the user: `"resume audit verdict: <PASS|PASS-WITH-WARNINGS|FAIL>, CRITICAL=<A>, WARN=<B>, INFO=<C>"`.
