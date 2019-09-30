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
        
        self.scene.objects['MainCamera'].setParent(self.hero.vert_center)
        self.scene.objects['LightRig'].setParent(self.hero.vert_center)
        

        
        self.scene.active_camera = self.camera.camera
        bge.render.showMouse(True)
    
    def update(self, delta):
        self.mouse.update()
        self.camera.update(self.mouse.drag_delta, self.mouse.scroll_delta)
        
        if self.mouse.did_click:
            over = self.mouse.get_over(self.scene)
            
            guns = self.hero.miniguns
            if bge.events.LEFTSHIFTKEY in bge.logic.keyboard.active_events:
                guns = self.hero.railguns

            for gun in guns:
                gun.target(over.obj)

        
        


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
    
