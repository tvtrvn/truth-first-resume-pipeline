---
name: output-packager
description: Assemble every artifact from a tailoring run into a single outputs/<company>_<role>_<date>/ folder with a clean manifest. Refuses to package if the resume-auditor returned FAIL. Last step of the pipeline.
---

# output-packager

## Purpose

Take the disparate artifacts a tailoring run produced and put them in one folder with a manifest, so the user can review, send, and archive a single bundle.

## Inputs

All artifacts that should already exist in `outputs/<company>_<role>_<date>/` or in adjacent locations:

| Artifact | Produced by | Required? |
| --- | --- | --- |
| `tailored_resume.tex` | `resume-tailor-no-hallucination` | required |
| `tailored_resume.pdf` | `latex-to-pdf-renderer` | required (no PDF = no package) |
| `{{CANDIDATE}}_Resume.pdf` | this skill | **created here** — submission-ready copy of `tailored_resume.pdf`, named with the candidate's name (keep both files; identical bytes) |
| `evidence_report.md` | `resume-tailor-no-hallucination` | required |
| `keyword_map.md` | `ats-keyword-mapper` | required |
| `skills_gap.md` | `skills-gap-analyzer` | required |
| `audit_report.md` | `resume-auditor` | required |
| `hackerrank_score.md` | `hackerrank-resume-scorer` | required (every run) — advisory LLM-screener score + truthful fixes; mandatory artifact, never a blocker |
| `cover_letter.tex` | `cover-letter-grounded` | optional |
| `cover_letter.pdf` | `latex-to-pdf-renderer` | required if `cover_letter.tex` present |
| `{{CANDIDATE}}_Cover_Letter.pdf` | this skill | **created here** if `cover_letter.pdf` present — submission-ready copy (keep both files) |
| `cover_letter_evidence.md` | `cover-letter-grounded` | required if `cover_letter.tex` present |
| `<company>_<role>_<date>.analysis.md` | `job-posting-analyzer` | required (copy from `job_postings/` into the run folder) |
| `workday_skills.md` | this skill | **required, ALWAYS created (every run, regardless of posting body)** — paste-ready Workday-portal skills list, evidence-backed, **A/B/C as PRIORITY tiers (not categories): one 45-deep posting-relevance ranking split into thirds — A = rank 1–15, B = 16–30, C = 31–45 — each numbered in descending priority**, hard cap 15/15/15 (durable formatting rule). Packager refuses to mark "packaged" without it. |
| `run_summary.md` | this skill | **created here** |

## Output

The same `outputs/<company>_<role>_<date>/` folder, now with a `run_summary.md` index and any missing files clearly flagged.

### run_summary.md schema

```markdown
# Run Summary — <Company> <Role>

**Date:** <YYYY-MM-DD>
**Posting source:** <relative path>
**Truth DB version:** <date last regenerated>

## Verdict
- Resume audit: PASS / PASS-WITH-WARNINGS / FAIL
- Skills gap recommendation: APPLY / APPLY-IF-FLEXIBLE / SKIP
- Keyword coverage: <M/N matched in Bucket A>
- LLM-screener score (advisory): <N>/120 — top truthful fix: <one-liner from hackerrank_score.md>

## What's in this folder
1. [{{CANDIDATE}}_Resume.pdf](./{{CANDIDATE}}_Resume.pdf) — **the file to attach when applying** (identical bytes to `tailored_resume.pdf`)
2. [tailored_resume.pdf](./tailored_resume.pdf) — internal/archival copy
3. [tailored_resume.tex](./tailored_resume.tex) — LaTeX source (re-render if you edit)
4. [evidence_report.md](./evidence_report.md) — bullet-by-bullet justification
5. [keyword_map.md](./keyword_map.md) — ATS keywords mapped to evidence
6. [skills_gap.md](./skills_gap.md) — required/preferred skill coverage + honest recommendation
7. [audit_report.md](./audit_report.md) — final hallucination check
7b. [hackerrank_score.md](./hackerrank_score.md) — LLM-screener (HackerRank-rubric) score + truthful fixes
8. [{{CANDIDATE}}_Cover_Letter.pdf](./{{CANDIDATE}}_Cover_Letter.pdf) (if requested) — **the cover letter to attach** (identical bytes to `cover_letter.pdf`)
9. [cover_letter.pdf](./cover_letter.pdf) (if requested) — internal/archival copy
10. [cover_letter.tex](./cover_letter.tex) (if requested) — LaTeX source
11. [cover_letter_evidence.md](./cover_letter_evidence.md) (if cover letter present) — paragraph-by-paragraph evidence map
12. [&lt;analysis file&gt;.md](./...) — copy of the posting analysis used as input

## Why specific bullets were chosen
- Bullet "A" was prioritized because the posting emphasized X (analysis §2 evidence).
- Bullet "B" was prioritized over the equally-true "B'" because B has a number and matched ATS keyword "Y".
- ...

## What was intentionally omitted (and why)
- Did NOT claim "Terraform" — no evidence in the truth DB.
- Did NOT claim a personal connection to the company — career_source/notes/<company>.md not provided.
- Did NOT use a simulated dollar figure from a demo project — would be misleading on a resume.
- ...

## Open items for next time
- <e.g., "Add career_source/notes/<company>.md before the next application for this company so the cover letter has an anchor.">
```

