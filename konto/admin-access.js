/* Administrative preview only. Future paid server endpoints require their own authorization. */
(function(root){'use strict';
function create(options){var active=false,until=0,revision=0,disposed=false,expiry=null,checked=false;var now=options.now||Date.now,lease=options.leaseMs||60000,timeout=options.timeoutMs||10000;
 function allowed(){return active&&now()<until&&!disposed;}
 function notify(value){try{if(options.onChange)options.onChange(value);}catch(e){}}
 function change(value){var previous=active;clearTimeout(expiry);active=!!value;until=active?now()+lease:0;if(active)expiry=setTimeout(function(){revoke();},lease);if(previous!==active)notify(active);}
 function revoke(){revision++;change(false);}
 async function refresh(){if(disposed)return false;var ticket=++revision,timer;try{var result=await Promise.race([Promise.resolve().then(options.getUser),new Promise(function(resolve){timer=setTimeout(function(){resolve({error:true});},timeout);})]);if(disposed||ticket!==revision)return allowed();var user=result&&result.data&&result.data.user;var admin=!result.error&&user&&user.id&&user.email_confirmed_at&&!user.is_anonymous&&user.app_metadata&&user.app_metadata.gk_admin===true;change(!!admin);checked=true;try{if(options.onChecked)options.onChecked();}catch(e){}return allowed();}catch(e){if(ticket===revision&&!disposed){change(false);checked=true;try{if(options.onChecked)options.onChecked();}catch(e){}}return false;}finally{clearTimeout(timer);}}
 function dispose(){revoke();disposed=true;}
 return Object.freeze({allowed:allowed,refresh:refresh,revoke:revoke,dispose:dispose,checked:function(){return checked;}});
}
var api=Object.freeze({create:create});if(typeof module==='object'&&module.exports)module.exports=api;else Object.defineProperty(root,'GKAdminGate',{value:api,writable:false,configurable:false});
})(typeof window==='object'?window:globalThis);
