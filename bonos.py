#!/usr/bin/env python3
"""Descarga de FRED el rendimiento de los bonos del Tesoro (30, 10 y 2 años) y lo guarda en bonos.json."""
import json, sys, time, urllib.request
from datetime import datetime, timezone

SERIES = ["DGS30", "DGS10", "DGS2"]
DESDE = "2000-01-01"


def bajar(sid):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={DESDE}"
    for intento in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (HubFinanciero)"})
            with urllib.request.urlopen(req, timeout=40) as r:
                txt = r.read().decode("utf-8", "replace")
            out = []
            for linea in txt.strip().splitlines()[1:]:
                p = linea.split(",")
                if len(p) < 2:
                    continue
                try:
                    out.append([p[0], float(p[1])])
                except ValueError:
                    continue  # días sin dato (".")
            if len(out) > 50:
                return out
            print(f"{sid}: respuesta corta ({len(out)} filas)", file=sys.stderr)
        except Exception as e:
            print(f"{sid}: intento {intento + 1} falló: {e}", file=sys.stderr)
        time.sleep(3 * (intento + 1))
    return None


def main():
    try:
        previo = json.load(open("bonos.json"))["s"]
    except Exception:
        previo = {}
    s, ok = {}, 0
    for sid in SERIES:
        d = bajar(sid)
        if d:
            s[sid] = d
            ok += 1
            print(f"{sid}: {len(d)} filas, último {d[-1]}")
        elif sid in previo:
            s[sid] = previo[sid]
            print(f"{sid}: se mantiene el dato anterior")
    if ok == 0:
        print("No se pudo descargar ninguna serie", file=sys.stderr)
        sys.exit(1)
    with open("bonos.json", "w") as f:
        json.dump({"t": datetime.now(timezone.utc).isoformat(timespec="seconds"), "s": s}, f, separators=(",", ":"))


if __name__ == "__main__":
    main()
