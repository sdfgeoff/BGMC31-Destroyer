import bge
import math
import mathutils
import random
import utils
import scheduler
import bullet

from utils import BaseClass

MAX_SHOTS_PER_FRAME = 3

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
        self.time_since_last_shot += delta

        if self.barrel_velocity < self.config['ROUNDS_PER_MINUTE'] / 60 / self.config['BARRELS']:
            self.barrel_velocity += self.config['BARREL_ACCELERATION'] * delta
        else:
            self.barrel_velocity = self.config['ROUNDS_PER_MINUTE'] / 60 / self.config['BARRELS']

        if self.barrel_velocity == 0:
            return
        time_per_shot = 1/(self.barrel_velocity * self.config['BARRELS'])

        counter = MAX_SHOTS_PER_FRAME
        while self.time_since_last_shot > time_per_shot and counter > 0:
            self.time_since_last_shot -= time_per_shot
            counter -= 1

            self.rounds_remaining -= 1

            if 1:#self.time_since_last_shot < 0.025:
                new_flash = self.spawner.scene.addObject(self.config['MUZZLE_FLASH_OBJECT'], self.spawner, 5)
                new_flash.worldTransform = self.spawner.worldTransform

            self.log.debug(self.M("minigun_firing", rounds_remaining=self.rounds_remaining))
            bullet.create_bullet(
                self,
                self.spawner,
                self.time_since_last_shot,
                self.config['PROJECTILE_CONFIG'],
                self.rounds_remaining % self.config['ROUNDS_PER_TRACER'] == 0
            )
        if counter == 0:
            self.log.warn(self.M("shots_per_frame_exceeded", since_last_shot=self.time_since_last_shot, per_shot=time_per_shot, delta=delta))
            self.time_since_last_shot = 0.0

    def __del__(self):
        scheduler.remove_event(self._event)


