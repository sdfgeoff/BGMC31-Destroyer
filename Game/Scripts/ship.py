import scheduler
import utils
import minigun
import railgun
import defs
import bge

class Ship(utils.BaseClass):
    CONFIG_ITEMS = [
        'MINIGUN_CONFIG',
        'RAILGUN_CONFIG',
    ]
    def __init__(self, obj, config):
        super().__init__(config)
        self.log.info(self.M("ship_create"))
        utils.parent_groups(obj)
        
        self.obj = obj
        self.hull = [o for o in self.obj.childrenRecursive if 'HULL' in o][0]
        self.vert_center = [o for o in self.hull.childrenRecursive if 'VERT_CENTER' in o][0]
        
        self._event = scheduler.Event(self.update)
        scheduler.add_event(self._event)
        
        self.miniguns = [minigun.MiniGun(o, self.config["MINIGUN_CONFIG"]) for o in self.obj.childrenRecursive if 'MINIGUN' in o]
        self.railguns = [railgun.RailGun(o, self.config["RAILGUN_CONFIG"]) for o in self.obj.childrenRecursive if 'RAILGUN' in o]
        self.thrusters = [Thruster(self.hull, o) for o in self.obj.childrenRecursive if 'THRUSTER' in o]
        
        self.hull.removeParent()
    
    def update(self, delta):
        if bge.events.WKEY in bge.logic.keyboard.active_events:
            self.hull.applyForce([0,200000,0], True)
        if bge.events.SKEY in bge.logic.keyboard.active_events:
            self.hull.applyForce([0,-200000,0], True)
        if bge.events.AKEY in bge.logic.keyboard.active_events:
            self.hull.applyTorque([0,0,2000000], True)
        if bge.events.DKEY in bge.logic.keyboard.active_events:
            self.hull.applyTorque([0,0,-2000000], True)
        

class Thruster:
    RANGE = 20
    def __init__(self, ship_obj, obj):
        self.obj = obj
        self.ship_obj = ship_obj
        self._event = scheduler.Event(self.update)
        scheduler.add_event(self._event)
        
    
    def update(self, delta):
        here = self.obj.worldPosition
        direction = self.obj.getAxisVect([0,0,1])
        there = here + direction * self.RANGE
        hit_obj, hit_pos, hit_nor = self.ship_obj.rayCast(there, here)
        
        thrust = 0
        if hit_obj != None:
            distance = (hit_pos - here).length
            thrust = -(self.RANGE - distance) / self.RANGE
        
        thrust *= self.ship_obj.mass * 10.0
        
        self.ship_obj.applyImpulse(self.obj.worldPosition, thrust * direction * delta)
