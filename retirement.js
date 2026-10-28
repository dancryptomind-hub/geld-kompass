/* Cash actually required from a portfolio. Dividends are part of that cash, not extra. */
(function(root,factory){var fn=factory();if(typeof module==='object'&&module.exports)module.exports=fn;else root.GeldEntnahme=fn;})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';return function(input){
  function positive(v){v=Number(v);return Number.isFinite(v)?Math.max(0,v):0;}
  var cost=positive(input.cost),external=positive(input.external),dividends=positive(input.dividends),swr=positive(input.swr)||4;
  var need=Math.max(0,cost-external),usedDiv=Math.min(need,dividends);
  return {monthlyNeed:need,portfolioUse:need*12,dividendsUsed:usedDiv,sales:Math.max(0,need-usedDiv),unusedDividends:Math.max(0,dividends-usedDiv),target:need*12/(swr/100)};
 };
});
