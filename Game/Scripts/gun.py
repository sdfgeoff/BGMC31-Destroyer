import utils
import bullet
import sounds


class Gun(utils.BaseClass):
    CONFIG_ITEMS = [
        'NUMBER_ROUNDS',
        'MUZZLE_FLASH_OBJECT',
        'PROJECTILE_CONFIG',
        'GUNSHOT_SOUND',
    ]
    def __init__(self, obj, conf):
        self.cluster = obj['CLUSTER']
        self.name = obj['NAME']
        self.number = obj['ID']
        
        super().__init__(conf)
        self._rounds_remaining = conf['NUMBER_ROUNDS']

    def remove_ammo(self):
        """ Attempts a shot and removes the ammunition. Returns True
        if there was enough ammo for the shot, False if there wasn't
        """
        assert self._rounds_remaining >= 0
        if self._rounds_remaining > 0:
            self._rounds_remaining -= 1
            return True
        return False
    
    def has_ammo(self):
        """ Checks if the gun can fire without removing the ammunition
        from stores. Call "remove_ammo" immediately before firing the
        gun """
        return self._rounds_remaining > 0
    
    def ammo_remaining(self):
        return self._rounds_remaining

    def ammo_maximum(self):
        return self.config['NUMBER_ROUNDS']
        
    def create_bullet(self, spawner, time_since_shot, tracer):
        self.log.debug(self.M("gun_firing"))
        
        new_flash = spawner.scene.addObject(self.config['MUZZLE_FLASH_OBJECT'], spawner, 5)
        new_flash.worldTransform = spawner.worldTransform
        
        sounds.play_effect_single(
            self.config["GUNSHOT_SOUND"],
            spawner.worldPosition,
            time_since_shot,
            0.1,
            0.3
        )

        bullet.create_bullet(
            self,
            spawner,
            time_since_shot,
            self.config['PROJECTILE_CONFIG'],
            tracer
        )
        
        
