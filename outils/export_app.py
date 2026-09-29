"""Assemble data/app.json (public) depuis un export de la base du terminal.
Usage : python outils/export_app.py <dossier_export>
Le dossier contient valeurs/*.json et marche/{snapshot,geo,matieres}.json
(tels qu'écrits par ArtifactData list avec out_dir). Rien de privé n'y entre :
pas de data/users/ (favoris, portefeuille, journal restent sur chaque téléphone)."""
import json, sys, glob, os, datetime
src = sys.argv[1]
def load(p):
    d = json.load(open(p, encoding="utf-8"))
    return d.get("data", d) if isinstance(d, dict) and "data" in d and len(d) <= 4 else d
vals = []
for f in sorted(glob.glob(os.path.join(src, "valeurs", "*.json"))):
    v = load(f)
    for k in ("histo", "zb", "notes"):
        v.pop(k, None)
    vals.append(v)
m = {k: load(os.path.join(src, "marche", k + ".json")) for k in ("snapshot", "geo")}
mat = load(os.path.join(src, "marche", "matieres.json"))
notes = {k: s.get("note") for k, s in mat.get("series", {}).items() if s.get("note")}
props = []
for f in sorted(glob.glob(os.path.join(src, "propositions", "*.json"))):
    props.append(load(f))
out = {"propositions": props, "genere": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
       "snapshot": m["snapshot"], "geo": m["geo"], "matieresNotes": notes,
       "matieresNote": mat.get("note"), "valeurs": vals}
os.makedirs("data", exist_ok=True)
json.dump(out, open("data/app.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("data/app.json", len(vals), "valeurs", os.path.getsize("data/app.json"), "octets")
