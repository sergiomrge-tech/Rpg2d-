shader_type canvas_item;
uniform sampler2D noise_tex : repeat_enable, filter_linear;
uniform vec2 map_px;
uniform float strength = 0.14;
uniform float clouds = 0.12;
void fragment() {
	vec4 c = texture(TEXTURE, UV);
	vec2 wp = UV * map_px;
	float n = texture(noise_tex, wp / 700.0).r;
	float cl = texture(noise_tex, wp / 1400.0 + vec2(TIME * 0.006, TIME * 0.0025)).r;
	c.rgb *= 1.0 + (n - 0.5) * strength * 2.0;
	c.rgb *= 1.0 - smoothstep(0.5, 0.8, cl) * clouds;
	COLOR = c;
}
