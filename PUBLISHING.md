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
