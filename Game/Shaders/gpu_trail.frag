<defines>

uniform vec4 color;
uniform float fade_offset;
varying vec2 trail_position;
varying float segment;
varying float percent;
varying float intensity;

void main(void){
    float center = 1.0 - abs(trail_position.y); //pow(1.0 - abs(trail_position.y), 2.0);
    float falloff = pow(clamp(
        1.0 - (trail_position.x - fade_offset / float(NUM_ELEMENTS - 2)
    ), 0.0, 1.0), 2.0);
    
    float multiplier = center * falloff * intensity;
    vec4 col = color * multiplier + pow(multiplier, 2.0);
    gl_FragColor = vec4(col);
}
