extends Node
## Static game data (items, demons, recipes) loaded from res://data/*.json plus the balance model.

var items := {}
var demons := {}
var recipes: Array = []

const RARITY_COLORS := [
	Color(0.92, 0.9, 0.85), Color(0.45, 0.9, 0.45), Color(0.35, 0.65, 1.0), Color(0.78, 0.45, 1.0), Color(1.0, 0.68, 0.2),
]

const RARITY_NAMES := ["Comum", "Incomum", "Raro", "Épico", "Lendário"]


func _ready() -> void:
	items = _load("items")
	demons = _load("demons")
	recipes = _load("recipes")


func _load(n: String) -> Variant:
	var f := FileAccess.open("res://data/%s.json" % n, FileAccess.READ)
	return JSON.parse_string(f.get_as_text())


# Balance: enemy HP grows with the player's damage, enemy damage with the player's max HP.
func hp_scale(lv: int) -> float:
	return 1.0 + 0.28 * (lv - 1)


func dmg_scale(lv: int) -> float:
	return 1.0 + 0.14 * (lv - 1)


func xp_to_next(lv: int) -> int:
	return roundi(90.0 * lv * (1.0 + 0.05 * lv))
