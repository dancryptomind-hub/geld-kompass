# AGENTS.md — Geld-Kompass (Multi-Agent-Arbeitsregeln)

Gilt verbindlich für alle Coding-Agenten (Codex CLI / `codex-free`, Claude Code / `claude-free`, Antigravity / `agy` und weitere über OmniRoute `FREE-CODING` angebundene Agenten).

## 1. Pflichtablauf vor und nach jeder Aufgabe

1. **Vor Arbeitsbeginn:**
   - Lies `AGENTS.md` (diese Datei) und `PROJECT_STATE.md` im Repo-Root.
   - Lies bei projektspezifischer Historie zusätzlich `/Users/dancryptomind/Desktop/Geld-Kompass Projekt/_Projektdateien/abschluss/WEITERARBEIT.md`.
   - Prüfe `git branch --show-current`, `git rev-parse --short HEAD` und `git status -sb`.
2. **Während der Arbeit:**
   - Keine geheimen Schlüssel, OAuth-Codes, Tokens oder API-Keys ins Repository, in Chatverläufe oder in Obsidian schreiben.
   - Bestehende Zahlungswege (**Stripe**) niemals entfernen oder beschädigen. Neue Zahlungsanbieter (**Wise Business**) ausschließlich als **zusätzliche Alternative** neben Stripe integrieren.
   - Bei HTML-Änderungen immer `python3 scripts/csp.py` + `python3 scripts/csp.py --check`, bei Supabase-Funktionen `deno check` + `deno test --allow-env supabase/functions/_shared/` ausführen.
   - Keine kostenpflichtigen API-Aufrufe ohne ausdrückliche Freigabe von Dan. Für automatisiertes Coding OmniRoute-Profil `FREE-CODING` (`http://127.0.0.1:20128/v1`) verwenden.
3. **Nach Änderungen (Übergabepflicht):**
   - Aktualisiere `PROJECT_STATE.md` im Repo-Root (Branch, Commit, erledigte/offene Aufgaben, Testergebnisse, bekannte Fehler, exakter nächster Arbeitsschritt).
   - Synchronisiere `PROJECT_STATE.md` nach `/Users/dancryptomind/Desktop/Geld-Kompass Projekt/PROJECT_STATE.md` und in das Obsidian-Vault `/Users/dancryptomind/Desktop/DanAi/01_Projekte/Geld-Kompass/PROJECT_STATE.md`.
   - Committe und pushe saubere Zwischenstände auf den jeweiligen Feature-Branch (kein direktes Überschreiben fremder Branches oder Force-Push auf `main`).

## 2. Kanonische Pfade & Infrastruktur

- **GitHub-Repository:** `https://github.com/dancryptomind-hub/geld-kompass`
- **Aktiver lokaler Git-Checkout (außerhalb von iCloud!):** `/Users/dancryptomind/Developer/geld-kompass`
- **Projekt-Hauptordner (Dokumente/PDFs/Bücher):** `/Users/dancryptomind/Desktop/Geld-Kompass Projekt`
- **Obsidian-Vault:** `/Users/dancryptomind/Desktop/DanAi/01_Projekte/Geld-Kompass/`
- **OmniRoute-Endpunkt:** `http://127.0.0.1:20128/v1` (Profil `FREE-CODING`: Codex OAuth → Google/Antigravity OAuth → Ollama Lokal)
- **Coding-Agent-CLI-Wrapper:** `codex-free` (`~/.local/bin/codex-free`) und `claude-free` (`~/.local/bin/claude-free`)
