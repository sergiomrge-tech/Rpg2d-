extends Node
## Procedural SFX (autoload "Sfx"): sounds are synthesised into AudioStreamWAV once at startup.

const RATE := 22050
var sounds := {}
var players: Array = []
var music_player: AudioStreamPlayer
var music_name := ""

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i in 10:
		var p := AudioStreamPlayer.new()
		p.bus = "Master"
		add_child(p)
		players.append(p)
	music_player = AudioStreamPlayer.new()
	music_player.volume_db = -8.0
	add_child(music_player)
	_build()

func play(name: String, vol := 0.0, pitch := 1.0) -> void:
	if not sounds.has(name):
		return
	for p in players:
		if not p.playing:
			p.stream = sounds[name]
			p.volume_db = vol
			p.pitch_scale = pitch
			p.play()
			return

func music(name: String) -> void:
	if name == music_name:
		return
	music_name = name
	var path := "res://assets/music/%s.ogg" % name
	if name == "" or not ResourceLoader.exists(path):
		music_player.stop()
		return
	music_player.stream = load(path)
	music_player.play()

# ------------------------------------------------------------------ synthesis
func _tone(t: float, f: float, kind: String) -> float:
	var ph := fmod(t * f, 1.0)
	match kind:
		"sine": return sin(ph * TAU)
		"square": return 1.0 if ph < 0.5 else -1.0
		"tri": return 4.0 * absf(ph - 0.5) - 1.0
		"saw": return 2.0 * ph - 1.0
	return 0.0

func _make(dur: float, fn: Callable) -> AudioStreamWAV:
	var n := int(dur * RATE)
	var data := PackedByteArray()
	data.resize(n * 2)
	for i in n:
		var t := float(i) / RATE
		var v: float = clampf(fn.call(t, t / dur), -1.0, 1.0)
		data.encode_s16(i * 2, int(v * 32000.0))
	var s := AudioStreamWAV.new()
	s.format = AudioStreamWAV.FORMAT_16_BITS
	s.mix_rate = RATE
	s.data = data
	return s

func _noise() -> float:
	return randf() * 2.0 - 1.0

func _env(f: float, a := 0.01, power := 2.0) -> float:
	return minf(1.0, f / a) * pow(1.0 - f, power)

