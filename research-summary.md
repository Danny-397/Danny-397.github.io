# Research Summary

<!--
  The opening line below is deliberately DESCRIPTIVE, not argumentative -- it
  states what this document is, and nothing about what the author thinks. That
  keeps it shippable without putting words in your mouth.

  If you want a sentence about WHY you built these, replace the paragraph below
  with it. That is the one place here worth writing yourself: everything else is
  a measurement, and it would be the only claim. Not required for the document
  to work.

  All figures verified against source on 2026-08-01; RL-Trader and Tradeski
  figures re-verified 2026-09-30.
-->

Six projects, each deployed to a public URL. Each entry states what the project does
and what it measured.

**QuantumSafe Scan** · [quantumsafescan.com](https://quantumsafescan.com) · [DOI](https://doi.org/10.5281/zenodo.23843488) — Finds
cryptography a quantum computer would break, scores exposure 0–100, names the
NIST-standard replacement. The hard part isn't matching `RSA`; it's *not* matching it
in a comment or a dead code path. A hybrid AST-and-regex engine with reachability
ranking took precision from **49.1% to 100%** on a 9-language benchmark at 100% recall
over 50 seeded cases. Audited 11,275 files; of 37 PyPI packages, 86% had a finding.
Exports SARIF and CycloneDX CBOM, so it drops into real CI.

**RL-Trader** · [4-page paper](reports/RL-Trader-Paper.pdf) · [DOI](https://doi.org/10.5281/zenodo.23843503) — PPO from scratch, aimed
at markets as a hostile testbed, asking whether an agent that looks brilliant once
survives thirty runs. It doesn't. One seed showed **+275%** against a **+19%** benchmark.
Two pre-registered studies then audited the result: they found and fixed two real flaws
(a PPO that trailed a reference library, a crypto split that leaked across coins), and
the conclusion held. Over 30 seeds the stock agent trails buy-and-hold in **all 300 runs**
(p = 0.002); the crypto agent trails on five of six coins (p = 0.19). Retrained across four
periods of history, it trails in every period on stocks and three of four on crypto. Its
daily long-or-short calls are right **50.0%** of the time. Its own significance tooling
caught the false positive a naive version ships, reproducing Henderson et al. (2018) in a
new domain. Adds an original surrogate-data test separating "the agent is weak" from
"there is no signal."

**AlphaZero-style Chess Engine** · [rlchess.xyz](https://rlchess.xyz) — Self-play from
the rules, with no openings or human games. Dual-headed ResNet, PUCT tree search,
4,672-move policy head, playable in-browser via ONNX Runtime Web. Self-play collapses into
a **draw cycle** (all threefold repetition from iteration 3), and 10× the self-play leaves
88% of games undecided. Across three training seeds per arm, measured against each run's own
starting network, training inside the cycle made the network **worse**: −93 Elo against random
(95% CI −125 to −60) and −155 against a material-greedy opponent. A material-assisted search only held
level (+6, −19 to +31); a July single-seed gain of +31 did not replicate, and an earlier "signal, not
compute" headline was withdrawn after a confound in its evaluation was found. Scoring drawn
games by material did not help either (−93 again). After fixing a search bug that hid repetitions
of earlier game positions and adding self-play contempt, repetitions fell from 82% of games to 16%
and checkmates tripled, but the network still declined by the same amount (−91): the cycle is real,
not the cause.

**AlphaGlyph** · [alphaglyph.org](https://alphaglyph.org) — Symbolic-regression alpha
discovery, evaluated against its own overfitting. Combinatorial Purged Cross-Validation
puts the **probability of backtest overfitting at 72%** across a 42-variant grid, with
about **52%** of in-sample Sharpe surviving out-of-sample. The figure is
window-dependent, and the report documents that instability rather than quoting the
friendlier run. 337 tests in CI.

**Tradeski** · [tradeski.dev](https://www.tradeski.dev/) — Live market, macro, and
sentiment data in one dashboard: 11 ticker symbols, 7 FRED series hourly, a 29-symbol
screener, a retrieval-grounded assistant, 336 tests. Its most useful lesson was a bug:
live prices never reached the browser because the server emitted on one Socket.IO
namespace while the client listened on another. Both halves were correct alone, and all
71 tests passed throughout — every one of them tested a pure function, so no test
covered a contract *between* components. One now does. The assistant is measured the same
way: a 32-question eval scores 79% on held-out questions written before any fix, and its
first run (57%) mostly measured a broken grader, not the model.

**Neural Canvas** · [github.com/Danny-397/neural-canvas](https://github.com/Danny-397/neural-canvas)
— Painting by hand gesture through a webcam: 21 3-D landmarks per hand at ~60
inferences/second, fully on-device, one HTML file, no build step, no server. The hard
problem isn't detection but estimating *intent* from a noisy 60 Hz signal — a fixed
low-pass filter trades jitter against lag, so strokes use a one-euro adaptive filter
whose cutoff rises with hand velocity.
