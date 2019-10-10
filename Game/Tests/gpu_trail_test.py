import bge
from effects import gpu_trail
import defs
import logging

logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def test(cont):
    '''This is used to test the camera class from Camera.blend. It checks
    to see if the game object exists, and if it does not, runs the camera'''
    # If the camera object does not exist, create it
    if 'TRAIL' not in cont.owner:
        cont.owner['TRAIL'] = gpu_trail.trail_manager.attach_trail(
            cont.owner, 0.1, 5.0,
            [bge.logic.getRandomFloat() for _ in range(4)]
        )
        cont.owner['TRAIL'].set_intensity(1.0)
        #bge.render.showMouse(True)
    else:
        # Otherwise run it with the status of the mouse click as a test
        # input
        if bge.events.UPARROWKEY in bge.logic.keyboard.active_events:
            cont.owner['TRAIL'].set_intensity(1.0)
        if bge.events.DOWNARROWKEY in bge.logic.keyboard.active_events:
            cont.owner['TRAIL'].set_intensity(0.0)
