#!/usr/bin/env python3
"""Check the site's headline numbers against their sources, and optionally fix them.

WHY THIS EXISTS
The test total and the "N weeks" span on the home page went stale three times
(345 -> 420 -> 1,298), each time understating or overstating the work by a few
percent, because each was transcribed by hand from somewhere else. A wrong
number is a published inaccuracy on a site whose argument is that numbers
should be checked. Both figures have a mechanical source, so they are derived
here instead of remembered.

SOURCES
    Test counts   the "N passed" line in each repo's latest green CI run on main
                  (matrix jobs run the same suite, so the largest count is used)
    Week span     first commit of the oldest project -> newest commit of any project

USAGE
    python tools/check_numbers.py          # exit 1 and list every stale figure
    python tools/check_numbers.py --fix    # rewrite them in place

Requires the GitHub CLI (`gh`), authenticated; in Actions, GH_TOKEN is enough.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
OWNER = "Danny-397"

# repo -> name of the workflow whose log carries the pytest summary
TESTED = {
    "Quantum-Safe-Scan": "CI",
    "Alphaglyph": "CI",
    "Tradeski": "CI Pipeline",
    "RL-for-Crypto-and-stocks-": "CI",
    "RL-Chess-Engine": "tests",
}
PROJECTS = list(TESTED) + ["neural-canvas"]


def _gh() -> str:
    exe = shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"
    if not Path(exe).exists():
        sys.exit("the GitHub CLI (gh) is required")
    return exe


def gh(*args: str) -> str:
    return subprocess.run([_gh(), *args], check=True, capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def test_count(repo: str, workflow: str) -> int:
    runs = json.loads(gh("run", "list", "-R", f"{OWNER}/{repo}", "--branch", "main",
                         "--status", "success", "--workflow", workflow, "-L", "1",
                         "--json", "databaseId"))
    if not runs:
        sys.exit(f"{repo}: no successful '{workflow}' run on main")
    log = gh("run", "view", str(runs[0]["databaseId"]), "-R", f"{OWNER}/{repo}", "--log")
    counts = [int(n) for n in re.findall(r"\b(\d+) passed\b", log)]
    if not counts:
        sys.exit(f"{repo}: no 'N passed' line in the latest '{workflow}' log")
    return max(counts)


def commit_date(repo: str, oldest: bool) -> datetime:
    path = f"repos/{OWNER}/{repo}/commits?per_page=1"
    if oldest:
        head = gh("api", "-i", path)
        last = re.search(r'[?&]page=(\d+)>; rel="last"', head)
        if last:
            path += f"&page={last.group(1)}"
    date = gh("api", path, "-q", ".[0].commit.author.date").strip()
    return datetime.fromisoformat(date.replace("Z", "+00:00"))


class Claim:
    """One number on the site: where it is, and the value it should have."""

    def __init__(self, label: str, file: str, pattern: str, expected: str):
        self.label, self.file, self.pattern, self.expected = label, file, pattern, expected

    def check(self, fix: bool) -> bool:
        path = SITE / self.file
        text = path.read_text(encoding="utf-8")
        m = re.search(self.pattern, text)
        if not m:
            # Failing here is deliberate: a pattern that stops matching after the
            # wording changes would otherwise pass silently forever.
            print(f"PATTERN LOST  {self.label} ({self.file}): /{self.pattern}/")
            return False
        found = m.group(1)
        if found == self.expected:
            print(f"ok            {self.label}: {found}")
            return True
        print(f"STALE         {self.label}: site says {found}, source says {self.expected}")
        if fix:
            a, b = m.span(1)
            path.write_text(text[:a] + self.expected + text[b:], encoding="utf-8", newline="\n")
            print(f"  fixed in {self.file}")
            return True
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fix", action="store_true", help="rewrite stale figures in place")
    args = ap.parse_args()

    counts = {repo: test_count(repo, wf) for repo, wf in TESTED.items()}
    for repo, n in counts.items():
        print(f"source        {repo}: {n} passed")
    total = sum(counts.values())

    first = min(commit_date(r, oldest=True) for r in PROJECTS)
    newest = max(commit_date(r, oldest=False) for r in PROJECTS)
    weeks = (newest - first).days // 7
    print(f"source        span {first:%Y-%m-%d} -> {newest:%Y-%m-%d} = {weeks} weeks")

    claims = [
        Claim("home: total tests", "index.html",
              r"<dt>([\d,]+)</dt>\s*<dd>automated tests running in CI", f"{total:,}"),
        Claim("home: week span", "index.html",
              r"<dt>(\d+) weeks</dt>\s*<dd>from the first commit", str(weeks)),
        Claim("share card: week span", "assets/og-card.html",
              r"<b>(\d+) weeks</b>", str(weeks)),
        Claim("home: QuantumSafe tests", "index.html",
              r"(\d[\d,]*) automated tests in continuous integration",
              f"{counts['Quantum-Safe-Scan']:,}"),
        Claim("summary: AlphaGlyph tests", "research-summary.md",
              r"(\d+) tests in CI\.", str(counts["Alphaglyph"])),
        Claim("summary: Tradeski tests", "research-summary.md",
              r"retrieval-grounded assistant, (\d+) tests", str(counts["Tradeski"])),
    ]
    results = [c.check(args.fix) for c in claims]
    if all(results):
        return 0
    if not args.fix:
        print("\nRun `python tools/check_numbers.py --fix`, then rebuild what is generated "
              "from the fixed files: python tools/build_reports.py --only research-summary "
              "and python tools/render_og.py.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
