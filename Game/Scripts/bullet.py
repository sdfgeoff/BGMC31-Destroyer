import utils
import mathutils
import scheduler


class Bullet(utils.BaseClass):
    CONFIG_ITEMS = [
        'VELOCITY', 
        'TRACER_OBJECT',
        'TRACER_STRETCH_FACTOR'
    ]
    def __init__(self, gun, spawner, time_since_shot, conf, is_tracer):
        super().__init__(conf)
        
        self.log.debug(self.M("create_bullet", config=conf))
        self.gun = gun
        self.spawner = spawner  # TODO: Make not depend on spawner
        if is_tracer:
            self.log.debug(self.M("create_tracer"))
            self.obj = self.spawner.scene.addObject(self.config['TRACER_OBJECT'])
            self.obj.worldOrientation = self.spawner.worldOrientation
        else:
            self.obj = None

        self.collided = False

        self._event = scheduler.Event(self.update)
        scheduler.add_event(self._event)

        self.position = self.spawner.worldPosition.copy()
        self.direction = self.spawner.getAxisVect([0,0,1]).normalized()

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
        self.log.debug(self.M("deleting_bullet"))
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
