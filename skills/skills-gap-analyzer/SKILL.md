---
name: skills-gap-analyzer
description: Compare a job posting's required/preferred skills against the verified truth database, returning verified / adjacent / cannot-claim buckets plus an honest hireability read. Use after job-posting-analyzer and resume-source-truth, in parallel with ats-keyword-mapper. The two skills overlap but answer different questions — keyword-mapper is for ATS surface forms; gap-analyzer is for the human-readable "should I even apply?" judgment.
---

# skills-gap-analyzer

## Purpose

Answer two questions for the user:
1. **Should I apply?** — what fraction of the posting's required skills do I genuinely have?
2. **If I apply, where am I going to get pressed in an interview?** — what skills are weak / adjacent / missing?

This is honesty-mode. It is NOT the resume tailor; it does not invent a way to claim a missing skill.

## Inputs

1. `job_postings/<company>_<role>_<date>.analysis.md` — sections 2 (required) and 3 (preferred) are the canonical input.
2. `career_truth/source_of_truth.json` — primary truth source. **Prefer reading the specific section file** (`career_truth/sections/06_skills.md`, `04_projects.md`, etc.) over the full monolith to save tokens. Sections and monolith are kept in sync by `resume-source-truth`.
3. `career_truth/uncertain_items.md` — for the "cannot-claim" floor.

**Code-graph (GitNexus) FIRST for numeric/count claims on indexed projects.** When verifying a skill claim that involves a count (e.g., "N REST APIs built", "N unit tests written"), check the code graph before trusting truth-DB numbers. Tools: `mcp__gitnexus__route_map` (route counts), `mcp__gitnexus__query` (test counts, symbol existence), `mcp__gitnexus__api_impact` (third-party integration counts). MCP tools are deferred — call ToolSearch with `select:<tool_name>` first. Indexed projects + stale flags + not-indexed list live in a shared `indexed_projects.json` registry (use file inspection for any project under `not_indexed`).

## Output

`outputs/<company>_<role>_<date>/skills_gap.md`:

```markdown
# Skills Gap — <Company> <Role>

**Posting source:** <relative path>
**Truth DB:** <date>

## Required skills
| Required skill | Status | Evidence (if verified) / Note (if not) |
| --- | --- | --- |
| Python | Verified | source_of_truth.md §6 — used in the portfolio-dashboard + trade-simulator backends |
| Terraform | Cannot claim | no mention anywhere in the truth DB |
| TDD | Adjacent | Pytest test suites exist (trade-simulator: 76 tests; JUnit on a university team project), but no explicit "tests-first" workflow documented |

## Preferred skills
| Preferred skill | Status | Evidence / Note |
| ... | ... | ... |

## Hireability read
- **Required coverage:** R / R_total verified, X adjacent, Y missing.
- **Preferred coverage:** P / P_total verified, ...
- **Showstoppers** (required-and-missing, posting suggests it's a hard filter): <list or "none">
- **Interview pressure points** (claims that will get probed if you apply): <list, ranked>
- **Honest recommendation:** APPLY / APPLY-IF-FLEXIBLE / SKIP — with one-sentence why.

## What to study before the interview (if applying)
- Top 3 adjacent / missing skills, with concrete starter resources only if the user has explicitly asked for them.
```

## Bucket definitions (strict)

- **Verified** — the skill appears in `source_of_truth.md §6` under "high confidence" AND there is at least one project or certification anchor.
- **Adjacent** — closely related skill OR same skill at lower depth. Examples: posting wants Vue, you have React; posting wants Django, you have FastAPI; posting wants TDD, you have written tests but not test-first.
- **Cannot claim** — listed in `uncertain_items.md` as unclaimable, OR not in `source_of_truth.md` at all, OR only inferred from a course title with no project to anchor it.

## Rules

- Required-skill misses are scored harder than preferred-skill misses. A posting saying "5+ years X" on an internship is a **soft** required (most internship recruiters waive it); a posting saying "must have built a production system in X" on an internship is a **hard** required.
- The "Honest recommendation" line must be a single sentence and one of: `APPLY`, `APPLY-IF-FLEXIBLE` (i.e., you cover required but lack 1–2 preferred), or `SKIP` (you'd be claiming things you don't have to make it past ATS).
- Do not pad the verified count by re-counting the same skill in two rows.
- If `uncertain_items.md` flags a skill as "claimed on resume but unsupported" and the posting requires it, this is a **double-warning** in the report — both an interview risk AND an honesty risk.
- Never recommend `APPLY` if the showstopper list is non-empty.

## Done when

- The `skills_gap.md` file exists.
- Every required AND preferred skill from the posting appears in one of the three buckets.
- The recommendation line is exactly one of the three allowed values.
- Print to the user: `"skills gap: required X/Y verified, preferred A/B verified, recommendation: <verdict>"`.
