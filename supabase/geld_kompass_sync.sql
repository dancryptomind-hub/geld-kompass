-- Geld-Kompass Plus: Konto, verschlüsselte Synchronisierung und Kursalarme (vorbereitet, noch nicht angelegt).
-- Der Server sieht keine Finanzdaten: die App verschlüsselt im Browser (AES-GCM, Schlüssel aus dem Sync-Passwort per PBKDF2),
-- gespeichert wird nur der verschlüsselte Block. Anmeldung per E-Mail-Link (Supabase Auth).
create table if not exists public.vault (
  user_id uuid primary key references auth.users(id) on delete cascade,
  blob text not null,            -- verschlüsselte Sicherung (Base64)
  iv text not null,
  salt text not null,
  version bigint not null default 1,
  updated_at timestamptz not null default now()
);
alter table public.vault enable row level security;
create policy "vault: eigene Zeile lesen" on public.vault for select using (auth.uid() = user_id);
create policy "vault: eigene Zeile anlegen" on public.vault for insert with check (auth.uid() = user_id);
create policy "vault: eigene Zeile ändern" on public.vault for update using (auth.uid() = user_id);
create policy "vault: eigene Zeile löschen" on public.vault for delete using (auth.uid() = user_id);

-- Kursalarme für Push (nur Symbol und Grenzwerte, keine Bestände)
create table if not exists public.alerts (
  id bigserial primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  symbol text not null,
  above numeric,
  below numeric,
  currency text not null default 'EUR',
  triggered_at timestamptz,
  created_at timestamptz not null default now()
);
alter table public.alerts enable row level security;
create policy "alerts: eigene" on public.alerts for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.push_subscriptions (
  id bigserial primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  endpoint text not null unique,
  p256dh text not null,
  auth text not null,
  created_at timestamptz not null default now()
);
alter table public.push_subscriptions enable row level security;
create policy "push: eigene" on public.push_subscriptions for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
-- Edge Function „alerts-check“ (alle 15 Minuten per pg_cron): lädt https://geld-kompass.com/data/markets.json,
-- prüft offene Alarme und sendet Web-Push (VAPID). Plus-Status später über Tabelle subscriptions (Zahlungsanbieter-Webhook).
