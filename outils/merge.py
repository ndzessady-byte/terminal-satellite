"""Fusionne les nouvelles de veille dans data/analyses/valeurs/<TICKER>.json.
Usage : python3 outils/merge.py <fichier.json> <YYYY-MM-DD>   (depuis la racine du dépôt)
Format d'entrée : {"<TICKER>": {"faits":[{d,t}], "actu":[{d,fait,impact,horizon,lecture}],
  "pub": "YYYY-MM-DD"|null, "pubLabel": "...", "suivi":[{element,etat,reponse,preuve,source}], "sources":[urls]}}
Les entrées {"rien": true} sont ignorées. Une clé "pub" présente avec null efface la date.
"""
import json, sys, difflib, re

def cle(d):
    m = re.match(r"(\d{1,2})/(\d{1,2})", str(d or ""))
    return (int(m.group(2)), int(m.group(1))) if m else (0, 0)

def fusion(anciens, nouveaux, champ, n=4):
    vus = {(x.get("d"), x.get(champ)) for x in nouveaux}
    tout = nouveaux + [x for x in anciens if (x.get("d"), x.get(champ)) not in vus]
    tout.sort(key=lambda x: cle(x.get("d")), reverse=True)
    return tout[:n]

def proche(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

src, date = sys.argv[1], sys.argv[2]
data = json.load(open(src))
for t, n in data.items():
    if t.startswith("_") or not isinstance(n, dict) or n.get("rien"):
        continue
    f = f"data/analyses/valeurs/{t}.json"
    try:
        v = json.load(open(f))
    except FileNotFoundError:
        print("absent", t); continue
    if n.get("faits"):
        v["faits"] = fusion(v.get("faits", []), n["faits"], "t")
    if n.get("actu"):
        a = v.setdefault("analyse", {})
        a["actu"] = fusion(a.get("actu", []), n["actu"], "fait")
        a["majLe"] = date
    if "pub" in n:
        v["pub"] = n["pub"]
        if n.get("pubLabel") is not None or n["pub"] is None:
            v["pubLabel"] = n.get("pubLabel")
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
