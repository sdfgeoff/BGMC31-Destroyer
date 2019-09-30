import json
import logging
import collections


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
    return a * t + b * (1.0 - t)


def clamp(n, mi, ma):
    return max(mi, min(n, ma))


class BaseClass:
    ID_MAX = 0
    CONFIG_ITEMS = []
    def __init__(self, conf):
        self.log = logging.getLogger(self.__class__.__name__)
        self.id = BaseClass.ID_MAX
        
        self.config = conf
        
        for item in self.CONFIG_ITEMS:
            if item not in self.config:
                raise Exception("Configuration error for {}. Missing item {}".format(self.__class__.__name__, item))
        for item in self.config:
            if item not in self.CONFIG_ITEMS:
                raise Exception("Extra item {} in configuration for {}".format(item, self.__class__.__name__))
                
        BaseClass.ID_MAX += 1
    
    def M(self, message, **kwargs):
        return StructuredMessage(message, i=self.id, cls=self.__class__.__name__, **kwargs)
        
