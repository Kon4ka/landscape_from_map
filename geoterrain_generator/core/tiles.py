import os, pathlib, urllib.request

TILE_URLS = {
    'YANDEX': ("https://static-maps.yandex.ru/1.x/?ll={lon},{lat}&z={z}"
               "&l=sat&size=650,450"),
    'MAPTILER':"https://api.maptiler.com/tiles/satellite-v2/{z}/{x}/{y}.jpg?key={key}",
}

def fetch_image(lat, lon, zoom, provider, api_key, out_path):
    if provider == 'YANDEX':
        url = TILE_URLS['YANDEX'].format(lat=lat, lon=lon, z=zoom)
        width, height = 650, 450          # ← size в URL
    else:
        url   = TILE_URLS[provider].format(lat=lat, lon=lon, z=zoom,
                                           x=0, y=0, key=api_key)
        width, height = 512, 512          # MapTiler xyz по умолчанию
    urllib.request.urlretrieve(url, out_path)
    return width / height         
