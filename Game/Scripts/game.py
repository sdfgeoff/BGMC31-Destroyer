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
from gui import hud

import sys
import gc

class Game(utils.BaseClass):
    CONFIG_ITEMS = [
        'HUD_CONFIG',
        'HERO_CONFIG',
        'CAMERA_CONFIG',
        'MOUSE_CONFIG'
    ]
    def __init__(self, scene, conf):
        super().__init__(conf)
        
        logging.basicConfig(level=config.get('SYS/LOG_LEVEL'), format='%(message)s')
        if config.get('SYS/EXIT_ON_ERROR'):
            self.log.info("exit_with_error_enabled")
            sys.excepthook = err
        else:
            sys.excepthook = sys.__excepthook__
        
        for cb in gc.callbacks.copy():
            gc.callbacks.remove(cb)
        gc.callbacks.append(gc_notify)
        
        exit_key = config.get('KEYS/EMERGENCY_ABORT_KEY')
        if exit_key:
            bge.logic.setExitKey(
                bge.events.__dict__[exit_key]
            )
        
        
            
        self.log.info(self.M("init_game"))
        self._event = scheduler.Event(self.update)
        scheduler.add_event(self._event)
        
        bge.logic.addScene('HUD')
        self.scene = scene
        self.hud = None
        self.hud_scene = None
        
        self.hero = ship.Ship(self.scene.objects['HeroShipMain'], self.config['HERO_CONFIG'])
        self.camera = camera.Camera(self.scene.objects['MainCamera'], self.config['CAMERA_CONFIG'])
        self.mouse = mouse.Mouse(self.config['MOUSE_CONFIG'])
        
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
        
    def setup_hud(self):
        self.hud_scene = [s for s in bge.logic.getSceneList() if s.name == "HUD"][0]
        self.hud = hud.HUD(
            self.hud_scene,
            self.config['HUD_CONFIG'],
            self.mouse
        )
        self.hud.set_ship(self.hero)
        self.mouse.scenes = [self.scene, self.hud_scene]
        
    def update(self, delta):
        if self.hud is None:
            self.setup_hud()
            return

        self.mouse.update()
        self.camera.update(self.mouse.drag_delta, self.mouse.scroll_delta)
        
        self.environment.set_player_position(self.hero.vert_center.worldPosition)
        self.environment.set_camera_position(self.camera.camera.worldPosition)
        
        over_hud = self.mouse.get_over(self.hud_scene)
        if over_hud.obj is not None:
            # User is interacting with HUD, not the game world
            return
        
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
                guns = self.hud.weapon_selector.get_selected_guns()
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
    
