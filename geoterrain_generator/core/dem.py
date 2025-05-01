import json, urllib.request, numpy as np

OE_URL = "https://api.open-elevation.com/api/v1/lookup"
CHUNK  = 200      # безопасно < 250

def _chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i+size]

def fetch_dem(lat_c, lon_c, side_m=1000, samples=50):
    delta = side_m / 111_320 / 2
    lats  = np.linspace(lat_c - delta, lat_c + delta, samples, dtype=float)
    lons  = np.linspace(lon_c - delta, lon_c + delta, samples, dtype=float)

    pts = [{"latitude": la, "longitude": lo} for la in lats for lo in lons]
    elev = []

    for chunk in _chunked(pts, CHUNK):
        data = json.dumps({"locations": chunk}).encode()
        req  = urllib.request.Request(OE_URL, data=data,
                                      headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            js = json.load(resp)
            elev.extend(p["elevation"] for p in js["results"])

    return np.array(elev, dtype=np.float32).reshape(samples, samples)
