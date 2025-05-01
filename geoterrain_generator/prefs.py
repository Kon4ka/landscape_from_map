import bpy, os
from bpy.props import FloatProperty, IntProperty, EnumProperty, StringProperty
from geoterrain_generator.envutils import load_dotenv

load_dotenv("YANDEX_STATIC_KEY")


class GeoTG_Preferences(bpy.types.AddonPreferences):
    bl_idname = "geoterrain_generator"

    # —————————————————  API и кеш  —————————————————
    provider: EnumProperty(
        name="Tile Provider",
        items=[('YANDEX', "Yandex Satellite", ""),
               ('MAPTILER', "MapTiler",        "")],
        default='YANDEX') # type: ignore
    api_key: StringProperty(
        name="API Key", subtype='PASSWORD',
        default=os.getenv("YANDEX_STATIC_KEY", "")) # type: ignore
    cache_dir: StringProperty(
        name="Cache Folder", subtype='DIR_PATH',
        default=os.path.expanduser("~/GeoCache")) # type: ignore

    # —————————————————  координаты + плотность  —————————————————
    lat1 : FloatProperty(name="Lat1 (SW)", default=64.517191)
    lon1 : FloatProperty(name="Lon1 (SW)", default=59.116188)
    lat2 : FloatProperty(name="Lat2 (NE)", default=64.513225)
    lon2 : FloatProperty(name="Lon2 (NE)", default=59.129578)
    grid_n: IntProperty  (name="Grid N",   default=120, min=30, max=512)

    def draw(self, context):
        lay = self.layout
        box = lay.box()
        box.label(text="Provider:")
        box.prop(self, "provider")
        box.prop(self, "api_key")
        box.prop(self, "cache_dir")
        box.separator()
        box.label(text="Default Coordinates:")
        col = box.column(align=True)
        col.prop(self, "lat1"); col.prop(self, "lon1")
        col.prop(self, "lat2"); col.prop(self, "lon2")
        box.prop(self, "grid_n")
