# Demo — the pipeline on a synthetic candidate

Everything in this folder is fictional: the candidate (Ada Nguyen), her
university (Lakeshore University), her employer, her projects, and the company
posting the job (Harbourline Financial). No real person's data appears here, and any resemblance to a real company is coincidental.
The artifacts are written to look exactly like real pipeline output, because
that is what they demonstrate.

## The 90-second reading order

1. **`posting/harbourline_backend_intern.md`** — a backend internship asking
   for Python, REST APIs, SQL, Docker, CI/CD, teamwork. Note Docker is a
   *required* qualification.

2. **`expected_outputs/keyword_map.md`** — the ats-keyword-mapper sorts the
   posting's keywords into three buckets against Ada's truth DB
   (`truth_db/persona.md`): Python/REST/SQL are **matched** with evidence
   paths; CI/CD is **adjacent** (her GitHub Actions workflow runs tests, so
   she may claim CI but not the D); Docker is **cannot-claim** — she has no
   container evidence, so the word is banned from the resume outright.

3. **`expected_outputs/evidence_report_excerpt.md`** — how bullets get
   written. Every bullet ships with a four-field contract: the rewrite
   (≤130 chars, X-as-measured-by-Y-by-doing-Z), its evidence paths, what
   changed, and — the interesting field — what was *rejected*. You can watch
   the writer be tempted by "used by 100+ home cooks" and turn it down for
   lack of evidence.

4. **`expected_outputs/audit_report_REFUSAL.md`** — the point of the whole
   system. We deliberately seeded a false bullet ("Containerized the
   deployment with Docker and Kubernetes") into Ada's draft. The auditor finds
   it has no truth-DB citation, cross-checks the cannot-claim bucket, marks it
   CRITICAL, returns **FAIL**, and the packager refuses to produce output.
   One fabricated line stops the entire pipeline.

## Why the refusal matters

Most LLM resume tools optimize for impressiveness: give them a posting and a
resume, and they will happily bridge any gap with plausible-sounding claims.
This pipeline is architected to refuse instead. Every claim must trace to an
evidence path in a truth database built before tailoring begins, and the
auditor that grades the draft is a separate agent from the writer that
produced it — because the agent that writes a claim cannot be trusted to grade
it. When evidence is missing, the honest outputs are a hedged adjacent claim
or a refusal, never an invention. The FAIL report in this folder is the
system working as designed.
