"""Take down the hosting-status note once every backend answers again.

When the Render backends are down, index.html carries a dated note
(<p class="caveat" id="hosting-status">) and the affected projects' chips are
switched to `tag warn` with a title starting "Backend paused". The daily uptime
check runs this when everything answers, so the note can't outlive the outage.

Exit status: 0 if index.html changed, 1 if there was nothing to remove.

    python tools/clear_status_note.py           # rewrite index.html in place
    python tools/clear_status_note.py --check   # report only
"""
import argparse
import io
import re
import sys
from pathlib import Path

INDEX = Path(__file__).resolve().parent.parent / "index.html"

# The note's lines plus the blank line after it, so the page reads as it did before.
NOTE = re.compile(r'^[ \t]*<p class="caveat" id="hosting-status">.*?</p>[ \t]*\r?\n[ \t]*\r?\n', re.S | re.M)
CHIP = re.compile(r'<span class="tag warn" title="Backend paused[^"]*">')


def clear(html: str) -> str:
    html = NOTE.sub("", html, count=1)
    return CHIP.sub('<span class="tag live">', html)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="report and write nothing")
    args = ap.parse_args()

    html = io.open(INDEX, encoding="utf-8", newline="").read()
    out = clear(html)
    if out == html:
        print("no hosting-status note or paused chips to remove")
        return 1
    print(f"removing the note: {bool(NOTE.search(html))}; chips restored: {len(CHIP.findall(html))}")
    if not args.check:
        io.open(INDEX, "w", encoding="utf-8", newline="").write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
