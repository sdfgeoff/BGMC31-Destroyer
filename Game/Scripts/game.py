import scheduler
import utils
import logging
import defs
import bge
import config

import ship
import camera
import mouse

import sys

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
            for gun in self.hero.miniguns:
                gun.target(over.obj)
            
        


def init(cont):
    if 'GAME' not in cont.owner:
        cont.owner['GAME'] = Game(cont.owner.scene, defs.MAIN_CONFIG)


def err(exctype, value, traceback):
    bge.logic.endGame()
    sys.__excepthook__(exctype, value, traceback)


