shader_type canvas_item;
// Ground shadow of an upright sprite: the sprite is flattened onto the ground and sheared away from the light.
// The node origin is the object's feet, so VERTEX.y < 0 means "height above the ground".
uniform float shear = 0.5;      // horizontal travel per unit of height (sign = direction away from the sun)
uniform float flat_k = 0.28;    // ground length per unit of height (longer when the sun is low)
uniform float strength = 0.34;
uniform vec3 tint = vec3(0.04, 0.05, 0.11);

void vertex() {
	VERTEX = vec2(VERTEX.x - VERTEX.y * shear, -VERTEX.y * flat_k);
}

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	// shadows get softer with distance from the object's base
	COLOR = vec4(tint, c.a * strength * (0.4 + 0.6 * UV.y));
}
