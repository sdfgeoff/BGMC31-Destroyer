import utils
import scheduler 
import math
import mathutils
import bullet

class RailGun(utils.BaseClass):
    CONFIG_ITEMS = [
        'NUMBER_ROUNDS',
        'YAW_SPEED',
        'BARREL_CONFIG',
        'MUZZLE_FLASH_OBJECT',
        'PROJECTILE_CONFIG',
        'RELOAD_TIME',
        'SALVO_SEPARATION_TIME',
    ]
    def __init__(self, obj, conf):
        super().__init__(conf)
        self.log.debug(self.M("create_railgun", game_object=obj.name))
        utils.parent_groups(obj)
        objs = obj.childrenRecursive

        self.obj = obj
        self.yaw = [o for o in objs if 'MAIN_YAW' in o][0]
        
        
        
        self.pitch = [o for o in objs if 'PITCH' in o][0]
        self.barrels = [Barrel(o, self.config['BARREL_CONFIG']) for o in objs if 'SPAWNER' in o]

        self._target = None
        
        self.rounds_remaining = self.config['NUMBER_ROUNDS']

        self._event = scheduler.Event(self.update)
        scheduler.add_event(self._event)
        
        self.salvo_number = 0
        self.time_since_last_shot = self.config['RELOAD_TIME']


    def target(self, obj):
        if obj == None:
            self.log.debug(self.M("set_railgun_target", target=None))
        else:
            self.log.debug(self.M("set_railgun_target", target=obj.name))
        self._target = obj


    def update(self, delta):
        self.time_since_last_shot += delta
        
        if self._target != None:
            self._aim_at(self._target.worldPosition, delta, [self._target])  # TODO: motion prediction
    
    def _aim_at(self, target_position, delta, valid_objects):
        turret_to_target_worldspace = target_position - self.yaw.worldPosition
        turret_to_target_turretspace = self.yaw.worldOrientation.inverted() * turret_to_target_worldspace

        yaw_current_angle = self.yaw.localOrientation.to_euler().z
        yaw_delta_angle = -math.atan2(turret_to_target_turretspace.y, turret_to_target_turretspace.x)
        max_yaw_delta = delta * self.config['YAW_SPEED']
        limited_delta_angle = min(max(yaw_delta_angle, -max_yaw_delta), max_yaw_delta)

        self.yaw.localOrientation = [0, 0, yaw_current_angle - limited_delta_angle]

        can_fire = True
        for barrel in self.barrels:
            can_fire &= barrel.aim_at(target_position, delta, valid_objects)
        
        
        if can_fire or self.salvo_number != 0:
            self._fire(delta)


    def _fire(self, delta):
        if self.rounds_remaining == 0:
            return

        if self.salvo_number == 0:
            # First shot in salvo
            time_between = self.config['RELOAD_TIME']
        else:
            time_between = self.config['SALVO_SEPARATION_TIME']


        while self.time_since_last_shot > time_between:
            self.rounds_remaining -= 1
            self.time_since_last_shot = 0  # So that salvos are timed properly
            
            assert self.salvo_number < len(self.barrels)
            barrel = self.barrels[self.salvo_number]
            
            self.salvo_number += 1
            if self.salvo_number > len(self.barrels) - 1:
                self.salvo_number = 0

            if 1:#self.time_since_last_shot < 0.025:
                new_flash = barrel.spawner.scene.addObject(self.config['MUZZLE_FLASH_OBJECT'], barrel.spawner, 5)
                new_flash.worldTransform = barrel.spawner.worldTransform

            self.log.debug(self.M("minigun_firing", rounds_remaining=self.rounds_remaining))
            bullet.Bullet(
                self,
                barrel.spawner,
                self.time_since_last_shot,
                self.config['PROJECTILE_CONFIG'],
                True
            )

    def __del__(self):
        scheduler.remove_event(self._event)


class Barrel(utils.BaseClass):
    CONFIG_ITEMS = [
        'MAX_PITCH',
        'MIN_PITCH',
        'MAX_YAW',
        'MIN_YAW',
        'PITCH_SPEED',
        'YAW_SPEED',
        'RECOIL_DISTANCE',
    ]
    def __init__(self, obj, conf):
        super().__init__(conf)
        self.spawner = obj
        self.barrel = self.up_heirarchy_till_property(self.spawner, 'BARREL')
        self.pitch = self.up_heirarchy_till_property(self.barrel, 'PITCH')
        self.yaw = self.up_heirarchy_till_property(self.pitch, 'BARREL_YAW')
        self.log.info(self.M("barrel_create", spawner=self.spawner.name, barrel=self.barrel.name, pitch=self.pitch.name, yaw=self.yaw.name))
        
    def aim_at(self, target_position, delta, valid_objects):
        spawner_to_target_worldspace = target_position - self.spawner.worldPosition
        turret_to_target_spawnerspace = self.spawner.worldOrientation.inverted() * spawner_to_target_worldspace

        yaw_current_angle = self.yaw.localOrientation.to_euler().z
        yaw_delta_angle = -math.atan2(turret_to_target_spawnerspace.y, turret_to_target_spawnerspace.z)

        yaw_delta_angle = min(max(yaw_delta_angle, -delta * self.config['YAW_SPEED']), delta * self.config['YAW_SPEED'])
        yaw_angle = utils.clamp(
            yaw_current_angle - yaw_delta_angle,
            -self.config['MAX_YAW'],
            self.config['MAX_YAW'],
        )
        
        self.yaw.localOrientation = [0, 0, yaw_angle]

        pitch_current_angle = self.pitch.localOrientation.to_euler().y
        pitch_delta_angle = -math.atan2(turret_to_target_spawnerspace.x, turret_to_target_spawnerspace.z)
        pitch_delta_angle = min(max(pitch_delta_angle, -delta * self.config['PITCH_SPEED']), delta * self.config['PITCH_SPEED'])

        pitch_angle = utils.clamp(
            pitch_current_angle - pitch_delta_angle,
            -self.config['MAX_PITCH'],  # Min max flipped due to negative being tilting upwards
            -self.config['MIN_PITCH']
        )

        self.pitch.localOrientation = [0, pitch_angle, 0]
        
        angle_error = 1.0 - turret_to_target_spawnerspace.normalized().dot(mathutils.Vector([0,0,1]))
        if angle_error > 0.02:
            return False

        rayres = self.spawner.rayCast(target_position, self.spawner.worldPosition)
        if rayres[0] not in valid_objects:
            return False
        return True

    
    def up_heirarchy_till_property(self, obj, prop):
        tip = obj
        while prop not in tip:
            if tip.parent == None:
                raise Exception("Unable to find property in heirarchy")
            tip = tip.parent
        return tip
        
