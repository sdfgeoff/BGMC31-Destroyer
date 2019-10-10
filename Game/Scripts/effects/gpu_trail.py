import bge
import mathutils
import utils
import collections
import os
import scheduler

NUM_SEGMENTS = 24

FRAGMENT_SHADER_TEMPLATE = open(os.path.join(utils.ROOT_PATH, 'Shaders', 'gpu_trail.frag')).read()
VERTEX_SHADER_TEMPLATE = open(os.path.join(utils.ROOT_PATH, 'Shaders', 'gpu_trail.vert')).read()



class _GpuTrail(utils.BaseClass):
    def __init__(self, mesh_obj):
        super().__init__({})
        self.owner = None
        self.mesh_obj = None
        
        self._hidden_mesh_obj = mesh_obj
        self.mesh_obj = None
        self._shader = self.create_shader(self._hidden_mesh_obj)
        self.intensity = 0.0
        
        self._positions = []
        self._time_per_segment = 0.0
        self._time_since_emit = 0.0
        
        # Tee position on the previous frame is used to compute
        # the velocity for the trails
        # The velocity is used to align the start of the trail
        self._previous_position = mathutils.Vector([0,0,0])
        self._velocity = mathutils.Vector([0,0,0])
        
   
    def attach(self, owner, width, trail_length_seconds, color):
        self.mesh_obj = owner.scene.addObject(self._hidden_mesh_obj)
        self.mesh_obj.worldPosition = owner.worldPosition
        self.mesh_obj.setParent(owner)

        self._shader.setUniform1f('width', width)
        self._shader.setUniform4f('color', color[0], color[1], color[2], color[3])
        self._time_per_segment = trail_length_seconds / NUM_SEGMENTS
        self.owner = owner
        self.clear()
        
    
    def clear(self):
        self._time_since_emit = 0.0
        self._velocity = mathutils.Vector([0,0,0])
        cur_pos = self.owner.worldPosition
        self._previous_position.xyz = cur_pos.xyz
        self._positions = collections.deque([
            mathutils.Vector([cur_pos.x, cur_pos.y, cur_pos.z, 0])
            for _ in range(NUM_SEGMENTS - 2)
        ])
        self._set_all()
        
        
    def create_shader(self, mesh_object):
        mesh = mesh_object.meshes[0]
        assert len(mesh.materials) == 1
        material = mesh.materials[0]
        shader = material.getShader()
        assert shader is not None, "Does not have material???"
        assert not shader.isValid(), "Already has a custom shader???"            
        shader.setSource(*_generate_shader(NUM_SEGMENTS), 1)
        assert shader.isValid()
        return shader

    
    def set_intensity(self, intensity):
        """ Sets the intensity with which to emit subsequent sections
        of trail """
        self.intensity = intensity
        
    def update(self, delta):
        """ Uses self.owner to set the positions etc. """
        self._time_since_emit += delta
        
        self._velocity = self._previous_position - self.owner.worldPosition
        self._previous_position.xyz = self.owner.worldPosition.xyz
        
    def draw(self):
        """ Send data to the GPU """
        cur_pos = self.owner.worldPosition
        
        if self._time_since_emit > self._time_per_segment:
            # shuffle everything
            self._positions.rotate(1)
            self._positions[0].xyz = cur_pos.xyz
            self._positions[0].w = self.intensity
            
            self._time_since_emit = 0.0
            self._set_all()
            
            
        inv_view_matrix = self.owner.scene.active_camera.worldTransform
        self._shader.setUniformMatrix4('view_matrix', inv_view_matrix.inverted())
        self._shader.setUniformMatrix4('inv_view_matrix', inv_view_matrix)
        self._shader.setUniform1f('fade_offset', 1.0 - self._time_since_emit / self._time_per_segment)
        
        heading = cur_pos + self._velocity * (self._time_per_segment + self._time_since_emit)
        self._shader.setUniform4f('t0', cur_pos.x, cur_pos.y, cur_pos.z, self.intensity)
        self._shader.setUniform4f('t1', heading.x, heading.y, heading.z, self.intensity)
    
    def _set_all(self):
        """ Update all the positions in the shader """
        for i, pos in enumerate(self._positions):
            self._shader.setUniform4f('t'+str(i+2), pos.x, pos.y, pos.z, pos.w)



def _generate_shader(num_points):
    """ Fills out the shader templates for the correct number of points in the trail """
    fragment_shader = FRAGMENT_SHADER_TEMPLATE
    fragment_shader = fragment_shader.replace(
        "<defines>", "#define NUM_ELEMENTS {}".format(num_points)
    )
    
    vertex_shader = VERTEX_SHADER_TEMPLATE
    vertex_shader = vertex_shader.replace(
        "<defines>", "#define NUM_ELEMENTS {}".format(num_points)
    )
    vertex_shader = vertex_shader.replace(
        "<uniforms>", '\n'.join(
            ["uniform vec4 t{};".format(i) for i in range(num_points)]
        )
    )
    vertex_shader = vertex_shader.replace(
        "<array>", "vec4[](" + 
        ', '.join(["t{}".format(i) for i in range(num_points)]) +
        ");"
    )
    return [vertex_shader, fragment_shader]


class TrailManager(utils.BaseClass):
    def __init__(self, scene):
        super().__init__({})
        self.scene = scene
        self.unused_trails = [_GpuTrail(t) for t in self.scene.objectsInactive if '__TRAIL_INSTANCE__' in t]
        self.used_trails = []

        self._event = scheduler.Event(self.update)
        scheduler.add_event(self._event)
        self.scene.pre_draw.append(self._draw)
        
    def attach_trail(self, owner, width, trail_length_seconds, color):
        """ Attaches a trail to an object and returns a handle that
        can be used to control the trail """
        if self.unused_trails:
            trail = self.unused_trails.pop()
            trail.attach(owner, width, trail_length_seconds, color)
            self.used_trails.append(trail)
            return trail
        return None
        
    
    def _draw(self):
        for trail in self.used_trails:
            trail.draw()
        
    def update(self, delta):
        for trail in self.used_trails:
            trail.update(delta)

trail_manager = TrailManager(bge.logic.getCurrentScene())
