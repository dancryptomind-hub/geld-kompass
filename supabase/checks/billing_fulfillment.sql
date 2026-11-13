-- Transactional checks: all fixture records are rolled back, no payments are made.
begin;
do $$ declare actual text; s text; sid text; pi text; n integer:=0;
begin
 foreach s in array array['refunded','disputed','flagged'] loop
  n:=n+1;sid:='cs_test_gk_check_early_'||n;pi:='pi_gk_check_early_'||n;
  perform billing.block_payment(pi,s);
  perform billing.fulfill_purchase(sid,pi,null,'gk_workbook_de',999,'eur');
  select status into actual from billing.purchases where checkout_session_id=sid;
  if actual is distinct from s then raise exception 'early block lost: % vs %',actual,s;end if;
  perform billing.fulfill_purchase(sid,pi,null,'gk_workbook_de',999,'eur');
  select status into actual from billing.purchases where checkout_session_id=sid;
  if actual is distinct from s then raise exception 'duplicate fulfillment reactivated %',s;end if;
  sid:='cs_test_gk_check_late_'||n;pi:='pi_gk_check_late_'||n;
  perform billing.fulfill_purchase(sid,pi,null,'gk_workbook_de',999,'eur');
  perform billing.block_payment(pi,s);
  perform billing.fulfill_purchase(sid,pi,null,'gk_workbook_de',999,'eur');
  select status into actual from billing.purchases where checkout_session_id=sid;
  if actual is distinct from s then raise exception 'late block lost: % vs %',actual,s;end if;
 end loop;
 perform billing.fulfill_purchase('cs_test_gk_check_paid','pi_gk_check_paid',null,'gk_workbook_de',999,'eur');
 perform billing.fulfill_purchase('cs_test_gk_check_paid','pi_gk_check_paid',null,'gk_workbook_de',999,'eur');
 select status into actual from billing.purchases where checkout_session_id='cs_test_gk_check_paid';
 if actual is distinct from 'paid' then raise exception 'paid purchase not fulfilled';end if;
 perform billing.block_payment('pi_gk_check_paid','refunded');
 perform billing.block_payment('pi_gk_check_paid','flagged');
 select status into actual from billing.purchases where checkout_session_id='cs_test_gk_check_paid';
 if actual is distinct from 'refunded' then raise exception 'refund overwritten by lesser block';end if;
 if has_function_privilege('anon','billing.fulfill_purchase(text,text,text,text,integer,text)','execute') or has_function_privilege('authenticated','billing.block_payment(text,text)','execute') then raise exception 'public access to private purchase writes';end if;
end $$;
rollback;
select 'PASS: early/late/duplicate blocks, paid delivery, refund priority, private access; fixtures rolled back' as result;
