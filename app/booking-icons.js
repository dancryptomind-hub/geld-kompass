/* Original Geld-Kompass pictograms. Drawn for this project, no icon font or third-party assets. */
(function(root){'use strict';
var shapes={
 salary:'<path d="M7 11h18v13H7zM12 11V8h8v3M7 15q9 5 18 0M14 17h4v4h-4z"/>',
 independent:'<path d="M8 24V11l8-5 8 5v13M12 24v-7h8v7M12 12h8M15 8l2 2"/>',
 sidejob:'<path d="M7 25l10-10M17 15a6 6 0 0 0 7-8l-4 4-3-3 4-4a6 6 0 0 0-8 7L5 22z"/>',
 rent:'<path d="M5 15L16 6l11 9M8 13v12h16V13M13 25v-8h6v8M21 7v4"/><circle cx="10" cy="19" r="1"/>',
 dividends:'<ellipse cx="13" cy="22" rx="7" ry="3"/><path d="M6 17v5M20 17v5M6 17c0-4 14-4 14 0s-14 4-14 0M18 7l3 4 5-7M21 11V4"/>',
 benefits:'<path d="M7 14c0-9 18-9 18 0v7H7zM7 21l-3 4M25 21l3 4M8 13h16M16 6v7"/><circle cx="12" cy="25" r="1.5"/><circle cx="22" cy="25" r="1.5"/>',
 refund:'<path d="M10 11H5V6M5 11a11 11 0 1 1 0 10M11 17h12M11 17l4-4M11 17l4 4"/>',
 income:'<path d="M6 21v5h20v-5M16 5v15M10 14l6 6 6-6"/><path d="M8 8h3M23 8h2"/>',
 home:'<path d="M4 15L16 5l12 10M8 13v13h16V13M13 26v-9h6v9M21 7v4"/>',
 groceries:'<path d="M6 13h20l-3 13H9zM11 13l4-7M21 13l-3-7M12 17v5M16 17v5M20 17v5"/>',
 restaurant:'<path d="M7 6v7q0 4 5 0V6M9.5 6v20M25 6q-8 3-5 12h5M25 6v20"/><path d="M15 17q2 5 5 6"/>',
 car:'<path d="M5 16l3-8h16l3 8v9h-4v-4H9v4H5zM5 16h22M9 18h3M21 18h3M10 8l1-3h10l1 3"/>',
 shield:'<path d="M16 5l10 4v7c0 6-10 11-10 11S6 22 6 16V9zM11 16l4 4 7-8"/>',
 health:'<path d="M11 6h10v6h6v10h-6v6H11v-6H5V12h6zM14 15h4M16 13v4"/>',
 streaming:'<rect x="5" y="7" width="22" height="16" rx="3"/><path d="M13 11l8 4-8 4zM12 27h8M16 23v4"/>',
 phone:'<rect x="10" y="4" width="13" height="24" rx="3"/><path d="M14 8h5M15 24h3M5 8q-4 8 0 16M27 10q3 6 0 12"/>',
 leisure:'<path d="M5 10h22v5a3 3 0 0 0 0 6v5H5v-5a3 3 0 0 0 0-6zM19 10v3M19 17v2M19 23v3M10 15l5 3-5 3z"/>',
 travel:'<rect x="6" y="9" width="20" height="16" rx="3"/><path d="M12 9V5h8v4M11 9v16M21 9v16M10 28v-3M22 28v-3"/>',
 clothing:'<path d="M10 6l-7 6 5 6 3-2v12h10V16l3 2 5-6-7-6q-6 6-12 0zM13 24h6"/>',
 education:'<path d="M5 7q6-2 11 2 5-4 11-2v18q-6-2-11 2-5-4-11-2zM16 9v18M8 12l4 1M20 13l4-1M8 17l4 1"/>',
 family:'<circle cx="10" cy="10" r="4"/><circle cx="23" cy="11" r="3"/><circle cx="17" cy="19" r="3"/><path d="M3 24v-3q0-6 7-6M23 16q6 0 6 6v2M11 28v-2q0-4 6-4t6 4v2"/>',
 pet:'<ellipse cx="16" cy="22" rx="7" ry="6"/><ellipse cx="6" cy="15" rx="3" ry="4"/><ellipse cx="12" cy="8" rx="3" ry="4"/><ellipse cx="22" cy="8" rx="3" ry="4"/><ellipse cx="28" cy="15" rx="2" ry="3"/>',
 taxes:'<path d="M8 4l4 2 4-2 4 2 4-2v24l-4-2-4 2-4-2-4 2zM12 11h8M12 16h4M13 22l6-6"/><circle cx="13" cy="17" r="1"/><circle cx="19" cy="22" r="1"/>',
 gift:'<path d="M5 13h22v5H5zM8 18v10h16V18M16 13v15M16 13c-12-1-10-13-3-8q3 2 3 8c0-6 0-9 4-9 7 0 6 9-4 9"/>',
 alcohol:'<path d="M9 5h14l-2 9q-5 7-10 0zM16 18v9M10 27h12M11 11h10"/>',
 tobacco:'<path d="M5 19h22v6H5zM21 19v6M17 19v6M11 15q-5-3-1-6t0-6M20 15q-4-3 0-6"/>',
 gambling:'<rect x="6" y="6" width="20" height="20" rx="5"/><circle cx="11" cy="11" r="1.4"/><circle cx="21" cy="11" r="1.4"/><circle cx="16" cy="16" r="1.4"/><circle cx="11" cy="21" r="1.4"/><circle cx="21" cy="21" r="1.4"/>',
 snacks:'<path d="M10 11h12v13H10zM10 11L4 7v8l6 2M22 17l6-2V7l-6 4M13 14l6 7M13 21l6-7"/>',
 wallet:'<path d="M6 11V7l17-3v7M5 11h22v16H5zM21 17h6v6h-6a3 3 0 0 1 0-6"/><circle cx="22" cy="20" r=".8"/>',
 stocks:'<path d="M5 26V8M5 26h23M9 21l6-8 5 3 7-10M21 6h6v6"/><path d="M10 25v-3M16 25v-6M22 25v-7"/>',
 crypto:'<path d="M16 4l10 6v12l-10 6-10-6V10zM11 11h7q7 0 4 5 5 6-4 6h-7M14 9v15M11 16h9"/>',
 reserve:'<path d="M9 9h14v4q5 4 3 10-2 6-10 6T6 23q-2-6 3-10zM11 5h10M13 9V5M19 9V5M11 19h10M16 15v8"/>',
 pension:'<path d="M5 17Q16-1 27 17zM16 7v17q0 6 5 3M8 17q4-5 8 0 4-5 8 0"/>',
 property:'<path d="M6 28V7h14v21M20 16h6v12M10 11h2M15 11h2M10 16h2M15 16h2M10 21h2M15 21h2M12 28v-3h4v3"/>',
 investment:'<path d="M16 28V14M16 20Q3 20 5 9q12-2 11 11M16 15Q15 3 28 5q2 11-12 10M10 28h12"/>',
 loan:'<path d="M5 8h22v17H5zM5 13h22M10 20h3M18 21l5-5M18 16h5v5"/>',
 credit:'<rect x="4" y="7" width="24" height="19" rx="4"/><path d="M4 13h24M9 20h5M22 19v4M20 21h4"/>',
 mortgage:'<path d="M4 14L16 4l12 10M8 13v14h10M12 26v-8h6v5"/><circle cx="24" cy="23" r="4"/><path d="M20 27l-3 3M23 22l2 2"/>',
 bnpl:'<path d="M6 7h20v20H6zM6 13h20M11 4v6M21 4v6M10 18h3M19 18h3M10 23h3M19 23h3"/>',
 student:'<path d="M3 12l13-7 13 7-13 7zM8 15v8q8 7 16 0v-8M29 12v12"/>',
 coffee:'<path d="M6 13h16v8q0 7-8 7t-8-7zM22 14h3q6 0 2 7h-5M10 9q-3-3 0-6M17 9q-3-3 0-6"/>',
 water:'<path d="M16 3C13 9 6 14 6 20a10 10 0 0 0 20 0C26 14 19 9 16 3zM10 20q0 6 6 6"/>',
 juice:'<path d="M8 11h16l-2 18H10zM17 20l4-16h7M9 16h14M13 23h5"/>',
 gold:'<path d="M7 12h18l4 13H3zM7 12l4-5h10l4 5M11 7l2 5M9 18h6M21 18h2"/>',
 cinema:'<path d="M6 12h20v16H6zM5 5l20-3 2 8-20 3zM10 5l4 6M18 4l4 6M13 17l7 4-7 4z"/>'
};
var cats={};
function bind(names,keys){names.forEach(function(n,i){cats[n]=keys[i];});}
bind(['Gehalt','Selbstständigkeit','Nebenjob','Mieteinnahmen','Zinsen & Dividenden','Kindergeld & Leistungen','Rückerstattung','Sonstige Einnahmen'],['salary','independent','sidejob','rent','dividends','benefits','refund','income']);
bind(['Wohnen & Nebenkosten','Lebensmittel','Restaurant & Lieferdienst','Mobilität','Versicherungen','Gesundheit & Pflege','Abos & Streaming','Telefon & Internet','Freizeit & Hobby','Reisen','Kleidung & Shopping','Bildung & Bücher','Familie & Kinder','Haustier','Steuern & Gebühren','Geschenke & Spenden','Alkohol','Zigaretten & Tabak','Glücksspiel','Snacks & Impulskäufe','Sonstiges'],['home','groceries','restaurant','car','shield','health','streaming','phone','leisure','travel','clothing','education','family','pet','taxes','gift','alcohol','tobacco','gambling','snacks','wallet']);
bind(['ETF & Aktien','Krypto','Tagesgeld & Notgroschen','Altersvorsorge','Immobilie','Sonstige Investition'],['stocks','crypto','reserve','pension','property','investment']);
bind(['Kreditrate','Kreditkarte','Baufinanzierung','Ratenkauf / BNPL','Studienkredit'],['loan','credit','mortgage','bnpl','student']);
function key(e){var title=String(e.title||'').toLowerCase();if(e.type==='expense'){if(/\b(kino|cinema)\b/.test(title))return 'cinema';if(/kaffee|coffee|starbucks|cappuccino|espresso/.test(title))return 'coffee';if(/\b(wasser|water|volvic|evian)\b/.test(title))return 'water';if(/\b(saft|juice|smoothie)\b/.test(title))return 'juice';}if(e.type==='invest'&&/\bgold\b/.test(title))return 'gold';return cats[e.cat]||({income:'income',invest:'investment',debt:'loan'}[e.type])||'wallet';}
function render(e){var k=key(e);return '<svg viewBox="0 0 32 32" aria-hidden="true" data-entry-icon="'+k+'"><circle class="icon-wash" cx="16" cy="16" r="12"/><g class="icon-line">'+shapes[k]+'</g><path class="icon-spark" d="M27 26l.8 1.8 1.9.7-1.9.8L27 31l-.8-1.7-1.9-.8 1.9-.7z"/></svg>';}
root.GKBookingIcons={key:key,render:render,categories:cats};
})(window);
