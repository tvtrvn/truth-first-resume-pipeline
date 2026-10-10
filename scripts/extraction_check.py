#!/usr/bin/env python3
"""ATS text-extraction gate for rendered resume/cover-letter PDFs.

Asserts the PDF text layer is parser-safe:
  1. No ligature presentation forms (U+FB00-U+FB06) — exact-string ATS keyword
     matchers miss "workflow"/"staff"/"certification" when fi/fl/ff ligate.
     (Found live in a submitted resume rendered with fontenc+lmodern.)
  2. No U+FFFD replacement characters (mojibake).
  3. Every --expect string survives extraction verbatim (name, email, phone,
     URLs, keyword samples) — catches kern-split tokens like "T aylor".

Usage:
  python3 extraction_check.py <file.pdf> --expect "Ada Nguyen" --expect "ada.nguyen@example.com" ...

Exit 0 on PASS, 1 on FAIL. Prints a JSON report either way.
"""
import json
import sys

from pypdf import PdfReader


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 1
    pdf_path = args[0]
    expects = [args[i + 1] for i, a in enumerate(args) if a == "--expect" and i + 1 < len(args)]

    text = "".join(page.extract_text() or "" for page in PdfReader(pdf_path).pages)

    ligatures = sorted({c for c in text if 0xFB00 <= ord(c) <= 0xFB06})
    mojibake = "�" in text
    missing = [s for s in expects if s not in text]

    report = {
        "pdf": pdf_path,
        "ligature_glyphs": ligatures,
        "replacement_chars": mojibake,
        "missing_expected": missing,
        "verdict": "PASS" if not (ligatures or mojibake or missing) else "FAIL",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
