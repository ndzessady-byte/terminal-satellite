"""Fusionne les nouvelles de veille dans data/analyses/valeurs/<TICKER>.json.
Usage : python3 outils/merge.py <fichier.json> <YYYY-MM-DD>   (depuis la racine du dépôt)
Format d'entrée : {"<TICKER>": {"faits":[{d,t}], "actu":[{d,fait,impact,horizon,lecture}],
  "pub": "YYYY-MM-DD"|null, "pubLabel": "...", "suivi":[{element,etat,reponse,preuve,source}], "sources":[urls]}}
Une entrée {"rien": true} date seulement la veille (analyse.veilleLe). "pub": null n'efface la date que si pubLabel est donné.
"""
import json, sys, difflib, re

def cle(d):
    m = re.match(r"^(\d{1,2})/(\d{1,2})(?:/(\d{4}))?$", str(d or "").strip())
    if not m:
        return (0, 0, 0)
    j, mo = int(m.group(1)), int(m.group(2))
    an = int(m.group(3)) if m.group(3) else (ANNEE - 1 if mo > MOIS + 1 else ANNEE)
    return (an, mo, j)

def fusion(anciens, nouveaux, champ, n=4):
    vus = {(x.get("d"), x.get(champ)) for x in nouveaux}
    tout = nouveaux + [x for x in anciens if (x.get("d"), x.get(champ)) not in vus]
    tout.sort(key=lambda x: cle(x.get("d")), reverse=True)
    return tout[:n]

def proche(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

src, date = sys.argv[1], sys.argv[2]
ANNEE, MOIS = int(date[:4]), int(date[5:7])
data = json.load(open(src))
for t, n in data.items():
    if t.startswith("_") or not isinstance(n, dict):
        continue
    f = f"data/analyses/valeurs/{t}.json"
    try:
        v = json.load(open(f))
    except FileNotFoundError:
        print("absent", t); continue
    # la veille est datée même quand il n'y a rien de neuf
    v.setdefault("analyse", {})["veilleLe"] = date
    if n.get("rien"):
        json.dump(v, open(f, "w"), ensure_ascii=False, indent=1)
        print("rien", t); continue
    if n.get("faits"):
        v["faits"] = fusion(v.get("faits", []), n["faits"], "t")
    if n.get("actu"):
        a = v.setdefault("analyse", {})
        a["actu"] = fusion(a.get("actu", []), n["actu"], "fait")
        a["majLe"] = date
    # pub : une date remplace ; null n'efface que si pubLabel explique pourquoi
    if n.get("pub"):
        v["pub"] = n["pub"]
        if n.get("pubLabel"):
            v["pubLabel"] = n["pubLabel"]
    elif "pub" in n and n.get("pubLabel"):
        v["pub"] = None
        v["pubLabel"] = n["pubLabel"]
    if n.get("sources"):
        s = v.setdefault("analyse", {}).setdefault("sources", [])
        for u in n["sources"]:
            if u not in s:
                s.insert(0, u)
    if n.get("suivi"):
        su = v.setdefault("societe", {}).setdefault("suivi", {})
        for e in n["suivi"]:
            best, score = None, 0
            for liste, k in ((su.get("croire", []), "c"), (su.get("questions", []), "q")):
                for x in liste:
                    r = proche(e["element"], x.get(k, ""))
                    if r > score:
                        best, score = x, r
            if best is not None and score >= 0.6:
                for k in ("etat", "reponse", "preuve", "source"):
                    if e.get(k):
                        best[k] = e[k]
            else:
                print("suivi non rattaché", t, e["element"][:60])
        su["le"] = date
    json.dump(v, open(f, "w"), ensure_ascii=False, indent=1)
    print("ok", t)
