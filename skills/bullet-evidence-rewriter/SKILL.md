---
name: bullet-evidence-rewriter
description: Rewrite an individual resume bullet to be tighter and more keyword-aligned, while preserving truth and citing evidence. Use when the user wants to "rewrite this bullet", "tighten these bullets", or as a sub-step of resume-tailor-no-hallucination.
user-invocable: false
---

# bullet-evidence-rewriter

## Purpose

Given (a) an original bullet, (b) the posting's keyword list, and (c) the underlying evidence, produce a tighter, stronger bullet — without inventing anything.

**Wired-in role:** this skill is invoked by `resume-tailor-no-hallucination` **once per project during step 6, with all of that project's bullets batched into the one invocation** (was once per bullet; the bullets share KEYWORDS + PROJECT TECH, so batching dedupes the shared context and cuts 6–12 agent calls per run to 2–3). It is NOT a standalone skill in the normal pipeline. The tailor passes the batched input contract; the rewriter returns one four-field output record PER BULLET; the tailor appends every record to `evidence_report.md` using the format in `templates/evidence_report.md`.

## Input contract

One invocation per project, 1–4 bullets per invocation:

```
KEYWORDS: <ranked list from the posting analysis>
PROJECT TECH: <subset of technologies for this project, from truth DB>
BULLET 1 ORIGINAL: <existing bullet text>
BULLET 1 EVIDENCE: <path:line(s) + the relevant quote from the source>
BULLET 2 ORIGINAL: ...
BULLET 2 EVIDENCE: ...
```

(Single-bullet invocations remain valid — e.g., when the user asks to rewrite one bullet standalone.)

**Isolation rule:** each bullet's rewrite may use ONLY its own EVIDENCE line. Never borrow a metric, tech, or claim from a sibling bullet's evidence — the auditor verifies each bullet against its own citation and will flag cross-contamination.

## Output contract

One complete four-field record **per input bullet** (the per-bullet contract is unchanged by batching):

```
BULLET <n>
REWRITE: <≤ 130 chars, verb-first, one metric max, ATS-aligned, Google XYZ structure>
EVIDENCE: <unchanged or narrowed — never broader than THIS bullet's input evidence>
CHANGES: <one short line: what was added / removed / swapped>
REJECTED ALTERNATIVES: <one short line: what was tempting but unsupported>
```

The full four-field record (ORIGINAL + REWRITE + EVIDENCE + CHANGES + REJECTED ALTERNATIVES) is appended to `evidence_report.md` by the tailor using the format in `templates/evidence_report.md`.

## Rewriting rules

1. **Google XYZ formula — target structure for every REWRITE.** Map the bullet to: "Accomplished [X] as measured by [Y] by doing [Z]." X = outcome, Y = how measured or evidenced (metric, status, scope anchor), Z = method/action. When no numeric metric exists, use a status anchor ("since launch", "production", "zero reported issues") or a scope anchor ("across N REST routes", "across all 12 tracked securities"). Never invent a Y value. If no Y anchor is available at all, the XYZ structure degrades gracefully — still lead with the outcome (X) then the method (Z).
   - BAD: "Built defense-in-depth middleware with rate limits and TTL pruning."
   - GOOD: "Passed 76 tests across 4 suites and hardened the API with per-IP rate limits (120 req/min), a 64 KB body cap, security headers and a daily cron for price refresh and 30-day TTL cleanup." (outcome + measurement + method, every number in evidence)

2. **AI-orchestration voice rule.** If the bullet mentions AI usage, the user MUST be the actor and AI must be the tool. Apply unconditionally.
   - FORBIDDEN: "AI-assisted development of X" / "leveraged AI to build Y" / "used Claude to generate Z."
   - REQUIRED: "Orchestrated Claude Code agents to [outcome]" / "Directed MCP agent pipeline to ship X."
   - If the ORIGINAL has passive AI phrasing, the REWRITE corrects it automatically and notes this in CHANGES.

