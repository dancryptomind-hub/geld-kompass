-- Smart-TV-Edition Paket (Geld-Kompass-Pro-TV.zip) ausschließlich für Edge Function tv-download (Plus-Mitglieder & Admin).
create table if not exists gk_private.tv_release (
  version text primary key,
  filename text not null,
  sha256 text not null,
  size_bytes integer not null,
  zip_b64 text not null,
  updated_at timestamptz not null default now()
);
alter table gk_private.tv_release enable row level security;
revoke all on gk_private.tv_release from public, anon, authenticated;
