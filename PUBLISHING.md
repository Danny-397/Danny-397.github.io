# Publishing notes

## The writing section is deliberately unpublished

`writing.html` and `essays/` are on disk but **untracked and gitignored**, so
they are not served from danny-397.github.io.

They were live once. `essays/the-lucky-seed.html` went out with its drafting
scaffold still in place — the dashed `.draft` boxes holding outline prompts
("Steelman it", "Nobody is grading your implementation here", "Keep your own
voice") rather than the essay. Anyone clicking **Writing** in the nav landed on
notes about an essay instead of an essay. It was pulled on 2026-08-08.

The scaffold itself is fine and worth keeping — it's a working outline. The
mistake was that the outline was reachable from the public nav.

### To republish, once the prose is written

1. Delete every `<div class="draft">…</div>` block from
   `essays/the-lucky-seed.html`. Search for `class="draft"` — if any match
   remains, it is not ready.
2. Drop `writing.html` and `essays/` from `.gitignore`.
3. Restore the three links that were removed:
   - `index.html` — the "Also" rail, beside `Technical reports →`
   - `index.html` — the "On the numbers" colophon paragraph
   - `reports.html` — the top nav, between `Reports` and `GitHub`
4. `git add -f writing.html essays/` (they're gitignored until step 2 lands).

### Check before pushing

```bash
grep -rn 'class="draft"' essays/ writing.html   # must return nothing
```

The `.draft` styles in `site.css` are commented "delete these as you write" —
they exist only to make unfinished sections obvious while drafting. If a draft
box is visible on the live site, something has gone wrong.

## Social preview

`og-image.png` (1200×630) is referenced by absolute URL in `index.html`. If the
headline on the page changes, regenerate the card so the two agree — the card is
plain HTML screenshotted at 1200×630, not a hand-drawn asset.

## Project media (`media/`)

Every plate on `index.html` is captured from the **deployed** application, never
from a local dev server and never mocked up. That claim is printed in the
colophon ("On the screens"), so it has to stay true.

| File | What it is | How it was produced |
| --- | --- | --- |
| `rltrader-lab.mp4` | Agent Playground running an episode | Playwright: load the lab, click `#pg-run`, record |
| `rltrader-arms.webp` | The memorised-vs-generalised figure | Element screenshot of `#rs-arms` |
| `quantumsafe-scan.webp` | A real snippet scan | Click `#demo-sample`, screenshot the result panel |
| `alphaglyph-replay.mp4` | "Watch it trade" day-by-day replay | Run a backtest, press Play on the replay, record |
| `rlchess-selfplay.mp4` | The engine playing itself | Play tab → `#watchBtn`, record |
| `tradeski-dashboard.webp` | The terminal with the backend up | From `Tradeski/docs/screenshots/dashboard.png` |
| `neuralcanvas-paint.mp4` | The brush engine in idle mode | See the camera note below |

Recordings are captured as Playwright video (VP8 `.webm`), then cropped and
re-encoded to H.264 `.mp4`. **Do not ship these as GIFs** — the same 12-second
Neural Canvas clip is 178 KB as MP4 and 12 MB as a GIF, because glowing
gradients on black are close to the worst case for a 256-colour palette. The
`<video muted loop playsinline>` elements behave exactly like a GIF, lazy-load
via `IntersectionObserver`, and pause when off-screen.

### Capturing Neural Canvas without a webcam

The idle ("attract") mode draws itself with the real brush engine once no hand
has been seen for 15 s, which is what the clip shows. The render loop only runs
when a video track is actually producing frames, so it needs *a* camera —
but **not yours**. Replace `getUserMedia` before any page script runs:

```js
await ctx.addInitScript(() => {
  const c = document.createElement('canvas');
  c.width = 1280; c.height = 720;
  const g = c.getContext('2d');
  (function paint(){ /* draw a dark gradient */ requestAnimationFrame(paint); })();
  const stream = c.captureStream(30);
  navigator.mediaDevices.getUserMedia = () => Promise.resolve(stream);
});
```

Chromium's `--use-fake-device-for-media-capture` flag **did not take effect**
here and the real webcam was opened instead — the first take recorded the room.
Stub `getUserMedia` as above and do not grant the `camera` permission, so a
failed stub denies rather than falls back to the physical device. Check the
first frame of any Neural Canvas capture before committing it.

## Service status

`index.html` tags each project with its real status.

As of 2026-10-20 all six resolve and all four Render backends answer, so every
record carries a plain `tag live` chip and there are no `.caveat` paragraphs.
Tradeski and QuantumSafe were both down earlier in October -- Tradeski suspended,
QuantumSafe's API accepting connections and never replying -- and each carried an
honest-status note until the service came back.

If one goes down again: give that record a `tag warn` chip and a `.caveat`
paragraph saying what still works and what does not, rather than leaving a `live`
chip on a dead link. Tradeski's dashboard falls back to a recorded snapshot
(`frontend/demo-snapshot.js`) and QuantumSafe's home page keeps its in-browser
snippet scanner, so in both cases something real remains to point at.

Both outages traced to the same cause: Render's 750 free instance-hours are per
*workspace* per month, shared across all four backends, and running them out
suspends every free service. See `Alphaglyph/.github/workflows/keepwarm.yml`,
whose ping window was narrowed for exactly this reason.

## Technical reports: HTML alongside the PDFs

`reports/*.html` are generated by `tools/build_reports.py` from the markdown in
each project's own repository — the same source the PDFs come from, so the page,
the PDF and the code stay in step.

```bash
pip install markdown-it-py
python tools/build_reports.py            # all eight
python tools/build_reports.py --check    # just verify the sources resolve
python tools/build_reports.py --only quantumsafe-technical-report
```

The sources live in **sibling repositories** (`../Quantum-Safe-Scan`, `../Alphaglyph`
and so on), so this runs locally and the output HTML is committed — exactly how
the PDFs are already handled. There is no build step on GitHub Pages. Re-run it
after editing any report's markdown, or the committed HTML goes stale.

All ten documents are built this way, including RL-Trader's paper. That one's
source is LaTeX, so it goes through an extra step first: run
`python tools/paper_to_markdown.py` in the RL-for-Crypto repo to produce
`paper/rl_trader.md`, then build here as usual. That script exists because
pandoc alone drops the abstract, every citation and the figure path — see its
docstring. Re-run it whenever the .tex changes.

A report may also declare `assets` in the manifest (relative paths its markdown
references, e.g. `figures/fig_ablation.png`). Those are copied into `reports/`
keeping the same relative path, so the `<img>` resolves without rewriting the
markdown.

Each page links the PDF beside it, and every `##` section gets an `id` and a
hover anchor, so a reader can be sent straight to a limitations section instead
of to page 7 of a download. Styling is `report.css` on top of `site.css`, so both
themes follow from the existing tokens with nothing to keep in sync.
