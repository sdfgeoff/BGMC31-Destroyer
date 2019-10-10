#version 120
<defines>

<uniforms>


uniform mat4 view_matrix;
uniform mat4 inv_view_matrix;
uniform float width;

uniform float curviness = 0.25 * 0.866;

varying vec4 color;
varying vec3 varyingNormalDirection;
varying vec2 trail_position;
varying float segment;
varying float percent;
varying float intensity;

void main(){
    //Texture map:
    gl_TexCoord[0] = gl_MultiTexCoord0;
    
    
    trail_position = gl_MultiTexCoord0.xy;
    trail_position.y = (0.5 - trail_position.y) * 2.0;

    vec4 a[NUM_ELEMENTS] = <array>;
    float pos = trail_position.x * (NUM_ELEMENTS - 3);
    
    int index_here = int(floor(pos));
    vec4 p1 = a[index_here];
    vec4 p2 = a[index_here+1];    
    vec4 p3 = a[index_here+2];
    vec4 p4 = a[index_here+3];
    
    // The current vert lies between p2 and p3 as determined
    // by the percentage:
    percent = mod(pos, 1.0);
    segment = float(index_here);
    intensity = mix(p2.w, p3.w, percent);

    // Construct bezier points using the four points and Lucas'
    // magic method
    vec3 handle_neg = (p3 - p1).xyz;
    vec3 handle_pos = (p2 - p4).xyz;
    vec3 b1 = p2.xyz;
    vec3 b2 = p2.xyz + handle_neg * curviness;
    vec3 b3 = p3.xyz + handle_pos * curviness;
    vec3 b4 = p3.xyz;
    
    // Sample the bezier point where we are
    vec3 i3 = (
        pow((1.0 - percent), 3.0) * b1 +
        3 * pow((1.0 - percent), 2.0) * percent * b2 +
        3 * (1.0 - percent) * pow(percent, 2.0) * b3 +
        pow(percent, 3.0) * b4
    );
        
    
    //~ // Comput the trail so that it faces the camera
    vec3 vect_to_camera = inv_view_matrix[2].xyz;
    vec3 trail_direction = normalize(b4 - b1) * trail_position.y * width;
    vec3 offset = cross(trail_direction, vect_to_camera);
    
    vec3 vert_position = i3 + offset;
    //vert_position.z = percent;
    
    gl_Position = (gl_ProjectionMatrix * view_matrix) * vec4(vert_position, 1.0);
}
