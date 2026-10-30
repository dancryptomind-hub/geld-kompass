// Rendert die Pinterest-Pins (1000 × 1500) als JPG.
// Deutsch: node scripts/build_pins.js      -> pins/pin-XX.jpg (aus scripts/pins.html)
// Englisch: node scripts/build_pins.js en  -> pins/en-XX.jpg  (aus scripts/pins_en.html)
const {chromium}=require('playwright');const path=require('path');const {execSync}=require('child_process');
const en=process.argv[2]==='en';
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1100,height:1600}});
await p.goto('file://'+path.resolve(__dirname,en?'pins_en.html':'pins.html'));await p.waitForTimeout(1200);
const ids=await p.$$eval('.pin',a=>a.map(e=>e.id));
for(const id of ids){const out=path.resolve(__dirname,'../pins/'+(en?'en-':'pin-')+id.slice(1)+'.png');await (await p.$('#'+id)).screenshot({path:out});
  execSync('python3 -c "from PIL import Image;import sys;Image.open(sys.argv[1]).convert(\'RGB\').save(sys.argv[1][:-4]+\'.jpg\',quality=88,optimize=True)" '+JSON.stringify(out));require('fs').unlinkSync(out);}
await b.close();console.log(ids.length,'Pins');})();
