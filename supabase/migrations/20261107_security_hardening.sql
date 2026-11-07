-- Sicherheits-Härtung 07.11.2026 (bereits auf Projekt cwznthfefbeglamnwyry angewendet).
-- 1) rls_auto_enable ist nur als Event-Trigger gedacht (schaltet RLS für neue Tabellen ein) und darf nicht per /rest/v1/rpc aufrufbar sein.
revoke execute on function public.rls_auto_enable() from public, anon, authenticated;

-- 2) Rate-Limit für Edge Functions (Checkout, Status, Portal). Schlüssel = Funktionsname + HMAC-Hash der IP bzw. Konto-ID, keine Klar-IP.
create table if not exists billing.rate_limits (
  key text not null,
  bucket timestamptz not null,
  hits integer not null default 1,
  primary key (key, bucket)
);
alter table billing.rate_limits enable row level security;
revoke all on billing.rate_limits from public, anon, authenticated;

create or replace function billing.hit(p_key text, p_window integer) returns integer
language sql set search_path = '' as $$
  insert into billing.rate_limits (key, bucket, hits)
  values (p_key, to_timestamp(floor(extract(epoch from now()) / p_window) * p_window), 1)
  on conflict (key, bucket) do update set hits = billing.rate_limits.hits + 1
  returning hits;
$$;
revoke execute on function billing.hit(text, integer) from public, anon, authenticated;
