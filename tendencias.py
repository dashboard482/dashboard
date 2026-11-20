# Gráficos de tendencia: baja velas semanales, calcula canal, niveles y texto. Escribe tendencias.json
import json, os, time, math, random, urllib.request, urllib.parse
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
U = [
    ("^GSPC", "S&P 500", "Índices"), ("^NDX", "Nasdaq 100", "Índices"), ("^DJI", "Dow Jones", "Índices"),
    ("^IBEX", "IBEX 35", "Índices"), ("^GDAXI", "DAX", "Índices"),
    ("NVDA", "Nvidia", "Acciones"), ("MSFT", "Microsoft", "Acciones"), ("AAPL", "Apple", "Acciones"),
    ("AMZN", "Amazon", "Acciones"), ("GOOGL", "Alphabet", "Acciones"), ("TSLA", "Tesla", "Acciones"),
    ("SAN.MC", "Santander", "Acciones"), ("ITX.MC", "Inditex", "Acciones"),
    ("BTC-USD", "Bitcoin", "Cripto"), ("ETH-USD", "Ethereum", "Cripto"), ("GC=F", "Oro", "Materias primas"),
]


def num(x):
    d = 0 if abs(x) >= 1000 else 2
    return f"{x:,.{d}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x, signo=False):
    s = f"{x:+.1f}" if signo else f"{x:.1f}"
    return s.replace(".", ",") + " %"


def _pedir(host, sym, rango, inter):
    u = "https://%s.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=%s" % (host, urllib.parse.quote(sym), rango, inter)
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25))
    res = r["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    bars = []
    for i, t in enumerate(res["timestamp"]):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if None in (o, h, l, c):
            continue
        bars.append([int(t), float(o), float(h), float(l), float(c)])
    return bars, res["meta"].get("regularMarketPrice")


def a_semanal(d):
    """Agrupa velas diarias en semanales (lunes a domingo)."""
    out = {}
    for t, o, h, l, c in d:
        k = datetime.fromtimestamp(t, timezone.utc).isocalendar()[:2]
        if k not in out:
            out[k] = [t, o, h, l, c]
        else:
            w = out[k]
            w[2] = max(w[2], h)
            w[3] = min(w[3], l)
            w[4] = c
    return [out[k] for k in sorted(out)]


def descargar(sym):
    if os.environ.get("SAMPLE"):
        return simular(sym)
    ultimo = None
    # Yahoo limita las peticiones (error 429): se reintenta esperando cada vez más
    intentos = (("query1", "1wk", 0), ("query2", "1wk", 12), ("query1", "1d", 30), ("query2", "1d", 60), ("query1", "1wk", 90))
    for host, inter, espera in intentos:
        if espera:
            time.sleep(espera)
        try:
            bars, mp = _pedir(host, sym, "5y", inter)
            if inter == "1d":
                bars = a_semanal(bars)
            if len(bars) < 40:
                raise ValueError("pocos datos (%d)" % len(bars))
            if mp:
                bars[-1][4] = float(mp)
                bars[-1][2] = max(bars[-1][2], float(mp))
                bars[-1][3] = min(bars[-1][3], float(mp))
            return bars
        except Exception as e:
            ultimo = "%s 5y %s: %s" % (host, inter, e)
            if "429" not in str(e):
                time.sleep(2)
    print("  error de descarga", sym, "->", ultimo)
    return None


def simular(sym):
    rnd = random.Random(sum(map(ord, sym)))
    p = 100 * (1 + rnd.random() * 20)
    drift = rnd.choice([0.004, 0.003, -0.001, 0.0])
    t = 1700000000
    bars = []
    for i in range(260):
        o = p
        c = o * math.exp(drift + rnd.gauss(0, 0.028))
        h = max(o, c) * (1 + abs(rnd.gauss(0, 0.01)))
        l = min(o, c) * (1 - abs(rnd.gauss(0, 0.01)))
        bars.append([t + i * 604800, o, h, l, c])
        p = c
    return bars


def pivotes(bars, k=4):
    H, L = [], []
    n = len(bars)
    for i in range(k, n - k):
        if bars[i][2] >= max(b[2] for b in bars[i - k:i + k + 1]):
            H.append(i)
        if bars[i][3] <= min(b[3] for b in bars[i - k:i + k + 1]):
            L.append(i)
    return H, L


def cuantil(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, max(0, int(round(q * (len(v) - 1)))))]


