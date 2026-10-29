"""Contrôle de la veille, à lancer à chaque passage (avant et après la fusion).
Usage : python3 outils/controle.py <YYYY-MM-DD>   (depuis la racine du dépôt)
Avant la fusion : la liste PRIORITÉS dit quelles valeurs creuser en premier.
Après la fusion : TROUS doit être vide avant de publier (sinon relancer ou couvrir soi-même).
"""
import json, glob, re, sys, datetime as dt

jour = dt.date.fromisoformat(sys.argv[1])

def dk(d, ref=jour):
    m = re.match(r"^(\d{1,2})/(\d{1,2})(?:/(\d{4}))?$", str(d or "").strip())
    if not m:
        return None
    j, mo = int(m.group(1)), int(m.group(2))
    an = int(m.group(3)) if m.group(3) else (ref.year - 1 if mo > ref.month + 1 else ref.year)
    try:
        return dt.date(an, mo, j)
    except ValueError:
        return None

def zone(txt, px):
    t = re.sub(r"(\d)\s(\d)", r"\1\2", txt or "").replace(",", ".")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:€|NOK|\$|USD|¥|JPY)?\s*(?:à|-|et)\s*(\d+(?:\.\d+)?)", t)
    if not m or not px:
        return None
    a, b = sorted((float(m.group(1)), float(m.group(2))))
    return (a, b) if a >= px * .4 and b <= px * 2.5 else None

px = json.load(open("data/prices.json")).get("series", {})
prio, trous, pubs = [], [], []
for f in sorted(glob.glob("data/analyses/valeurs/*.json")):
    v = json.load(open(f)); t = v["ticker"]; a = v.get("analyse", {})
    cours = (px.get(t) or {}).get("dernier") or v.get("cours")
    raisons = []
    z = zone((a.get("zones") or {}).get("interet"), cours)
    if z and cours and z[0] <= cours <= z[1] * 1.03:
        raisons.append("en zone d'intérêt" if cours <= z[1] else "juste au-dessus de la zone")
    pub = v.get("pub")
    if pub:
        d = (dt.date.fromisoformat(pub[:10]) - jour).days
        if -3 <= d <= 2:
            raisons.append(f"publication {'aujourd’hui' if d == 0 else ('dans %d j' % d if d > 0 else 'il y a %d j' % -d)}")
        if -7 <= d < 0:
            dern = max([x for x in (dk(e.get("d")) for e in v.get("faits", [])) if x] or [dt.date(2000, 1, 1)])
            if dern < dt.date.fromisoformat(pub[:10]):
                pubs.append(f"{t} : publication du {pub[8:10]}/{pub[5:7]} sans fait noté depuis")
    ko = [x for x in (v.get("societe", {}).get("suivi", {}).get("croire", []) + v.get("societe", {}).get("suivi", {}).get("questions", [])) if x.get("etat") == "ko"]
    if v.get("statut") == "cassee" or ko:
        raisons.append("thèse cassée" if v.get("statut") == "cassee" else f"{len(ko)} point(s) ko")
    if raisons:
        prio.append(f"{t} ({', '.join(raisons)})")
    if max([x for x in (a.get("veilleLe"), a.get("majLe"), v.get("societe", {}).get("suivi", {}).get("le")) if x] or [""]) != jour.isoformat():
        trous.append(t)

mouv = []
for t, sr in sorted(px.items()):
    h = sr.get("histo") or []
    if len(h) > 1 and h[-1][0] == jour.isoformat() and h[-2][1]:
        var = (h[-1][1] / h[-2][1] - 1) * 100
        if abs(var) >= 5:
            mouv.append(f"{t} {var:+.1f} %")

geo = json.load(open("data/analyses/marche/geo.json"))
points = []
for p in geo.get("points", []):
    ds = [x for x in (dk(e.get("d")) for e in p.get("faits", [])) if x]
    age = (jour - max(ds)).days if ds else 999
    if age > 7:
        points.append(f"{p['id']} (dernier fait il y a {age} j)")

print("PRIORITÉS (à creuser en premier) :", "; ".join(prio) or "aucune")
print("MOUVEMENTS DU JOUR ≥ 5 % (cause à trouver et à noter) :", "; ".join(mouv) or "aucun")
print("PUBLICATIONS MANQUÉES :", "; ".join(pubs) or "aucune")
print("POINTS CHAUDS EN RETARD (> 7 j) :", "; ".join(points) or "aucun")
print("TROUS (valeurs non vérifiées aujourd'hui) :", ", ".join(trous) or "aucun")
sys.exit(1 if (trous or pubs) else 0)
