import math
import os
import sys
import urllib.request
from PIL import Image
import argparse
from dotenv import load_dotenv

TILE_SIZE = 512           # стандартный размер тайла у MapTiler
ZOOM = 18                 # максимум ≈ 0.6 м/пиксель, можно 17/16
TILESET = "satellite-v2"  # спутниковый слой

load_dotenv()
API_KEY = os.getenv("MAPTILER_KEY")
if not API_KEY:
    print(" MAPTILER_KEY не найден в .env")
    sys.exit(1)

def deg2num(lat, lon, zoom):
    """Широта-долгота в tile номера"""
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return x, y

def num2deg(x, y, zoom):
    """Tile номера в широту-долготу"""
    n = 2.0 ** zoom
    lon = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat = math.degrees(lat_rad)
    return lat, lon

def download_tile(x, y, zoom, out_path):
    url = f"https://api.maptiler.com/tiles/{TILESET}/{zoom}/{x}/{y}.jpg?key={API_KEY}"
    urllib.request.urlretrieve(url, out_path)

def main(lat1, lon1, lat2, lon2, zoom=ZOOM, out_file="output.jpg"):
    lat_min, lat_max = min(lat1, lat2), max(lat1, lat2)
    lon_min, lon_max = min(lon1, lon2), max(lon1, lon2)

    x_min, y_max = deg2num(lat_min, lon_min, zoom)
    x_max, y_min = deg2num(lat_max, lon_max, zoom)

    tiles_x = x_max - x_min + 1
    tiles_y = y_max - y_min + 1
    total = tiles_x * tiles_y
    count = 0

    print(f"📡 Скачиваем {tiles_x}×{tiles_y} тайлов (zoom {zoom})...")

    full_img = Image.new('RGB', (tiles_x * TILE_SIZE, tiles_y * TILE_SIZE))

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            filename = f"tile_{x}_{y}.jpg"
            try:
                download_tile(x, y, zoom, filename)
                tile = Image.open(filename)
                i = x - x_min
                j = y - y_min
                full_img.paste(tile, (i * TILE_SIZE, j * TILE_SIZE))
                os.remove(filename)
            except Exception as e:
                print(f"\n⚠️ Ошибка тайла {x},{y}: {e}")
            count += 1
            # Выводим прогресс в одну строку
            print(f"\r🧩 Загружено {count}/{total} тайлов "
                  f"({(count / total * 100):.1f}%)", end='', flush=True)

    print()  # перенос строки после прогресса
    full_img.save(out_file)
    print(f"✅ Готово: сохранено в {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("lat1", type=float)
    parser.add_argument("lon1", type=float)
    parser.add_argument("lat2", type=float)
    parser.add_argument("lon2", type=float)
    parser.add_argument("output", type=str)
    parser.add_argument("--max_tiles", type=int, default=None,
                        help="Максимум тайлов (автовыбор zoom)")
    args = parser.parse_args()

    lat1, lon1, lat2, lon2 = args.lat1, args.lon1, args.lat2, args.lon2

    # если указан лимит — подбираем zoom
    if args.max_tiles is not None:
        for z in reversed(range(0, 21)):  # zoom 20...0
            x_min, y_max = deg2num(min(lat1, lat2), min(lon1, lon2), z)
            x_max, y_min = deg2num(max(lat1, lat2), max(lon1, lon2), z)
            count = (x_max - x_min + 1) * (y_max - y_min + 1)
            if count <= args.max_tiles:
                print(f"🔍 Выбран zoom={z} (всего {count} тайлов)")
                ZOOM = z
                break
        else:
            print("❌ Не удалось подобрать zoom под ограничение по тайлам")
            sys.exit(1)

    main(lat1, lon1, lat2, lon2, zoom=ZOOM, out_file=args.output)

# Example: python .\geoterrain_generator\libs\download_yandex_satellite.py 54.924560, 36.897892 54.935001, 36.879245 area.jpeg --max_tiles 50
# Example: python .\geoterrain_generator\libs\download_yandex_satellite.py 54.947714, 36.930685 54.928758, 36.875809 area.jpeg --max_tiles 50