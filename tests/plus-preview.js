/* Nur für Tests: Plus-Funktionen prüfen, ohne echtes Konto.
   1) Kontokonfiguration mit previewOpen:true (nur per Playwright-Route im Testbrowser).
   2) Den Plus-Code liefert der Server nur an zahlende Konten. Im Test kommt er aus dem privaten Repo (Umgebungsvariable PLUS_BUNDLE).
   Ohne PLUS_BUNDLE (öffentliche CI) gibt die Funktion false zurück und der Test wird übersprungen; er läuft in der CI des privaten Repos. */
const fs = require('fs'); const path = require('path');
module.exports = async function plusPreview(target) {
  const file = process.env.PLUS_BUNDLE;
  if (!file || !fs.existsSync(file)) return false;
  const body = fs.readFileSync(path.join(__dirname, '..', 'konto', 'config.js'), 'utf8').replace('previewOpen:false', 'previewOpen:true');
  const bundle = fs.readFileSync(file, 'utf8');
  await target.route(/\/konto\/config\.js(\?.*)?$/, r => r.fulfill({ contentType: 'application/javascript', body }));
  await target.route(/\/functions\/v1\/plus-code(\?.*)?$/, r => r.fulfill({ contentType: 'text/javascript', body: bundle, headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'GET, OPTIONS' } }));
  return true;
};
