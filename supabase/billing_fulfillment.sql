-- Private payment states; no customer-facing RPC. Apply as the database owner.
begin;
create table if not exists billing.payment_blocks (
 payment_intent_id text primary key,
 status text not null check (status in ('refunded','disputed','flagged')),
 created_at timestamptz not null default now()
);
alter table billing.payment_blocks enable row level security;
revoke all on billing.payment_blocks from public, anon, authenticated;
create index if not exists purchases_payment_intent_idx on billing.purchases(payment_intent_id);

create or replace function billing.block_payment(p_pi text,p_status text) returns void
language plpgsql security invoker set search_path='' as $$
declare blocked text;
begin
 if p_pi is null or p_pi='' then return; end if;
 if p_status not in ('refunded','disputed','flagged') then raise exception 'invalid payment block'; end if;
 perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended('gk-payment:'||p_pi,0));
 insert into billing.payment_blocks(payment_intent_id,status) values(p_pi,p_status)
 on conflict(payment_intent_id) do update set status=case
  when billing.payment_blocks.status='refunded' or excluded.status='refunded' then 'refunded'
  when billing.payment_blocks.status='disputed' or excluded.status='disputed' then 'disputed'
  else 'flagged' end returning status into blocked;
 update billing.purchases set status=blocked where payment_intent_id=p_pi;
end $$;
revoke execute on function billing.block_payment(text,text) from public, anon, authenticated;

create or replace function billing.fulfill_purchase(p_session text,p_pi text,p_email text,p_product text,p_amount integer,p_currency text) returns void
language plpgsql security invoker set search_path='' as $$
declare blocked text;
begin
 if p_session is null or p_session='' or p_product not in ('gk_workbook_de','gk_freedom_report') then raise exception 'invalid purchase'; end if;
 if p_pi is not null and p_pi<>'' then
  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended('gk-payment:'||p_pi,0));
  select status into blocked from billing.payment_blocks where payment_intent_id=p_pi;
 end if;
 insert into billing.purchases(checkout_session_id,email,product,amount_total,currency,status,payment_intent_id,fulfilled_at)
 values(p_session,p_email,p_product,p_amount,p_currency,coalesce(blocked,'paid'),p_pi,case when blocked is null then now() else null end)
 on conflict(checkout_session_id) do update set
  status=excluded.status,amount_total=excluded.amount_total,currency=excluded.currency,payment_intent_id=excluded.payment_intent_id,
  email=coalesce(billing.purchases.email,excluded.email),fulfilled_at=coalesce(billing.purchases.fulfilled_at,excluded.fulfilled_at)
 where billing.purchases.status not in ('refunded','disputed','flagged');
end $$;
revoke execute on function billing.fulfill_purchase(text,text,text,text,integer,text) from public, anon, authenticated;
commit;
