/* Nur für Tests: Plus-Funktionen prüfen, ohne echtes Konto. Liefert im Testbrowser die Kontokonfiguration mit previewOpen:true aus.
   Auf der echten Seite gibt es diesen Weg nicht (previewOpen ist dort false, Plus nur für Admin-Konto oder bezahltes Abo). */
const fs = require('fs'); const path = require('path');
module.exports = async function plusPreview(target) {
  const body = fs.readFileSync(path.join(__dirname, '..', 'konto', 'config.js'), 'utf8').replace('previewOpen:false', 'previewOpen:true');
  await target.route(/\/konto\/config\.js(\?.*)?$/, r => r.fulfill({ contentType: 'application/javascript', body }));
};
