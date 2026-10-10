---
name: ats-keyword-mapper
description: Map a job posting's keywords to verified evidence in the truth database. Outputs a three-bucket table (matched / adjacent / cannot-claim) so the resume tailor knows which keywords are safe to surface. Use after job-posting-analyzer and resume-source-truth, before resume-tailor-no-hallucination.
---

# ats-keyword-mapper

## Purpose

Take the posting's ATS keyword list and decide, keyword-by-keyword, **what evidence we have for it in `career_truth/`** — so the resume tailor never claims a keyword we can't defend.

## Inputs

1. `job_postings/<company>_<role>_<date>.analysis.md` — produced by `job-posting-analyzer`. The "§6 ATS keywords (verbatim, ranked)" list is the input we walk.
2. `career_truth/source_of_truth.json` — primary lookup target (machine-readable, has confidence levels). **Prefer reading the specific section file** (`career_truth/sections/06_skills.md`, `04_projects.md`, etc.) over the full monolith to save tokens. The monolith and sections are kept in sync by `resume-source-truth`.
3. `career_truth/source_of_truth.md` — for evidence-pointer quotes (use section file when possible).
4. `career_truth/uncertain_items.md` — to detect keywords we already know are not claimable.

**Code-graph (GitNexus) FIRST for numeric/count claims on indexed projects.** For any keyword that implies a count (e.g., "REST API experience" where the number of routes matters, "unit testing" where test count anchors the claim), verify the count via the code graph BEFORE trusting a number in the truth DB. Tools: `mcp__gitnexus__route_map` (route counts), `mcp__gitnexus__query` (test counts, symbol existence), `mcp__gitnexus__api_impact` (integration counts). MCP tools are deferred — call ToolSearch with `select:<tool_name>` first to load the schema. Indexed projects + stale flags + not-indexed list live in a shared `indexed_projects.json` registry (use file inspection for any project under `not_indexed`).

## Output

`outputs/<company>_<role>_<date>/keyword_map.md`:

```markdown
# Keyword Map — <Company> <Role>

**Posting:** <relative path to analysis.md>
**Truth DB version:** <date last regenerated>

## A. Matched (safe to surface)
| Posting keyword | Evidence in truth | Where it should appear on the resume |
| --- | --- | --- |
| Next.js | ordering-platform (Experience), video-browser-app (Project tech) — `[evidence: source_of_truth.md §3 Experience, §4.8]` | Experience bullet + Skills row |
| ... | ... | ... |

## B. Adjacent (close but not exact — surface only with caveat)
| Posting keyword | Closest evidence | Caveat the tailor must respect |
| --- | --- | --- |
| GraphQL | REST APIs across multiple projects — *not* GraphQL | Do not list "GraphQL". List "REST APIs" instead and surface in Skills only if the posting accepts REST. |
| ... | ... | ... |

## C. Cannot claim (DO NOT use as a keyword)
| Posting keyword | Why it cannot be claimed | Action |
| --- | --- | --- |
| Terraform | no mention anywhere in the truth DB | Omit. If the posting treats it as a hard filter, surface it to the user as a gap. |
| ... | ... | ... |

## D. Coverage summary
- Posting required keywords matched: M / N (X %)
- Posting preferred keywords matched: P / Q (Y %)
- Hard filters at risk: <list, with which bucket each lands in>
- Recommended top-of-resume keyword cluster (4–6 from bucket A, ordered by posting emphasis): ...
```

## Rules

- **One row per posting keyword.** Do not skip a keyword just because it's awkward. If it's in the posting's "ranked ATS list", it goes in the map.
- Every Bucket A row MUST carry an evidence pointer back to `source_of_truth.md` or `.json`. No pointer → it doesn't belong in Bucket A.
- Surface-form matters for ATS scanners. If the posting writes "JavaScript" and the truth file writes "JS", record the posting's surface form and note in the resume tailor's instructions to spell it out as "JavaScript".
- Bucket B is for keywords where evidence is **related** (e.g., posting says "Vue", truth has "React" — both component-based UI frameworks, but **not interchangeable as a keyword claim**). Use sparingly; when in doubt, downgrade to Bucket C.
- Bucket C is non-negotiable: if `uncertain_items.md` says we can't claim it, we can't.
- If a keyword in the posting has alternates (`X | Y`), score each alternate separately and report the better of the two buckets.
- Do NOT invent skills to inflate Bucket A. Bucket coverage % is allowed to be low — that's the gap signal, not a reason to lie.

## Done when

- The `keyword_map.md` file exists in `outputs/<company>_<role>_<date>/`.
- Every posting keyword from §6 of the analysis appears in exactly one of A / B / C.
- The coverage summary lists hard-filter risks explicitly.
- A short print to the user: `"keyword map written: A=<n> matched, B=<n> adjacent, C=<n> cannot-claim, hard filters at risk: [list]"`.
