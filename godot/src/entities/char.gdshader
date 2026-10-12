shader_type canvas_item;
uniform float flash : hint_range(0.0, 1.0) = 0.0;
uniform vec4 flash_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform vec4 tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform vec4 add_color : source_color = vec4(0.0, 0.0, 0.0, 0.0);
uniform float dissolve : hint_range(0.0, 1.0) = 0.0;
uniform vec4 edge_color : source_color = vec4(1.0, 0.6, 0.2, 1.0);
uniform float outline : hint_range(0.0, 1.0) = 0.0;
uniform vec4 outline_color : source_color = vec4(1.0, 0.95, 0.5, 1.0);

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	bool edge = false;
	if (outline > 0.0 && c.a < 0.1) {
		vec2 px = TEXTURE_PIXEL_SIZE;
		float a = texture(TEXTURE, UV + vec2(px.x, 0.0)).a + texture(TEXTURE, UV - vec2(px.x, 0.0)).a + texture(TEXTURE, UV + vec2(0.0, px.y)).a + texture(TEXTURE, UV - vec2(0.0, px.y)).a;
		if (a > 0.1) {
			edge = true;
		}
	}
	if (edge) {
		COLOR = vec4(outline_color.rgb, outline);
	} else {
		c *= tint;
		if (dissolve > 0.0) {
			vec2 cell = floor(UV / TEXTURE_PIXEL_SIZE / 2.0);
			float n = hash(cell) * 0.7 + (1.0 - UV.y) * 0.3;
			float t = dissolve * 1.15;
			if (n < t) {
				c.a = 0.0;
			} else if (n < t + 0.08) {
				c.rgb = edge_color.rgb;
			}
		}
		c.rgb = mix(c.rgb, flash_color.rgb, flash * c.a) + add_color.rgb * c.a;
		COLOR = c;
	}
}
