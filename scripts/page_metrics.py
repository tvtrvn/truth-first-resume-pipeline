#!/usr/bin/env python3
"""Report page count + how full the last page is + verdict for a PDF.

Usage:
    python3 page_metrics.py <path-to-pdf>

Output (stdout): single JSON line with:
    page_count        — total page count
    last_page_fill    — how far down the text area the last baseline sits (0-1)
    last_page_lines   — non-empty line count on the last page (informational)
    verdict           — PASS (fill >= 0.93) | BORDERLINE (0.85-0.93) | DEAD-SPACE (< 0.85)

Fill is measured, not line count: since 2026-10-11 entries carry two-line headers and a gap
before each one, so a full page holds a different number of lines depending on how many
entries it has. Geometry: letter paper, 0.5in margins (the résumé template). PASS leaves at
most ~50pt (about 4 text lines) empty at the bottom — the same slack the old ">= 50 of ~54
lines" floor allowed. Fit by trimming or adding CONTENT, never by changing spacing/margins/font
(see the SPACING CONTRACT in resume_template.tex).
"""
import json
import sys

from pypdf import PdfReader

MARGIN = 36.0           # 0.5in in PDF points
FULL_PAGE = 0.93        # >= this = acceptable fill
BORDERLINE_LOW = 0.85   # 0.85-0.93 = borderline (recommend one filler)
# < BORDERLINE_LOW       = dead space (must add content)


def lowest_baseline(page) -> float:
    """Smallest y (PDF points from the page bottom) of any visible text on the page."""
    ys = []

    def visit(text, cm, tm, _font, _size):
        if text.strip():
            ys.append(cm[1] * tm[4] + cm[3] * tm[5] + cm[5])

    page.extract_text(visitor_text=visit)
    return min(ys) if ys else float(page.mediabox.top)


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

    last = pages[-1]
    height = float(last.mediabox.top) - float(last.mediabox.bottom)
    text_top = height - MARGIN
    fill = (text_top - lowest_baseline(last)) / (height - 2 * MARGIN)
    fill = round(max(0.0, min(1.0, fill)), 3)
    lines = [line for line in (last.extract_text() or "").split("\n") if line.strip()]

    if fill >= FULL_PAGE:
        verdict = "PASS"
    elif fill >= BORDERLINE_LOW:
        verdict = "BORDERLINE"
    else:
        verdict = "DEAD-SPACE"

    print(json.dumps({
        "page_count": len(pages),
        "last_page_fill": fill,
        "last_page_lines": len(lines),
        "verdict": verdict,
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