func _build() -> void:
	sounds["swing"] = _make(0.16, func(t, f): return (_noise() * 0.5 * (1.0 - f) + _tone(t, lerpf(420, 160, f), "tri") * 0.3) * _env(f, 0.02) * 0.6)
	sounds["swing2"] = _make(0.22, func(t, f): return (_noise() * 0.5 * (1.0 - f) + _tone(t, lerpf(300, 90, f), "saw") * 0.3) * _env(f, 0.02) * 0.7)
	sounds["hit"] = _make(0.12, func(t, f): return (_noise() * 0.6 + _tone(t, lerpf(240, 70, f), "square") * 0.4) * _env(f, 0.003, 2.5) * 0.8)
	sounds["crit"] = _make(0.22, func(t, f): return (_noise() * 0.5 + _tone(t, lerpf(900, 120, f), "saw") * 0.4 + _tone(t, lerpf(1400, 600, f), "square") * 0.2) * _env(f, 0.003, 2.0) * 0.9)
	sounds["hurt"] = _make(0.25, func(t, f): return (_tone(t, lerpf(320, 70, f), "saw") * 0.5 + _noise() * 0.3) * _env(f, 0.005, 1.5) * 0.9)
	sounds["dodge"] = _make(0.2, func(t, f): return _noise() * 0.5 * sin(PI * f) * 0.5)
	sounds["fire"] = _make(0.35, func(t, f): return (_noise() * 0.4 + _tone(t, lerpf(200, 520, f), "saw") * 0.3) * _env(f, 0.03) * 0.7)
	sounds["ice"] = _make(0.32, func(t, f): return (_tone(t, lerpf(1600, 700, f), "tri") * 0.4 + _tone(t, lerpf(2400, 1200, f), "sine") * 0.25) * _env(f, 0.01) * 0.7)
	sounds["bolt"] = _make(0.28, func(t, f): return (_tone(t, lerpf(1900, 120, f), "saw") * 0.35 + _noise() * 0.4 * (1.0 - f)) * _env(f, 0.003, 1.5) * 0.8)
	sounds["heal"] = _make(0.55, func(t, f): return (_tone(t, 523.0 + floorf(f * 4.0) * 130.0, "tri") * 0.4) * _env(f, 0.02, 1.2) * 0.8)
	sounds["buff"] = _make(0.4, func(t, f): return (_tone(t, lerpf(400, 900, f), "tri") * 0.4 + _tone(t, lerpf(600, 1200, f), "sine") * 0.2) * _env(f, 0.02) * 0.8)
	sounds["shield"] = _make(0.4, func(t, f): return (_tone(t, lerpf(300, 640, f), "sine") * 0.5 + _tone(t, 900.0, "tri") * 0.12) * _env(f, 0.02) * 0.8)
	sounds["slam"] = _make(0.5, func(t, f): return (_noise() * 0.6 * (1.0 - f) + _tone(t, lerpf(120, 40, f), "sine") * 0.7) * _env(f, 0.003, 1.6) * 1.0)
	sounds["explosion"] = _make(0.7, func(t, f): return (_noise() * 0.8 * (1.0 - f) + _tone(t, lerpf(100, 30, f), "sine") * 0.6) * _env(f, 0.004, 1.4) * 1.0)
	sounds["meteor"] = _make(0.8, func(t, f): return (_tone(t, lerpf(900, 90, f), "saw") * 0.25 + _noise() * 0.2) * _env(f, 0.05, 0.6) * 0.8)
	sounds["pickup"] = _make(0.14, func(t, f): return _tone(t, 880.0 if f < 0.45 else 1320.0, "square") * _env(f, 0.003, 1.0) * 0.35)
	sounds["coin"] = _make(0.16, func(t, f): return _tone(t, 988.0 if f < 0.3 else 1319.0, "square") * _env(f, 0.003, 1.2) * 0.3)
	sounds["chest"] = _make(0.5, func(t, f): return _tone(t, [392.0, 523.0, 659.0, 784.0, 1047.0][mini(4, int(f * 5.0))], "square") * _env(fmod(f * 5.0, 1.0), 0.01, 1.0) * 0.35)
	sounds["levelup"] = _make(0.8, func(t, f): return _tone(t, [523.0, 659.0, 784.0, 1047.0, 784.0, 1047.0, 1319.0][mini(6, int(f * 7.0))], "square") * _env(fmod(f * 7.0, 1.0), 0.01, 1.0) * 0.35)
	sounds["ui_move"] = _make(0.05, func(t, f): return _tone(t, 660.0, "square") * _env(f, 0.003, 1.0) * 0.18)
	sounds["ui_ok"] = _make(0.14, func(t, f): return _tone(t, 660.0 if f < 0.4 else 990.0, "square") * _env(f, 0.003, 1.0) * 0.25)
	sounds["ui_back"] = _make(0.1, func(t, f): return _tone(t, lerpf(500, 300, f), "square") * _env(f, 0.003, 1.0) * 0.2)
	sounds["error"] = _make(0.2, func(t, f): return _tone(t, 160.0 if f < 0.5 else 130.0, "square") * _env(fmod(f * 2.0, 1.0), 0.003, 1.0) * 0.3)
	sounds["talk"] = _make(0.04, func(t, f): return _tone(t, 380.0 + randf() * 140.0, "square") * _env(f, 0.003, 1.0) * 0.1)
	sounds["tele"] = _make(0.13, func(t, f): return _tone(t, 900.0 if f < 0.5 else 1200.0, "square") * _env(fmod(f * 2.0, 1.0), 0.003, 1.0) * 0.14)
	sounds["alert"] = _make(0.12, func(t, f): return _tone(t, lerpf(500, 900, f), "tri") * _env(f, 0.003, 1.0) * 0.25)
	sounds["growl"] = _make(0.4, func(t, f): return (_tone(t, lerpf(110, 70, f), "saw") * 0.5 + _noise() * 0.2) * _env(f, 0.03, 1.0) * 0.8)
	sounds["swoosh"] = _make(0.2, func(t, f): return _noise() * 0.5 * sin(PI * f) * 0.45)
	sounds["arrow"] = _make(0.14, func(t, f): return (_noise() * 0.3 + _tone(t, lerpf(900, 400, f), "tri") * 0.3) * _env(f, 0.003, 1.5) * 0.5)
	sounds["magic"] = _make(0.25, func(t, f): return (_tone(t, lerpf(500, 1000, f), "sine") * 0.4 + _tone(t, lerpf(750, 1500, f), "tri") * 0.2) * _env(f, 0.01, 1.2) * 0.6)
	sounds["charge"] = _make(0.4, func(t, f): return _tone(t, lerpf(260, 780, f), "sine") * 0.3 * sin(PI * f) * 0.7)
	sounds["whirl"] = _make(0.55, func(t, f): return (_noise() * 0.4 * sin(PI * f) + _tone(t, 220.0 + sin(f * 40.0) * 40.0, "saw") * 0.12) * 0.8)
	sounds["dash"] = _make(0.25, func(t, f): return (_noise() * 0.5 * (1.0 - f) + _tone(t, lerpf(1200, 300, f), "saw") * 0.2) * _env(f, 0.005) * 0.7)
	sounds["spirit"] = _make(0.5, func(t, f): return (_tone(t, lerpf(500, 1000, f), "sine") * 0.4 + _tone(t, lerpf(750, 1500, f), "tri") * 0.2) * sin(PI * f) * 0.8)
	sounds["die"] = _make(0.4, func(t, f): return (_tone(t, lerpf(400, 60, f), "square") * 0.4 + _noise() * 0.3 * (1.0 - f)) * _env(f, 0.005, 1.4) * 0.8)
	sounds["save"] = _make(0.8, func(t, f): return _tone(t, [659.0, 784.0, 988.0, 1319.0][mini(3, int(f * 4.0))], "sine") * _env(fmod(f * 4.0, 1.0), 0.01, 0.8) * 0.4)
	sounds["roar"] = _make(0.9, func(t, f): return (_tone(t, lerpf(110, 55, f), "saw") * 0.55 + _noise() * 0.25) * _env(f, 0.05, 0.9) * 1.0)
	sounds["door"] = _make(0.22, func(t, f): return (_noise() * 0.4 + _tone(t, lerpf(200, 120, f), "tri") * 0.4) * _env(f, 0.01, 1.4) * 0.6)
