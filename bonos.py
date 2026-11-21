#!/usr/bin/env python3
"""Rendimiento de los bonos del Tesoro de EEUU (30, 10 y 2 años) -> bonos.json.
Fuente principal: Tesoro de EEUU (datos oficiales). Respaldo: FRED."""
import csv, io, json, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

COLS = {"DGS30": "30 Yr", "DGS10": "10 Yr", "DGS2": "2 Yr"}
DESDE = 2000
UA = {"User-Agent": "Mozilla/5.0 (HubFinanciero)"}


def get(url, timeout=25, intentos=2):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8-sig", "replace")
        except Exception as e:
            print(f"  fallo {url[:90]}... intento {i + 1}: {e}", file=sys.stderr)
            time.sleep(2)
    return None


def tesoro_anio(y):
    url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
           f"daily-treasury-rates.csv/{y}/all?type=daily_treasury_yield_curve"
           f"&field_tdr_date_value={y}&page&_format=csv")
    txt = get(url)
    if not txt:
        return y, None
    filas = list(csv.DictReader(io.StringIO(txt)))
    return y, filas


def desde_tesoro():
    anios = list(range(DESDE, datetime.now(timezone.utc).year + 1))
    with ThreadPoolExecutor(max_workers=5) as ex:
        res = list(ex.map(tesoro_anio, anios))
    out = {k: [] for k in COLS}
    malos = 0
    for y, filas in res:
        if filas is None:
            malos += 1
            continue
        for f in filas:
            try:
                m, d, a = f["Date"].split("/")
                fecha = f"{a}-{m}-{d}"
            except Exception:
                continue
            for k, c in COLS.items():
                try:
                    v = float(f[c])
                except (KeyError, ValueError, TypeError):
                    continue
                out[k].append([fecha, v])
    for k in out:
        out[k].sort(key=lambda p: p[0])
    print(f"Tesoro: {malos} años sin descargar; filas " + ", ".join(f"{k}={len(v)}" for k, v in out.items()))
    return {k: v for k, v in out.items() if len(v) > 50}


def desde_fred(sid):
    txt = get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={DESDE}-01-01", timeout=20, intentos=2)
    if not txt:
        return None
    out = []
    for linea in txt.strip().splitlines()[1:]:
        p = linea.split(",")
        try:
            out.append([p[0], float(p[1])])
        except (IndexError, ValueError):
            pass
    return out if len(out) > 50 else None


def main():
    try:
        previo = json.load(open("bonos.json"))["s"]
    except Exception:
        previo = {}
    s = desde_tesoro()
    for sid in COLS:
        if sid not in s:
            print(f"{sid}: probando FRED")
            d = desde_fred(sid)
            if d:
                s[sid] = d
            elif sid in previo:
                s[sid] = previo[sid]
                print(f"{sid}: se mantiene el dato anterior")
    if not s:
        print("No se pudo descargar ninguna serie", file=sys.stderr)
        sys.exit(1)
    for k, v in s.items():
        print(f"{k}: {len(v)} filas, último {v[-1]}")
    with open("bonos.json", "w") as f:
        json.dump({"t": datetime.now(timezone.utc).isoformat(timespec="seconds"), "s": s}, f, separators=(",", ":"))


if __name__ == "__main__":
    main()
