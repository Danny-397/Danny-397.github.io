#!/usr/bin/env python3
"""Render each technical report's markdown to a readable HTML page.

WHY THIS EXISTS
The reports shipped as PDF only. A PDF can't be deep-linked (you cannot send
someone straight to a limitations section), reads badly on a phone, and is
invisible to search. The markdown already exists in each project's own
repository -- reports.html says so -- and these pages are built from that same
source, so the HTML, the PDF and the code stay in step.

The PDFs are kept and still linked. This adds a route, it does not replace one.

USAGE
    python tools/build_reports.py            # build all
    python tools/build_reports.py --only quantumsafe-technical-report
    python tools/build_reports.py --check    # fail if any source is missing

Sources live in sibling repositories, so this is run locally and the generated
HTML is committed -- exactly how the PDFs are already handled. There is no
build step on GitHub Pages.

Requires: markdown-it-py  (pip install markdown-it-py)
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

try:
    from markdown_it import MarkdownIt
except ImportError:
    sys.exit("markdown-it-py is required:  pip install markdown-it-py")

SITE = Path(__file__).resolve().parent.parent
SIBLINGS = SITE.parent  # C:/Users/dlich — where the project repos live
OUT_DIR = SITE / "reports"

GITHUB = "https://github.com/Danny-397"


class Report:
    """One report: where its markdown lives, and how to present it."""

    def __init__(self, slug, title, project, repo, source, pdf, blurb):
        self.slug = slug
        self.title = title
        self.project = project
        self.repo = repo
        self.source = source      # path within the repo
        self.pdf = pdf            # filename in reports/
        self.blurb = blurb

    @property
    def src_path(self) -> Path:
        # repo "." means the markdown lives in this site's own repository.
        base = SITE if self.repo == "." else SIBLINGS / self.repo
        return base / self.source

    @property
    def source_url(self) -> str:
        repo = "Danny-397.github.io" if self.repo == "." else self.repo
        return f"{GITHUB}/{repo}/blob/main/{self.source}"


# Order matches reports.html.
REPORTS = [
    Report("research-summary", "Research Summary", "All six projects",
           ".", "research-summary.md", "Research-Summary.pdf",
           "One page across all six projects: what each claimed, and what the numbers said."),
    Report("quantumsafe-technical-report", "QuantumSafe — Technical Report", "QuantumSafe Scan",
           "Quantum-Safe-Scan", "docs/TECHNICAL_REPORT.md", "QuantumSafe-Technical-Report.pdf",
           "What the scanner is, how the hybrid engine works, and how well it scores."),
    Report("quantumsafe-whitepaper", "QuantumSafe — Whitepaper", "QuantumSafe Scan",
           "Quantum-Safe-Scan", "docs/WHITEPAPER.md", "QuantumSafe-Whitepaper.pdf",
           "The long form: threat model, algorithm math, and references."),
    Report("rl-chess-technical-report", "AlphaZero Chess — Technical Report", "RL-Chess-Engine",
           "RL-Chess-Engine", "docs/technical-report.md", "RL-Chess-Technical-Report.pdf",
           "Network, MCTS, self-play loop, and the training curve."),
    Report("rl-chess-experiment-results", "AlphaZero Chess — Experiment Results", "RL-Chess-Engine",
           "RL-Chess-Engine", "docs/experiment-results.md", "RL-Chess-Experiment-Results.pdf",
           "What the engine learned, measured against fixed opponents."),
    Report("alphaglyph-technical-report", "AlphaGlyph — Technical Report", "AlphaGlyph",
           "Alphaglyph", "docs/technical-report.md", "AlphaGlyph-Technical-Report.pdf",
           "Signal generation, the risk layer, and the live trading loop."),
    Report("tradeski-technical-report", "Tradeski — Technical Report", "Tradeski",
           "Tradeski", "docs/technical-report.md", "Tradeski-Technical-Report.pdf",
           "Streaming architecture, indicator maths on raw NumPy, and the screener."),
    Report("neural-canvas-technical-report", "Neural Canvas — Technical Report", "Neural Canvas",
           "neural-canvas", "docs/technical-report.md", "Neural-Canvas-Technical-Report.pdf",
           "Hand tracking, the brush engine, and the attract-mode renderer."),
]

# RL-Trader's paper is LaTeX (paper/rl_trader.tex), not markdown, so it is not
# built here -- a .tex to HTML pass needs different tooling and would be a
# second, lossier converter. Its PDF remains the route to it.


def slugify(text: str) -> str:
    """A stable, readable anchor id."""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_]+", "-", text).strip("-") or "section"


def md_renderer() -> MarkdownIt:
    """CommonMark plus tables and strikethrough.

    Deliberately NOT 'gfm-like': that turns on linkify, which needs another
    dependency and would rewrite bare URLs inside code spans.
    """
    return MarkdownIt("commonmark").enable("table").enable("strikethrough")


def add_heading_anchors(body: str) -> tuple[str, list[tuple[int, str, str]]]:
    """Give every h2/h3 an id and a quiet link, and collect them for a TOC."""
    toc: list[tuple[int, str, str]] = []
    seen: dict[str, int] = {}

    def repl(m: re.Match) -> str:
        level, attrs, inner = int(m.group(1)), m.group(2), m.group(3)
        slug = slugify(inner)
        seen[slug] = seen.get(slug, 0) + 1
        if seen[slug] > 1:                      # two sections, same words
            slug = f"{slug}-{seen[slug]}"
        label = re.sub(r"<[^>]+>", "", inner).strip()
        toc.append((level, slug, html.unescape(label)))
        return (f'<h{level} id="{slug}"{attrs}>{inner}'
                f'<a class="anchor" href="#{slug}" aria-label="Link to this section">#</a>'
                f'</h{level}>')

    body = re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", repl, body, flags=re.S)
    return body, toc


def wrap_tables(body: str) -> str:
    """Tables are the one thing allowed to be wider than the column."""
    return body.replace("<table>", '<div class="tablewrap"><table>') \
               .replace("</table>", "</table></div>")


def rewrite_links(body: str, built: set[str], repo: str) -> str:
    """Point relative .md links at a sibling page if we built one, else GitHub.

    A report that links to ARCHITECTURE.md should not produce a dead local link.
    """
    by_source = {r.source.rsplit("/", 1)[-1].lower(): r.slug
                 for r in REPORTS if r.slug in built and r.repo == repo}

    def repl(m: re.Match) -> str:
        quote, target = m.group(1), m.group(2)
        name = target.rsplit("/", 1)[-1].lower()
        frag = ""
        if "#" in name:
            name, frag = name.split("#", 1)
            frag = "#" + frag
        if name in by_source:
            return f'href={quote}{by_source[name]}.html{frag}{quote}'
        return f'href={quote}{GITHUB}/{repo}/blob/main/{target}{quote}'

    return re.sub(r'href=(["\'])((?!https?:|#|mailto:)[^"\']*?\.md(?:#[^"\']*)?)\1',
                  repl, body)


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} — Dan Lichtenberger</title>
<meta name="description" content="{blurb}">
<meta name="author" content="Dan Lichtenberger">
<link rel="canonical" href="https://danny-397.github.io/reports/{slug}.html">

<meta property="og:type" content="article">
<meta property="og:site_name" content="Dan Lichtenberger">
<meta property="og:url" content="https://danny-397.github.io/reports/{slug}.html">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{blurb}">
<meta property="og:image" content="https://danny-397.github.io/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{title} — Dan Lichtenberger">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{blurb}">
<meta name="twitter:image" content="https://danny-397.github.io/og-image.png">

<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%230F1319'/><text x='50' y='54' font-size='58' font-family='Georgia,serif' fill='%237FA6E8' text-anchor='middle' dominant-baseline='central'>D</text></svg>">
<script>document.documentElement.className += " js";
/* Apply the saved theme before first paint, as index.html and reports.html do. */
try {{ var savedTheme = localStorage.getItem('theme');
      if (savedTheme === 'dark' || savedTheme === 'light')
        document.documentElement.setAttribute('data-theme', savedTheme); }}
catch (e) {{ /* private mode */ }}</script>
<link rel="stylesheet" href="../site.css">
<link rel="stylesheet" href="../report.css">
<script src="../analytics.js" defer></script>
</head>
<body>

<a class="skip" href="#doc">Skip to the report</a>

<header class="bar">
  <div class="wrap">
    <a class="name" href="../index.html">Dan Lichtenberger</a>
    <nav>
      <a href="../index.html">Work</a>
      <a href="../reports.html" aria-current="page">Reports</a>
      <a href="{GITHUB}/Danny-397">GitHub</a>
      <button type="button" class="themebtn" aria-label="Switch between light and dark">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <g class="i-moon"><path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a6.6 6.6 0 0 0 10.5 10.5Z"/></g>
          <g class="i-sun"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.6v2.2M12 19.2v2.2M2.6 12h2.2M19.2 12h2.2M5.4 5.4 7 7M17 17l1.6 1.6M18.6 5.4 17 7M7 17l-1.6 1.6"/></g>
        </svg>
      </button>
    </nav>
  </div>
</header>
"""

