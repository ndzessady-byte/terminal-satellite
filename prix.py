"""Télécharge un an de cours pour la watchlist du Terminal Satellite et calcule les indicateurs.
Résultat : data/prices.json (lu chaque soir par la mise à jour automatique du terminal)."""
import json, math, os, datetime as dt
import yfinance as yf

def rsi(closes, n=14):
    if len(closes) <= n: return None
    gains, losses = [], []
    for a, b in zip(closes[:-1], closes[1:]):
        d = b - a; gains.append(max(d, 0)); losses.append(max(-d, 0))
    ag = sum(gains[:n]) / n; al = sum(losses[:n]) / n
    for g, l in zip(gains[n:], losses[n:]):          # lissage de Wilder
        ag = (ag * (n - 1) + g) / n; al = (al * (n - 1) + l) / n
    return 100.0 if al == 0 else round(100 - 100 / (1 + ag / al), 1)

def mm(closes, n):
    return round(sum(closes[-n:]) / n, 2) if len(closes) >= n else None

def perf(closes, jours):
    return round((closes[-1] / closes[-1 - jours] - 1) * 100, 1) if len(closes) > jours else None

def devise(sym):
    try: return yf.Ticker(sym).fast_info["currency"]
    except Exception: return None

tickers = json.load(open("tickers.json"))
out = {"genere": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ"), "series": {}, "erreurs": {}}
for code, sym in tickers.items():
    try:
        h = yf.Ticker(sym).history(period="400d", interval="1d", auto_adjust=False)
        h = h.dropna(subset=["Close"])
        if h.empty: raise ValueError("aucune donnée")
        closes = [round(float(c), 3) for c in h["Close"]]
        dates = [d.strftime("%Y-%m-%d") for d in h.index]
        un_an = closes[-252:]
        out["series"][code] = {
            "symbole": sym, "devise": devise(sym),
            "dernier": closes[-1], "dernierLe": dates[-1],
            "mm50": mm(closes, 50), "mm200": mm(closes, 200), "rsi14": rsi(closes[-120:]),
            "haut52": round(max(un_an), 2), "bas52": round(min(un_an), 2),
            "perf1m": perf(closes, 21), "perf3m": perf(closes, 63), "perf12m": perf(closes, 251),
            "histo": [[d, round(c, 2)] for d, c in zip(dates[-260:], closes[-260:])],
        }
    except Exception as e:
        out["erreurs"][code] = f"{sym} : {e}"
# Matières premières et changes (même calcul, rangés à part)
out["matieres"] = {}
try: matieres = json.load(open("matieres.json"))
except Exception: matieres = {}
for code, m in matieres.items():
    sym = m["symbole"]
    try:
        h = yf.Ticker(sym).history(period="400d", interval="1d", auto_adjust=False).dropna(subset=["Close"])
        if h.empty: raise ValueError("aucune donnée")
        closes = [round(float(c), 4) for c in h["Close"]]
        dates = [d.strftime("%Y-%m-%d") for d in h.index]
        un_an = closes[-252:]
        out["matieres"][code] = {
            "symbole": sym, "nom": m.get("nom"), "unite": m.get("unite"),
            "dernier": closes[-1], "dernierLe": dates[-1],
            "mm50": mm(closes, 50), "mm200": mm(closes, 200), "rsi14": rsi(closes[-120:]),
            "haut52": round(max(un_an), 4), "bas52": round(min(un_an), 4),
            "perf1s": perf(closes, 5), "perf1m": perf(closes, 21), "perf3m": perf(closes, 63), "perf12m": perf(closes, 251),
            "histo": [[d, round(c, 4)] for d, c in zip(dates[-260:], closes[-260:])],
        }
    except Exception as e:
        out["erreurs"]["MP_" + code] = f"{sym} : {e}"
# ETF suivis (cœur et candidats), même calcul
out["etfs"] = {}
try: etfs = json.load(open("etfs.json"))
except Exception: etfs = {}
for code, m in etfs.items():
    sym = m["symbole"]
    try:
        h = yf.Ticker(sym).history(period="400d", interval="1d", auto_adjust=False).dropna(subset=["Close"])
        if h.empty: raise ValueError("aucune donnée")
        closes = [round(float(c), 4) for c in h["Close"]]
        dates = [d.strftime("%Y-%m-%d") for d in h.index]
        un_an = closes[-252:]
        out["etfs"][code] = {
            "symbole": sym, "nom": m.get("nom"), "devise": devise(sym),
            "dernier": closes[-1], "dernierLe": dates[-1],
            "haut52": round(max(un_an), 4), "bas52": round(min(un_an), 4),
            "perf1m": perf(closes, 21), "perf3m": perf(closes, 63), "perf12m": perf(closes, 251),
            "histo": [[d, round(c, 4)] for d, c in zip(dates[-260:], closes[-260:])],
        }
    except Exception as e:
        out["erreurs"]["ETF_" + code] = f"{sym} : {e}"
# Yahoo renvoie parfois une série en retard d'un jour : on garde alors la version précédente, plus récente.
try:
    ancien = json.load(open("data/prices.json"))
    for rub in ("series", "matieres", "etfs"):
        for code, s in ancien.get(rub, {}).items():
            n = out[rub].get(code)
            if n is None or (s.get("dernierLe") or "") > (n.get("dernierLe") or ""):
                out[rub][code] = s
except Exception:
    pass
os.makedirs("data", exist_ok=True)
json.dump(out, open("data/prices.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(f"{len(out['series'])} valeurs OK, {len(out['matieres'])} matières, {len(out['etfs'])} ETF, {len(out['erreurs'])} erreurs", out["erreurs"])
