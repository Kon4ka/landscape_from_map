import bpy
import math
from mathutils import Vector
from ..core.dem import fetch_dem  # Импортируем DEM
import numpy as np

BLENDER_SCALE = 100.0  # 1 BU = 100 метров, как в op_build_height.py

class OP_OT_create_flight_curve(bpy.types.Operator):
    bl_idname = "geotg.create_flight_curve"
    bl_label = "Create Flight Curve"
    bl_description = "Creates a flight curve at a specified height"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        curve_type = context.scene.geotg_flight_curve_type
        height = context.scene.geotg_flight_height

        # Найти террейн
        terrain = None
        for obj in context.scene.objects:
            if (obj.name.startswith("GeoTerrainGrid")):
                terrain = obj
                break
        if not terrain:
            self.report({'ERROR'}, "Не найден объект террейна (GeoTerrainGrid)")
            return {'CANCELLED'}

        # Получить размеры террейна в локальных координатах
        bbox = [terrain.matrix_world @ Vector(corner) for corner in terrain.bound_box]
        min_x = min(v.x for v in bbox)
        max_x = max(v.x for v in bbox)
        min_y = min(v.y for v in bbox)
        max_y = max(v.y for v in bbox)
        center_x = 0.5 * (min_x + max_x)
        center_y = 0.5 * (min_y + max_y)
        size_x = max_x - min_x
        size_y = max_y - min_y

        # Получить границы участка из preferences (как в op_fetch_trees)
        prefs = context.preferences.addons[__name__.split('.')[0]].preferences
        lat1, lat2 = min(prefs.lat1, prefs.lat2), max(prefs.lat1, prefs.lat2)
        lon1, lon2 = min(prefs.lon1, prefs.lon2), max(prefs.lon1, prefs.lon2)
        lat_c = 0.5 * (lat1 + lat2)
        lon_c = 0.5 * (lon1 + lon2)
        # Проверка на валидность координат (например, если пользователь не вводил значения)
        if any(abs(x) < 1e-6 for x in [lat1, lat2, lon1, lon2]):
            self.report({'ERROR'}, "Coordinates not set. Enter coordinates in the addon panel.")
            return {'CANCELLED'}
        # Размер участка в метрах (аналогично op_area_load)
        meters_lat = 111_320
        lat_mid = lat_c
        meters_lon = meters_lat * math.cos(math.radians(lat_mid))
        side_x = max((lon2 - lon1) * meters_lon, 1.0)
        side_y = max((lat2 - lat1) * meters_lat, 1.0)
        samples = 120  # Можно сделать настраиваемым
        dem = fetch_dem(lat_c, lon_c, side_m=side_y, samples=samples)
        z_min, z_max = dem.min(), dem.max()
        z_scale = (z_max - z_min) / BLENDER_SCALE

        # Для преобразования x/y в индексы DEM
        def xy_to_dem_idx(x, y):
            # x, y в Blender-единицах
            xi = int((x - min_x) / (size_x) * (samples - 1))
            yi = int((y - min_y) / (size_y) * (samples - 1))
            xi = np.clip(xi, 0, samples - 1)
            yi = np.clip(yi, 0, samples - 1)
            return xi, yi

        # Генерация точек кривой (XY), Z будет по DEM
        points = []
        if curve_type == 'STRAIGHT':
            if size_x >= size_y:
                points = [
                    (min_x, center_y),
                    (max_x, center_y)
                ]
            else:
                points = [
                    (center_x, min_y),
                    (center_x, max_y)
                ]
        elif curve_type == 'CIRCLE':
            r = 0.4 * 0.5 * min(size_x, size_y)
            n = 32
            points = [
                (center_x + r * math.cos(2*math.pi*i/n),
                 center_y + r * math.sin(2*math.pi*i/n)) for i in range(n+1)
            ]
        elif curve_type == 'SNAKE':
            waves = 5
            n = 100
            if size_x >= size_y:
                for i in range(n+1):
                    t = i / n
                    x = min_x + t * (max_x - min_x)
                    y = center_y + 0.4*size_y*math.sin(waves*math.pi*t)
                    points.append((x, y))
            else:
                for i in range(n+1):
                    t = i / n
                    y = min_y + t * (max_y - min_y)
                    x = center_x + 0.4*size_x*math.sin(waves*math.pi*t)
                    points.append((x, y))
        elif curve_type == 'SPIRAL':
            turns = 2
            n = 100
            r_max = 0.4 * 0.5 * min(size_x, size_y)
            for i in range(n+1):
                t = i / n
                angle = 2 * math.pi * turns * t
                r = r_max * t
                x = center_x + r * math.cos(angle)
                y = center_y + r * math.sin(angle)
                points.append((x, y))
        elif curve_type == 'CUSTOM':
            r = 0.3 * 0.5 * min(size_x, size_y)
            n = 16
            points = [
                (center_x + r * math.cos(2*math.pi*i/n),
                 center_y + r * math.sin(2*math.pi*i/n)) for i in range(n+1)
            ]
        else:
            self.report({'ERROR'}, f"Неизвестный тип кривой: {curve_type}")
            return {'CANCELLED'}

        # Корректируем Z по DEM для каждой точки
        points_3d = []
        for x, y in points:
            xi, yi = xy_to_dem_idx(x, y)
            z_dem = (dem[yi, xi] - z_min) / (z_max - z_min) * z_scale
            z = z_dem + height / BLENDER_SCALE
            points_3d.append((x, y, z))

        # Создать кривую как NURBS
        curve_data = bpy.data.curves.new('FlightCurve', type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new('NURBS')
        spline.points.add(len(points_3d)-1)
        for i, pt in enumerate(points_3d):
            spline.points[i].co = (pt[0], pt[1], pt[2], 1)
        spline.order_u = min(4, len(points_3d))  # порядок NURBS
        curve_obj = bpy.data.objects.new('FlightCurve', curve_data)
        context.collection.objects.link(curve_obj)
        curve_obj.select_set(True)
        context.view_layer.objects.active = curve_obj

        self.report({'INFO'}, f"Кривая '{curve_type}' создана с учётом рельефа (DEM) и высоты {height} м")
        return {'FINISHED'}
