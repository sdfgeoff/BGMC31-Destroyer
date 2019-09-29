import bge
import mathutils
import utils


class Mouse(object):
    '''Contains some functions to check if the mouse has moved and by how
    much'''
    def __init__(self):
        self.click_start_position = None

        # These are publically acessible variables that can be queried
        # to find out about what the mouse is doing
        self.did_click = False             # True if the mouse has clicked
        self.drag_delta = None             # Motion in last frame
        self.drag_vector = None            # Total motion from start
        self.scroll_delta = 0

        # To calculate the drag info we need to store the previous positions
        self._prev_pos = None              # Position in the last frame
        self._click_start_position = None  # Where the click started

        # Cache what the mouse is over because it is computationally
        # expensive so we should only run it once
        self._over_cache = dict()
        self.scenes = list()

    def update(self):
        '''Update the status of the mouse'''
        self._update_clicking()
        self._update_over()
        self._update_scroll()
        
    def _update_scroll(self):
        if bge.events.WHEELUPMOUSE in bge.logic.mouse.active_events:
            self.scroll_delta = 1.0
        elif bge.events.WHEELDOWNMOUSE in bge.logic.mouse.active_events:
            self.scroll_delta = -1.0
        else:
            self.scroll_delta = 0.0

    def _update_clicking(self):
        '''Updates the information on the mouses click status'''
        click_status = bge.logic.mouse.events[bge.events.LEFTMOUSE]
        mouse_position = mathutils.Vector(bge.logic.mouse.position)

        if click_status == bge.logic.KX_INPUT_JUST_ACTIVATED:
            self._click_start_position = mouse_position
            self._prev_pos = mouse_position

        elif click_status == bge.logic.KX_INPUT_ACTIVE:
            self.drag_vector = self._click_start_position - mouse_position
            self.drag_delta = self._prev_pos - mouse_position
            self._prev_pos = mouse_position

            # Stop accidental modification when you read values
            self.drag_delta.freeze()
            self.drag_vector.freeze()

        elif click_status == bge.logic.KX_INPUT_JUST_RELEASED:
            # If the mouse hasn't moved too far since it was clicked, then
            # register this as a click:
            if self.drag_vector != None:
                self.did_click = self.drag_vector.length < 0.1
            else:
                # Single frame click/release
                self.did_click = True

        else:
            self.did_click = False
            self.drag_delta = None
            self.drag_vector = None

    def _update_over(self):
        '''Updates what object the mouse is "over" in the cache'''
        for scene in self.scenes:
            cam = scene.active_camera
            pos = bge.logic.mouse.position
            
            if cam.perspective:
                here = cam.worldPosition - cam.getScreenVect(pos[0], pos[1]) * cam.near
                there = cam.worldPosition - cam.getScreenVect(pos[0], pos[1]) * cam.far
            else:
                aspect = bge.render.getWindowHeight() / bge.render.getWindowWidth()
                offset = mathutils.Vector([
                    (pos[0] - 0.5) * cam.ortho_scale, 
                    -(pos[1] - 0.5) * cam.ortho_scale * aspect,
                    0
                ])
                offset = cam.worldOrientation * offset
                here = cam.worldPosition + offset - cam.getAxisVect([0,0,1]) * cam.near
                there = cam.worldPosition + offset - cam.getAxisVect([0,0,1]) * cam.far
                print(here, there)

            self._over_cache[scene.name] = utils.RayHitUVResult(*cam.rayCast(there, here, cam.far, '', 1, 0, 2))

    def get_over(self, scene):
        '''Returns the object the mouse is over - in the specific scene'''
        return self._over_cache.get(scene.name)
