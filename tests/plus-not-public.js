/* Sicherheit: Der Plus-Code darf nie wieder in der öffentlichen App stehen. Er liegt im privaten Repo geld-kompass-plus
   und wird nur vom Server (Edge Function plus-code) an Konten mit Plus, das Admin-Konto oder nach Report-Kauf geliefert. */
const fs = require('fs'); const path = require('path'); const bad = [];
const forbidden = ['nomadHTML', 'taxCockpitHTML', 'taxCockpitOther', 'cashflowPlan', 'cfDetail', 'frSteps', 'sellHint', 'taxYearOther', 'schengenInfo', 'nomadPrint', 'taxExportCSV', 'nomadTaxHTML', 'payerBadges'];
function walk(d) { for (const f of fs.readdirSync(d)) { if (['.git', 'node_modules', 'tests', 'supabase'].includes(f)) continue; const p = path.join(d, f); const st = fs.statSync(p);
  if (st.isDirectory()) walk(p); else if (/\.(html|js)$/.test(f)) { const s = fs.readFileSync(p, 'utf8'); forbidden.forEach(n => { if (new RegExp('function\\s+' + n + '\\s*\\(').test(s)) bad.push(path.relative('.', p) + ': ' + n); }); } } }
walk('.');
if (fs.existsSync('tax-guide.js')) bad.push('tax-guide.js liegt wieder öffentlich');
const app = fs.readFileSync('app/index.html', 'utf8');
if (!/function plusLoad\(/.test(app) || !/plus-code/.test(app)) bad.push('Plus-Lader fehlt');
if (/previewOpen:true/.test(fs.readFileSync('konto/config.js', 'utf8'))) bad.push('Vorschau ist offen');
if (bad.length) { console.error('FEHLER:\n' + bad.join('\n')); process.exit(1); }
console.log('OK plus-not-public');
