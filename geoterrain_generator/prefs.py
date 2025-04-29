import bpy, os
from bpy.props import EnumProperty, StringProperty
from geoterrain_generator.envutils import load_dotenv

load_dotenv("YANDEX_STATIC_KEY")

class GeoTG_Preferences(bpy.types.AddonPreferences):
    bl_idname = "geoterrain_generator"          # имя пакета

    provider: EnumProperty(
        name="Tile Provider",
        items=[('YANDEX', "Yandex Satellite", ""),
               ('MAPTILER', "MapTiler",        "")],
        default='YANDEX')

    api_key: StringProperty(
        name="API Key",
        subtype='PASSWORD',
        description="Provider API key",
        default=os.getenv("YANDEX_STATIC_KEY", "")
    )

    # по умолчанию — подпапка “GeoCache” в домашнем каталоге
    cache_dir: StringProperty(
        name="Cache Folder", subtype='DIR_PATH',
        default=os.path.expanduser("H:\\Projects\\Programming\\landscape_from_map\\GeoCashe"))

    def draw(self, context):
        box = self.layout.box()
        box.prop(self, "provider")
        box.prop(self, "api_key")
        box.prop(self, "cache_dir")
