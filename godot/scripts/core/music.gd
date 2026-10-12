extends Node
## Procedurally composed background music (no audio files). Each track is a seeded 8-bar loop
## (pads + bass + melody + optional drums) rendered on a worker thread, then cross-faded in.

const RATE := 16000
const SPECS := {
	"village":    {"root": 293.66, "scale": [0, 2, 4, 7, 9], "bpm": 96, "prog": [[0, 2, 4], [4, 6, 8], [5, 7, 9], [3, 5, 7]], "melody": 0.55, "drums": 0, "seed": 11, "bright": 1.0},
	"velmoor":    {"root": 220.0, "scale": [0, 2, 3, 5, 7, 9, 10], "bpm": 70, "prog": [[0, 2, 4], [3, 5, 7], [4, 6, 8], [0, 2, 4]], "melody": 0.4, "drums": 0, "seed": 23, "bright": 0.8},
	"valemont":   {"root": 174.61, "scale": [0, 2, 4, 5, 7, 9, 11], "bpm": 84, "prog": [[0, 2, 4], [3, 5, 7], [4, 6, 8], [0, 2, 4]], "melody": 0.5, "drums": 0, "seed": 31, "bright": 0.9},
	"kharis":     {"root": 293.66, "scale": [0, 1, 4, 5, 7, 8, 10], "bpm": 100, "prog": [[0, 2, 4], [0, 2, 4], [1, 3, 5], [0, 2, 4]], "melody": 0.45, "drums": 1, "seed": 47, "bright": 0.9},
	"mines":      {"root": 130.81, "scale": [0, 2, 3, 5, 7, 8, 10], "bpm": 64, "prog": [[0, 2, 4], [0, 2, 4], [5, 7, 9], [4, 6, 8]], "melody": 0.2, "drums": 0, "seed": 53, "bright": 0.5},
	"mirewail":   {"root": 164.81, "scale": [0, 2, 3, 5, 7, 8, 10], "bpm": 60, "prog": [[0, 2, 4], [5, 7, 9], [0, 2, 4], [3, 5, 7]], "melody": 0.25, "drums": 0, "seed": 61, "bright": 0.6},
	"peaks":      {"root": 233.08, "scale": [0, 2, 4, 6, 7, 9, 11], "bpm": 66, "prog": [[0, 2, 4], [1, 3, 5], [4, 6, 8], [0, 2, 4]], "melody": 0.4, "drums": 0, "seed": 71, "bright": 1.1},
	"castle":     {"root": 146.83, "scale": [0, 2, 3, 5, 7, 8, 10], "bpm": 88, "prog": [[0, 2, 4], [5, 7, 9], [3, 5, 7], [4, 6, 8]], "melody": 0.35, "drums": 1, "seed": 83, "bright": 0.8},
	"wastelands": {"root": 138.59, "scale": [0, 2, 3, 5, 7, 8, 10], "bpm": 80, "prog": [[0, 2, 4], [0, 2, 4], [5, 7, 9], [4, 6, 8]], "melody": 0.3, "drums": 1, "seed": 97, "bright": 0.7},
	"citadel":    {"root": 123.47, "scale": [0, 2, 3, 5, 7, 8, 11], "bpm": 76, "prog": [[0, 2, 4], [5, 7, 9], [0, 2, 4], [4, 6, 8]], "melody": 0.3, "drums": 1, "seed": 101, "bright": 0.7},
	"boss":       {"root": 110.0, "scale": [0, 2, 3, 5, 7, 8, 11], "bpm": 138, "prog": [[0, 2, 4], [0, 2, 4], [5, 7, 9], [4, 6, 8]], "melody": 0.7, "drums": 2, "seed": 113, "bright": 1.0},
}

var enabled := true
var volume := 0.3
var _tracks := {}
var _threads := {}
var _want := ""
var _cur := ""
var _players: Array[AudioStreamPlayer] = []
var _active := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i in 2:
		var p := AudioStreamPlayer.new()
		p.volume_db = -60.0
		add_child(p)
		_players.append(p)


func play(track: String) -> void:
	if not enabled or not SPECS.has(track) or track == _want:
		return
	_want = track
	if _tracks.has(track):
		_fade_to(track)
	elif not _threads.has(track):
		var t := Thread.new()
		_threads[track] = t
		t.start(_build.bind(track))


func _fade_to(track: String) -> void:
	if track != _want or track == _cur:
		return
	_cur = track
	var old := _players[_active]
	_active = 1 - _active
	var nw := _players[_active]
	nw.stream = _tracks[track]
	nw.volume_db = -60.0
	nw.play()
	var tw := create_tween().set_parallel(true)
	tw.tween_property(nw, "volume_db", linear_to_db(volume), 2.0)
	tw.tween_property(old, "volume_db", -60.0, 2.0)
	tw.chain().tween_callback(old.stop)


func _build(track: String) -> void:
	var w := _render(SPECS[track])
	_done.call_deferred(track, w)


func _done(track: String, w: AudioStreamWAV) -> void:
	_threads[track].wait_to_finish()
	_threads.erase(track)
	_tracks[track] = w
	_fade_to(track)


