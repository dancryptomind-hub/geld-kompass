# PROJECT_STATE.md — Geld-Kompass

> Zuletzt aktualisiert: 2026-11-28 (OmniRoute-OAuth abgeschlossen, Checkout nach `~/Developer/geld-kompass` verlagert, Wise-Business-Integration neben Stripe umgesetzt & getestet)

## 1. Projektziel

Geld-Kompass (`https://geld-kompass.com`, Repo `dancryptomind-hub/geld-kompass`) ist die deutsch-/englischsprachige Finanz-, Rechner-, Tracker- und White-Label-Plattform von Dan (`FreedomByDan LLC`).
**Aktueller Schwerpunkt:** Integration von **Wise Business** als zusätzlicher Zahlungsalternative neben **Stripe** (für Arbeitsbuch, Freiheits-Report, Plus-Pässe und White-Label-Lizenzen). **Stripe bleibt dabei zu 100 % unverändert erhalten.**

## 2. Aktueller Entwicklungsstand

- **Aktiver lokaler Git-Checkout (außerhalb von iCloud):** `/Users/dancryptomind/Developer/geld-kompass` (Branch `codex/whitelabel-billing-nov28`, Basis `origin/main` `88807e8`).
- **Stripe (Live auf `main` — vollständig erhalten):** `billing-checkout`, `billing-webhook`, `billing-status`, `billing-portal`, `#abBuy` und Plus-/Report-Checkout unverändert aktiv.
- **Wise Business (neu auf `codex/whitelabel-billing-nov28`, sicher hinter Feature-Flag `wiseEnabled: false` / `WISE_ENABLED=1`):**
  - `billing-config.js`: um `wiseEnabled: false`, `providers: { stripe: true, wise: false }` und White-Label-Preise erweitert.
  - `supabase/migrations/20261128_wise_business_payments.sql`: neue Tabelle `billing.wise_payments` inkl. Indizes & RLS (Stripe-Tabellen unberührt).
  - `supabase/functions/_shared/wise.ts`: Wise-Katalog (EUR), eindeutiger Referenz-Generator (`GK-WISE-<CODE>-<8HEX>`), Payment-Link-/IBAN-Resolver, offizielle RSA-SHA256-Webhook-Signaturprüfung (`X-Signature-SHA256`).
  - `supabase/functions/wise-checkout/index.ts`: Edge Function für Wise-Zahlungsanweisungen (`payment_link` oder `bank_transfer`) mit Rate-Limiting & Persistenz in `billing.wise_payments`.
  - `supabase/functions/wise-webhook/index.ts`: Edge Function für `balances#credit` & `transfers#state-change` mit RSA-SHA256-Verifikation und idempotentem `paid`-Update.
  - `arbeitsbuch/index.html` & `en/workbook/index.html`: optionaler Zweit-Button `#abBuyWise` (bei `wiseEnabled: false` verborgen; bei `true` neben Stripe `#abBuy` sichtbar) inkl. aktualisierter CSP-Hashes (`scripts/csp.py`).
  - `supabase/functions/_shared/wise_test.ts` & `tests/wise-billing.js`: automatisierte Unit- und UI-Tests.
- **Offener PR #2:** `codex/confirmed-embed-pricing-nov28` („Aktualisiere White-Label-Tarife auf DE/EN-Seiten“) — unberührt.

## 3. Git-Branch und Commit

- **Repository:** `https://github.com/dancryptomind-hub/geld-kompass`
- **Aktiver Arbeits-Checkout:** `/Users/dancryptomind/Developer/geld-kompass`
- **Aktiver Branch:** `codex/whitelabel-billing-nov28` (gepusht auf `origin/codex/whitelabel-billing-nov28`)
- **Basis-Commit (`origin/main`):** `88807e8`

## 4. Erledigte Aufgaben

