#!/usr/bin/env python3
"""Motor de señales del Hub Financiero.
Descarga el histórico diario (1 año) de Yahoo Finance, calcula indicadores
técnicos estándar y una nota de 0 a 100, y escribe senales.json.
Sin dependencias externas (solo biblioteca estándar)."""
import json, math, os, random, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

# (símbolo, nombre, grupo, mercado, moneda)
U = [
 # IA y semiconductores
 ("ANT", "Anthropic", "IA", "NASDAQ", "$"), ("NVDA", "Nvidia", "IA", "NASDAQ", "$"),
 ("AVGO", "Broadcom", "IA", "NASDAQ", "$"), ("PLTR", "Palantir", "IA", "NASDAQ", "$"),
 ("AMD", "AMD", "IA", "NASDAQ", "$"), ("TSM", "TSMC", "IA", "NYSE", "$"),
 ("ARM", "Arm Holdings", "IA", "NASDAQ", "$"), ("SMCI", "Super Micro", "IA", "NASDAQ", "$"),
 ("CRWV", "CoreWeave", "IA", "NASDAQ", "$"), ("MU", "Micron", "IA", "NASDAQ", "$"),
 ("QCOM", "Qualcomm", "IA", "NASDAQ", "$"), ("INTC", "Intel", "IA", "NASDAQ", "$"),
 ("ASML", "ASML", "IA", "NASDAQ", "$"), ("AMAT", "Applied Materials", "IA", "NASDAQ", "$"),
 ("SNOW", "Snowflake", "IA", "NYSE", "$"), ("ORCL", "Oracle", "IA", "NYSE", "$"),
 # Gigantes tecnológicos
 ("AAPL", "Apple", "Big Tech", "NASDAQ", "$"), ("MSFT", "Microsoft", "Big Tech", "NASDAQ", "$"),
 ("AMZN", "Amazon", "Big Tech", "NASDAQ", "$"), ("GOOGL", "Alphabet", "Big Tech", "NASDAQ", "$"),
 ("META", "Meta", "Big Tech", "NASDAQ", "$"), ("TSLA", "Tesla", "Big Tech", "NASDAQ", "$"),
 ("NFLX", "Netflix", "Big Tech", "NASDAQ", "$"),
 # Espacio, cuántica e innovación
 ("SPCX", "SpaceX", "Innovación", "NASDAQ", "$"), ("RKLB", "Rocket Lab", "Innovación", "NASDAQ", "$"),
 ("IONQ", "IonQ", "Innovación", "NYSE", "$"), ("MP", "MP Materials", "Innovación", "NYSE", "$"),
 # Banca y pagos
 ("JPM", "JPMorgan", "Banca y pagos", "NYSE", "$"), ("V", "Visa", "Banca y pagos", "NYSE", "$"),
 ("MA", "Mastercard", "Banca y pagos", "NYSE", "$"), ("PYPL", "PayPal", "Banca y pagos", "NASDAQ", "$"),
 ("BRK-B", "Berkshire Hathaway", "Banca y pagos", "NYSE", "$"),
 # Cripto en bolsa
 ("COIN", "Coinbase", "Cripto en bolsa", "NASDAQ", "$"), ("MSTR", "Strategy (MSTR)", "Cripto en bolsa", "NASDAQ", "$"),
 ("MARA", "Marathon Digital", "Cripto en bolsa", "NASDAQ", "$"), ("CRCL", "Circle", "Cripto en bolsa", "NYSE", "$"),
 ("HOOD", "Robinhood", "Cripto en bolsa", "NASDAQ", "$"), ("PURR", "Hyperliquid Strategies", "Cripto en bolsa", "NASDAQ", "$"),
 # Consumo y salud
 ("WMT", "Walmart", "Consumo y salud", "NYSE", "$"), ("COST", "Costco", "Consumo y salud", "NASDAQ", "$"),
 ("KO", "Coca-Cola", "Consumo y salud", "NYSE", "$"), ("PEP", "PepsiCo", "Consumo y salud", "NASDAQ", "$"),
 ("MCD", "McDonald's", "Consumo y salud", "NYSE", "$"), ("NKE", "Nike", "Consumo y salud", "NYSE", "$"),
 ("DIS", "Disney", "Consumo y salud", "NYSE", "$"), ("PG", "Procter & Gamble", "Consumo y salud", "NYSE", "$"),
 ("JNJ", "Johnson & Johnson", "Consumo y salud", "NYSE", "$"), ("LLY", "Eli Lilly", "Consumo y salud", "NYSE", "$"),
 ("NVO", "Novo Nordisk", "Consumo y salud", "NYSE", "$"), ("UBER", "Uber", "Consumo y salud", "NYSE", "$"),
 # Energía, defensa e industria
 ("XOM", "ExxonMobil", "Energía e industria", "NYSE", "$"), ("CVX", "Chevron", "Energía e industria", "NYSE", "$"),
 ("BA", "Boeing", "Energía e industria", "NYSE", "$"), ("LMT", "Lockheed Martin", "Energía e industria", "NYSE", "$"),
 # Bolsa española
 ("SAN.MC", "Santander", "España", "BME", "€"), ("BBVA.MC", "BBVA", "España", "BME", "€"),
 ("ITX.MC", "Inditex", "España", "BME", "€"), ("IBE.MC", "Iberdrola", "España", "BME", "€"),
 ("TEF.MC", "Telefónica", "España", "BME", "€"), ("REP.MC", "Repsol", "España", "BME", "€"),
 ("CABK.MC", "CaixaBank", "España", "BME", "€"), ("ELE.MC", "Endesa", "España", "BME", "€"),
 ("AMS.MC", "Amadeus", "España", "BME", "€"), ("NTGY.MC", "Naturgy", "España", "BME", "€"),
 ("BKT.MC", "Bankinter", "España", "BME", "€"), ("SAB.MC", "Banco Sabadell", "España", "BME", "€"),
 ("ACS.MC", "ACS", "España", "BME", "€"), ("FER.MC", "Ferrovial", "España", "BME", "€"),
 ("GRF.MC", "Grifols", "España", "BME", "€"), ("MAP.MC", "Mapfre", "España", "BME", "€"),
 ("CLNX.MC", "Cellnex", "España", "BME", "€"), ("IAG.MC", "IAG (Iberia)", "España", "BME", "€"),
 ("ANA.MC", "Acciona", "España", "BME", "€"), ("ENG.MC", "Enagás", "España", "BME", "€"),
 ("RED.MC", "Redeia", "España", "BME", "€"), ("AENA.MC", "Aena", "España", "BME", "€"),
 ("ROVI.MC", "Rovi", "España", "BME", "€"), ("IDR.MC", "Indra", "España", "BME", "€"),
 ("ACX.MC", "Acerinox", "España", "BME", "€"), ("COL.MC", "Colonial", "España", "BME", "€"),
 # Europa
 ("SAP", "SAP", "Europa", "NYSE", "$"), ("MC.PA", "LVMH", "Europa", "París", "€"),
 ("SHEL", "Shell", "Europa", "NYSE", "$"),
 # ETFs
 ("SPY", "S&P 500 (SPY)", "ETFs", "NYSE Arca", "$"), ("QQQ", "Nasdaq 100 (QQQ)", "ETFs", "NASDAQ", "$"),
 ("SMH", "Semiconductores (SMH)", "ETFs", "NASDAQ", "$"), ("XLE", "Energía (XLE)", "ETFs", "NYSE Arca", "$"),
 ("GLD", "Oro (GLD)", "ETFs", "NYSE Arca", "$"), ("SLV", "Plata (SLV)", "ETFs", "NYSE Arca", "$"),
 ("TLT", "Bonos 20A (TLT)", "ETFs", "NASDAQ", "$"), ("IBIT", "Bitcoin ETF (IBIT)", "ETFs", "NASDAQ", "$"),
 ("EEM", "Emergentes (EEM)", "ETFs", "NYSE Arca", "$"),
 # Índices
 ("^GSPC", "S&P 500", "Índices", "Índice", ""), ("^IXIC", "Nasdaq", "Índices", "Índice", ""),
 ("^IBEX", "IBEX 35", "Índices", "Índice", ""), ("^GDAXI", "DAX", "Índices", "Índice", ""),
 ("^STOXX50E", "Euro Stoxx 50", "Índices", "Índice", ""), ("^N225", "Nikkei 225", "Índices", "Índice", ""),
 # Cripto
 ("BTC-USD", "Bitcoin", "Cripto", "Cripto", "$"), ("ETH-USD", "Ethereum", "Cripto", "Cripto", "$"),
 ("SOL-USD", "Solana", "Cripto", "Cripto", "$"), ("BNB-USD", "BNB", "Cripto", "Cripto", "$"),
 ("XRP-USD", "XRP", "Cripto", "Cripto", "$"), ("ADA-USD", "Cardano", "Cripto", "Cripto", "$"),
 ("AVAX-USD", "Avalanche", "Cripto", "Cripto", "$"), ("LINK-USD", "Chainlink", "Cripto", "Cripto", "$"),
 ("DOGE-USD", "Dogecoin", "Cripto", "Cripto", "$"), ("SUI20947-USD", "Sui", "Cripto", "Cripto", "$"),
 ("HYPE32196-USD", "Hyperliquid", "Cripto", "Cripto", "$"),
 # Materias primas y divisas
 ("GC=F", "Oro", "Materias primas", "Futuros", "$"), ("SI=F", "Plata", "Materias primas", "Futuros", "$"),
 ("HG=F", "Cobre", "Materias primas", "Futuros", "$"), ("CL=F", "Petróleo WTI", "Materias primas", "Futuros", "$"),
 ("NG=F", "Gas natural", "Materias primas", "Futuros", "$"), ("EURUSD=X", "EUR/USD", "Materias primas", "Divisa", ""),
]
ORDEN = ["Venta fuerte", "Venta", "Neutral", "Compra", "Compra fuerte"]
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def etiqueta(n):
    return "Compra fuerte" if n >= 72 else "Compra" if n >= 57 else "Neutral" if n >= 43 else "Venta" if n >= 28 else "Venta fuerte"