## Hard rules

- **REFUSE TO PACKAGE if `audit_report.md` verdict is `FAIL`.** Print which CRITICAL flags blocked it. The user must rerun `resume-tailor-no-hallucination` after fixing.
- **REFUSE TO PACKAGE if `tailored_resume.pdf` is missing or older than `tailored_resume.tex`.** The user must re-run `latex-to-pdf-renderer` after editing the `.tex`.
- **REFUSE TO PACKAGE if `hackerrank_score.md` is missing.** It is produced every run by `hackerrank-resume-scorer` (the standing LLM-screener check). Its *content* is advisory — a low score never blocks packaging — but the *artifact* is mandatory, same contract as `workday_skills.md`. If it is missing, run `hackerrank-resume-scorer` before packaging.
- **REFUSE TO PACKAGE if `workday_skills.md` is missing.** Generate it as part of the packaging step — every run, regardless of what the posting body says. The Workday/Dayforce "Skills" field exists on every Workday portal whether the posting mentions it or not. **Groups are PRIORITY tiers, not categories:** build one 45-deep ranking by relevance to THIS posting (rank 1 = most posting-critical), then split — A = rank 1–15, B = 16–30, C = 31–45 — each group numbered in descending priority. Hard caps: Group A ≤ 15, Group B ≤ 15, Group C ≤ 15 (rank by relevance, no filler-padding to hit 15). A/B strict evidence floor; C may add adjacency Bucket B terms with a gap note; never cannot-claim.
- **ALWAYS produce a candidate-named copy.** After all audit checks pass, copy `tailored_resume.pdf` to `{{CANDIDATE}}_Resume.pdf` in the same folder (keep BOTH files — `tailored_resume.pdf` stays as the canonical/archival name; the candidate-named copy is the submission file). If a cover letter PDF exists, also copy `cover_letter.pdf` → `{{CANDIDATE}}_Cover_Letter.pdf`. Use `cp` (not `mv`) so the originals remain. Verify byte-identical with `cmp` after copying.
- If a "required" artifact is missing, do NOT silently package. Print the list of missing files and stop.
- The packager does not rewrite any of the artifacts — it only indexes them (and renders the PDF per the auto-render rule). In particular it MUST NOT edit `tailored_resume.tex`.
- **NEVER crush spacing to force a 1-page fit (hard rule, regression-proofed).** If the rendered PDF is 2 pages, the packager's ONLY valid response is to REFUSE and bounce back to `resume-tailor-no-hallucination` to trim **content**. Do NOT "fix" overflow by narrowing the margin, shrinking the font, or reducing `titlespacing`/`itemsep`/`topsep` — and never push any of those negative or below 1pt. Negative/sub-1pt spacing produces the squished, overlapping-line resume the user explicitly rejected; the template's LOCKED SPACING CONTRACT is off-limits to every skill. Fit is a content problem, owned by the tailor, never solved here.
- **ALWAYS sweep stray pipeline siblings before declaring done.** After `run_summary.md` is written and the submission-named PDFs are in place, run the cleanup script (`cleanup-job-postings`) to remove any staging copies of `<slug>.analysis.md`, `<slug>.keyword_map.md`, `<slug>.audit.md`, etc. left behind in `job_postings/` by the upstream pipeline skills. The packager owns the end-of-pipeline contract — `job_postings/` must be left holding only the base posting `<slug>.md`. (A Stop hook also runs this as a safety net, but the packager should not depend on it firing.)
- Filenames inside the run folder MUST be relative-link-able from `run_summary.md` (no spaces in names; use `<company>_<role>_<date>` directory naming convention).
- `<company>` and `<role>` slugs: lowercased, hyphenated, ASCII only. Example: `acme-corp_swe-intern_2026-05-13/`.

## Done when

- `run_summary.md` exists in the run directory and links every artifact.
- `{{CANDIDATE}}_Resume.pdf` exists alongside `tailored_resume.pdf` in the run directory and is byte-identical (verified via `cmp`). If a cover letter PDF was produced, `{{CANDIDATE}}_Cover_Letter.pdf` is also present and byte-identical to `cover_letter.pdf`.
- `workday_skills.md` exists in the run directory (mandatory, every run).
- `hackerrank_score.md` exists in the run directory (mandatory, every run; advisory content).
- The cleanup sweep has run; `job_postings/` contains only the base `<slug>.md` for this run (no sibling-suffixed staging copies).
- A printed list to the user: `"packaged at <path>, audit=<verdict>, gap=<verdict>, files=<n>"`.
- If FAILed: a printed `"refused to package: <reason>"` and the run directory is left unchanged.
