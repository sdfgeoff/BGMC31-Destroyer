import scheduler
import utils
import logging
import defs
import bge
import config
import time

import ship
import camera
import mouse
import environment

import sys
import gc

class Game(utils.BaseClass):
    CONFIG_ITEMS = [
    ]
    def __init__(self, scene, conf):
        super().__init__(conf)
        
        logging.basicConfig(level=config.get('LOG_LEVEL'), format='%(message)s')
        if config.get('EXIT_ON_ERROR'):
            self.log.info("exit_with_error_enabled")
            sys.excepthook = err
        else:
            sys.excepthook = sys.__excepthook__
        
        for cb in gc.callbacks.copy():
            gc.callbacks.remove(cb)
        gc.callbacks.append(gc_notify)
        
        
            
        self.log.info(self.M("init_game"))
        self._event = scheduler.Event(self.update)
        scheduler.add_event(self._event)
        
        self.scene = scene
        self.is_setup = False
        
        self.hero = ship.Ship(self.scene.objects['HeroShipMain'], defs.HERO_CONFIG)
        self.camera = camera.Camera(self.scene.objects['MainCamera'], defs.CAMERA_CONFIG)
        self.mouse = mouse.Mouse()
        self.mouse.scenes = [self.scene]
        
        self.environment = environment.Environment(
            self.scene.objects['LightRig'],
            self.scene.objects['TerrainTiles'],
            self.scene.objects['SkySphere'],
        )
        
        self.scene.objects['MainCamera'].setParent(self.hero.vert_center)
        self.camera.set_view(0.5, -0.5, 0.2)
        
        self.navigation_waypoints = []
        
        self.scene.active_camera = self.camera.camera
        bge.render.showMouse(True)
    
    def update(self, delta):
        self.mouse.update()
        self.camera.update(self.mouse.drag_delta, self.mouse.scroll_delta)
        
        self.environment.set_player_position(self.hero.vert_center.worldPosition)
        self.environment.set_camera_position(self.camera.camera.worldPosition)
        
        over = self.mouse.get_over(self.scene)
        
        if self.mouse.did_click and over.obj is not None:
            if 'TERRAIN_TILES' in over.obj:
                if bge.events.LEFTSHIFTKEY not in bge.logic.keyboard.active_events:
                    for waypoint in self.navigation_waypoints:
                        waypoint.endObject()
                    self.navigation_waypoints.clear()
                    
                waypoint = self.scene.addObject("HeroWaypoint")
                waypoint.worldOrientation = [0,0,0]
                waypoint.worldPosition = over.position
                self.navigation_waypoints.append(waypoint)

                    
            else:
                target = over.obj
                guns = self.hero.miniguns
                if bge.events.LEFTSHIFTKEY in bge.logic.keyboard.active_events:
                    guns = self.hero.railguns
                if bge.events.LEFTCTRLKEY in bge.logic.keyboard.active_events:
                    target = None

                for gun in guns:
                    gun.target(target)
        
        
        if self.navigation_waypoints:
            old_waypoint = self.navigation_waypoints[0]
            self.hero.navigation_target = old_waypoint.worldPosition.copy()
            if (self.hero.hull.worldPosition.xy - old_waypoint.worldPosition.xy).length < 40:
                old_waypoint.endObject()
                self.navigation_waypoints = self.navigation_waypoints[1:]
            

        
        


def init(cont):
    if 'GAME' not in cont.owner:
        cont.owner['GAME'] = Game(cont.owner.scene, defs.MAIN_CONFIG)


def err(exctype, value, traceback):
    bge.logic.endGame()
    sys.__excepthook__(exctype, value, traceback)


gc_time = 0

def gc_notify(phase, info):
    global gc_time
    if phase == 'start':
        gc_time = time.time()
    else:
        logging.warn("Garbage Collection Duration: %f, %s", time.time() - gc_time, str(info))
    
