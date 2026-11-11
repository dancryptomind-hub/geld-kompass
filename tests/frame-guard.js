/* Sicherheit: Klick-Fallen-Schutz (frame-guard.js). /app/ und /konto/ in einer FREMDEN Seite eingebettet =>
   entweder bricht die Seite aus dem Rahmen aus (wird Hauptseite) oder – wenn der Rahmen das verbietet (sandbox) –
   zeigt sie nur einen Link zum Öffnen im eigenen Tab. Gleiche Herkunft und direkter Aufruf laufen normal.
   Lokal: python3 -m http.server 8765 & node tests/frame-guard.js */
const {chromium}=require('playwright');const assert=require('assert');const BASE=process.env.BASE||'http://localhost:8765';
const EVIL=BASE.replace('localhost','127.0.0.1')+'/__evil'; // andere Herkunft (Host), lokal erreichbar
const frameHTML=(src,sandbox)=>'<!doctype html><title>x</title><iframe id=f '+(sandbox?'sandbox="allow-scripts allow-same-origin allow-popups" ':'')+'src="'+src+'" width=800 height=600></iframe>';
(async()=>{const b=await chromium.launch({args:['--disable-features=LocalNetworkAccessChecks,BlockInsecurePrivateNetworkRequests,PrivateNetworkAccessSendPreflights']});try{
 const c=await b.newContext({serviceWorkers:'block'});
 await c.route('**/*',r=>{const u=r.request().url();
  if(u.startsWith(EVIL+'/sandbox'))return r.fulfill({contentType:'text/html',body:frameHTML(BASE+u.slice((EVIL+'/sandbox').length),true)});
  if(u.startsWith(EVIL))return r.fulfill({contentType:'text/html',body:frameHTML(BASE+u.slice(EVIL.length),false)});
  if(u.startsWith(BASE+'/__same/'))return r.fulfill({contentType:'text/html',body:frameHTML(BASE+u.slice((BASE+'/__same').length),false)});
  return u.startsWith(BASE)?r.continue():r.abort();});
 const p=await c.newPage();
 for(const path of ['/app/?lang=de','/konto/']){
  // 1) fremde Seite ohne Sandbox: Ausbrechen erwartet (oder Sperrbild)
  await p.goto(EVIL+path);await p.waitForTimeout(1500);
  const broke=p.url().startsWith(BASE+path.split('?')[0]);
  if(!broke){const f=p.frames().find(x=>x.url().startsWith(BASE));assert.ok(f,'Rahmen geladen '+path);
   const r=await f.evaluate(()=>({link:!!document.querySelector('[data-gk-frame-guard]'),n:document.body?document.body.children.length:0}));
   assert.ok(r.link&&r.n===1,'Fremde Einbettung gesperrt: '+path+' '+JSON.stringify(r));}
  // 2) fremde Seite mit Sandbox (Ausbrechen verboten): nur Öffnen-Link
  await p.goto(EVIL+'/sandbox'+path);await p.waitForTimeout(1500);
  assert.ok(p.url().startsWith(EVIL),'Sandbox verhindert Ausbrechen');
  const f2=p.frames().find(x=>x.url().startsWith(BASE));assert.ok(f2,'Sandbox-Rahmen geladen '+path);
  const r2=await f2.evaluate(()=>({link:!!document.querySelector('[data-gk-frame-guard]'),n:document.body?document.body.children.length:0,vis:getComputedStyle(document.documentElement).visibility}));
  assert.ok(r2.link&&r2.n===1&&r2.vis==='visible','Sandbox-Einbettung zeigt nur den Öffnen-Link: '+path+' '+JSON.stringify(r2));
  // 3) eigene Seite bettet ein: normal
  await p.goto(BASE+'/__same'+path);await p.waitForTimeout(1500);
  const g=p.frames().find(x=>x!==p.mainFrame()&&x.url().startsWith(BASE+path.split('?')[0]));assert.ok(g,'eigener Rahmen '+path);
  const s=await g.evaluate(()=>({link:!!document.querySelector('[data-gk-frame-guard]'),n:document.body.children.length}));
  assert.ok(!s.link&&s.n>1,'Gleiche Herkunft bleibt nutzbar: '+path);
  // 4) direkt: normal
  await p.goto(BASE+path);await p.waitForTimeout(800);
  assert.ok(!(await p.locator('[data-gk-frame-guard]').count())&&(await p.evaluate(()=>document.body.children.length))>1,'Ohne Rahmen normal: '+path);
  console.log(path+': fremd '+(broke?'ausgebrochen':'gesperrt')+', Sandbox gesperrt, eigen + direkt normal');}
 console.log('OK: Klick-Fallen-Schutz für App und Konto');}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
