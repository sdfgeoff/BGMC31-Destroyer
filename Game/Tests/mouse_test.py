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
    if 'MOUSE' not in cont.owner:
        cont.owner['MOUSE'] = mouse.Mouse()
        bge.render.showMouse(True)
        cont.owner['MOUSE'].scenes = [cont.owner.scene]
    else:
        # Otherwise run it with the status of the mouse click as a test
        # input
        cont.owner['MOUSE'].update()
        print(cont.owner['MOUSE'].get_over(cont.owner.scene))
