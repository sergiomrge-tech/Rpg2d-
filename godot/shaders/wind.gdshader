shader_type canvas_item;
// Wind: the sprite bends from its base (feet at the node origin), more at the top, with slow gusts. Phase comes from the world position.
uniform float amp = 4.0;        // sideways travel of the very top, in pixels
uniform float height = 260.0;   // height that counts as "the top"
uniform float speed = 1.3;
uniform float boost = 1.0;      // storms push harder

void vertex() {
	vec2 wp = MODEL_MATRIX[3].xy;
	float ph = wp.x * 0.0055 + wp.y * 0.003;
	float h = clamp(-VERTEX.y / height, 0.0, 1.0);
	float bend = pow(h, 1.5);
	float gust = 0.6 + 0.4 * sin(TIME * 0.33 + wp.x * 0.0009 + wp.y * 0.0004);
	float s = sin(TIME * speed + ph) * 0.9 + sin(TIME * speed * 2.3 + ph * 1.7) * 0.35;
	VERTEX.x += s * amp * boost * bend * gust;
	VERTEX.y += abs(s) * amp * 0.10 * bend;
}