TAIL = """
<footer class="colophon">
  <div class="wrap">
    <p class="eyebrow">On this document</p>
    <p>
      Rendered from <a href="{source_url}"><code>{source}</code></a> in the
      {project} repository, so this page, the PDF and the code stay in step.
      <a href="../reports.html">All reports &rarr;</a>
    </p>
  </div>
</footer>

<script>
(function () {{
  var root = document.documentElement;
  function currentlyDark() {{
    var t = root.getAttribute('data-theme');
    return t ? t === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
  }}
  Array.prototype.forEach.call(document.querySelectorAll('.themebtn'), function (b) {{
    b.addEventListener('click', function () {{
      var next = currentlyDark() ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try {{ localStorage.setItem('theme', next); }} catch (e) {{ /* private mode */ }}
    }});
  }});
}})();
</script>
</body>
</html>
"""


def build(report: Report, built: set[str], renderer: MarkdownIt) -> str:
    src = report.src_path
    raw = src.read_text(encoding="utf-8")

    # The markdown opens with its own H1; the page supplies the title, so drop
    # the duplicate rather than showing the same words twice.
    raw = re.sub(r"\A\s*#\s+.*?\n", "", raw, count=1)

    body = renderer.render(raw)
    body = rewrite_links(body, built, report.repo)
    body, toc = add_heading_anchors(body)
    body = wrap_tables(body)

    toc_html = ""
    tops = [t for t in toc if t[0] == 2]
    if len(tops) > 2:
        items = "\n".join(
            f'      <li><a href="#{slug}">{html.escape(label)}</a></li>'
            for _, slug, label in tops)
        toc_html = ('  <nav class="toc" aria-label="Sections">\n'
                    '    <p class="eyebrow">Sections</p>\n'
                    f'    <ol>\n{items}\n    </ol>\n'
                    '  </nav>\n')

    pdf_link = (f'<a class="doclink" href="{report.pdf}">PDF &darr;</a>'
                if report.pdf else "")

    head = HEAD.format(title=html.escape(report.title),
                       blurb=html.escape(report.blurb),
                       slug=report.slug,
                       GITHUB=GITHUB)

    masthead = f"""
<main id="doc" class="wrap doc">
  <p class="eyebrow">{html.escape(report.project)} &middot; technical report</p>
  <h1>{html.escape(report.title)}</h1>
  <p class="standfirst">{html.escape(report.blurb)}</p>
  <p class="doclinks">
    <a class="doclink" href="{report.source_url}">Source markdown &nearr;</a>
    {pdf_link}
  </p>
{toc_html}  <article class="prose-doc">
{body}
  </article>
</main>
"""

    tail = TAIL.format(source_url=report.source_url,
                       source=html.escape(report.source),
                       project=html.escape(report.project))
    return head + masthead + tail


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="build just this slug")
    ap.add_argument("--check", action="store_true",
                    help="report missing sources and build nothing")
    args = ap.parse_args()

    wanted = [r for r in REPORTS if not args.only or r.slug == args.only]
    if args.only and not wanted:
        print(f"no such slug: {args.only}", file=sys.stderr)
        print("known:", ", ".join(r.slug for r in REPORTS), file=sys.stderr)
        return 2

    missing = [r for r in wanted if not r.src_path.exists()]
    for r in missing:
        print(f"MISSING  {r.slug}: {r.src_path}", file=sys.stderr)
    if args.check:
        print(f"{len(wanted) - len(missing)}/{len(wanted)} sources present")
        return 1 if missing else 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    renderer = md_renderer()
    built = {r.slug for r in wanted if r.src_path.exists()}

    for r in wanted:
        if r in missing:
            continue
        out = OUT_DIR / f"{r.slug}.html"
        out.write_text(build(r, built, renderer), encoding="utf-8", newline="")
        print(f"  {out.relative_to(SITE)}  ({out.stat().st_size // 1024} KB)")

    print(f"built {len(built)} report page(s)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
