#!/usr/bin/env python3
"""Render report markdown to the print-styled PDFs linked from reports.html.

WHY THIS EXISTS
The PDFs were produced twice by a script that lived in a session's scratch
folder and was lost both times, so a one-line correction to a report could no
longer reach its PDF. This is that pipeline, committed: markdown -> HTML through
the same renderer as tools/build_reports.py, then printed by headless Edge.

Only reports with a HEADERS entry are built; add one to bring another PDF over.
Relative image paths resolve against the markdown's own directory, so figures
render (the old experiment-log PDF had shipped with a broken image).

USAGE
    python tools/build_pdfs.py                          # every report in HEADERS
    python tools/build_pdfs.py --only rl-chess-technical-report
    python tools/build_pdfs.py --copy-to-repo           # also write the copy in the project's docs/

Requires: markdown-it-py, playwright (uses the installed Edge).
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_reports import REPORTS, SITE, md_renderer, rewrite_links, wrap_tables  # noqa: E402

# slug -> the header block printed above the body (the markdown's own h1 is dropped).
HEADERS = {
    "rl-chess-technical-report": {
        "eyebrow": "Technical report",
        "title": "An AlphaZero-Style Chess Engine, Built From Scratch",
        "subtitle": "Implementation, a controlled study of the training plateau I call the "
                    "draw cycle, and the diagnosis that it is a signal problem, not a "
                    "compute ceiling.",
        "date": "July 2026",
        "site": "rlchess.xyz",
        "repo_pdf": "docs/RL-Chess-Technical-Report.pdf",
    },
    "rl-chess-experiment-results": {
        "eyebrow": "Experiment log",
        "title": "Self-Play Scaling Experiments: Per-Iteration Results",
        "subtitle": "The full empirical record behind the draw-cycle study — every training "
                    "iteration, evaluation match, and Elo estimate from the 9.8-hour GPU run.",
        "date": "July 2026",
        "site": "rlchess.xyz",
        "repo_pdf": "docs/RL-Chess-Experiment-Results.pdf",
    },
}

CSS = """
@page { size: Letter; margin: 0.8in 0.85in 0.85in; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
       font-size: 10.5pt; line-height: 1.55; color: #15181E; margin: 0; }
.eyebrow { font-family: "Segoe UI", system-ui, sans-serif; font-size: 8pt; letter-spacing: .22em;
           text-transform: uppercase; color: #1F4B99; margin: 0 0 10pt; }
h1.title { font-weight: 400; font-size: 22pt; line-height: 1.15; margin: 0 0 8pt; }
.subtitle { font-style: italic; color: #565B64; margin: 0 0 12pt; font-size: 11pt; }
.byline { font-family: "Segoe UI", system-ui, sans-serif; font-size: 8.5pt; color: #15181E; margin: 0; }
.links { font-family: "Segoe UI", system-ui, sans-serif; font-size: 8.5pt; margin: 2pt 0 0; }
.links a { color: #1F4B99; text-decoration: none; }
hr.head { border: 0; border-top: 1.5pt solid #1F4B99; margin: 14pt 0 16pt; }
h2 { font-size: 13.5pt; margin: 18pt 0 6pt; padding-bottom: 3pt; border-bottom: .5pt solid #C7C3B8;
     break-after: avoid; }
h3 { font-size: 11.5pt; margin: 14pt 0 4pt; break-after: avoid; }
h4 { font-size: 10.5pt; margin: 12pt 0 4pt; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
a { color: #1F4B99; }
code { font-family: "Cascadia Mono", Consolas, monospace; font-size: 8.6pt;
       background: #EFEDE7; padding: .5pt 3pt; border-radius: 2pt; }
pre { background: #F3F1EC; border: .5pt solid #D9D6CC; border-radius: 3pt; padding: 7pt 9pt;
      font-size: 8.4pt; line-height: 1.4; white-space: pre-wrap; break-inside: avoid; }
pre code { background: none; padding: 0; }
blockquote { margin: 10pt 0; padding: 2pt 0 2pt 11pt; border-left: 2.5pt solid #1F4B99; color: #3A3F47; }
.tablewrap { margin: 9pt 0; break-inside: avoid; }
table { border-collapse: collapse; width: 100%; font-family: "Segoe UI", system-ui, sans-serif;
        font-size: 8.4pt; font-variant-numeric: tabular-nums; }
th { text-align: left; font-weight: 600; border-top: 1pt solid #15181E; border-bottom: .75pt solid #15181E;
     padding: 3.5pt 6pt; }
td { border-bottom: .5pt solid #D9D6CC; padding: 3.5pt 6pt; vertical-align: top; }
tr:last-child td { border-bottom: 1pt solid #15181E; }
img { max-width: 100%; display: block; margin: 8pt auto; break-inside: avoid; }
"""

FOOTER = ('<div style="width:100%;font-family:Segoe UI,sans-serif;font-size:7.5pt;color:#6B6F76;'
          'padding:0 0.85in;display:flex;justify-content:space-between">'
          '<span>{title}</span><span><span class="pageNumber"></span> / '
          '<span class="totalPages"></span></span></div>')


def build(report, head: dict) -> str:
    src = report.src_path
    body = md_renderer().render(src.read_text(encoding="utf-8"))
    body = re.sub(r"<h1[^>]*>.*?</h1>", "", body, count=1, flags=re.S)   # header replaces it
    body = wrap_tables(rewrite_links(body, set(), report.repo, report.source))
    repo_url = f"https://github.com/Danny-397/{report.repo}"
    e = html.escape
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<base href="{src.parent.resolve().as_uri()}/"><style>{CSS}</style></head><body>
<p class="eyebrow">{e(head['eyebrow'])}</p>
<h1 class="title">{e(head['title'])}</h1>
<p class="subtitle">{e(head['subtitle'])}</p>
<p class="byline">Daniel Lichtenberger · {e(head['date'])}</p>
<p class="links"><a href="https://{e(head['site'])}">{e(head['site'])}</a> ·
   <a href="{repo_url}">Source on GitHub</a></p>
<hr class="head">
{body}
</body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only", help="build just this slug")
    ap.add_argument("--copy-to-repo", action="store_true",
                    help="also write the PDF into the project's own docs/")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    todo = [r for r in REPORTS if r.slug in HEADERS and (not args.only or r.slug == args.only)]
    if not todo:
        sys.exit(f"no PDF header defined for {args.only!r}")
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        browser = p.chromium.launch(channel="msedge")
        for r in todo:
            head = HEADERS[r.slug]
            page_html = Path(tmp) / f"{r.slug}.html"
            page_html.write_text(build(r, head), encoding="utf-8")
            page = browser.new_page()
            page.goto(page_html.as_uri(), wait_until="networkidle")
            broken = page.evaluate("[...document.images].filter(i => !i.naturalWidth).map(i => i.src)")
            if broken:
                print(f"  BROKEN IMAGE in {r.slug}: {broken}", file=sys.stderr)
            out = SITE / "reports" / r.pdf
            page.pdf(path=str(out), print_background=True, display_header_footer=True,
                     header_template="<div></div>",
                     footer_template=FOOTER.format(title=html.escape(head["title"])))
            page.close()
            print(f"  wrote reports/{r.pdf}")
            if args.copy_to_repo and head.get("repo_pdf"):
                dest = r.src_path.parents[len(Path(r.source).parts) - 1] / head["repo_pdf"]
                dest.write_bytes(out.read_bytes())
                print(f"  copied to {dest}")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
