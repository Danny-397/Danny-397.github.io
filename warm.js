/* Wake the project backends while the visitor is still reading.

   Four of the projects run on Render's free tier, which sleeps an idle service
   and takes 30-75 s to wake it (measured 2026-10-27: AlphaGlyph 74 s,
   QuantumSafe 32 s). A reader spends longer than that on this page before
   clicking "Try it live", so one ping per visit, on arrival, means the demo
   is usually awake by the time they get there.

   A scheduled keep-alive would do the same at all hours, but the free tier
   allows 750 instance-hours a month across every service, and going over
   suspends them all. Waking on a real visit spends hours only when someone is
   actually looking.

   One ping per backend per browser session; skipped for automated browsers
   and data-saver mode. "no-cors" because only the request matters, not the
   response. */
(function () {
  "use strict";
  var BACKENDS = [
    "https://trading-bot-jy87.onrender.com/health",          // AlphaGlyph
    "https://tradeski.onrender.com/health",                  // Tradeski
    "https://quantumsafe-api.onrender.com/health",           // QuantumSafe
    "https://rl-for-crypto-and-stocks.onrender.com/health",  // RL Trader lab
  ];
  var KEY = "warm-pinged";

  if (navigator.webdriver) return;
  if (navigator.connection && navigator.connection.saveData) return;
  try { if (sessionStorage.getItem(KEY)) return; } catch (e) { /* storage blocked: ping anyway */ }

  function ping() {
    try { sessionStorage.setItem(KEY, "1"); } catch (e) { /* ignore */ }
    BACKENDS.forEach(function (url) {
      try { fetch(url, { mode: "no-cors", cache: "no-store", keepalive: true }).catch(function () {}); }
      catch (e) { /* very old browser: nothing to do */ }
    });
  }

  // After the page has painted, and only once it is actually being looked at.
  function whenVisible() {
    if (document.visibilityState === "visible") { setTimeout(ping, 1500); return; }
    document.addEventListener("visibilitychange", function onVis() {
      if (document.visibilityState !== "visible") return;
      document.removeEventListener("visibilitychange", onVis);
      setTimeout(ping, 1500);
    });
  }
  if (document.readyState === "complete") whenVisible();
  else window.addEventListener("load", whenVisible);
})();
