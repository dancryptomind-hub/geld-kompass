/* Sicherheit: Schutz gegen Klick-Fallen (Clickjacking). App und Konto dürfen nicht unsichtbar in fremden Seiten
   eingebettet werden. GitHub Pages kann dafür keinen Header setzen (frame-ancestors), daher hier im Browser.
   Eigene Seiten (gleiche Herkunft) dürfen weiter einbetten. Eingebunden als erstes Skript im <head>. */
(function () {
  if (window.top === window.self) return;
  var same = false;
  try { same = window.top.location.origin === location.origin; } catch (e) { same = false; }
  if (same) return;
  document.documentElement.style.visibility = "hidden";
  try { window.top.location.replace(location.href); } catch (e) { /* Sandbox/Browser blockt das Ausbrechen */ }
  // Laden sofort beenden: kein weiteres App-Skript läuft im fremden Rahmen, es bleibt nur der Öffnen-Link.
  try { window.stop(); } catch (e) {}
  function show() {
    var html = document.documentElement;
    var b = document.body;
    if (!b) { b = document.createElement("body"); html.appendChild(b); }
    while (b.firstChild) b.removeChild(b.firstChild);
    var a = document.createElement("a");
    a.href = location.href; a.target = "_blank"; a.rel = "noopener";
    a.textContent = "Geld-Kompass öffnen · Open Geld-Kompass";
    a.setAttribute("data-gk-frame-guard", "1");
    b.appendChild(a);
    html.style.visibility = "visible";
  }
  setTimeout(show, 0);
})();
