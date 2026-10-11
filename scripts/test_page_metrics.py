"""Run: python3 scripts/test_page_metrics.py   (exit 1 on any failure)

Builds one-page PDFs at the résumé geometry (letter, 10pt, 0.5in margins) with Tectonic and checks
that page_metrics.py reads how far down the page the text reaches (fill), not how many lines it has.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "page_metrics.py"
PREAMBLE = "\\documentclass[letterpaper,10pt]{article}\\usepackage[margin=0.5in]{geometry}\\pagestyle{empty}\n"

CASES = {
    # name: (body, expected verdict)
    "full": ("TOP\\par\\vspace*{\\fill}BOTTOM\\par", "PASS"),
    "mid": ("TOP\\par\\vspace*{0.86\\textheight}MID\\par", "BORDERLINE"),
    "sparse": ("one\\par two\\par three\\par", "DEAD-SPACE"),
    # boundary cases pin MARGIN and both thresholds
    "just_pass": ("TOP\\par\\vspace*{0.91\\textheight}X\\par", "PASS"),
    "just_borderline": ("TOP\\par\\vspace*{0.89\\textheight}X\\par", "BORDERLINE"),
    "just_border_low": ("TOP\\par\\vspace*{0.83\\textheight}X\\par", "BORDERLINE"),
    "just_dead": ("TOP\\par\\vspace*{0.81\\textheight}X\\par", "DEAD-SPACE"),
}


def metrics(body: str, workdir: Path, name: str) -> dict:
    tex = workdir / f"{name}.tex"
    tex.write_text(PREAMBLE + "\\begin{document}\n" + body + "\n\\end{document}\n", encoding="utf-8")
    subprocess.run(["tectonic", tex.name], cwd=workdir, check=True, capture_output=True)
    out = subprocess.run([sys.executable, str(SCRIPT), str(workdir / f"{name}.pdf")],
                         check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def main() -> int:
    failures = []
    with tempfile.TemporaryDirectory() as d:
        for name, (body, want) in CASES.items():
            m = metrics(body, Path(d), name)
            if "last_page_fill" not in m:
                failures.append(f"{name}: no last_page_fill in {m}")
            elif m["verdict"] != want:
                failures.append(f"{name}: verdict {m['verdict']} (fill {m['last_page_fill']}), want {want}")
            if m.get("page_count") != 1:
                failures.append(f"{name}: page_count {m.get('page_count')}, want 1")
    for f in failures:
        print("FAIL", f)
    print(f"{len(CASES)} fill cases: {'FAIL' if failures else 'PASS'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
