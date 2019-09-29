import bge
import math
import mathutils
import random
import utils
import scheduler

from utils import BaseClass



class MiniGun(BaseClass):
    """ A minigun with rotation barrels """
    CONFIG_ITEMS = [
        "YAW_SPEED",
        "PITCH_SPEED",
        "ROUNDS_PER_MINUTE",
        "BARREL_ACCELERATION",
        "BARREL_DECELERATION",
        "BARRELS",
        "MUZZLE_FLASH_OBJECT",
        "PROJECTILE_CONFIG",
        "NUMBER_ROUNDS",
        "ROUNDS_PER_TRACER"
    ]
    def __init__(self, obj, config):
        super().__init__(config)
        self.log.debug(self.M("create_minigun", game_object=obj.name))
        utils.parent_groups(obj)
        objs = obj.childrenRecursive

        self.obj = obj
        self.yaw = [o for o in objs if 'YAW' in o][0]
        self.pitch = [o for o in objs if 'PITCH' in o][0]
        self.barrel = [o for o in objs if 'BARREL' in o][0]
        self.spawner = [o for o in objs if 'SPAWNER' in o][0]

        self._target = None
        self.barrel_angle = 0.0
        self.barrel_velocity = 0.0
        self.time_since_last_shot = 0.0

        self.rounds_remaining = self.config['NUMBER_ROUNDS']

        self._event = scheduler.Event(self.update)
        scheduler.add_event(self._event)

    def target(self, obj):
        if obj == None:
            self.log.debug(self.M("set_minigun_target", target=None))
        else:
            self.log.debug(self.M("set_minigun_target", target=obj.name))
        self._target = obj

    def update(self, delta):
        
        if self._target != None:
            self._aim_at(self._target.worldPosition, delta, [self._target])  # TODO: motion prediction
    
    def _aim_at(self, target_position, delta, valid_objects):
        spawner_to_target_worldspace = target_position - self.spawner.worldPosition
        turret_to_target_spawnerspace = self.spawner.worldOrientation.inverted() * spawner_to_target_worldspace


        yaw_current_angle = self.yaw.localOrientation.to_euler().z
        yaw_delta_angle = -math.atan2(turret_to_target_spawnerspace.y, turret_to_target_spawnerspace.z)

        yaw_delta_angle = min(max(yaw_delta_angle, -delta * self.config['YAW_SPEED']), delta * self.config['YAW_SPEED'])

        self.yaw.localOrientation = [0, 0, yaw_current_angle - yaw_delta_angle]


        pitch_current_angle = self.pitch.localOrientation.to_euler().y
        pitch_delta_angle = -math.atan2(turret_to_target_spawnerspace.x, turret_to_target_spawnerspace.z)
        pitch_delta_angle = min(max(pitch_delta_angle, -delta * self.config['PITCH_SPEED']), delta * self.config['PITCH_SPEED'])

        self.pitch.localOrientation = [0, pitch_current_angle - pitch_delta_angle, 0]

        self.barrel_angle += self.barrel_velocity * delta * 2 * math.pi
        self.barrel.localOrientation = [0,0,self.barrel_angle]

        rayres = self.spawner.rayCast(target_position, self.spawner.worldPosition)
        if rayres[0] not in valid_objects:
            return

        angle_error = 1.0 - turret_to_target_spawnerspace.normalized().dot(mathutils.Vector([0,0,1]))
        if angle_error < 0.02:
            self._fire(delta)
        else:
            if self.barrel_velocity > 0:
                self.barrel_velocity -= self.config['BARREL_DECELERATION'] * delta
            else:
                self.barrel_velocity = 0.0


    def _fire(self, delta):
        if self.rounds_remaining == 0:
            return


        if self.barrel_velocity < self.config['ROUNDS_PER_MINUTE'] / 60 / self.config['BARRELS']:
            self.barrel_velocity += self.config['BARREL_ACCELERATION'] * delta
        else:
            self.barrel_velocity = self.config['ROUNDS_PER_MINUTE'] / 60 / self.config['BARRELS']

        if self.barrel_velocity == 0:
            return
        time_per_shot = 1/(self.barrel_velocity * 6)
        self.time_since_last_shot += delta


        while self.time_since_last_shot > time_per_shot:
            self.time_since_last_shot -= time_per_shot

            self.rounds_remaining -= 1

            if 1:#self.time_since_last_shot < 0.025:
                new_flash = self.spawner.scene.addObject(self.config['MUZZLE_FLASH_OBJECT'], self.spawner, 5)
                new_flash.worldTransform = self.spawner.worldTransform

            self.log.debug(self.M("minigun_firing", rounds_remaining=self.rounds_remaining))
            MinigunBullet(
                self,
                self.spawner,
                self.time_since_last_shot,
                self.config['PROJECTILE_CONFIG'],
                self.rounds_remaining % self.config['ROUNDS_PER_TRACER'] == 0
            )

    def __del__(self):
        scheduler.remove_event(self._event)



class MinigunBullet(BaseClass):
    CONFIG_ITEMS = ['VELOCITY', 'TRACER_OBJECT']
    def __init__(self, gun, spawner, time_since_shot, config, is_tracer):
        super().__init__(config)
        
        self.log.debug(self.M("create_minigun_bullet", is_tracer=is_tracer))

        self.gun = gun
        self.spawner = spawner  # TODO: Make not depend on spawner
        if is_tracer:
            self.obj = self.spawner.scene.addObject(self.config['TRACER_OBJECT'])
            self.obj.worldOrientation = self.spawner.worldOrientation
        else:
            self.obj = None

        self.collided = False

        self._event = scheduler.Event(self.update)
        scheduler.add_event(self._event)

        self.position = self.spawner.worldPosition.copy()
        self.direction = self.spawner.getAxisVect([0,0,1])

        self._move(
            self.position,
            self.position + self.direction * self.config['VELOCITY'] * time_since_shot
        )
        if self.should_remove():
            self.do_remove()

    def update(self, delta):
        """ Moves the projectile, checks if it hit things etc. """
        assert not self.collided

        self._move(
            self.position,
            self.position + self.direction * self.config['VELOCITY'] * delta
        )

        if self.should_remove():
            self.do_remove()

    def _move(self, from_position, to_position):
        """ Moves the projectile, using a raycast to check it didn't hit
        anything """
        obj, hit_pos, hit_nor = self.spawner.rayCast(to_position, from_position)
        self.collided = obj != None

        if not self.collided:
            self.position = to_position
        else:
            self.position = hit_pos

        if self.obj != None:
            self.obj.worldPosition = self.position

    def do_remove(self):
        """ Removes the object and cleans up """
        self.log.debug(self.M("deleting_minigun_bullet"))
        if self.obj is not None:
            self.obj.endObject()
        scheduler.remove_event(self._event)

    def should_remove(self):
        """ Checks if this object should be removed (eg timed out or hit
        something) or if it still needs to exist """
        remove = False
        remove |= (self.spawner.worldPosition - self.position).length > 2000
        remove |= self.collided
        return remove