def analizar(sym, name, grupo, bars):
    n = len(bars)
    cl = [b[4] for b in bars]
    H, L = pivotes(bars)
    ult = cl[-1]
    # ventana del canal: últimas 156 semanas (3 años) o toda la serie
    W = min(n, 156)
    x0 = n - W
    xs = list(range(W))
    ys = [math.log(cl[x0 + i]) for i in xs]
    mx = sum(xs) / W
    my = sum(ys) / W
    sxx = sum((x - mx) ** 2 for x in xs)
    m = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    b = my - m * mx
    resH = [math.log(bars[i][2]) - (m * (i - x0) + b) for i in H if i >= x0]
    resL = [math.log(bars[i][3]) - (m * (i - x0) + b) for i in L if i >= x0]
    if not resH:
        resH = [max(math.log(bars[i][2]) - (m * (i - x0) + b) for i in range(x0, n))]
    if not resL:
        resL = [min(math.log(bars[i][3]) - (m * (i - x0) + b) for i in range(x0, n))]
    br = b + cuantil(resH, 0.92)
    bs = b + cuantil(resL, 0.08)
    xl = n - 1 - x0
    res_ahora = math.exp(m * xl + br)
    sup_ahora = math.exp(m * xl + bs)
    f = 26
    res_fut = math.exp(m * (xl + f) + br)
    sup_fut = math.exp(m * (xl + f) + bs)
    pos = (math.log(ult) - (m * xl + bs)) / ((br - bs) or 1e-9)
    pend = (math.exp(m * 52) - 1) * 100
    tq = lambda P, line: sum(1 for i, bb in P if abs(math.log(bb) - line(i)) < 0.02)
    toc_r = sum(1 for i in H if i >= x0 and abs(math.log(bars[i][2]) - (m * (i - x0) + br)) < 0.025)
    toc_s = sum(1 for i in L if i >= x0 and abs(math.log(bars[i][3]) - (m * (i - x0) + bs)) < 0.025)
    # niveles horizontales
    pts = sorted([bars[i][2] for i in H] + [bars[i][3] for i in L])
    cl_ = []
    for p in pts:
        if cl_ and abs(math.log(p / (sum(cl_[-1]) / len(cl_[-1])))) < 0.018:
            cl_[-1].append(p)
        else:
            cl_.append([p])
    niv = [(sum(c) / len(c), len(c)) for c in cl_ if len(c) >= 2]
    deb = sorted([x for x in niv if x[0] < ult * 0.995], key=lambda a: -a[0])[:3]
    arr = sorted([x for x in niv if x[0] > ult * 1.005], key=lambda a: a[0])[:3]
    niveles = [{"p": round(p, 4), "n": k, "t": "s"} for p, k in deb] + [{"p": round(p, 4), "n": k, "t": "r"} for p, k in arr]
    # estado
    if pos > 1.02:
        est, cod = "Rompe la resistencia del canal", "rompe_up"
    elif pos < -0.02:
        est, cod = "Pierde el soporte del canal", "rompe_dn"
    elif pend > 6:
        est, cod = ("Canal alcista, cerca del soporte" if pos < 0.25 else "Canal alcista, cerca de la resistencia" if pos > 0.75 else "Canal alcista"), "alc"
    elif pend < -6:
        est, cod = ("Canal bajista, cerca del soporte" if pos < 0.25 else "Canal bajista, cerca de la resistencia" if pos > 0.75 else "Canal bajista"), "baj"
    else:
        est, cod = "Rango lateral", "lat"
    maxw = max(b[2] for b in bars)
    minw = min(b[3] for b in bars[-52:])
    tx = []
    tx.append(f"Canal de {W} semanas con pendiente de {pct(pend, True)} anual. {toc_r} {'toque' if toc_r == 1 else 'toques'} en la resistencia y {toc_s} en el soporte.")
    tx.append(f"El precio ({num(ult)}) está al {max(0, min(100, pos * 100)):.0f} % de la altura del canal (0 % = soporte, 100 % = resistencia).")
    tx.append(f"Hoy el soporte está en {num(sup_ahora)} y la resistencia en {num(res_ahora)}. Si el canal se mantiene, dentro de 26 semanas estarían en {num(sup_fut)} y {num(res_fut)}.")
    if deb:
        tx.append(f"Si pierde el soporte, el siguiente apoyo horizontal está en {num(deb[0][0])} ({pct((deb[0][0] / ult - 1) * 100, True)}), con {deb[0][1]} toques históricos.")
    if arr:
        tx.append(f"Primer freno por arriba: {num(arr[0][0])} ({pct((arr[0][0] / ult - 1) * 100, True)}), con {arr[0][1]} toques.")
    tx.append(f"Máximo de las últimas {n} semanas: {num(maxw)} ({pct((ult / maxw - 1) * 100, True)} desde ahí). Mínimo de 52 semanas: {num(minw)}.")
    return {
        "s": sym, "n": name, "g": grupo, "p": round(ult, 4), "cod": cod, "est": est,
        "w": [[b[0], round(b[1], 4), round(b[2], 4), round(b[3], 4), round(b[4], 4)] for b in bars],
        "ch": {"x0": x0, "m": round(m, 6), "bs": round(bs, 5), "br": round(br, 5)},
        "k": {"pend": round(pend, 1), "pos": round(pos, 3), "sup": round(sup_ahora, 4), "res": round(res_ahora, 4),
              "supf": round(sup_fut, 4), "resf": round(res_fut, 4), "ts": toc_s, "tr": toc_r},
        "niv": niveles, "tx": tx,
    }


def main():
    previo = {}
    try:
        with open("tendencias.json") as f:
            for x in json.load(f).get("d", []):
                previo[x["s"]] = x
    except Exception:
        pass
    out = []
    for sym, name, g in U:
        bars = descargar(sym)
        if not bars:
            print("sin datos:", sym)
            if sym in previo:
                out.append(previo[sym])
                print("  se mantiene el cálculo anterior de", sym)
            time.sleep(5)
            continue
        try:
            out.append(analizar(sym, name, g, bars))
            print("ok", sym, out[-1]["est"])
        except Exception as e:
            print("error", sym, e)
        time.sleep(3)
    if not out:
        print("No se pudo descargar ningún activo; no se sobrescribe tendencias.json")
        raise SystemExit(1)
    with open("tendencias.json", "w") as f:
        json.dump({"t": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "d": out}, f, separators=(",", ":"), ensure_ascii=False)
    print(len(out), "activos")


if __name__ == "__main__":
    main()
