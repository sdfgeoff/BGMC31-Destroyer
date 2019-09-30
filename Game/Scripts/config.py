DATA = {
    'MOUSE_SMOOTHING': 0.4,
    'MOUSE_ZOOM_SMOOTHING': 0.9,
    'TOUCH_FRIENDLY': False,
    'MOUSE_ZOOM_SENSITIVITY': 0.05,
    'MOUSE_SENSITIVITY': 4.0,
    'MOUSE_Y_INVERT': False,
    'EXIT_ON_ERROR': True,
    'LOG_LEVEL': 'INFO',
    'PROFILE': True,
}


def get(key):
    return DATA[key]
