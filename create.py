import os

def create_project_structure(base_path):
    """Создает структуру папок и пустые файлы на основе переданного дерева."""
    structure = {
        "geoterrain_generator": {
            "__init__.py": None,
            "prefs.py": None,
            "ui": {
                "panel_main.py": None,
                "panel_settings.py": None,
            },
            "operators": {
                "op_area_select.py": None,
                "op_fetch_tiles.py": None,
                "op_build_height.py": None,
                "op_scatter_assets.py": None,
                "op_cleanup.py": None,
            },
            "core": {
                "tiles.py": None,
                "dem.py": None,
                "textures.py": None,
                "geo_utils.py": None,
                "scatter.py": None,
            },
            "assets": {},
            "vendor": {
                "gdal_wrapper.py": None,
            },
        }
    }

    def create_items(path, items):
        for name, content in items.items():
            item_path = os.path.join(path, name)
            if content is None:
                # Создаем пустой файл
                os.makedirs(os.path.dirname(item_path), exist_ok=True)
                with open(item_path, 'w') as f:
                    pass
                print(f"Создан файл: {item_path}")
            elif isinstance(content, dict):
                # Создаем папку и рекурсивно обрабатываем ее содержимое
                os.makedirs(item_path, exist_ok=True)
                print(f"Создана папка: {item_path}")
                create_items(item_path, content)

    create_items(base_path, structure)
    print("Структура проекта успешно создана.")

if __name__ == "__main__":
    target_path = input("Пожалуйста, введите путь к папке, где вы хотите создать структуру проекта: ")
    create_project_structure(target_path)