- [x] OmniRoute-OAuth für **OpenAI Codex** (`codex`) und **Google / Antigravity** (`antigravity`) über sicheren lokalen Loopback-Callback abgeschlossen (keine OAuth-Codes im Chat oder Obsidian gespeichert).
- [x] Routing-Profil `FREE-CODING` mit Priority-Rotation **Codex OAuth → Google/Antigravity OAuth → Ollama Lokal** konfiguriert und live getestet (automatisches Failover bei Codex `429 model_cooldown` auf Antigravity `claude-sonnet-5-5-medium` in < 1 s).
- [x] Aktiven Git-Checkout sauber aus iCloud nach `/Users/dancryptomind/Developer/geld-kompass` verlagert.
- [x] Wise Business als zusätzliche Zahlungsalternative neben Stripe implementiert (Migration, `_shared/wise.ts`, `wise-checkout`, `wise-webhook`, `billing-config.js`, DE/EN Arbeitsbuch-UI, CSP, Deno- & Playwright-Tests).
- [x] Branch `codex/whitelabel-billing-nov28` auf GitHub gepusht und `PROJECT_STATE.md` mit Projektordner + Obsidian-Vault synchronisiert.

## 5. Offene Aufgaben

- [ ] **White-Label-Checkout-UI (`/einbinden/` & `/en/embed/`):** Optional nach Merge von PR #2 (`codex/confirmed-embed-pricing-nov28`) den Wise-Business-Button (`wise-checkout` für `whitelabel_pro_*` / `whitelabel_team_*`) auch auf den White-Label-Seiten ergänzen.
- [ ] **Supabase Deployment & Secrets (nach Freigabe durch Dan):**
  1. Migration `supabase/migrations/20261128_wise_business_payments.sql` auf Projekt `cwznthfefbeglamnwyry` anwenden.
  2. Edge Functions `wise-checkout` und `wise-webhook` deployen.
  3. Wise-Business-Secrets in Supabase setzen (`WISE_ENABLED=1`, `WISE_PAYMENT_LINKS_JSON` und/oder `WISE_ACCOUNT_IBAN` + `WISE_ACCOUNT_HOLDER` + `WISE_ACCOUNT_BIC`, `WISE_WEBHOOK_PUBLIC_KEY`).
  4. Erst nach erfolgreichem End-to-End-Test `wiseEnabled: true` in `billing-config.js` freischalten.
- [ ] **PR für `codex/whitelabel-billing-nov28` erstellen & CI (`Tests`-Workflow inkl. Playwright) prüfen.**

## 6. Testergebnisse (2026-11-28)

- **OmniRoute `FREE-CODING` Live-Failover:** Bestanden — Codex `429 model_cooldown` → automatischer Wechsel auf Google/Antigravity (`claude-sonnet-5-5-medium`, `200 OK`; `gemini-3.8-flash-high`, 2,8 s `200 OK`) + lokaler Ollama-Fallback (`qwen2.5-32k`, 14 s `200 OK`).
- **`python3 scripts/csp.py --check`:** Bestanden (`OK: CSP in allen Seiten aktuell`).
- **`deno check` (`wise-checkout`, `wise-webhook`, `billing-checkout`, `billing-webhook`):** Bestanden (0 Fehler).
- **`deno test --allow-env supabase/functions/_shared/`:** Bestanden (**18/18 Tests grün**: 14 bestehende Stripe-/Policy-Tests + 4 neue Wise-Tests inkl. RSA-SHA256-Signaturprüfung).
- **JS-Syntaxprüfung (`node --check billing-config.js tests/wise-billing.js`):** Bestanden.
- **Playwright lokal:** `playwright` ist im lokalen Repo nicht installiert (läuft in GitHub Actions CI).

## 7. Bekannte Fehler / Einschränkungen

- **Wise Business noch nicht live aktiviert (`wiseEnabled: false`):** Bewusst sicher deaktiviert, bis Dan die Wise-Business-Secrets in Supabase hinterlegt und einen echten Live-/Sandbox-Test freigibt.
- **Codex OAuth temporär im Cooldown (`429 model_cooldown`):** OmniRoute umgeht den Cooldown automatisch über Google/Antigravity OAuth und bindet Codex nach Ablauf des Cooldowns wieder automatisch ein.

## 8. Exakter nächster Arbeitsschritt

1. In `/Users/dancryptomind/Developer/geld-kompass` auf Branch `codex/whitelabel-billing-nov28` einen Pull Request gegen `main` öffnen (oder nach Merge von PR #2 `scripts/build_embed.py` um die Wise-Zahlungsoption für White-Label-Tarife erweitern) und die GitHub-Actions-CI inkl. Playwright (`tests/billing-ui.js` & `tests/wise-billing.js`) prüfen.
2. Nach Dans Freigabe und Hinterlegung der Wise-Secrets in Supabase: Migration + `wise-checkout`/`wise-webhook` deployen, testen und `wiseEnabled: true` schalten.