func _hz(spec: Dictionary, deg: int) -> float:
	var sc: Array = spec["scale"]
	var n := sc.size()
	var oct := floori(float(deg) / n)
	return float(spec["root"]) * pow(2.0, (float(sc[posmod(deg, n)]) + 12.0 * oct) / 12.0)


func _note(buf: PackedFloat32Array, start: float, dur: float, f: float, vol: float, kind: String, bright: float) -> void:
	var s0 := int(start * RATE)
	var n := int((dur + 0.5) * RATE)
	var total := buf.size()
	var w := TAU * f / RATE
	for i in n:
		var t := float(i) / RATE
		var env: float
		var v: float
		if kind == "pad":
			env = minf(t / 0.5, 1.0) * (1.0 if t < dur else exp(-(t - dur) * 5.0))
			var ph := w * i
			v = sin(ph) + 0.5 * sin(ph * 1.004) + 0.25 * sin(ph * 2.0) * bright
		elif kind == "bass":
			env = minf(t / 0.02, 1.0) * exp(-t * 2.2)
			var ph := w * i
			v = sin(ph) + 0.4 * sin(ph * 2.0)
		else:   # pluck
			env = minf(t / 0.008, 1.0) * exp(-t * 4.5)
			var ph := w * i
			v = sin(ph) + 0.35 * bright * sin(ph * 2.0) + 0.15 * bright * sin(ph * 3.0)
		var idx := (s0 + i) % total
		buf[idx] += v * env * vol


func _drum(buf: PackedFloat32Array, start: float, kind: String, rng: RandomNumberGenerator) -> void:
	var s0 := int(start * RATE)
	var total := buf.size()
	var n := int((0.28 if kind == "kick" else 0.12) * RATE)
	var ph := 0.0
	for i in n:
		var t := float(i) / RATE
		var v: float
		if kind == "kick":
			ph += TAU * (45.0 + 90.0 * exp(-t * 28.0)) / RATE
			v = sin(ph) * exp(-t * 11.0) * 0.9
		elif kind == "snare":
			v = (rng.randf() * 2.0 - 1.0) * exp(-t * 22.0) * 0.35 + sin(TAU * 190.0 * t) * exp(-t * 30.0) * 0.2
		else:
			v = (rng.randf() * 2.0 - 1.0) * exp(-t * 60.0) * 0.12
		buf[(s0 + i) % total] += v


func _render(spec: Dictionary) -> AudioStreamWAV:
	var rng := RandomNumberGenerator.new()
	rng.seed = int(spec["seed"])
	var beat := 60.0 / float(spec["bpm"])
	var bars := 8
	var length := beat * 4.0 * bars
	var buf := PackedFloat32Array()
	buf.resize(int(length * RATE))
	var bright := float(spec["bright"])
	var prog: Array = spec["prog"]
	var n_sc: int = spec["scale"].size()
	var deg := n_sc + 2
	for bar in bars:
		var chord: Array = prog[bar % prog.size()]
		var t0 := bar * beat * 4.0
		for c in chord:
			_note(buf, t0, beat * 4.0, _hz(spec, int(c)), 0.16, "pad", bright)
		var rootd := int(chord[0]) - n_sc
		for h in 4:
			_note(buf, t0 + h * beat, beat * 0.9, _hz(spec, rootd), 0.3, "bass", bright)
		var steps := 8
		for st in steps:
			if rng.randf() < float(spec["melody"]):
				deg = clampi(deg + rng.randi_range(-2, 2), n_sc, n_sc * 2 + 3)
				if st % 4 == 0:
					deg = int(chord[rng.randi_range(0, 2)]) + n_sc * (1 if int(chord[0]) < n_sc else 0)
					deg = clampi(deg, n_sc, n_sc * 2 + 3)
				_note(buf, t0 + st * beat * 0.5, beat * 0.5, _hz(spec, deg), 0.2, "pluck", bright)
		var dr: int = spec["drums"]
		if dr > 0:
			for b in 4:
				if dr == 2 or b % 2 == 0:
					_drum(buf, t0 + b * beat, "kick", rng)
				if b % 2 == 1 and dr == 2:
					_drum(buf, t0 + b * beat, "snare", rng)
			if dr == 2:
				for e in 8:
					_drum(buf, t0 + e * beat * 0.5, "hat", rng)
	# cheap circular reverb (two comb taps)
	var out := buf.duplicate()
	for tap in [[0.19, 0.28], [0.37, 0.2], [0.53, 0.12]]:
		var d := int(float(tap[0]) * RATE)
		for i in buf.size():
			out[i] += buf[(i - d + buf.size()) % buf.size()] * float(tap[1])
	var peak := 0.001
	for v in out:
		peak = maxf(peak, absf(v))
	var bytes := PackedByteArray()
	bytes.resize(out.size() * 2)
	for i in out.size():
		bytes.encode_s16(i * 2, int(clampf(out[i] / peak * 0.85, -1.0, 1.0) * 32000.0))
	var w := AudioStreamWAV.new()
	w.format = AudioStreamWAV.FORMAT_16_BITS
	w.mix_rate = RATE
	w.stereo = false
	w.data = bytes
	w.loop_mode = AudioStreamWAV.LOOP_FORWARD
	w.loop_end = out.size()
	return w
