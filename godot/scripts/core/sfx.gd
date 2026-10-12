extends Node
## Procedurally synthesised sound effects (no audio files) + ambient loop.

const RATE := 22050
var _clips := {}
var _pool: Array[AudioStreamPlayer] = []
var _next := 0
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.seed = 7
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i in 14:
		var p := AudioStreamPlayer.new()
		add_child(p)
		_pool.append(p)


func play(name: String, vol: float = 0.5, pitch: float = 1.0) -> void:
	var c := _clip(name)
	if c == null:
		return
	var p := _pool[_next]
	_next = (_next + 1) % _pool.size()
	p.stream = c
	p.volume_db = linear_to_db(maxf(vol, 0.001))
	p.pitch_scale = pitch
	p.play()


## One whispered syllable for a typed character. `voice` (0..1) bends pitch/formants per speaker.
func whisper(ch: String, voice: float, vol: float = 0.3) -> void:
	var c := ch.to_lower()
	var clip := ""
	if c in ["a", "á", "à", "â", "ã"]: clip = "a"
	elif c in ["e", "é", "ê"]: clip = "e"
	elif c in ["i", "í"]: clip = "i"
	elif c in ["o", "ó", "ô", "õ"]: clip = "o"
	elif c in ["u", "ú"]: clip = "u"
	elif c in ["s", "x", "z", "f", "ç", "h"]: clip = "s"
	else: return
	play("wh_%s_%d" % [clip, _rng.randi() % 3], vol, lerpf(0.82, 1.28, voice) * _rng.randf_range(0.96, 1.05))


func loop(name: String, vol: float) -> void:
	var p := AudioStreamPlayer.new()
	p.stream = _clip(name)
	p.volume_db = linear_to_db(vol)
	add_child(p)
	p.play()


func _clip(name: String) -> AudioStreamWAV:
	if _clips.has(name):
		return _clips[name]
	var d := _synth(name)
	if d.is_empty():
		return null
	var w := AudioStreamWAV.new()
	w.format = AudioStreamWAV.FORMAT_16_BITS
	w.mix_rate = RATE
	w.stereo = false
	var bytes := PackedByteArray()
	bytes.resize(d.size() * 2)
	for i in d.size():
		bytes.encode_s16(i * 2, clampi(int(d[i] * 32000.0), -32767, 32767))
	w.data = bytes
	if name == "ambience":
		w.loop_mode = AudioStreamWAV.LOOP_FORWARD
		w.loop_end = d.size()
	_clips[name] = w
	return w


func _buf(sec: float) -> PackedFloat32Array:
	var b := PackedFloat32Array()
	b.resize(ceili(sec * RATE))
	return b


func _env(t: float, a: float, dcy: float) -> float:
	return t / a if t < a else exp(-(t - a) / dcy)


func _n() -> float:
	return _rng.randf() * 2.0 - 1.0


func _noise(sec: float, cutoff: float, a: float, dcy: float, gain: float = 1.0) -> PackedFloat32Array:
	var b := _buf(sec)
	var y := 0.0
	var k := clampf(cutoff, 0.0, 1.0)
	for i in b.size():
		var t := i / float(RATE)
		y += (_n() - y) * k
		b[i] = y * _env(t, a, dcy) * gain
	return b


const FORMANTS := {"a": [800.0, 1250.0], "e": [520.0, 1900.0], "i": [310.0, 2300.0], "o": [520.0, 900.0], "u": [330.0, 800.0]}


## Breathy whisper syllable: noise pushed through two vowel resonators ("wh_<vowel>_<variant>"), or a soft "wh_s_<n>" hiss.
func _whisper(n: String) -> PackedFloat32Array:
	var parts := n.split("_")
	var v := parts[1]
	var variant := int(parts[2])
	var sec := 0.10 + 0.012 * variant
	var b := _buf(sec)
	if v == "s":
		var y := 0.0
		for i in b.size():
			var t := i / float(RATE)
			var x := _n()
			y = x - y * 0.55          # crude high-pass: bright "sh/s" breath
			b[i] = y * 0.35 * sin(PI * clampf(t / sec, 0.0, 1.0))
		return b
	var f: Array = FORMANTS[v]
	var shift := 1.0 + 0.06 * (variant - 1)
	var y1 := [0.0, 0.0]
	var y2 := [0.0, 0.0]
	var rr := 0.985
	for i in b.size():
		var t := i / float(RATE)
		var x := _n()
		var out := 0.0
		for k in 2:
			var w := TAU * float(f[k]) * shift / RATE
			var y: float = x * 0.06 + 2.0 * rr * cos(w) * float(y1[k]) - rr * rr * float(y2[k])
			y2[k] = y1[k]
			y1[k] = y
			out += y * ((0.55 if (v == "i" or v == "u") else 1.0) if k == 0 else 0.8)
		b[i] = out * sin(PI * clampf(t / sec, 0.0, 1.0)) + x * 0.03
	var pk := 0.001
	for q in b:
		pk = maxf(pk, absf(q))
	for i in b.size():
		b[i] = b[i] / pk * 0.7
	return b


