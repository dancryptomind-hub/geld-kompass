"""Setzt <lastmod> in sitemap.xml auf das Datum der letzten Änderung der jeweiligen Seite (aus git)."""
import re, subprocess

def lastmod(path):
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path], capture_output=True, text=True).stdout.strip()
    return out or None

s = open("sitemap.xml", encoding="utf-8").read()
def fix(m):
    url = m.group(1)
    path = url.replace("https://geld-kompass.com/", "") + "index.html"
    d = lastmod(path)
    return m.group(0) if not d else re.sub(r"<lastmod>[^<]*</lastmod>", "<lastmod>" + d + "</lastmod>", m.group(0))
s2 = re.sub(r"<url><loc>(.*?)</loc><lastmod>[^<]*</lastmod></url>", fix, s)
open("sitemap.xml", "w", encoding="utf-8").write(s2)
print("lastmod aktualisiert:", s2.count("<lastmod>"))
