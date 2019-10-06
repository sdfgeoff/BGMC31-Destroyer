import json
import logging
import collections
import os
import bge


# Path to the root of this project
ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))


# Helpers for handling ray casts from BGE
RayHitUVResult = collections.namedtuple('RayHitUVResult', ['obj', 'position', 'normal', 'polygon', 'uv'])
RayHitPolyResult = collections.namedtuple('RayHitUVResult', ['obj', 'position', 'normal', 'polygon'])
RayHitResult = collections.namedtuple('RayHitUVResult', ['obj', 'position', 'normal'])


class StructuredMessage(object):
    """ Unify logging output format """
    def __init__(self, message, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return '%s >>> %s' % (self.message, json.dumps(self.kwargs))



def parent_groups(obj):
    """ Attached grouped objects to an object """
    for obj in [obj] + list(obj.childrenRecursive):
        if obj.groupMembers is not None:
            for member in obj.groupMembers:
                if member.parent == None:
                    member.setParent(member.groupObject)


def lerp(a, b, t):
    """ Linear interpolate. Nice and simple """
    return a * t + b * (1.0 - t)


def clamp(n, mi, ma):
    """ Makes sure a number is between a min and max bound """
    return max(mi, min(n, ma))


class BaseClass:
    """ A generic class used a lot through this project, mostly
    for it's ability to do some checks on config dictionaries.
    
    Also contains a logger and a structured message creator """
    ID_MAX = 0
    CONFIG_ITEMS = []
    def __init__(self, conf):
        self.log = logging.getLogger(self.__class__.__name__)
        self.id = BaseClass.ID_MAX
        BaseClass.ID_MAX += 1
        
        self.default_message_data = {
			'i': self.id,
			'cls': self.__class__.__name__
        }
        
        self.load_config(conf)
    
    def M(self, message, **kwargs):
        return StructuredMessage(message, **self.default_message_data, **kwargs)
        
    def load_config(self, conf):
        self.config = conf
        
        for item in self.CONFIG_ITEMS:
            if item not in self.config:
                raise Exception("Configuration error for {}. Missing item {}".format(self.__class__.__name__, item))
        for item in self.config:
            if item not in self.CONFIG_ITEMS:
                raise Exception("Extra item {} in configuration for {}".format(item, self.__class__.__name__))
                

def fix_text(obj):
    '''Compute a font object's ideal resolution assuming an orthographic camera'''
    # Defined in blender source: an object 1 unit high with a resultion of 1 will have 100px
    return
    
    # ONLY FOR UPBGE:
    
    default_px_per_bu = 100  

    window_width = bge.render.getWindowWidth()

    # Measure the size of the font object (height)
    text = obj.text
    obj.text = '|'
    obj_height = obj.dimensions[1]
    obj.text = text
    
    if not obj.scene.active_camera.perspective:
        view_width = obj.scene.active_camera.ortho_scale
    else:
        raise Exception("Only for orthographic cameras at the moment")


    pixel_ratio = window_width / view_width # pixels / bu
    obj_pixels = pixel_ratio * obj_height


    obj.resolution = obj_pixels / obj_height / default_px_per_bu
