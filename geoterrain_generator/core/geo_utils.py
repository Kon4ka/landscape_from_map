import urllib.request
import json
import urllib.parse

def fetch_geojson_by_bbox(bbox, url_template):
    """
    bbox: (lon1, lat1, lon2, lat2)
    url_template: строка с {bbox} для подстановки bbox
    """
    # Если в url_template есть 'data=', то параметр после data= нужно url-энкодить
    if '{bbox}' in url_template:
        bbox_str = ','.join(map(str, bbox))
        url = url_template.format(bbox=bbox_str)
        if 'data=' in url:
            base, data = url.split('data=', 1)
            url = base + 'data=' + urllib.parse.quote(data)
    else:
        url = url_template
    with urllib.request.urlopen(url) as response:
        return json.load(response)


def point_in_polygon(x, y, polygon):
    # Алгоритм луча (Ray Casting) для проверки попадания точки в полигон
    num = len(polygon)
    j = num - 1
    c = False
    for i in range(num):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            c = not c
        j = i
    return c
