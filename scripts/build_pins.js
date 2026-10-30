// Rendert scripts/pins.html zu pins/pin-XX.jpg (1000 × 1500). Aufruf: node scripts/build_pins.js
const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1100,height:1600}});
await p.goto('file://'+path.resolve(__dirname,'pins.html'));await p.waitForTimeout(800);
const ids=await p.$$eval('.pin',a=>a.map(e=>e.id));
for(const id of ids){await (await p.$('#'+id)).screenshot({path:path.resolve(__dirname,'../pins/pin-'+id.slice(1)+'.png')});}
await b.close();console.log(ids.length,'Pins');})();
