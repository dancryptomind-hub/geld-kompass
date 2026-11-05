const assert=require('node:assert/strict');
const audit=require(process.env.GK_AUDIT_MODULE||'../audit-engine.js');
const h=(symbol,type,value,extra={})=>({symbol,type,name:symbol,value,...extra});
const budget=(income,spend,invest=0,debts=[],liquid=5000)=>({income,spend,invest,debts,liquid,hasIncome:true,hasSpending:true,hasLiquid:true});
const run=(holdings,context={},extra={})=>audit.analyze({holdings,context,today:'2026-11-05',...extra});
let global=run([h('VWCE.DE','ETF',75000),h('AAPL','Aktie',25000)]);
let sector=run([h('IQQH.DE','ETF',75000),h('AAPL','Aktie',25000)]);
let unknown=run([h('FUND','ETF',75000),h('AAPL','Aktie',25000)]);
assert.equal(global.exposure.global,.75);assert.equal(sector.exposure.global,0);assert.equal(unknown.exposure.global,0);
assert.ok(global.scores.div>sector.scores.div,'global equity and energy sector are different');
assert.ok(sector.findings.some(f=>f.code==='focused-fund'));assert.ok(unknown.findings.some(f=>f.code==='unknown-fund'));
assert.ok(!sector.findings.some(f=>f.code==='global-equity'));
let miners=run([h('GDX','ETF',100000)]);assert.equal(miners.exposure.metals,0);assert.equal(miners.exposure.sector,1);
let gold=run([h('GOLD-G','Edelmetall',100000)]);assert.equal(gold.exposure.metals,1);
assert.ok(!global.findings.some(f=>f.code==='missing-gold'||f.code==='missing-crypto'),'no mandatory metal or crypto quota');
let a=run([h('BTC','Krypto',31000),h('BTC','Krypto',20200),h('VWCE.DE','ETF',48800)]);
assert.equal(a.top.share,.512);assert.equal(a.findings.find(f=>f.code==='concentration').loss,25600);
let healthy=run([h('VWCE.DE','ETF',10000)],budget(2500,1700,500));
let costly=run([h('VWCE.DE','ETF',10000)],budget(2500,1700,500,[{balance:20000,rate:18,payment:500,kind:'card'}],200));
assert.ok(costly.scores.calm<healthy.scores.calm);assert.ok(costly.findings.some(f=>f.code==='debt-investing'));
let shortfall=run([h('VWCE.DE','ETF',10000)],budget(2500,2400,400));assert.ok(shortfall.findings.some(f=>f.code==='investment-gap'));
let mortgage=run([h('VWCE.DE','ETF',500000)],budget(7000,3500,1500,[{balance:100000,rate:2,payment:400,kind:'mortgage'}],50000));assert.ok(!mortgage.findings.some(f=>f.code==='debt-investing'));
let low=run([h('VWCE.DE','ETF',10000)],budget(2000,1400,400));let high=run([h('VWCE.DE','ETF',10000)],budget(10000,9700,200));
assert.equal(low.context.investmentRate,.2);assert.equal(high.context.investmentRate,.02);assert.ok(low.context.investmentRate>high.context.investmentRate);
let noIncome=run([h('VWCE.DE','ETF',10000)]);assert.equal(noIncome.context.investmentRate,null);assert.equal(noIncome.known.calm,false);
let duplicate=run([h('EUNL.DE','ETF',50000),h('XDWD.DE','ETF',50000)]);assert.ok(duplicate.findings.some(f=>f.code==='overlap'));
let manual=run([h('CUSTOM','ETF',100000,{focus:'sector'})]);assert.equal(manual.exposure.sector,1);
let future=run([h('AAPL','Aktie',10000,{transactions:[{d:'2030-01-01',k:'in',q:1,p:100}]} )]);assert.equal(future.transactions.length,0);
let past=run([h('AAPL','Aktie',10000,{price:200,transactions:[{d:'2026-01-01',k:'in',q:1,p:100}]} )],{}, {realized:[{name:'AAPL',symbol:'AAPL',qty:1,price:100,current:200,pl:-20,date:'2026-02-01'}]});
assert.ok(past.findings.some(f=>f.code==='sale-comparison'));assert.ok(!past.findings.some(f=>/panic|fomo/.test(f.code)),'price path does not prove emotion');
let noFees=run([h('AAPL','Aktie',10000,{transactions:[{d:'2026-01-01',k:'in',q:1,p:100}]} )]);assert.equal(noFees.known.cost,false);
let frozen={holdings:[h('VWCE.DE','ETF',500)],context:budget(1000,500,100),today:'2026-11-05'};const original=JSON.stringify(frozen);audit.analyze(frozen);assert.equal(JSON.stringify(frozen),original,'analysis does not mutate user data');
console.log('Audit: global/sector/unknown funds, gold vs miners, duplicate-wallet weights, context/debt/budget, income ratios, missing data, overlap, future dates, neutral sale analysis, no invented fees and no mutation');

let factor=run([h('IS3Q.DE','ETF',75000),h('AAPL','Aktie',25000)]);assert.equal(factor.exposure.globalFactor,.75);assert.ok(factor.scores.div>sector.scores.div,'international factor funds are not single-sector funds');assert.ok(factor.findings.some(f=>f.code==='strategy-fund'));let brokenDate=run([h('AAPL','Aktie',1000,{transactions:[{d:'2026-01-99',k:'in',q:1,p:100}]} )]);assert.equal(brokenDate.transactions.length,0);

let stale=run([h('AAPL','Aktie',10000,{transactions:['2020-01-01','2020-02-01','2020-03-01'].map(d=>({d,k:'in',q:1,p:100}))})]);assert.equal(stale.known.disc,false,'old purchases do not prove current regularity');let sold=run([h('AAPL','Aktie',500,{transactions:[{d:'2026-10-01',k:'out',q:2,p:100}]})],{}, {realized:[{symbol:'AAPL',name:'AAPL',qty:2,price:100,current:150,date:'2026-10-01'},{symbol:'SOLD',name:'Sold asset',qty:1,price:200,current:250,date:'2026-10-02'}]});assert.equal(sold.transactions.filter(t=>t.kind==='out').length,2,'partial sale not counted twice; fully sold holding still counted');let transfer=run([h('BTC','Krypto',1000,{transactions:[{d:'2026-10-01',k:'in',q:1,p:null}]})]);assert.equal(transfer.avgTrades,0,'unpriced transfer is not a priced order');

let customInterest=run([h('VWCE.DE','ETF',10000)],{...budget(3000,1500,500,[{balance:10000,rate:6,payment:200}]),debtThreshold:5});assert.ok(customInterest.findings.some(f=>f.code==='debt-investing'));let zeroInterest=run([h('VWCE.DE','ETF',10000)],{...budget(3000,1500,500,[{balance:10000,rate:0,payment:200}]),debtThreshold:0});assert.ok(!zeroInterest.findings.some(f=>f.code==='debt-investing'),'zero interest is not expensive debt even with a zero threshold');

assert.equal(audit.analyze({holdings:[{symbol:"FLAT",type:"Aktie",value:100,cost:100,gain:0}]}).winners,0,"unchanged positions are not positions in profit");