def sma(c, n, end=None):
    end = len(c) if end is None else end
    if end < n:
        return None
    return sum(c[end - n:end]) / n


def ema_series(c, n):
    k = 2.0 / (n + 1)
    out = [c[0]]
    for x in c[1:]:
        out.append(x * k + out[-1] * (1 - k))
    return out


def rsi14(c):
    if len(c) < 16:
        return None
    g = l = 0.0
    for i in range(1, 15):
        d = c[i] - c[i - 1]
        g += max(d, 0)
        l += max(-d, 0)
    g /= 14
    l /= 14
    for i in range(15, len(c)):
        d = c[i] - c[i - 1]
        g = (g * 13 + max(d, 0)) / 14
        l = (l * 13 + max(-d, 0)) / 14
    return 100.0 if l == 0 else 100 - 100 / (1 + g / l)


def macd_hist(c):
    if len(c) < 35:
        return None, None
    e12, e26 = ema_series(c, 12), ema_series(c, 26)
    m = [a - b for a, b in zip(e12, e26)]
    sg = ema_series(m, 9)
    h = [a - b for a, b in zip(m, sg)]
    return h[-1], h[-4]


def pct(a, b):
    return a / b - 1 if b else 0.0


def analizar(c, v, spy):
    """Devuelve dict con nota, bloques, motivos... o None si no hay histórico mínimo."""
    n = len(c)
    if n < 60:
        return None
    p = c[-1]
    s20, s50, s200 = sma(c, 20), sma(c, 50), sma(c, 200)
    s50b = sma(c, 50, n - 10)
    rsi = rsi14(c)
    mh, mh3 = macd_hist(c)
    h52, l52 = max(c[-252:]), min(c[-252:])
    r1 = pct(p, c[-22]) if n > 22 else 0.0
    r3 = pct(p, c[-64]) if n > 64 else pct(p, c[0])
    rs3 = None
    if spy and len(spy) > 64:
        rs3 = r3 - pct(spy[-1], spy[-64])
    motivos = []

    # ---- Tendencia (0-25)
    pt = mx = 0.0
    mx += 7
    if p > s50:
        pt += 7
    if s200 is not None:
        mx += 8
        if p > s200:
            pt += 8
            motivos.append("Precio sobre la media de 200 sesiones (+%.1f %%)" % (pct(p, s200) * 100))
        else:
            motivos.append("Precio bajo la media de 200 sesiones (%.1f %%)" % (pct(p, s200) * 100))
        mx += 6
        if s50 > s200:
            pt += 6
            motivos.append("Media de 50 sobre la de 200: tendencia alcista")
        else:
            motivos.append("Media de 50 bajo la de 200: tendencia bajista")
    mx += 4
    if p > s20:
        pt += 4
    mx += 4
    if s50 > s50b:
        pt += 4
    if p > s50 and s200 is None:
        motivos.append("Precio sobre la media de 50 sesiones")
    elif p <= s50:
        motivos.append("Precio bajo la media de 50 sesiones")
    b_t = pt / mx * 25

    # ---- Momento (0-25)
    pt = mx = 0.0
    if rsi is not None:
        mx += 12
        if 45 <= rsi <= 70:
            pt += 12
            motivos.append("RSI %d: zona sana" % round(rsi))
        elif 70 < rsi <= 80:
            pt += 8
            motivos.append("RSI %d: fuerte, empieza a estar caro" % round(rsi))
        elif rsi > 80:
            pt += 4
            motivos.append("RSI %d: sobrecompra" % round(rsi))
        elif 35 <= rsi < 45:
            pt += 6
            motivos.append("RSI %d: débil" % round(rsi))
        else:
            pt += 2
            motivos.append("RSI %d: sobreventa" % round(rsi))
    if mh is not None:
        mx += 7
        if mh > 0:
            pt += 7
        mx += 6
        if mh > mh3:
            pt += 6
        motivos.append("MACD %s y %s" % ("positivo" if mh > 0 else "negativo", "mejorando" if mh > mh3 else "empeorando"))
    b_m = (pt / mx * 25) if mx else 12.5

    # ---- Fuerza relativa (0-25)
    pt = 0.0
    if rs3 is not None:
        pt += 12 * clamp((rs3 + 0.15) / 0.30)
        motivos.append("3 meses: %+.1f %% (vs S&P 500: %+.1f pts)" % (r3 * 100, rs3 * 100))
    else:
        pt += 6
        motivos.append("3 meses: %+.1f %%" % (r3 * 100))
    pt += 8 * clamp((r1 + 0.08) / 0.16)
    pt += 5 * clamp((r3 + 0.10) / 0.20)
    b_f = pt

    # ---- Posición y volumen (0-25)
    prox = p / h52 if h52 else 0
    pt = 15 * clamp((prox - 0.65) / 0.35)
    motivos.append("A %.1f %% de su máximo de 52 semanas" % ((1 - prox) * 100))
    ud = None
    if v and len(v) == n:
        up = dn = 0.0
        for i in range(n - 20, n):
            if v[i] is None:
                continue
            if c[i] >= c[i - 1]:
                up += v[i] or 0
            else:
                dn += v[i] or 0
        if up + dn > 0 and dn > 0:
            ud = up / dn
    if ud is not None:
        pt += 10 * clamp((ud - 0.6) / 1.0)
        motivos.append("Volumen: %s" % ("más en días de subida" if ud >= 1.1 else "más en días de bajada" if ud <= 0.9 else "equilibrado"))
    else:
        pt += 5
    b_p = pt

    import re
    motivos = [re.sub(r"(\d)\.(\d)", r"\1,\2", m) for m in motivos]
    nota = round(b_t + b_m + b_f + b_p)
    return {"p": p, "nota": nota, "b": [round(b_t, 1), round(b_m, 1), round(b_f, 1), round(b_p, 1)],
            "motivos": motivos, "rsi": None if rsi is None else round(rsi, 1),
            "s20": s20, "s50": s50, "s200": s200, "h52": h52, "l52": l52,
            "r1": round(r1 * 100, 2), "r3": round(r3 * 100, 2), "rs3": None if rs3 is None else round(rs3 * 100, 2)}