func _synth(n: String) -> PackedFloat32Array:
	if n.begins_with("wh_"):
		return _whisper(n)
	match n:
		"swing", "swing_heavy":
			var h := n == "swing_heavy"
			var b := _buf(0.38 if h else 0.26)
			var y := 0.0
			for i in b.size():
				var u := float(i) / b.size()
				var k := lerpf(0.05, 0.45, sin(u * PI))
				y += (_n() - y) * k
				b[i] = y * sin(u * PI) * (0.9 if h else 0.7)
			return b
		"hit":
			var b := _noise(0.22, 0.6, 0.001, 0.04, 0.9)
			for i in b.size():
				var t := i / float(RATE)
				b[i] += sin(TAU * (140.0 - 260.0 * t) * t) * _env(t, 0.001, 0.07) * 0.8
			return b
		"claw": return _noise(0.18, 0.75, 0.002, 0.035, 0.8)
		"step": return _noise(0.07, 0.15, 0.001, 0.015, 0.6)
		"roll": return _noise(0.3, 0.08, 0.02, 0.09, 0.9)
		"boom":
			var b := _noise(0.5, 0.12, 0.002, 0.12, 1.0)
			for i in b.size():
				var t := i / float(RATE)
				b[i] += sin(TAU * (90.0 - 60.0 * t) * t) * _env(t, 0.002, 0.15) * 0.7
			return b
		"spark", "charge", "fireball":
			var length := 0.45 if n == "charge" else 0.35
			var b := _buf(length)
			var f0 := 900.0 if n == "spark" else (300.0 if n == "charge" else 220.0)
			var f1 := 2200.0 if n == "spark" else (900.0 if n == "charge" else 120.0)
			var ph := 0.0
			for i in b.size():
				var t := i / float(RATE)
				var u := t / length
				ph += lerpf(f0, f1, u) / RATE
				var tone := sin(TAU * ph) + 0.4 * sin(TAU * ph * 2.01)
				var e := sin(u * PI) if n == "charge" else _env(t, 0.005, length * 0.35)
				b[i] = (tone * 0.35 + _n() * (0.5 if n == "fireball" else 0.15)) * e
			return b
		"imp_cry", "imp_hurt", "imp_die":
			var length := 0.6 if n == "imp_die" else 0.28
			var b := _buf(length)
			var ph := 0.0
			for i in b.size():
				var t := i / float(RATE)
				var u := t / length
				var f := 700.0 + 500.0 * sin(u * 9.0) if n == "imp_cry" else (900.0 - 400.0 * u if n == "imp_hurt" else 600.0 - 450.0 * u)
				f += 40.0 * sin(t * TAU * 35.0)
				ph += f / RATE
				var saw: float = 2.0 * (ph - floor(ph + 0.5))
				b[i] = (saw * 0.35 + _n() * 0.12) * _env(t, 0.01, length * 0.4)
			return b
		"hurt":
			var b := _noise(0.25, 0.35, 0.001, 0.06, 0.8)
			for i in b.size():
				var t := i / float(RATE)
				b[i] += sin(TAU * (220.0 - 120.0 * t) * t) * _env(t, 0.001, 0.08) * 0.6
			return b
		"coin", "pickup", "potion", "levelup", "ui":
			var notes: Array = [1318.0, 1975.0] if n == "coin" else ([660.0, 990.0] if n == "pickup" else ([523.0, 659.0, 784.0] if n == "potion" else ([523.0, 659.0, 784.0, 1046.0] if n == "levelup" else [880.0])))
			var step := 0.11 if n == "levelup" else 0.07
			var b := _buf(step * notes.size() + 0.35)
			for k in notes.size():
				var s0 := int(k * step * RATE)
				for i in range(s0, b.size()):
					var t := (i - s0) / float(RATE)
					b[i] += (sin(TAU * notes[k] * t) + 0.3 * sin(2.0 * TAU * notes[k] * t)) * _env(t, 0.003, 0.12) * 0.3
			return b
		"death":
			var b := _buf(1.2)
			for i in b.size():
				var t := i / float(RATE)
				b[i] = (sin(TAU * 220.0 * t) + sin(TAU * 261.0 * t) + sin(TAU * 311.0 * t)) * 0.15 * _env(t, 0.05, 0.5)
			return b
		"ambience":
			var length := 8.0
			var b := _buf(length)
			var y := 0.0
			for i in b.size():
				var t := i / float(RATE)
				y += (_n() - y) * 0.02
				b[i] = y * (0.5 + 0.5 * sin(TAU * t / length * 2.0)) * 0.6
			for k in 7:
				var t0 := _rng.randf() * (length - 0.5)
				var f := 2600.0 + _rng.randf() * 1400.0
				var s0 := int(t0 * RATE)
				for i in int(RATE * 0.18):
					if s0 + i >= b.size():
						break
					var t := i / float(RATE)
					b[s0 + i] += sin(TAU * (f + 900.0 * sin(t * 60.0)) * t) * _env(t, 0.01, 0.05) * 0.05
			return b
	return PackedFloat32Array()