3. **Verb-first.** Designed, Built, Implemented, Shipped, Refactored, Optimized, Modeled, Audited, Migrated, Wrote, Tested, Deployed, Reduced, Eliminated, Orchestrated. Pick the one that matches the source action.

4. **One number max.** If the original has 3 numbers, keep the most impressive truthful one and drop the rest.

5. **Promote a keyword only if the evidence supports it.** "Redux" can be added if the project's `technologies` array contains Redux. "Production deployment" can be added only if a source file states a live URL or deploy.

6. **Bullet quality rules (non-negotiable):**
   - **No README-as-bullet.** Never rewrite "documented architecture in a README" or "wrote 200-line README" into a resume bullet. If the original bullet is documentation-as-achievement, flag it in REJECTED ALTERNATIVES and request a new ORIGINAL with an actual outcome.
   - **Synthetic-metric ban.** If the ORIGINAL contains a simulated dollar figure (e.g., a "$X million under management" figure produced by a portfolio simulator's random-walk generator), drop it (do not substitute another scale number; describe the simulated scope plainly instead, e.g. "sample portfolios over simulated securities"). Note this removal in CHANGES.
   - **Role-differentiated bullet variants.** For a flagship project with per-audience variants of one bullet, pick exactly one variant based on the posting type supplied in PROJECT TECH or context. Worked example — a family restaurant's ordering platform (live production site), bullet 3:
     - SWE/AI/security: the HMAC-SHA256 auth variant.
     - BA/product/ops: the owner-editable menu-management variant (a feature that lets the non-technical owner update the menu without a developer or redeploy).
     - Data/analytics: the data-model variant citing that project's OWN stack (e.g., "Modeled the ordering data in Prisma on MongoDB, with Zod validating every JSON request body"). Never borrow another project's schema description — each variant must match the truth-DB entry of the project it describes.
     Never use two variants for the same role.

7. **Forbidden transforms:**
   - Adding scale/users/throughput where evidence has none.
   - Adding a teamwork claim ("collaborated with team of N engineers") not in evidence.
   - Adding "led" / "owned" / "drove" without explicit support.
   - Replacing a specific tool with a more impressive sibling (e.g., MongoDB → PostgreSQL).

8. **Allowed transforms:**
   - Tightening wordy phrases.
   - Swapping a generic verb for a more specific one (built → architected) if the evidence shows architecture decisions.
   - Reordering clauses so the keyword lands earlier.
   - Surface-form alignment with the posting ("REST API" → "RESTful API" if the posting uses that form).
   - Correcting passive AI phrasing to active orchestration phrasing (see rule 2).

9. **Hard cap: 130 characters.** If the bullet must exceed, split into two bullets.

## Example

```
ORIGINAL: Built a website for ordering food at my family's restaurant using Next.js and MongoDB.
EVIDENCE: projects/ordering-platform/RESUME.md §3a, §3b — "Solo-shipped a production Next.js + TypeScript ordering platform end-to-end" + "HMAC-SHA256 signed, HttpOnly … session cookies"
KEYWORDS: TypeScript, REST API, MongoDB, secure authentication

REWRITE: Solo-shipped a Next.js + TypeScript ordering platform with MongoDB and HMAC-signed session auth (production).
EVIDENCE: projects/ordering-platform/RESUME.md §3a, §3b
CHANGES: Added "TypeScript", "HMAC-signed session auth", and "production" — all in evidence. Tightened phrasing.
REJECTED ALTERNATIVES: "scaled to thousands of orders" — not in evidence.
```

## Done when

- Every rewrite has all five fields filled in (REWRITE / EVIDENCE / CHANGES / REJECTED ALTERNATIVES / and ORIGINAL is passed through for the record).
- No rewrite contains a fact absent from EVIDENCE.
- The REWRITE follows the Google XYZ structure where a Y anchor exists in evidence.
- AI-orchestration voice rule is applied: user is the actor, AI is the tool, in any bullet where AI tools are mentioned.
- The full record (all five fields) is returned to the tailor for appending to `evidence_report.md`.
