#!/usr/bin/env python3
"""Content-Security-Policy für alle Seiten (GitHub Pages kann keine Header setzen, daher als meta-Tag).

Aufruf:  python3 scripts/csp.py          -> setzt/aktualisiert den CSP-Tag in allen HTML-Seiten
         python3 scripts/csp.py --check  -> prüft nur (CI); Fehler = Seite hat keinen oder veralteten Tag

Inline-Skripte sind nur mit ihrem SHA-256-Hash erlaubt. Wer ein Inline-Skript ändert oder eine Seite neu
erzeugt (build_*.py, dividend_pages.py …), muss danach dieses Skript laufen lassen – sonst blockiert der
Browser das geänderte Skript und der Test „csp“ wird rot (Deploy stoppt, live bleibt alles heil).
Neue externe Dienste (fetch zu fremder Domain, fremdes Skript) unten in CONNECT/SCRIPT eintragen.
"""
import base64, hashlib, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"konto/index.html"}            # eigene, strengere CSP von Hand gepflegt
SKIP_PREFIX = ("scripts/", "tests/", "vendor/", "node_modules/")
SKIP_RE = re.compile(r"^google[0-9a-f]+\.html$")

SCRIPT = ["'self'", "https://static.cloudflareinsights.com", "https://s3.tradingview.com"]
CONNECT = ["'self'", "https://cwznthfefbeglamnwyry.supabase.co", "https://cloudflareinsights.com",
           "https://api.coingecko.com", "https://proxy.cors.dev", "https://api.frankfurter.app",
           "https://mempool.space", "https://eth.blockscout.com", "https://solana-rpc.publicnode.com",
           "https://xrplcluster.com", "https://ec.europa.eu"]
FRAME = ["'self'", "https://geld-kompass.com", "https://*.tradingview.com", "https://*.tradingview-widget.com"]
# Skripte, die zur Laufzeit in neue Fenster geschrieben werden (erben die CSP der App)
EXTRA = {"app/index.html": ["window.onload=function(){window.print();}"]}
# Nur die App lädt den Plus-Code (vom Server nach Prüfung des Kontos) als blob:-Skript.
SCRIPT_EXTRA = {"app/index.html": ["blob:"]}

TAG_RE = re.compile(r'[ \t]*<meta http-equiv="Content-Security-Policy" data-gk-csp[^>]*>\n?')
SCRIPT_RE = re.compile(r"<script(\s[^>]*)?>(.*?)</script>", re.S | re.I)
EXEC_TYPES = ("", "text/javascript", "application/javascript", "module")


def sha(text):
    return "'sha256-" + base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode() + "'"


def inline_hashes(html):
    out = []
    for attrs, body in SCRIPT_RE.findall(html):
        attrs = attrs or ""
        if re.search(r"\bsrc\s*=", attrs, re.I):
            continue
        m = re.search(r"\btype\s*=\s*[\"']?([^\"'\s>]+)", attrs, re.I)
        if m and m.group(1).lower() not in EXEC_TYPES:
            continue  # z. B. application/ld+json wird nicht ausgeführt
        out.append(sha(body))
    return out


def policy(hashes, rel=""):
    h = sorted(set(hashes))
    parts = [
        "default-src 'self'",
        "script-src " + " ".join(SCRIPT + SCRIPT_EXTRA.get(rel, []) + h),
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: blob: https:",
        "font-src 'self' data:",
        "connect-src " + " ".join(CONNECT),
        "frame-src " + " ".join(FRAME),
        "worker-src 'self'",
        "manifest-src 'self'",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
    ]
    return "; ".join(parts)


def build(rel, html):
    clean = TAG_RE.sub("", html)
    hashes = inline_hashes(clean) + [sha(x) for x in EXTRA.get(rel, [])]
    tag = '<meta http-equiv="Content-Security-Policy" data-gk-csp content="' + policy(hashes, rel) + '">'
    m = re.search(r"<meta charset=[^>]*>\n?", clean, re.I) or re.search(r"<head[^>]*>\n?", clean, re.I)
    if not m:
        return None
    return clean[:m.end()] + tag + ("\n" if clean[m.end() - 1:m.end()] == "\n" else "") + clean[m.end():]


def files():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = sorted(d for d in dn if not d.startswith(".") and d != "node_modules")
        for f in sorted(fn):
            if not f.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/")
            if rel in SKIP or rel.startswith(SKIP_PREFIX) or SKIP_RE.match(rel):
                continue
            yield rel


def update(check=False, quiet=False):
    """Setzt den CSP-Tag in allen Seiten (check=True: nur prüfen). Gibt die Liste geänderter bzw. veralteter Seiten zurück."""
    bad = []
    for rel in files():
        p = os.path.join(ROOT, rel)
        html = open(p, encoding="utf-8").read()
        new = build(rel, html)
        if new is None:
            bad.append(rel + " (kein <head>)")
            continue
        if new == html:
            continue
        bad.append(rel)
        if not check:
            open(p, "w", encoding="utf-8").write(new)
            if not quiet:
                print("CSP gesetzt:", rel)
    return bad


def main():
    if "--check" in sys.argv:
        bad = update(check=True)
        if bad:
            print("CSP fehlt oder ist veraltet in %d Seite(n): %s" % (len(bad), ", ".join(bad[:10])))
            print("Lösung: python3 scripts/csp.py ausführen und die Änderungen mit committen.")
            sys.exit(1)
        print("OK: CSP in allen Seiten aktuell")
    else:
        update()


if __name__ == "__main__":
    main()
