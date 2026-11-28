-- Wise Business als zusätzliche Zahlungsalternative neben Stripe (Stripe-Tabellen bleiben unverändert).
create schema if not exists billing;

create table if not exists billing.wise_payments (
  id uuid primary key default gen_random_uuid(),
  reference text not null unique,
  provider text not null default 'wise' check (provider = 'wise'),
  user_id uuid references auth.users(id) on delete set null,
  item text not null,
  amount_cents integer not null check (amount_cents > 0),
  currency text not null default 'EUR',
  mode text not null check (mode in ('payment_link', 'bank_transfer')),
  status text not null default 'pending' check (status in ('pending', 'paid', 'expired', 'refunded')),
  wise_transfer_id text unique,
  lang text not null default 'de',
  created_at timestamptz not null default now(),
  paid_at timestamptz
);

create index if not exists wise_payments_user_status_idx
  on billing.wise_payments (user_id, status);

create index if not exists wise_payments_status_created_idx
  on billing.wise_payments (status, created_at desc);

alter table billing.wise_payments enable row level security;

drop policy if exists "wise_payments_own_read" on billing.wise_payments;
create policy "wise_payments_own_read"
  on billing.wise_payments
  for select
  to authenticated
  using (auth.uid() = user_id);
