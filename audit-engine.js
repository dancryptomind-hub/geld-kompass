/* Lokale Auswertung: Produktinhalt, erfasste Monatswerte und Datenabdeckung.
   Kein Anlegervergleich, keine Diagnose und keine ausgedachten Kosten. */
(function(root,factory){var api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.GKAudit=api;})(typeof window==='object'?window:globalThis,function(){'use strict';
var GROUPS={
 'global-equity':['VWCE.DE','VGWL.DE','IUSQ.DE','SPYI.DE','VT'],
 'global-developed':['EUNL.DE','XDWD.DE','SPPW.DE','SWDA.L','IWDA.AS','URTH'],
 'regional':['IS3N.DE','EUNM.DE','XMME.DE','VFEM.DE','SXR8.DE','VUAA.DE','EXS1.DE','DBXD.DE','EXSA.DE','EUNK.DE','MEUD.PA','EXUS.DE','SPYM.DE','AEEM.PA','XMAS.DE','XCS6.DE','QDV5.DE','EUNN.DE','ISF.L','XIU.TO','VXUS','VEU','VWO','IEMG','EEM','FXI','MCHI','EWJ','EWY','EWT','INDA','VPL','SPY','VOO','IVV','VTI'],
 'sector':['SXRV.DE','EQQQ.DE','EXXT.DE','QDVE.DE','XAIX.DE','2B76.DE','IQQH.DE','G2X.DE','IS0E.DE','GDX','GDXJ','SIL','COPX','URA','PICK','URNM','KWEB','ICLN','XLE','QQQ'],
 'global-factor':['IUSN.DE','IS3Q.DE','IS3R.DE','VHYL.DE','TDIV.AS'],
 'regional-factor':['ZPRV.DE','ZPRX.DE'],
 'bonds':['EUNH.DE'],
 'metals':['SLV','GLD','IAU','SGLN.L','PHAU.L'],
 'commodity':['CPER'],
 'crypto':['IBIT','FBTC']
};
var EM={'IS3N.DE':1,'EUNM.DE':1,'XMME.DE':1,'VFEM.DE':1,'AEEM.PA':1,'SPYM.DE':1,'VWO':1,'IEMG':1,'EEM':1};
var INDEX=Object.create(null);Object.keys(GROUPS).forEach(function(k){GROUPS[k].forEach(function(s){INDEX[s]=k;});});
var FOCI=['global-equity','global-developed','regional','sector','factor','global-factor','regional-factor','bonds','metals','commodity','crypto','unknown'];
function num(v){v=Number(v);return Number.isFinite(v)?v:0;}
function clamp(v,a,b){return Math.min(b,Math.max(a,v));}
function profile(h){var type=h.type||h.t||'',s=String(h.symbol||h.s||'').toUpperCase(),manual=FOCI.indexOf(h.focus)>=0?h.focus:null;
 if(type==='ETF')return {kind:manual||INDEX[s]||'unknown',source:manual?'user':INDEX[s]?'catalogue':'missing',fund:true};
 return {kind:type==='Krypto'?'crypto':type==='Edelmetall'?'metals':type==='Rohstoff'?'commodity':type==='Anleihe'?'bonds':'stock',source:'holding',fund:false};}
function validDate(s,today){if(!/^\d{4}-\d{2}-\d{2}$/.test(s||'')||s>today)return false;var d=new Date(s+'T12:00:00Z');return Number.isFinite(d.getTime())&&d.toISOString().slice(0,10)===s;}
function analyze(input){input=input||{};var today=input.today||new Date().toISOString().slice(0,10),holdings=(input.holdings||[]).filter(function(h){return num(h.value)>0;}),total=holdings.reduce(function(s,h){return s+num(h.value);},0),groups=Object.create(null),findings=[],transactions=[],profiles=[],family={},scores={disc:50,calm:50,div:50,timing:50,cost:50},known={disc:false,calm:false,div:total>0,timing:false,cost:false};
 var exposure={global:0,developed:0,regional:0,sector:0,factor:0,globalFactor:0,regionalFactor:0,metals:0,commodity:0,crypto:0,bonds:0,stock:0,unknown:0};
 holdings.forEach(function(h){var p=profile(h),symbol=h.symbol||h.s||h.name,value=num(h.value),key=String(symbol),g=groups[key];if(!g)g=groups[key]={symbol:symbol,name:h.name||symbol,type:h.type||h.t,value:0,kind:p.kind,fund:p.fund};g.value+=value;if(g.kind!==p.kind)g.kind='unknown';var kind=p.kind==='global-equity'?'global':p.kind==='global-developed'?'developed':p.kind==='global-factor'?'globalFactor':p.kind==='regional-factor'?'regionalFactor':p.kind;exposure[kind]=(exposure[kind]||0)+value;profiles.push({symbol:symbol,name:h.name||symbol,value:value,profile:p});
  (h.transactions||[]).forEach(function(t){if(['in','out','plan'].indexOf(t.k)<0||!validDate(t.d,today)||num(t.q)<=0||num(t.p)<0)return;transactions.push({symbol:symbol,name:h.name||symbol,date:t.d,kind:t.k,qty:num(t.q),price:num(t.p),fee:t.fee==null?null:Math.max(0,num(t.fee))});});
 });
 Object.keys(exposure).forEach(function(k){exposure[k]/=total||1;});
 var list=Object.keys(groups).map(function(k){return groups[k];}).sort(function(a,b){return b.value-a.value;}),focused=list.filter(function(g){return ['global-equity','global-developed','global-factor','bonds'].indexOf(g.kind)<0;}),top=focused[0]||null,topShare=top?top.value/(total||1):0,global=exposure.global+exposure.developed;
 var focusShare=exposure.sector+exposure.factor*.5+exposure.globalFactor*.4+exposure.regionalFactor*.6+exposure.commodity+exposure.metals+exposure.crypto+exposure.unknown;
 if(top&&topShare>.3)findings.push({code:top.fund?'fund-concentration':'concentration',severity:'warn',symbol:top.symbol,name:top.name,share:topShare,loss:top.value*.5});
 if(exposure.sector+exposure.factor>.25)findings.push({code:'focused-fund',severity:'warn',share:exposure.sector+exposure.factor});
 if(exposure.regional+exposure.regionalFactor>.5)findings.push({code:'regional-fund',severity:'info',share:exposure.regional+exposure.regionalFactor});
 if(exposure.globalFactor+exposure.regionalFactor>.25)findings.push({code:'strategy-fund',severity:'info',share:exposure.globalFactor+exposure.regionalFactor,international:exposure.globalFactor});
 if(exposure.unknown>0)findings.push({code:'unknown-fund',severity:'info',share:exposure.unknown});
 if(global>.5)findings.push({code:'global-equity',severity:'info',share:global,developed:exposure.developed,allWorld:exposure.global});
 if(exposure.crypto>.25)findings.push({code:'crypto-share',severity:'warn',share:exposure.crypto});
 if(exposure.metals>.5)findings.push({code:'metals-share',severity:'info',share:exposure.metals});
 profiles.forEach(function(p){var familyKey=p.profile.kind;if(familyKey==='global-equity'||familyKey==='global-developed'){if(!family.equity)family.equity=new Set();family.equity.add(p.symbol);}});
 Object.keys(family).forEach(function(k){if(family[k].size>1)findings.push({code:'overlap',severity:'info',kind:k,symbols:Array.from(family[k])});});
/* Streuungs-Skala: MSCI World allein ≈ 70 (Industrieländer, rund 60-70 % USA), All-World/IMI oder World + Schwellenländer ≈ 85,
    dazu kleine Anteile Gold, Bitcoin, Anleihen oder vermietete Immobilien bis 100. Einzeltitel zählen je nach Anzahl. */
 var emShare=list.filter(function(g){return EM[String(g.symbol).toUpperCase()];}).reduce(function(s,g){return s+g.value;},0)/(total||1),dev=exposure.developed,emC=dev>0?Math.min(emShare,dev*.35):0,
  stocks=list.filter(function(g){return g.kind==='stock';}),stockTot=stocks.reduce(function(s,g){return s+g.value;},0),stockEff=stockTot>0?1/stocks.reduce(function(s,g){return s+Math.pow(g.value/stockTot,2);},0):0,
  divBase=(exposure.global+(emC>0?dev+emC:0))*85+(emC>0?0:dev*70)+exposure.globalFactor*72+Math.max(0,exposure.regional-emC)*55+exposure.regionalFactor*50+exposure.sector*35+exposure.factor*50+exposure.bonds*70+exposure.metals*60+exposure.commodity*45+exposure.crypto*40+exposure.unknown*50+exposure.stock*(45+Math.min(25,Math.max(0,stockEff-1)*2.5)),
  rawCtx=input.context||{},reShare=num(rawCtx.realEstate)>0?num(rawCtx.realEstate)/(num(rawCtx.realEstate)+total):0,
  divBonus=(exposure.metals>=.03&&exposure.metals<=.25?8:0)+(exposure.crypto>=.01&&exposure.crypto<=.15?6:0)+(exposure.bonds>=.05?5:0)+(reShare>=.1?3:0),
  divPen=Math.max(0,topShare-.2)*65+Math.max(0,exposure.crypto-.25)*60+Math.max(0,exposure.metals-.35)*40+Math.max(0,exposure.regional+exposure.regionalFactor-emC-.5)*20;
 scores.div=Math.round(clamp(divBase+divBonus-divPen,5,100));
 if(dev>.5&&emC<.02)findings.push({code:'us-heavy',severity:'info',share:dev});
 if(!total){var cashV=Math.max(0,num(rawCtx.liquid)),reV=Math.max(0,num(rawCtx.realEstate)),otV=Math.max(0,num(rawCtx.otherAssets));if(cashV+reV+otV>0){known.div=true;scores.div=Math.round(clamp(20+(reV>0?15:0)+(otV>0?10:0)+(cashV>0?5:0),5,60));findings.push({code:'no-portfolio',severity:'info',cash:cashV,realEstate:reV,other:otV});}}
 var raw=input.context||{},debtThreshold=raw.debtThreshold==null?8:clamp(num(raw.debtThreshold),0,1000),income=Math.max(0,num(raw.income)),spend=Math.max(0,num(raw.spend)),invest=Math.max(0,num(raw.invest)),liquid=Math.max(0,num(raw.liquid)),debts=(raw.debts||[]).filter(function(d){return num(d.balance)>0;}),debtTotal=debts.reduce(function(s,d){return s+num(d.balance);},0),debtPayment=debts.reduce(function(s,d){return s+Math.max(0,num(d.payment));},0),interest=debts.reduce(function(s,d){return s+num(d.balance)*Math.max(0,num(d.rate))/1200;},0),high=debts.filter(function(d){return d.rate!=null&&num(d.rate)>0&&num(d.rate)>=debtThreshold;}),context={income:income,spend:spend,invest:invest,available:income-spend,afterInvest:income-spend-invest,investmentRate:raw.hasIncome&&income>0?invest/income:null,freeRate:raw.hasIncome&&income>0?(income-spend)/income:null,debtTotal:debtTotal,debtPayment:debtPayment,interest:interest,liquid:liquid,reserveMonths:raw.hasLiquid&&raw.hasSpending&&spend>0?liquid/spend:null,hasIncome:!!raw.hasIncome,hasSpending:!!raw.hasSpending,hasLiquid:!!raw.hasLiquid,debtThreshold:debtThreshold,assets:raw.assets==null?null:Math.max(0,num(raw.assets)),netWorth:raw.assets==null?null:num(raw.assets)-debtTotal};
var investable=raw.investable==null?liquid+total:Math.max(0,num(raw.investable)),draw=spend-income;
 context.passive=Math.max(0,num(raw.passive));context.activeIncome=raw.activeIncome==null?null:Math.max(0,num(raw.activeIncome));context.investable=investable;context.withdrawal=Math.max(0,draw);
 context.withdrawalRate=draw>0&&investable>0?draw*12/investable:draw>0?null:0;context.runwayYears=draw>0&&investable>0?investable/draw/12:null;
 /* Einnahme ist Einnahme: Gehalt, Dividende, Miete, Rente oder Streams zählen gleich. Entscheidend ist nur, ob die Einnahmen die Ausgaben decken
    und, wenn nicht, ob ein Vermögen die Lücke trägt (Entnahmephase) oder nicht (Budgetlücke). Passiv ist nur eine Kennzeichnung. */
 context.passiveShare=income>0?Math.min(1,context.passive/income):0;
 context.phase=!context.hasSpending||spend<=0?'unknown':draw>0&&investable>0&&(investable>=draw*24||!context.hasIncome)?'withdrawal':'earning';
 if(context.phase==='withdrawal'){known.calm=true;var wr=context.withdrawalRate;
  scores.calm=wr==null?10:wr<=.035?82:wr<=.045?70:wr<=.06?50:wr<=.08?35:15;if(context.runwayYears!=null&&context.runwayYears<3)scores.calm=Math.min(scores.calm,15);
  findings.push({code:'capital-drawdown',severity:wr==null||wr>.045?'warn':'info',monthly:draw,rate:wr,years:context.runwayYears,investable:investable});
  if(context.hasLiquid&&spend>0&&context.reserveMonths<1){scores.calm-=10;findings.push({code:'reserve-short',severity:'warn',months:context.reserveMonths});}
  if(high.length&&invest>0){scores.calm-=25;findings.push({code:'debt-investing',severity:'warn',balance:high.reduce(function(s,d){return s+num(d.balance);},0),interest:high.reduce(function(s,d){return s+num(d.balance)*num(d.rate)/1200;},0),investment:invest,threshold:debtThreshold});}
 }
 else if(context.hasIncome&&context.hasSpending){known.calm=true;if(context.passive>0&&context.passive>=spend)findings.push({code:'passive-covers',severity:'info',cover:spend>0?context.passive/spend:0,passive:context.passive});if(context.available<0&&investable>0)findings.push({code:'capital-drawdown',severity:'warn',monthly:-context.available,rate:-context.available*12/investable,years:investable/(-context.available)/12,investable:investable,earning:true});scores.calm=70;if(invest>0&&context.afterInvest<-.01){scores.calm-=35;findings.push({code:'investment-gap',severity:'warn',gap:-context.afterInvest,investment:invest});}else if(context.available<0){scores.calm-=35;findings.push({code:'budget-gap',severity:'warn',gap:-context.available});}
  if(invest>0&&context.investmentRate!=null)findings.push({code:'investment-rate',severity:'info',rate:context.investmentRate,amount:invest,available:context.available});
  if(context.hasLiquid&&spend>0){if(context.reserveMonths<1){scores.calm-=20;findings.push({code:'reserve-short',severity:'warn',months:context.reserveMonths});}else if(context.reserveMonths>=3)scores.calm+=10;}
  if(high.length&&invest>0){scores.calm-=25;findings.push({code:'debt-investing',severity:'warn',balance:high.reduce(function(s,d){return s+num(d.balance);},0),interest:high.reduce(function(s,d){return s+num(d.balance)*num(d.rate)/1200;},0),investment:invest,threshold:debtThreshold});}
  if(income>0&&debtPayment/income>.35){scores.calm-=10;findings.push({code:'debt-service',severity:'info',share:debtPayment/income,payment:debtPayment});}
 }
 debts.forEach(function(d){if(d.rate!=null&&d.payment!=null&&num(d.rate)>0&&num(d.payment)<num(d.balance)*num(d.rate)/1200)findings.push({code:'debt-growing',severity:'warn',name:d.name||'',payment:num(d.payment),interest:num(d.balance)*num(d.rate)/1200});});
 if(debts.some(function(d){return d.rate==null;}))findings.push({code:'debt-rate-missing',severity:'info'});
 var existingSales=Object.create(null);function saleKey(r){return [r.symbol,r.date,num(r.qty),num(r.price)].join('|');}transactions.filter(function(t){return t.kind==='out';}).forEach(function(t){var k=saleKey(t);existingSales[k]=(existingSales[k]||0)+1;});(input.realized||[]).forEach(function(r){if(!validDate(r.date,today)||num(r.qty)<=0||num(r.price)<=0)return;var k=saleKey(r);if(existingSales[k]>0){existingSales[k]--;return;}transactions.push({symbol:r.symbol,name:r.name||r.symbol,date:r.date,kind:'out',qty:num(r.qty),price:num(r.price),fee:r.fee==null?null:Math.max(0,num(r.fee))});});
 var buys=transactions.filter(function(t){return t.kind!=='out'&&t.price>0;}),months=Array.from(new Set(buys.map(function(t){return t.date.slice(0,7);}))).sort(),plans=holdings.filter(function(h){return num(h.planAmount)>0;}).length,nowIndex=Number(today.slice(0,4))*12+Number(today.slice(5,7)),recent=months.filter(function(m){return nowIndex-(Number(m.slice(0,4))*12+Number(m.slice(5,7)))<12;});
 if(recent.length>=2){var firstIndex=Number(recent[0].slice(0,4))*12+Number(recent[0].slice(5,7)),span=nowIndex-firstIndex+1;known.disc=true;scores.disc=Math.round(clamp(recent.length/span*100,5,95));if(recent.length>=3)findings.push({code:'regular-investing',severity:'info',months:recent.length,span:span});}
 if(!known.disc){var im=Array.isArray(raw.investMonths)?raw.investMonths.length:0,dm=Math.min(12,Math.max(0,num(raw.dataMonths)));
  if(context.phase==='withdrawal'&&im===0&&invest<=0){known.disc=true;context.discMode='withdrawal';var w2=context.withdrawalRate;scores.disc=w2==null?10:w2<=.04?85:w2<=.06?55:w2<=.08?35:20;}
  else if(dm>=1){known.disc=true;context.discMode='bookings';scores.disc=Math.round(clamp(im/dm*100,5,95));if(im===0&&debtTotal>0){scores.disc=40;context.discMode='debt-first';}if(im===0)findings.push({code:'no-investing',severity:'info',months:dm});}}
 if(plans)findings.push({code:'plan-configured',severity:'info',count:plans});
 if(context.netWorth!=null&&context.netWorth<0&&invest>0)findings.push({code:'net-debt-investing',severity:'info',net:context.netWorth,debt:debtTotal});
 var tradeMonths=Array.from(new Set(transactions.filter(function(t){return t.price>0;}).map(function(t){return t.date.slice(0,7);}))),avg=tradeMonths.length?transactions.filter(function(t){return t.kind!=='plan'&&t.price>0;}).length/tradeMonths.length:0;
 if(avg>6)findings.push({code:'trade-frequency',severity:'info',count:avg});
 var pricedTrades=transactions.filter(function(t){return t.price>0;}),fees=pricedTrades.filter(function(t){return t.fee!=null;}),traded=fees.reduce(function(s,t){return s+t.price*t.qty;},0),feeTotal=fees.reduce(function(s,t){return s+t.fee;},0);
 if(pricedTrades.length&&fees.length===pricedTrades.length&&traded>0){known.cost=true;scores.cost=Math.round(clamp(100-feeTotal/traded*5000,5,100));findings.push({code:'recorded-fees',severity:'info',fees:feeTotal,rate:feeTotal/traded});}
if(!known.cost&&holdings.length){known.costEst=true;scores.cost=Math.round(clamp(92-Math.min(40,avg*5)-(exposure.sector+exposure.factor+exposure.unknown)*12-exposure.globalFactor*6,20,95));}
 var withCost=holdings.filter(function(h){return num(h.cost)>0&&h.gain!=null;}),cost=withCost.reduce(function(s,h){return s+num(h.cost);},0),gain=withCost.reduce(function(s,h){return s+num(h.gain);},0),knownDates=transactions.length;
 if(holdings.length){known.timing=true;scores.timing=Math.round(((withCost.length/holdings.length)*.5+(transactions.length?1:0)*.5)*100);}
 if(!holdings.length&&context.hasSpending){known.timing=true;scores.timing=(context.hasIncome?25:0)+25+(context.hasLiquid?25:0)+(num(raw.dataMonths)>=3?25:0);
  known.costEst=true;context.costMode='interest';scores.cost=Math.round(clamp(debts.length?100-(income>0?interest/income*400:interest>0?60:0):90,5,95));if(interest>0)findings.push({code:'interest-cost',severity:income>0&&interest/income>.1?'warn':'info',interest:interest,share:income>0?interest/income:null});}
 var comparisons=(input.realized||[]).filter(function(r){return validDate(r.date,today)&&num(r.qty)>0&&num(r.current)>0&&num(r.price)>0&&Math.abs(num(r.current)/num(r.price)-1)>.15;}).map(function(r){return {name:r.name||r.symbol,delta:(num(r.current)-num(r.price))*num(r.qty),date:r.date};});
 if(comparisons.length)findings.push({code:'sale-comparison',severity:'info',count:comparisons.length,delta:comparisons.reduce(function(s,r){return s+r.delta;},0)});
 var drawdowns=withCost.filter(function(h){return num(h.gain)/num(h.cost)<-.3;});if(drawdowns.length)findings.push({code:'drawdown',severity:'info',names:drawdowns.map(function(h){return h.name||h.symbol;})});
 Object.keys(scores).forEach(function(k){scores[k]=Math.round(clamp(scores[k],5,100));});
 var values=Object.keys(scores).filter(function(k){return (known[k]||(k==='cost'&&known.costEst))&&k!=='timing';}).map(function(k){return scores[k];}),score=values.length?Math.round(values.reduce(function(a,b){return a+b;},0)/values.length):null;
 var persona=context.phase==='earning'&&context.passive>0&&context.passive>=spend&&context.passiveShare>=.8?'rentier':context.phase==='withdrawal'?(context.withdrawalRate!=null&&context.withdrawalRate<=.045?'withdrawal':'drawdown'):findings.some(function(f){return f.code==='investment-gap'||f.code==='budget-gap';})?'budget':findings.some(function(f){return f.code==='debt-investing';})?'debt':exposure.crypto>.4?'crypto':exposure.metals>.5?'metals':exposure.sector+exposure.factor>.5?'focused':exposure.regional+exposure.regionalFactor>.6?'regional':exposure.globalFactor>.6?'factor':global>.7?'global':topShare>.5?'concentrated':recent.length>=3?'regular':total>0?'building':context.hasSpending?'basics':'starting';
 var shock=list.reduce(function(s,g){var r=g.kind==='crypto'?.65:g.kind==='metals'||g.kind==='commodity'?.2:g.kind==='bonds'?.1:.4;return s+g.value*r;},0);
 var hhi=list.reduce(function(s,g){return s+Math.pow(g.value/(total||1),2);},0),firstDate=buys.length?buys.map(function(t){return t.date;}).sort()[0]:null;
 return {total:total,holdings:holdings,groups:list,profiles:profiles,exposure:exposure,top:top?{name:top.name,symbol:top.symbol,share:topShare,value:top.value}:null,largest:list.length?list[0].value/(total||1):0,top3:focused.slice(0,3).reduce(function(s,g){return s+g.value;},0)/(total||1),scores:scores,known:known,score:score,persona:persona,findings:findings,context:context,transactions:transactions,avgTrades:avg,plans:plans,months:recent.length,effectivePositions:hhi?1/hhi:0,gainRate:cost>0?gain/cost:null,withCost:withCost.length,winners:withCost.filter(function(h){return num(h.gain)>0;}).length,historyDays:firstDate?Math.max(0,(new Date(today)-new Date(firstDate))/86400000):0,shock:shock,shockRate:shock/(total||1),coverage:{history:knownDates>0,fees:known.cost,budget:known.calm,unknownFunds:exposure.unknown}};
}
return Object.freeze({analyze:analyze,profile:profile,foci:FOCI.slice()});
});
