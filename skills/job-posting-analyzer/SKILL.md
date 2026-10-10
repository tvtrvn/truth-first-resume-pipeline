---
name: job-posting-analyzer
description: Parse a pasted job posting into a structured analysis — required skills, preferred skills, responsibilities, ATS keywords, and likely evaluation criteria. Use when the user pastes a posting into job_postings/ or says "analyze this posting".
---

# job-posting-analyzer

## Purpose

Convert a free-form job posting into a structured analysis file the rest of the pipeline can consume.

## Input

A file in `job_postings/` (markdown or plain text). The file may include the raw posting plus the user's notes ("they emphasized teamwork", etc.).

## Output

`job_postings/<company>_<role>_<date>.analysis.md` (sibling to the input), with this schema:

```markdown
# Job Posting Analysis — <Company> <Role>

## 1. Identification
- Company:
- Role title:
- Team / org (if stated):
- Location / remote:
- Internship term (e.g., Summer 2026):
- Posting URL (if provided):
- Source file: <relative path>

## 2. Required skills (explicit "must have")
- <skill> [evidence: "<quoted phrase from posting>"]

## 3. Preferred / nice-to-have skills
- <skill> [evidence: "<quoted phrase>"]

## 4. Responsibilities
- <verb-led responsibility> [evidence: "<quoted phrase>"]

## 5. Tech stack mentioned
- Languages:
- Frameworks:
- Databases:
- Cloud / infra:
- Tools / methodologies (Agile, code review, CI/CD, etc.):

## 6. ATS keywords (verbatim, ranked by repetition / emphasis)
1. <keyword> — appears N times
2. ...

## 7. Soft / behavioral signals
- <e.g., "collaborative", "fast-paced", "ownership", "self-starter">

## 8. Evaluation criteria (inferred)
- Hard filters likely applied by ATS:
- Recruiter scan priorities (top of resume real estate):
- Likely interview themes:

## 9. Domain context
- Industry:
- Product type:
- Special context (regulated, infra-heavy, startup, etc.):

## 10. Risks / red flags for this candidate
- Skills the posting requires that the truth database does NOT support
- Anything ambiguous that needs the user's clarification

## 11. Screener type & scoring model
- Primary screener (pick one): `keyword-ATS` / `LLM-resume-scorer` / `GitHub-aware`
- Signals that drove the call: <quoted phrases / platform names>
- GitHub profile likely read by the screener: YES / NO
```

## Rules

- Quote evidence verbatim — never paraphrase a required skill into something it didn't say.
- If the posting says "experience with X **or** Y", record it as `X | Y` (alternates), not both as required.
- "5+ years" requirements on an internship posting → flag as `low priority hard filter` (internship recruiters routinely waive these).
- Keep ATS keywords in the exact form the posting used (case-sensitive surface form matters for some scanners). When the posting uses both "JavaScript" and "JS", record both.
- Do NOT score the candidate's fit here. That's `skills-gap-analyzer`'s job.
- **§11 Screener-type classification (drives how the resume gets optimized downstream).** Two different threat models:
  - `keyword-ATS` (default): a string-matching scanner (Workday, Greenhouse, Taleo, iCIMS, Lever, Dayforce). Optimized via the keyword map. Assume this unless a stronger signal appears.
  - `LLM-resume-scorer`: an AI grades the resume on project complexity, links, and experience rather than keyword hits. Signals: the posting/platform names **HackerRank, CodeSignal, Knockri, HireVue AI, Eightfold, Covey**, or says "AI-powered screening / AI-assisted review / our AI evaluates". (Note: a generic "we may use AI in hiring" EEO disclosure footer is NOT this signal — that language is a legal boilerplate, not evidence of an LLM screener.)
  - `GitHub-aware`: the screener (or a human reviewer the posting describes) inspects the candidate's GitHub/portfolio. Signals: "include your GitHub", "link your portfolio/live projects", "we review your public repos", developer-relations / open-source-heavy roles. This can co-occur with either of the above.
  - When in doubt between keyword-ATS and LLM-scorer, record `keyword-ATS` but set "GitHub profile likely read" to YES if the posting asks for GitHub/portfolio links. The `hackerrank-resume-scorer` runs on every resume regardless; this field just tells the tailor/auditor how hard to weight link-surfacing and complexity-framing vs. keyword density.

## Done when

- The `.analysis.md` file exists next to the source posting.
- Every required/preferred skill has a verbatim evidence quote.
- §11 is filled with a screener-type call (`keyword-ATS` / `LLM-resume-scorer` / `GitHub-aware`) and the signals behind it.
- A short summary is printed: "N required, M preferred, K ATS keywords, R risks, screener: <type>".
