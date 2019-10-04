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
        'SPEED_LINEAR',
        'SPEED_TURN',
        'THRUSTER_CONFIG',
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
        
        self.miniguns = GunStorage(minigun.MiniGun(o, self.config["MINIGUN_CONFIG"]) for o in self.obj.childrenRecursive if 'MINIGUN' in o)
        self.railguns = GunStorage(railgun.RailGun(o, self.config["RAILGUN_CONFIG"]) for o in self.obj.childrenRecursive if 'RAILGUN' in o)
        self.thrusters = GunStorage(Thruster(self.hull, o, self.config['THRUSTER_CONFIG']) for o in self.obj.childrenRecursive if 'THRUSTER' in o)
        
        self.hull.removeParent()
        
        self.navigation_target = self.hull.worldPosition
    
    def update(self, delta):
        force = self.config['SPEED_LINEAR'] * self.hull.mass
        torque = self.config['SPEED_TURN'] * self.hull.mass
        
        hull_to_target = (self.hull.worldPosition - self.navigation_target)
        
        angle_delta = hull_to_target.normalized().dot(self.hull.getAxisVect([1,0,0]))
        angle_delta = utils.clamp(angle_delta, -1, 1)
        self.hull.applyTorque([0,0,torque * angle_delta], True)
        
        if hull_to_target.length > 60 or angle_delta < 0.2:
            thrust = hull_to_target.length / 60
            thrust -= self.hull.localLinearVelocity.y * 0.05
            thrust = utils.clamp(thrust, 0, 1)
            self.hull.applyForce([0, force * thrust, 0], True)
        

class Thruster(utils.BaseClass):
    CONFIG_ITEMS = [
        'HOVER_HEIGHT',
        'THRUST_MULTIPLIER',
    ]
    def __init__(self, ship_obj, obj, conf):
        super().__init__(conf)
        self.obj = obj
        self.ship_obj = ship_obj
        self._event = scheduler.Event(self.update)
        scheduler.add_event(self._event)
        
    
    def update(self, delta):
        here = self.obj.worldPosition
        direction = self.obj.getAxisVect([0,0,1])
        there = here + direction * self.config['HOVER_HEIGHT']
        hit_obj, hit_pos, hit_nor = self.ship_obj.rayCast(there, here)
        
        thrust = 0
        if hit_obj != None:
            distance = (hit_pos - here).length
            thrust = -(self.config['HOVER_HEIGHT'] - distance) / self.config['HOVER_HEIGHT']
        
        thrust *= self.ship_obj.mass * self.config['THRUST_MULTIPLIER']
        
        self.ship_obj.applyImpulse(self.obj.worldPosition, thrust * direction * delta)


class GunStorage(list):
	def by_cluster(self):
		clusters = {}
		for gun in self:
			existing = clusters.get(gun.cluster, GunStorage())
			existing.append(gun)
			clusters[gun.cluster] = existing
		return clusters
