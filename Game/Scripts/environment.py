import bge
import utils
import math

class LightRig():
    def __init__(self, obj):
        self.obj = obj
        utils.parent_groups(self.obj)
    
    def set_position(self, position):
        self.obj.worldPosition.xy = position.xy


class TerrainRig():
    def __init__(self, obj):
        self.obj = obj
        utils.parent_groups(self.obj)
        self.tiles = [_Tile(o) for o in self.obj.childrenRecursive if 'TERRAIN_TILES' in o]
        
    def set_position(self, position):
        for tile in self.tiles:
            tile.set_cam_position(position)


class _Tile:
    def __init__(self, obj):
        self.obj = obj
        self.original_location = self.obj.worldPosition.copy()
        self.obj.removeParent()
        
    def set_cam_position(self, position):
        WORLD_SIZE = 4000
        dp = position - self.original_location
        self.obj.worldPosition.x = round(dp.x/WORLD_SIZE) * WORLD_SIZE + self.original_location.x
        self.obj.worldPosition.y = round(dp.y/WORLD_SIZE) * WORLD_SIZE + self.original_location.y


class SkyboxRig():
    def __init__(self, obj):
        self.obj = obj
        utils.parent_groups(self.obj)
    
    def set_position(self, position):
        self.obj.worldPosition.xy = position.xy



class Environment:
    def __init__(self, light_obj, terrain_obj, skybox_obj):
        self.light = LightRig(light_obj)
        self.terrain = TerrainRig(terrain_obj)
        self.skybox = SkyboxRig(skybox_obj)
        
    def set_player_position(self, position):
        self.light.set_position(position)
        
    def set_camera_position(self, position):
        self.skybox.set_position(position)
        self.terrain.set_position(position)
