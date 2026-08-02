# Research Summary

<!--
  The opening line below is deliberately DESCRIPTIVE, not argumentative -- it
  states what this document is, and nothing about what the author thinks. That
  keeps it shippable without putting words in your mouth.

  If you want a sentence about WHY you built these, replace the paragraph below
  with it. That is the one place here worth writing yourself: everything else is
  a measurement, and it would be the only claim. Not required for the document
  to work.

  All figures verified against source on 2026-08-01.
-->

Six projects, built May–August 2026. Each entry states what the project does and what
it actually measured — including the three where the central idea did not hold up.

**QuantumSafe Scan** · [quantumsafescan.com](https://quantumsafescan.com) — Finds
cryptography a quantum computer would break, scores exposure 0–100, names the
NIST-standard replacement. The hard part isn't matching `RSA`; it's *not* matching it
in a comment or a dead code path. A hybrid AST-and-regex engine with reachability
ranking took precision from **49.1% to 100%** on a 9-language benchmark at 100% recall
over 50 seeded cases. Audited 10,938 files; of 37 PyPI packages, 86% had a finding.
Exports SARIF and CycloneDX CBOM, so it drops into real CI.

**RL-Trader** · [4-page paper](reports/RL-Trader-Paper.pdf) — PPO from scratch, aimed
at markets as a hostile testbed, asking whether an agent that looks brilliant once
survives five runs. It doesn't. One seed shows **+275%** against a **+19%** benchmark;
across five the same agent averages **−2.7%**, CI **[−31%, +27%]** — indistinguishable
from buy-and-hold, and significantly *worse* on equities (p ≈ 0.002). Its own
significance tooling caught the false positive a naive version ships, reproducing
Henderson et al. (2018) in a new domain. Adds an original surrogate-data test
separating "the agent is weak" from "there is no signal."

**AlphaZero-style Chess Engine** · [rlchess.xyz](https://rlchess.xyz) — Rules only: no
openings, no human games, no evaluation function. Dual-headed ResNet, PUCT tree search,
4,672-move policy head, playable in-browser via ONNX Runtime Web. Scaling self-play 10×
bought **14 Elo**. Diagnosed as a self-play *signal* problem, not a compute ceiling —
92% of games ended non-decisive, starving the value head of gradient. A classical
alpha-beta control beat the random baseline 10–0, confirming the harness was sound.

**AlphaGlyph** · [alphaglyph.org](https://alphaglyph.org) — Symbolic-regression alpha
discovery, evaluated against its own overfitting. Combinatorial Purged Cross-Validation
puts the **probability of backtest overfitting at 72%** across a 42-variant grid, with
about **52%** of in-sample Sharpe surviving out-of-sample. The figure is
window-dependent, and the report documents that instability rather than quoting the
friendlier run. 169 tests in CI.

**Tradeski** · [tradeski.dev](https://www.tradeski.dev/) — Live market, macro, and
sentiment data in one dashboard: 11 ticker symbols, 7 FRED series hourly, a 29-symbol
screener, a retrieval-grounded assistant, 75 tests. Its most useful lesson was a bug:
live prices never reached the browser because the server emitted on one Socket.IO
namespace while the client listened on another. Both halves were correct alone, and all
71 tests passed throughout — every one of them tested a pure function, so no test
covered a contract *between* components. One now does.

**Neural Canvas** · [github.com/Danny-397/neural-canvas](https://github.com/Danny-397/neural-canvas)
— Painting by hand gesture through a webcam: 21 3-D landmarks per hand at ~60
inferences/second, fully on-device, one HTML file, no build step, no server. The hard
problem isn't detection but estimating *intent* from a noisy 60 Hz signal — a fixed
low-pass filter trades jitter against lag, so strokes use a one-euro adaptive filter
whose cutoff rises with hand velocity.
