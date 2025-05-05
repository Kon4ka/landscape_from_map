import json, urllib.request, urllib.parse, numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

OE_URL   = "https://api.open-elevation.com/api/v1/lookup"
OTD_URL  = "https://api.opentopodata.org/v1"
CHUNK    = 100        # именно столько разрешает public OTD

def _chunked(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

def _pick_dataset(lat):
    """Выбираем DEM-источник по широте"""
    if lat > 60:   # Арктика
        return "arcticdem"        # 10-м мозаика
    if lat < -60: # Антарктида
        return "rema"             # 8-м мозаика
    return None                   # внутри ±60° остаёмся на SRTM

def _fetch_openelev(pts):
    """POST в Open-Elevation (до 250 точек за раз)"""
    data = json.dumps({"locations": pts}).encode()
    req  = urllib.request.Request(
        OE_URL, data=data,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        js = json.load(r)
    return (p["elevation"] for p in js["results"])

def _fetch_opentopo(dataset, pts):
    """POST в Open-Topo-Data; dataset вроде 'arcticdem' / 'mapzen'"""
    url = f"{OTD_URL}/{dataset}"
    # Формируем строку 'lat,lon|lat,lon'
    locs = "|".join(f"{p['latitude']:.6f},{p['longitude']:.6f}" for p in pts)
    data = urllib.parse.urlencode({"locations": locs}).encode()
    req  = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=10) as r:
        js = json.load(r)
    if js.get("status") != "OK":
        raise RuntimeError(js.get("error", "Unknown OTD error"))
    return (p["elevation"] if p["elevation"] is not None else 0.0
            for p in js["results"])

def fetch_dem(lat_c, lon_c, *, side_m=1000, samples=50):
    """Возвращает np.float32[samples×samples]"""
    delta = side_m / 111_320 / 2             # градусы на половину стороны
    lats  = np.linspace(lat_c - delta, lat_c + delta, samples, dtype=float)
    lons  = np.linspace(lon_c - delta, lon_c + delta, samples, dtype=float)

    pts   = [{"latitude": la, "longitude": lo} for la in lats for lo in lons]
    dataset = _pick_dataset(lat_c)

    elev = []
    chunks = list(_chunked(pts, CHUNK))

    def fetch_chunk(chunk):
        if dataset is None:                               # SRTM <=60°
            return list(_fetch_openelev(chunk))
        else:                                             # Arctic / Antarctica
            return list(_fetch_opentopo(dataset, chunk))

    # Последовательная обработка без потоков
    for chunk in chunks:
        elev.extend(fetch_chunk(chunk))

    return np.array(elev, dtype=np.float32).reshape(samples, samples)