def eventos(c, spy, v):
    ev = []
    n = len(c)
    if n >= 215:
        signos = []
        for k in range(10, -1, -1):
            a, b = sma(c, 50, n - k), sma(c, 200, n - k)
            signos.append(a > b)
        if not signos[0] and signos[-1]:
            ev.append("Cruce alcista de medias (50 sobre 200)")
        elif signos[0] and not signos[-1]:
            ev.append("Cruce bajista de medias (50 bajo 200)")
    if n >= 60 and c[-1] >= max(c[-252:-1]) * 0.999:
        ev.append("Nuevo máximo de 52 semanas")
    return ev


def descargar(sym):
    if os.environ.get("SAMPLE"):
        return simular(sym)
    for host in ("query1", "query2", "query1", "query2"):
        try:
            u = "https://%s.finance.yahoo.com/v8/finance/chart/%s?range=1y&interval=1d" % (host, urllib.parse.quote(sym))
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20))
            res = r["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            cl = q.get("close") or []
            vo = q.get("volume") or []
            pares = [(a, (vo[i] if i < len(vo) else None)) for i, a in enumerate(cl) if a is not None]
            if len(pares) < 2:
                raise ValueError("sin datos")
            c = [a for a, _ in pares]
            v = [b for _, b in pares]
            mp = res["meta"].get("regularMarketPrice")
            if mp:
                c[-1] = float(mp)
            return c, v
        except Exception:
            time.sleep(1.2)
    return None


def simular(sym):
    rnd = random.Random(sum(map(ord, sym)))
    if sym in ("SPCX", "ANT"):
        n = 6
    elif sym in ("HYPE32196-USD", "SUI20947-USD", "CRWV"):
        return None
    else:
        n = 252
    drift = rnd.uniform(-0.0008, 0.0016)
    vol = rnd.uniform(0.008, 0.03)
    x = rnd.uniform(5, 300)
    c, v = [], []
    for _ in range(n):
        x *= math.exp(drift + rnd.gauss(0, vol))
        c.append(x)
        v.append(rnd.uniform(1e6, 5e6))
    return c, v


def main():
    t0 = time.time()
    with ThreadPoolExecutor(6) as ex:
        datos = list(ex.map(lambda u: descargar(u[0]), U))
    spy = dict(zip([u[0] for u in U], datos)).get("SPY")
    spyc = spy[0] if spy else None
    out, faltan = [], []
    for (sym, nombre, grupo, mercado, cur), d in zip(U, datos):
        if not d:
            faltan.append(sym)
            continue
        c, v = d
        dia = pct(c[-1], c[-2]) * 100 if len(c) > 1 else 0.0
        fila = {"s": sym, "n": nombre, "g": grupo, "m": mercado, "cur": cur, "p": round(c[-1], 4), "c": round(dia, 2), "ses": len(c)}
        a = analizar(c, v, spyc)
        if a is None:
            fila["lab"] = "Sin histórico"
        else:
            prev = analizar(c[:-5], v[:-5] if v else None, spyc[:-5] if spyc else None)
            fila.update({"sc": a["nota"], "lab": etiqueta(a["nota"]), "b": a["b"], "r": a["motivos"], "rsi": a["rsi"],
                         "s20": round(a["s20"], 4), "s50": round(a["s50"], 4),
                         "s200": None if a["s200"] is None else round(a["s200"], 4),
                         "h52": round(a["h52"], 4), "l52": round(a["l52"], 4),
                         "r1": a["r1"], "r3": a["r3"], "rs3": a["rs3"], "ev": eventos(c, spyc, v),
                         "spark": [round(x, 4) for x in c[-60:]]})
            if prev:
                fila["prev"] = etiqueta(prev["nota"])
                fila["psc"] = prev["nota"]
                if fila["prev"] != fila["lab"]:
                    fila["ev"].insert(0, "Cambio de señal: de %s a %s (hace 5 sesiones)" % (fila["prev"], fila["lab"]))
        out.append(fila)
    print("ok", len(out), "de", len(U), "faltan", faltan, "en %.0f s" % (time.time() - t0))
    if len(out) >= 20:
        json.dump({"t": int(time.time()), "n": len(out), "faltan": faltan, "d": out}, open("senales.json", "w"), ensure_ascii=False, separators=(",", ":"))
    else:
        print("muy pocos datos: no se escribe senales.json")
        sys.exit(1)


if __name__ == "__main__":
    main()
