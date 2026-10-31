/* Prüft Zeichnungen statt nur Symbolnamen: jede Schnellwahl braucht eine eigene Geometrie. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const c={window:{}};vm.createContext(c);vm.runInContext(fs.readFileSync('app/booking-icons.js','utf8'),c);c.GKBookingIcons=c.window.GKBookingIcons;vm.runInContext(fs.readFileSync('app/transaction-presets.js','utf8'),c);
const groups=c.window.GKPresets.groups,items=groups.flatMap(g=>g.items),icons=c.GKBookingIcons;
const geometry=svg=>svg.match(/<g class="icon-line">([\s\S]*?)<\/g>/)[1];
assert.equal(items.length,70);assert.equal(new Set(items.map(q=>q[5])).size,items.length);
assert.equal(new Set(items.map(q=>geometry(icons.render({icon:q[5]})))).size,items.length,'Keine doppelte Zeichnung');
for(const q of items){assert.ok(icons.categories[q[2]],q[2]);for(const title of [q[0],q[1]]){const e={title,type:q[4],cat:q[2]};assert.equal(icons.key(e),q[5],title);assert.ok(!icons.render(e).includes('undefined'));}}
for(const en of [false,true]){const html=c.window.GKPresets.render('b',String,en);assert.equal([...html.matchAll(/data-entry-icon=/g)].length,70);assert.equal(new Set([...html.matchAll(/<g class="icon-line">([\s\S]*?)<\/g>/g)].map(m=>m[1])).size,70);}
assert.equal(icons.key({type:'income',cat:'Gehalt',title:'Wasser'}),'salary','Fremder Titel darf Kategorie nicht überschreiben');
assert.equal(icons.key({type:'expense',cat:'Unbekannt',title:'Eigener Text'}),'wallet');
console.log('70 eigenständige Zeichnungen; 140 deutsche/englische Buchungsnamen und bestehende Kategorien geprüft.');
