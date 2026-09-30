"""Reporte le flux de cours (data/prices.json) dans data/analyses : cours, histo, technique, perf, matières, ETF.
Usage : python3 outils/maj_flux.py   (depuis la racine du dépôt)
"""
import json, glob, datetime

def dm(d):
    return d[8:10] + "/" + d[5:7]

def fr(x):
    return f"{x:,.2f}".replace(",", " ").replace(".", ",")

SRC = "https://raw.githubusercontent.com/ndzessady-byte/terminal-satellite/main/data/prices.json"
p = json.load(open("data/prices.json"))
S = p.get("series", {})
maj = []
for f in sorted(glob.glob("data/analyses/valeurs/*.json")):
    v = json.load(open(f))
    s = S.get(v["ticker"])
    if not s or not s.get("dernier"):
        continue
    v["cours"] = round(s["dernier"], 4)
    v["coursLe"] = s["dernierLe"]
    v["histo"] = [[dm(d), c] for d, c in s["histo"][-260:]]
    v["perf"] = {"m1": s.get("perf1m"), "m3": s.get("perf3m"), "m12": s.get("perf12m")}
    t = v.setdefault("analyse", {}).setdefault("tech", {})
    for k in ("mm50", "mm200", "rsi14", "haut52", "bas52"):
        t[k] = s.get(k)
    t["cours"], t["coursLe"], t["source"] = v["cours"], v["coursLe"], SRC
    c, m50, m200, r = s["dernier"], s["mm50"], s["mm200"], s["rsi14"]
    if c > m50 > m200:
        t["tendance"], t["stade"] = "haussiere", 2
    elif c < m50 < m200:
        t["tendance"], t["stade"] = "baissiere", 4
    else:
        t["tendance"] = "neutre"
        t["stade"] = 3 if m50 > m200 else 1
    pos = round(100 * (c - s["bas52"]) / (s["haut52"] - s["bas52"])) if s["haut52"] > s["bas52"] else 50
    elan = "élan fort" if r >= 70 else "élan faible" if r <= 30 else "élan neutre"
    t["lecture"] = (f"Cours de {fr(c)} {'au-dessus' if c > m50 else 'en dessous'} de sa moyenne 50 jours ({fr(m50)}) "
                    f"et {'au-dessus' if c > m200 else 'en dessous'} de sa moyenne 200 jours ({fr(m200)}). RSI {str(r).replace('.', ',')} : {elan}. "
                    f"Il se situe à {pos} % de sa fourchette sur un an (de {fr(s['bas52'])} à {fr(s['haut52'])}), "
                    f"performance sur 12 mois de {str(s.get('perf12m')).replace('.', ',')} %. Clôture du {dm(s['dernierLe'])}/{s['dernierLe'][:4]}.")
    json.dump(v, open(f, "w"), ensure_ascii=False, indent=1)
    maj.append(v["ticker"])

# matières
mf = "data/analyses/marche/matieres.json"
m = json.load(open(mf))
for code, s in p.get("matieres", {}).items():
    old = m.setdefault("series", {}).get(code, {})
    new = dict(s)
    new["histo"] = [[dm(d), c] for d, c in s.get("histo", [])]
    if old.get("note"):
        new["note"] = old["note"]
    m["series"][code] = new
m["genere"] = p["genere"]
m["source"] = SRC
m["note"] = f"Relevé du {p['genere']} (UTC)."
json.dump(m, open(mf, "w"), ensure_ascii=False, indent=1)

# ETF cœur dans le snapshot
sf = "data/analyses/marche/snapshot.json"
sn = json.load(open(sf))
e = S.get("ETF") or p.get("etfs", {}).get("DCAM")
if e:
    sn["etf"] = {"nom": "Amundi PEA Monde MSCI World (DCAM)", "cours": round(e["dernier"], 4),
                 "coursLe": e["dernierLe"], "source": SRC}
json.dump(sn, open(sf, "w"), ensure_ascii=False, indent=1)
print("valeurs mises à jour :", len(maj), " ".join(maj))
