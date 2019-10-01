import utils
import mathutils
import scheduler
import defs







def create_bullet(gun, spawner, time_since_shot, conf, is_tracer):
    bullet_manager.create_bullet(
        gun,
        spawner,
        time_since_shot,
        conf,
        is_tracer
    )
    





class _Bullet(utils.BaseClass):
    CONFIG_ITEMS = [
        'VELOCITY', 
        'TRACER_OBJECT',
        'TRACER_STRETCH_FACTOR'
    ]
    __slots__ = ['collided', 'position', 'direction', 'gun', 'spawner', 'config']
    def __init__(self):
        self.collided = False
        
        self.position = mathutils.Vector()
        self.direction = mathutils.Vector()
        self.gun = None
        self.spawner = None


    def spawn(self, gun, spawner, time_since_shot, conf, is_tracer):
        self.load_config(conf)
        
        self.gun = gun
        self.spawner = spawner  # TODO: Make not depend on spawner past init time
        
        if is_tracer:
            self.obj = self.spawner.scene.addObject(self.config['TRACER_OBJECT'])
            self.obj.worldOrientation = self.spawner.worldOrientation
        else:
            self.obj = None
        
        self.position = self.spawner.worldPosition.copy()
        self.direction = self.spawner.getAxisVect([0,0,1]).normalized()


        self._move(
            self.position,
            self.position + self.direction * self.config['VELOCITY'] * time_since_shot
        )
        if self.should_remove():
            self.do_remove()
            return False
        return True
    

    def update(self, delta):
        """ Moves the projectile, checks if it hit things etc. """
        assert not self.collided

        self._move(
            self.position,
            self.position + self.direction * self.config['VELOCITY'] * delta
        )

        if self.should_remove():
            self.do_remove()
            return False
        return True

    def _move(self, from_position, to_position):
        """ Moves the projectile, using a raycast to check it didn't hit
        anything """
        obj, hit_pos, hit_nor = self.spawner.rayCast(to_position, from_position)
        self.collided = obj != None

        if not self.collided:
            end = to_position
        else:
            end = hit_pos

        self.position = end

        if self.obj != None:
            dist = (from_position - end).length
            self.obj.localScale.z = self.config['TRACER_STRETCH_FACTOR'] * dist
            self.obj.worldPosition = self.position

    def do_remove(self):
        """ Removes the object and cleans up """
        if self.obj is not None:
            self.obj.endObject()

    def should_remove(self):
        """ Checks if this object should be removed (eg timed out or hit
        something) or if it still needs to exist """
        remove = False
        remove |= (self.spawner.worldPosition - self.position).length > 2000
        remove |= self.collided
        return remove


class BulletManager(utils.BaseClass):
    CONFIG_ITEMS = [
        'BULLET_LIMIT'
    ]
    def __init__(self, conf):
        super().__init__(conf)
        self._event = scheduler.Event(self.update)
        scheduler.add_event(self._event)
        
        self.alive_bullets = set()
        self.dead_bullets = set()
        
        for _i in range(self.config['BULLET_LIMIT']):
            self.dead_bullets.add(_Bullet())
    
    
    def update(self, delta):
        newly_dead = set()
        for bullet in self.alive_bullets:
            if not bullet.update(delta):
                newly_dead.add(bullet)
        
        for bullet in newly_dead:
            self.alive_bullets.remove(bullet)
            self.dead_bullets.add(bullet)
    
    
    def create_bullet(self, gun, spawner, time_since_shot, conf, is_tracer):
        if self.dead_bullets:
            bullet = self.dead_bullets.pop()
            if bullet.spawn(gun, spawner, time_since_shot, conf, is_tracer):
                self.alive_bullets.add(bullet)
            else:
                self.dead_bullets.add(bullet)
        else:
            self.log.warn(self.M("out_of_bullets"))
        


bullet_manager = BulletManager(defs.BULLET_MANAGER_CONFIG)
