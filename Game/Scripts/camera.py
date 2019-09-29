import bge
import mathutils

import config
import utils



class Camera(utils.BaseClass):
    '''This object represents the camera - it can be rotated using mouse
    motion. Whether it is curently moving is set using the 'drag' parameter
    of the update function'''
    CONFIG_ITEMS = [
        'MIN_ANGLE',
        'MAX_ANGLE',
        'MIN_ZOOM_DIST',
        'MAX_ZOOM_DIST',
        'MIN_ZOOM_FOV',
        'MAX_ZOOM_FOV'
    ]
    def __init__(self, cam_center, config):
        super().__init__(config)
        self.log.info(self.M("create_camera"))
        utils.parent_groups(cam_center)
        self.cam_center = cam_center
        self.camera = [o for o in cam_center.childrenRecursive if 'CAMERA' in o][0]
        self.yaw = [o for o in cam_center.childrenRecursive if 'YAW' in o][0]
        self.pitch = [o for o in cam_center.childrenRecursive if 'PITCH' in o][0]

        # How fast it is currently spinning - this is so we can smooth it's
        # motion to make it prettier
        self.prev_vel = mathutils.Vector([0, 0])
        self.zoom_vel = 0
        self.zoom = 0.8
        
        self.update(mathutils.Vector([0,0]), 0)

    def update(self, drag_delta, zoom_delta):
        '''Rotates a set of nested empties to do a 3rd-person camera. The
        parameter drag_delta is a 2D vector of how much to rotate it by or None
        '''
        if drag_delta is not None:
            vel = drag_delta.copy()
            vel *= config.get('MOUSE_SENSITIVITY')
            if config.get('MOUSE_Y_INVERT'):
                vel.y *= -1
        else:
            vel = mathutils.Vector([0, 0])

        # Smooth the mouse motion
        vel = utils.lerp(self.prev_vel, vel, config.get('MOUSE_SMOOTHING'))
        self.prev_vel = vel
        
        zoom_vel = utils.lerp(self.zoom_vel, zoom_delta, config.get('MOUSE_ZOOM_SMOOTHING'))
        self.zoom_vel = zoom_vel

        # Rotate the objects
        self.yaw.applyRotation([0, vel[0], 0], True)
        self.pitch.applyRotation([0, vel[1], 0], True)

        # Stop rotation over the top
        current_rot = self.pitch.localOrientation.to_euler()
        current_rot.y = min(self.config['MAX_ANGLE'], max(self.config['MIN_ANGLE'], current_rot.y))
        self.pitch.localOrientation = current_rot
        
        # Do zooming:
        self.zoom += self.zoom_vel * config.get('MOUSE_ZOOM_SENSITIVITY')
        self.zoom = min(1, max(0, self.zoom))
        self.camera.localPosition.x = utils.lerp(
            self.config['MIN_ZOOM_DIST'],
            self.config['MAX_ZOOM_DIST'],
            self.zoom ** 0.5
        )
        self.camera.fov = utils.lerp(
            self.config['MIN_ZOOM_FOV'],
            self.config['MAX_ZOOM_FOV'],
            self.zoom ** 0.5
        )
