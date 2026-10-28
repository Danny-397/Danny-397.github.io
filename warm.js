/* Wake a project's backend when the visitor shows interest in that project.

   Four of the projects run on Render's free tier, which sleeps an idle service
   and takes 30-75 s to wake it (measured 2026-10-27: AlphaGlyph 74 s,
   QuantumSafe 32 s). Pinging a backend when the reader reaches that project's
   card gives it a head start before they click "Try it live".

   The first version pinged all four on every page load. Each wake keeps a
   service up for at least 15 minutes, so every visit cost about an hour of the
   750 instance-hours a month the free tier shares across all services, and on
   2026-10-28 the account ran out and every backend was suspended. This one
   pings only the project the reader hovers, focuses, or keeps on screen for
   1.5 s, at most once per backend per browser session.

   Skipped for automated browsers and data-saver mode. "no-cors" because only
   the request matters, not the response. */
(function () {
  "use strict";
  var BACKENDS = {
    "alphaglyph":  "https://trading-bot-jy87.onrender.com/health",
    "tradeski":    "https://tradeski.onrender.com/health",
    "quantumsafe": "https://quantumsafe-api.onrender.com/health",
    "rl-trader":   "https://rl-for-crypto-and-stocks.onrender.com/health",
  };

  if (navigator.webdriver) return;
  if (navigator.connection && navigator.connection.saveData) return;

  function ping(id) {
    var key = "warm-" + id;
    try { if (sessionStorage.getItem(key)) return; sessionStorage.setItem(key, "1"); }
    catch (e) { /* storage blocked: ping anyway */ }
    try { fetch(BACKENDS[id], { mode: "no-cors", cache: "no-store", keepalive: true }).catch(function () {}); }
    catch (e) { /* very old browser: nothing to do */ }
  }

  function wire() {
    Object.keys(BACKENDS).forEach(function (id) {
      var card = document.getElementById(id);
      if (!card) return;
      var once = function () { ping(id); };
      card.addEventListener("pointerenter", once, { once: true });
      card.addEventListener("focusin", once, { once: true });
      // Readers on phones never hover: a card that stays mostly on screen counts too.
      if ("IntersectionObserver" in window) {
        // Half the *screen*, not half the card: on a phone a card can be taller
        // than two screens and would never be half visible.
        // It must also stay there 1.5 s, so skimming past a card wakes nothing.
        var timer = null;
        var io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            var reading = e.intersectionRect.height >= window.innerHeight * 0.5;
            if (reading && !timer) {
              timer = setTimeout(function () { ping(id); io.disconnect(); }, 1500);
            } else if (!reading && timer) {
              clearTimeout(timer); timer = null;
            }
          });
        }, { threshold: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1] });
        io.observe(card);
      }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", wire);
  else wire();
})();
