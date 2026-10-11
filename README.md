# truth-first-resume-pipeline

**A hallucination-gated, evidence-cited resume tailoring pipeline built on Claude Code.**

Most LLM resume tools optimize for impressiveness. This one is architected to **refuse
unverifiable claims**: every bullet on the output resume must cite an evidence path in a
verified truth database, a dedicated auditor agent re-verifies every claim independently,
and packaging is **refused** on any unresolved critical flag. The interesting engineering
here is not that an LLM writes resumes — it's the grounding-and-evaluation harness wrapped
around it.

> This is a sanitized snapshot (July 2026; a few examples corrected in October) of a private, personal system. The live pipeline
> contains my transcripts, application history, and personal records, so it stays private.
> Everything in this repo — skill definitions, template, scripts, demo — is the real
> mechanism with personal data replaced by a fictional persona. See [Who built what](#who-built-what)
> and [What changed since this snapshot](#what-changed-since-this-snapshot-october-2026).

## The 90-second version

Read [`demo/`](demo/) in this order:

1. [`demo/posting/`](demo/posting/) — a fictional job posting asking for Docker, which the demo candidate has never used.
2. [`demo/expected_outputs/keyword_map.md`](demo/expected_outputs/keyword_map.md) — every posting keyword bucketed **matched / adjacent / cannot-claim**, each with a truth-DB evidence path. Docker lands in *cannot-claim*.
3. [`demo/expected_outputs/evidence_report_excerpt.md`](demo/expected_outputs/evidence_report_excerpt.md) — every rewritten bullet with its evidence path, what changed, and what was *rejected* as tempting but unsupported.
4. [`demo/expected_outputs/audit_report_REFUSAL.md`](demo/expected_outputs/audit_report_REFUSAL.md) — a deliberately seeded false claim ("Containerized the deployment with Docker and Kubernetes") reaches the auditor. It has no evidence citation. Verdict: **FAIL**. Packaging: **refused**.

A gate that never says no is decoration. This one says no, and the demo proves it.

## Architecture

```
                       ┌───────────────────────────┐
                       │   truth database           │  curated, citation-backed facts;
                       │   (evidence-path cited,    │  includes an explicit
                       │    per-fact confidence)    │  "Cannot claim" section
                       └────────────┬──────────────┘
                                    │  every downstream claim cites into this
        posting ──▶ [1 job-posting-analyzer]          (Sonnet)
                          │
              ┌───────────┴───────────┐        steps 2 and 3 run in parallel —
              ▼                       ▼        both consume only step 1's output
   [2 ats-keyword-mapper]  [3 skills-gap-analyzer]   (Sonnet ∥ Sonnet)
      matched/adjacent/       honest "should I
      cannot-claim buckets     even apply?" read
              └───────────┬───────────┘
                          ▼
        [4 resume-tailor  ──  bullet-evidence-rewriter]   (Sonnet)
           writes LaTeX citing truth-DB only; the rewriter is invoked
           once per project (bullets batched — shared evidence context),
           returns a four-field contract PER BULLET:
           REWRITE / EVIDENCE / CHANGES / REJECTED ALTERNATIVES
                          ▼
        [5 resume-auditor]                                (Sonnet)
           independent agent re-verifies every bullet against the
           truth DB. PASS / PASS-WITH-WARNINGS / FAIL.
           ──▶ FAIL blocks everything downstream.
                          ▼
        [5b hackerrank-resume-scorer]                     (Sonnet)
           scores the resume against an open-source LLM
           resume-screener rubric. ADVISORY — never blocks.
                          ▼
              *** human reviews the .tex — render is user-gated ***
                          ▼
        [6 renderer]  Tectonic → PDF                      (Haiku)
           blocked by two machine gates:
           • page geometry (exactly 1 page blocks; a page-fill check warns)
           • text-extraction gate: no ligature glyphs, no mojibake,
             name/email/keywords must survive extraction verbatim
                          ▼
        [7 output-packager]                               (Haiku)
           refuses to package without the audit PASS and
           every mandatory artifact present
```

Design rules the diagram encodes:

- **Builder ≠ validator.** The agent that writes a claim never grades it. The tailor and
  the auditor are separate agents reading the same primary source.
- **Advisory vs blocking is an explicit decision.** The screener-scorer advises (a low
  score is an honest structural fact); the auditor blocks (an unverified claim is fatal).
  Deciding which failures are fatal is the design work.
- **Model tiering by blast radius.** Judgment stages run on stronger models; mechanical
  stages (render, packaging) run on cheaper ones. The validator is never downgraded.
- **Humans gate irreversible steps.** In this snapshot nothing renders to a PDF until a
  person has read the LaTeX. In the current version the PDF renders automatically once the
  auditor passes, and the irreversible step — submitting an application — stays with the
  person: nothing is ever sent on their behalf.

## The parts worth stealing

**The four-field evidence contract** ([`skills/bullet-evidence-rewriter/`](skills/bullet-evidence-rewriter/)).
Every rewritten bullet ships with its evidence path, what changed, and — most useful —
what was *rejected as tempting but unsupported*. The rejection log is where truth-first
becomes visible.

**The locked spacing contract** ([`templates/resume_template.tex`](templates/resume_template.tex)).
Vertical-spacing values are declared a locked contract in the template itself, with the
rule "fit the content to the spacing, never the spacing to the content" and named
enforcement responsibilities for downstream agents. It exists because a real regression
(negative itemsep producing colliding lines) shipped once. Constraints written in blood
get written down.

**The extraction gate** ([`scripts/extraction_check.py`](scripts/extraction_check.py)).
Found empirically: PDFs rendered with a Type1 font stack extracted "workflows" as
"workﬂows" (U+FB02 ligature) — invisible to humans, fatal to exact-string ATS keyword
matchers. And OTF kern pairs split a heading-size surname after its first capital ("Taylor" extracts as "T aylor") under pypdf-class extractors.
The fix (fontspec, `Ligatures=NoCommon, Kerning=Off`) is pinned in the template, and the
gate makes the property machine-checked on every render instead of hoped-for.

**The "Cannot claim" section** (see [`demo/truth_db/persona.md`](demo/truth_db/persona.md)).
The truth database records what the candidate may *not* say — no production users, no
team-size claims on solo projects. An anti-hallucination system that only lists what's
true is half-built; the other half is enumerating the adjacent claims that are false.

## How do you test a fact-checker?

Seed known-false claims and confirm the gate closes. The demo's refusal artifact is
exactly that test: a poisoned bullet with no evidence citation goes in, a FAIL verdict and
a packaging refusal come out. A gate that passes broken input is worse than no gate,
because it launders bad output with an "audited" stamp.

## Results, honestly labeled

Self-reported, from the private tracker (single candidate, one hiring season, so treat as
anecdote — n=1 cannot attribute outcomes to the pipeline):

- **100+** tracked applications ran through the pipeline end-to-end (May–October 2026)
- the tracker logged **6** applications reaching an assessment stage, **2** reaching an interview
  stage, and **2** offers (one internship, one short project engagement); statuses were last
  refreshed in July
- **every** packaged resume passed the independent auditor with zero unresolved critical
  flags — packaging is refused otherwise. The gate checks claims against the truth database,
  so it cannot catch a wrong database entry: more than a dozen early runs had a critical flag
  that was fixed before packaging, and stale figures from an out-of-date truth entry did reach submitted
  resumes in May–June — which is why the rulings list and lint below exist

## Who built what

I designed and direct this system: the pipeline architecture, the truth-database schema
and its "cannot claim" policy, the gates and their blocking/advisory split, the evidence
contracts, the spacing/extraction invariants, and every rule in the skill files. Claude
(Anthropic) executes under those rules — it drafts, rewrites, audits, and compiles inside
the guardrails, including in this repo's own construction. Treating the AI as the executor
and the human as the accountable architect is not a disclaimer; it is the design.

## Limitations

- Personal productivity system, not a product: no installer, no multi-user story.
- The skill files target Claude Code specifically; porting to another agent runtime means
  rewriting the invocation contracts.
- The screener-scorer models one open-sourced rubric; real ATS/LLM screener weights are
  opaque and vary by vendor.
- Solo-built and solo-validated. The funnel numbers above prove the pipeline *ran*, not
  that it outperforms a hand-written resume — there is no control group.
- The skills reference helper scripts, registries and a truth database that are not included,
  so the chain is readable here, not runnable end-to-end.
- The private version also lets a skill the candidate has confirmed at beginner level appear
  with an explicit "(Basic)" qualifier and flags it for interview study; anything with no
  confirmed familiarity stays off.

## What changed since this snapshot (October 2026)

The files here are the July 2026 snapshot, except the layout revision below. The private pipeline has kept evolving; the
mechanism is the same, the gates are stricter:

- **14 skills** in the live pipeline; the 9 core ones of the tailoring chain are published here.
- **Screener rubric update.** The screener-scorer follows the upstream rubric's revision (five
  axes including AI fluency) and reports a band out of 130, because the screener itself varies
  run to run.
- **One rulings list + a deterministic lint.** Banned or stale claims (wrong dates, retired
  numbers, never-say phrases) live in one rulings file, and a script blocks rendering on any
  hit. Its tests seed a violation of each blocking rule and prove the rule fires.
- **Cut from an audited master.** Each one-page resume is cut from an audited two-page master,
  so most bullets are reused verbatim and only changed bullets need new evidence records.
- **Batch mode and model tiering.** Several postings run stage by stage in parallel; a stronger
  model orchestrates and adjudicates, mid-tier models analyze, tailor and audit, and a cheaper
  model renders and packages.
- **More gates before packaging:** every link on the resume is HTTP-checked, the PDF size is
  capped for applicant-tracking parsers, and a posting's rules on candidates' AI use are
  surfaced to the person before they apply.
- **Layout revision (updated here 2026-10-11).** The page read as crammed and jobs were hard to
  tell apart, so the template now gives jobs and education a two-line header (bold organisation,
  italic title and dates), puts a gap before every entry, and keeps bullets plain (bold only in
  headers and row labels). The page-fill gate now measures how far down the page the text reaches instead of
  counting lines, with its own tests (`scripts/test_page_metrics.py`). The template, that script
  and the tailor, renderer and auditor skills in this repo carry the change.

## Repo map

```
skills/      sanitized Claude Code skill definitions (the 9 skills of the chain)
templates/   the LaTeX resume template with the locked spacing contract
scripts/     machine gates: page geometry + text-extraction checks
demo/        fictional persona, posting, and pipeline artifacts incl. the refusal
docs/        pipeline workflow documentation
```
