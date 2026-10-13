shader_type canvas_item;
// Water overlay on top of the baked ground. Mask (1/4 res): R = inside water, G = depth from the shore, B = proximity to the shore from the land side.
uniform float strength = 1.0;

varying vec2 wpos;

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}

void fragment() {
	vec3 m = texture(TEXTURE, UV).rgb;
	float inside = smoothstep(0.42, 0.58, m.r);
	float depth = m.g;
	float shore = m.b;
	float t = TIME;
	// drifting ripple field (two crossing directions, domain-warped)
	vec2 p = wpos * 0.018;
	float warp = vnoise(p * 1.7 + t * 0.15);
	float r1 = sin((p.x * 1.3 + p.y * 0.7) * 6.0 + t * 1.1 + warp * 6.0);
	float r2 = sin((p.x * -0.8 + p.y * 1.4) * 7.0 - t * 0.9 + warp * 5.0);
	float ripple = smoothstep(0.82, 1.0, (r1 + r2) * 0.5 + 0.35 * vnoise(p * 9.0 + t * 0.4));
	// caustics in the shallows
	float c = vnoise(p * 6.0 + vec2(t * 0.25, -t * 0.2)) * vnoise(p * 6.5 - vec2(t * 0.2, t * 0.3));
	float caustic = smoothstep(0.30, 0.46, c) * (1.0 - smoothstep(0.0, 0.5, depth));
	// shore waves: bands travelling toward the bank, stronger and fatter near the edge
	float band = sin((depth * 14.0 - t * 1.4 + vnoise(wpos * 0.03) * 2.5) * 1.0);
	float wave = smoothstep(0.65, 1.0, band) * (1.0 - smoothstep(0.0, 0.55, depth));
	// foam lapping on the bank (swells in and out)
	float swell = 0.5 + 0.5 * sin(t * 0.9 + vnoise(wpos * 0.02) * 6.0);
	float lap = smoothstep(0.55 + 0.25 * swell, 1.0, shore) * (0.4 + 0.6 * swell);
	float edge_foam = (1.0 - smoothstep(0.0, 0.08 + 0.05 * swell, depth)) * inside;
	// depth tint (deeper = darker blue) and a soft sky sheen
	vec3 deep = vec3(0.02, 0.10, 0.20);
	float tint = smoothstep(0.1, 0.9, depth) * 0.30;
	float sheen = vnoise(p * 2.0 + vec2(t * 0.05, 0.0));
	vec4 col = vec4(0.0);
	col.rgb = deep;
	col.a = tint * inside;
	// highlights
	vec3 hi = vec3(0.80, 0.93, 1.0);
	float hl = (ripple * 0.55 + caustic * 0.45 + wave * 0.6 + edge_foam * 0.7) * inside;
	hl += lap * (1.0 - inside) * 0.6;
	hl += sheen * 0.05 * inside;
	float ha = clamp(hl, 0.0, 1.0) * strength;
	col.rgb = mix(col.rgb, hi, ha / max(ha + col.a, 0.001));
	col.a = clamp(col.a + ha * 0.75, 0.0, 0.9) * strength;
	COLOR = col;
}
