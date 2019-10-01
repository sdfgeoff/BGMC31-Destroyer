import aud
import os
import utils
import defs
import random

def create_factory(sound_name):
    return aud.Factory.buffer(aud.Factory(
        os.path.join(utils.ROOT_PATH, 'Sounds', sound_name)
    ))


EFFECT_SINGLES = {
    p: create_factory(p) for p in defs.SOUND_EFFECTS_SINGLE
}
DEVICE = aud.device()

def set_listener_transform(transform):
    DEVICE.listener_location = transform.translation
    DEVICE.listener_orientation = transform.to_quaternion()

def play_effect_single(path, position, seek_time, rand_volume, rand_pitch):
    handle = DEVICE.play(EFFECT_SINGLES[path])
    handle.distance_maximum = 1000
    handle.distance_reference = 100
    handle.relative = False
    
    handle.position = seek_time
    handle.location = position
    handle.volume += rand_volume * (random.random() - 0.5)
    handle.pitch += rand_pitch * (random.random() - 0.5)
