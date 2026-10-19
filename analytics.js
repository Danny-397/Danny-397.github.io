/* Page-view counting for the portfolio.
 *
 * WHY NOT VERCEL: the other sites in this set use Vercel Web Analytics, which
 * works because they are Vercel deployments and the script is edge-served at
 * /_vercel/insights/script.js. This site is GitHub Pages, so that path does
 * not exist here and the same approach would silently 404 — the exact failure
 * the QuantumSafe copy of this file documents.
 *
 * GoatCounter instead: host-independent, free for personal use, no cookies, no
 * personal data, nothing to consent to. It answers the only questions worth
 * asking here — does anyone open the technical reports, and which projects hold
 * attention — without tracking individuals.
 *
 * TO TURN THIS ON (about two minutes):
 *   1. Create a free site at https://www.goatcounter.com (pick any code, e.g.
 *      "danlichtenberger"; non-commercial use is free).
 *   2. Put that code in SITE_CODE below and push.
 *   3. Read the numbers at https://<your-code>.goatcounter.com
 *
 * Until SITE_CODE is set this file loads nothing and does nothing, so it is
 * safe to ship unconfigured.
 */
(function () {
  "use strict";

  var SITE_CODE = "";   // <-- your GoatCounter code goes here

  if (!SITE_CODE) return;                       // unconfigured: stay inert

  var host = location.hostname;
  if (host === "localhost" || host === "127.0.0.1" || host === "") return;

  /* Honour an explicit opt-out. GoatCounter is already anonymous, but a
     visitor who has asked not to be measured should not be measured. */
  try {
    if (navigator.doNotTrack === "1" || window.doNotTrack === "1") return;
  } catch (e) { /* older browsers: fall through and count */ }

  var s = document.createElement("script");
  s.async = true;
  s.src = "https://gc.zgo.at/count.js";
  s.setAttribute("data-goatcounter",
                 "https://" + SITE_CODE + ".goatcounter.com/count");
  document.head.appendChild(s);
})();
