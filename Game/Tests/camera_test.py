import bge
import mouse
import camera
import defs
import logging

logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def test(cont):
    '''This is used to test the camera class from Camera.blend. It checks
    to see if the game object exists, and if it does not, runs the camera'''
    # If the camera object does not exist, create it
    if 'CAMERA' not in cont.owner:
        cont.owner['MOUSE'] = mouse.Mouse()
        cont.owner['CAMERA'] = camera.Camera(cont.owner, defs.CAMERA_CONFIG)
        cont.owner.scene.active_camera = cont.owner['CAMERA'].camera
        bge.render.showMouse(True)
    else:
        # Otherwise run it with the status of the mouse click as a test
        # input
        cont.owner['MOUSE'].update()
        cont.owner['CAMERA'].update(cont.owner['MOUSE'].drag_delta, cont.owner['MOUSE'].scroll_delta)
