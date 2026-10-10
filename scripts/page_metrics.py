#!/usr/bin/env python3
"""Report page count + last-page line density + verdict for a PDF.

Usage:
    python3 page_metrics.py <path-to-pdf>

Output (stdout): single JSON line with:
    page_count        — total page count
    last_page_lines   — non-empty line count on the last page
    verdict           — PASS (>=50) | BORDERLINE (45-49) | DEAD-SPACE (<45)

Geometry constants assume the resume template (10pt / 0.5in margins, the
LOCKED spacing contract: titlespacing 5/2pt, itemsep/topsep 1.5pt), where a
full page holds ~52-56 non-empty content lines. The >=50 floor and the 1-page
ceiling therefore leave a narrow band -- fit by trimming CONTENT, never by
shrinking spacing/margins/font (see the SPACING CONTRACT in resume_template.tex).
"""
import json
import sys

from pypdf import PdfReader

FULL_PAGE = 50          # >= this = acceptable density
BORDERLINE_LOW = 45     # 45-49 = borderline (recommend one filler)
# < BORDERLINE_LOW       = dead space (must add content)


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "usage: page_metrics.py <pdf>"}), file=sys.stderr)
        return 2

    pdf_path = sys.argv[1]
    try:
        pages = PdfReader(pdf_path).pages
    except Exception as exc:
        print(json.dumps({"error": f"could not read PDF: {exc}"}), file=sys.stderr)
        return 1

    last_text = pages[-1].extract_text() or ""
    last_lines = [line for line in last_text.split("\n") if line.strip()]
    n = len(last_lines)

    if n >= FULL_PAGE:
        verdict = "PASS"
    elif n >= BORDERLINE_LOW:
        verdict = "BORDERLINE"
    else:
        verdict = "DEAD-SPACE"

    print(json.dumps({
        "page_count": len(pages),
        "last_page_lines": n,
        "verdict": verdict,
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
