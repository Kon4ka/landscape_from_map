# geoterrain_generator/core/dem.py
"""
Open-Elevation (https://api.open-elevation.com/) ‒ бесплатный REST-сервис
возвращает altitudes для списка точек. На участок 1×1 км (10×10 сэмплов)
достаточно одного HTTP-запроса.
"""
import json, urllib.parse, urllib.request
import numpy as np

def fetch_dem(lat_c, lon_c, side_m=1000, samples=50):
    """
    Возвращает np.float32[samples×samples] ‒ высоты в метрах относительно MSL.
    lat_c / lon_c  – центр прямоугольника; сетка квадратная `side_m`.
    """
    # шаг сетки в градусах (приближение: 1° lat ≈ 111 320 м)
    delta_deg = side_m / 111_320 / 2
    lats = np.linspace(lat_c - delta_deg, lat_c + delta_deg, samples)
    lons = np.linspace(lon_c - delta_deg, lon_c + delta_deg, samples)

    pts = [{"latitude": float(la), "longitude": float(lo)}
           for la in lats for lo in lons]

    url = "https://api.open-elevation.com/api/v1/lookup"
    data = json.dumps({"locations": pts}).encode()
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        js = json.load(resp)

    alt = np.array([p["elevation"] for p in js["results"]],
                   dtype=np.float32).reshape(samples, samples)
    return alt
