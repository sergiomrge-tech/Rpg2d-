shader_type canvas_item;
// Mirror image of a standing prop, drawn only where the water mask says there is water (mask atlas = 1/4-res map of the whole level).
uniform sampler2D mask : filter_linear;
uniform vec2 world_px = vec2(4096.0);
uniform float strength = 0.62;
uniform vec3 tint = vec3(0.55, 0.78, 0.95);

varying vec2 wpos;

void vertex() {
	VERTEX.x += sin(VERTEX.y * 0.13 + TIME * 1.7 + MODEL_MATRIX[3].x * 0.01) * 3.2;
	wpos = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

void fragment() {
	float inside = texture(mask, wpos / world_px).r;
	float w = smoothstep(0.55, 0.7, inside);
	vec4 c = texture(TEXTURE, UV);
	float fade = 1.0 - smoothstep(0.0, 0.9, 1.0 - UV.y);
	float ripple = 0.85 + 0.15 * sin(wpos.y * 0.35 + TIME * 2.4 + wpos.x * 0.05);
	COLOR = vec4(mix(c.rgb, tint * 0.6, 0.55), c.a * w * strength * ripple * (0.35 + 0.65 * fade));
}
