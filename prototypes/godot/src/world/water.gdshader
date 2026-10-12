shader_type canvas_item;
uniform sampler2D water_atlas : filter_nearest;
uniform sampler2D mask : filter_nearest;
uniform vec2 map_cells;
uniform float frames = 8.0;
uniform float fps = 6.0;
void fragment() {
	vec2 cell = UV * map_cells;
	vec2 c = floor(cell);
	float m = texture(mask, (c + 0.5) / map_cells).r;
	vec2 f = fract(cell);
	float fr = floor(mod(TIME * fps, frames));
	float row = m > 0.75 ? 1.0 : 0.0;
	vec4 col = texture(water_atlas, vec2((fr + f.x) / frames, (row + f.y) / 3.0));
	// edge-aware alpha: 1 for water cells, 0 elsewhere
	float is_water = step(0.1, m);
	COLOR = vec4(col.rgb, col.a * is_water);
}
