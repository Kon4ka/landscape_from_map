# Camera presets for GeoTerrain Generator

CAMERA_PRESETS = [
    ("DJI_X7", "DJI X7 (APS-C)", ""),
    ("PHASE_ONE_IXM100", "Phase One iXM-100", ""),
    ("SONY_ILX_LR1", "Sony ILX-LR1", ""),
    ("CUSTOM", "Custom", "")
]

CAMERA_PRESET_PARAMS = {
    "DJI_X7": {
        "resolution": (6016, 4000),
        "sensor_width": 23.5,
        "sensor_height": 15.7,
        "pixel_size": 3.91,
        "focal_length": 24.0,
        "shutter_type": 'MECHANICAL',
        "pitch_deg": 0.0,  # Смотрит строго вниз
    },
    "PHASE_ONE_IXM100": {
        "resolution": (11608, 8708),
        "sensor_width": 43.9,
        "sensor_height": 32.9,
        "pixel_size": 3.76,
        "focal_length": 50.0,
        "shutter_type": 'LEAF',
        "pitch_deg": 0.0,
    },
    "SONY_ILX_LR1": {
        "resolution": (9504, 6336),
        "sensor_width": 35.6,
        "sensor_height": 23.8,
        "pixel_size": 3.76,
        "focal_length": 35.0,
        "shutter_type": 'MECHANICAL',
        "pitch_deg": 0.0,
    },
    "CUSTOM": {
        # Пользователь задаёт вручную
        "pitch_deg": 0.0,
    }
}
