---
name: latex-to-pdf-renderer
description: Compile a tailored .tex resume (or cover letter) to PDF using Tectonic. Strictly user-gated — only runs after the user reviews the .tex and explicitly approves rendering, and only if resume-auditor returned PASS or PASS-WITH-WARNINGS. Use when the user says "render the PDF", "compile the resume", or "looks good, make the PDF".
disable-model-invocation: true
---

# latex-to-pdf-renderer

## Purpose

Turn a finalized `.tex` artifact (typically `tailored_resume.tex`, sometimes `cover_letter.tex`) into a PDF using the **Tectonic** engine. This is the LAST step before `output-packager`.

This skill never modifies the `.tex` content. It only compiles.

## Pre-flight checks (all must pass — refuse otherwise)

1. **Auditor passed.** An `audit_report.md` exists in the same `outputs/<company>_<role>_<date>/` folder, and its final verdict is `PASS` or `PASS-WITH-WARNINGS` (not `FAIL`). `WARN-UNRESOLVED` is not a valid auditor verdict — the auditor only produces `PASS`, `PASS-WITH-WARNINGS`, or `FAIL`. If the verdict is `PASS-WITH-WARNINGS`, surface all warnings to the user before compiling but do not block compilation. If the auditor was not run, run it first.
2. **User approval is explicit.** The user has said something like "render", "compile", "make the PDF", "looks good — generate" referring to THIS specific `.tex`. Implicit approval (e.g., just "continue") is not enough — ask.
3. **Tectonic is installed.** `tectonic --version` exits 0. If not, tell the user to run `brew install tectonic` — do NOT attempt to install it from inside this skill.
4. **Target file exists** and has no leftover `%% TAILOR: ... %%` markers. If markers remain, refuse and report which lines still need filling.

If any check fails, STOP and report the failing check. Do not partially render.

## Inputs

- Path to a `.tex` file inside `outputs/<company>_<role>_<YYYY-MM-DD>/`.
- (Implicit) the sibling `audit_report.md` for that folder.

## Procedure

1. Run pre-flight checks above.
2. `cd` to the output folder (Tectonic writes the PDF next to the source by default).
3. Run: `tectonic --keep-logs <file>.tex`
   Note: if the installed binary rejects `--synctex=none` (older builds do), drop that flag — `--keep-logs` alone is sufficient. Do not use `--synctex=none` unless you have confirmed it is accepted by `tectonic --help`.
4. On success: confirm `<file>.pdf` exists, print its size, and tell the user the path. Surface any warnings from the Tectonic log that mention overfull/underfull boxes or missing fonts.
5. **Post-render page-count verification.** After successful compilation, confirm the PDF is exactly 1 page:
   ```bash
   python3 scripts/page_metrics.py <file>.pdf
   ```
   Parse `page_count` from the JSON output. If `page_count > 1`, surface as a blocking warning — do not hand the PDF to the user as final. Bounce it back to the tailor to trim **content**. This renderer compiles only; it MUST NOT edit the `.tex` to fix overflow, and in particular MUST NOT reduce spacing/margins/font — the template's LOCKED SPACING CONTRACT (negative/sub-1pt itemsep, shrunken titlespacing, narrowed margin) is the documented cause of the squished-overlapping-lines regression. Fit is a content problem, owned by the tailor.
5b. **Post-render text-extraction gate (BLOCKING).** Every render must prove its text layer is ATS-parseable:
   ```bash
   python3 scripts/extraction_check.py <file>.pdf \
     --expect "<full name>" --expect "<email>" --expect "<phone>" \
     --expect "<github profile url>" --expect "<one bolded keyword per section, e.g. the top matched ATS keyword>"
   ```
   Pull the expected strings from the `.tex` header block and the keyword map. The script fails on: ligature presentation forms (U+FB00–U+FB06 — fi/fl/ff ligation that breaks exact-string keyword matching), U+FFFD mojibake, or any expected string missing from extraction (catches kern-split tokens like "T aylor"). On FAIL: treat exactly like a `page_count > 1` failure — do not hand the PDF forward; the fix belongs in the template's font stack or `newunicodechar` table, never in this skill. (This gate is why the template pins `fontspec` with `Ligatures=NoCommon, Kerning=Off` — see the FONT STACK comment in `templates/resume_template.tex`.)
6. On failure: print the last ~30 lines of the Tectonic output, identify the likely cause (missing package, bad escape, unbalanced braces), and do NOT retry blindly — surface to the user.

## Hard rules

- **Never edit the `.tex` to make compilation succeed.** If compilation fails, the upstream skill (`resume-tailor-no-hallucination` or `cover-letter-grounded`) produced bad LaTeX — fix it there, not here.
- **Never use `pdflatex` or `xelatex` directly.** The pipeline is standardized on Tectonic for reproducibility (single binary, on-demand package fetch, no TeX Live install).
- **Never silently overwrite an existing PDF without confirming** if its mtime is newer than the `.tex` (could indicate a manual edit the user wants to keep).
- **No network claims.** Tectonic may fetch packages on first run; that is expected. Don't pretend it's offline-only.

## Output

- `<file>.pdf` next to `<file>.tex`.
- A one-line summary printed: "Rendered <file>.pdf (<size>) in <duration>s. <N warnings>."

## Done when

- The PDF exists, opens without errors, and the user has been told the path.
- Page count is confirmed as exactly 1 via pypdf (not `mdls` — see note in `resume-tailor-no-hallucination` step 11).
- Any warnings (from Tectonic log or PASS-WITH-WARNINGS auditor verdict) have been surfaced to the user.
- Control returns to `output-packager` (or the user) for final bundling.
