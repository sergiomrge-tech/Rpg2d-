"""Check the six playable classes, strict weapon/skill restrictions and save continuity.

Source QA supplements, but never replaces, the separate native Godot runtime smoke.
"""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
game=root/"godot/scripts/game"
ui=root/"godot/scripts/ui"
hero=(game/"hero_classes.gd").read_text()
player=(game/"player.gd").read_text()
state=(game/"game_state.gd").read_text()
pet=(game/"spirit_pet.gd").read_text()
main=(game/"game.gd").read_text()
selector=(ui/"class_select.gd").read_text()
menu=(ui/"main_menu.gd").read_text()
book=(ui/"grimoire.gd").read_text()
items=json.loads((root/"godot/data/items.json").read_text())

classes=["warrior","mage","archer","paladin","assassin","summoner"]
for name in classes:
    assert f'"{name}": {{' in hero, ("class not defined",name)
    assert f'"{name}"' in selector or "HeroClasses.ORDER" in selector
    assert f'"{name}"' in player, ("combat branch missing",name)
    assert f'"{name}"' in main or 'HeroClasses.apply_new_game(state, class_id)' in main

assert "strong" in hero and "weak" in hero
for k in ["move","defense","crit","damage_taken","hp_gain","mp_gain","atk_gain","mag_gain"]:
    assert '"'+k+'"' in hero
assert '"weapon": "sword"' in hero
assert '"weapon": "bow"' in hero
assert '"weapon": "dual_daggers"' in hero
assert hero.count('"weapon": "none"')==2

assert "if not HeroClasses.can_equip(class_id, Data.items[id]):" in state
assert "if not gs.equip(id):" in book
assert 'class_id := "warrior"' in state
assert '"class_id": class_id' in state
assert "HeroClasses.apply_new_game(state, class_id)" in main
assert "menu.on_new = _open_class_select" in main
assert "class_select.setup(hud, _start_selected_class, _cancel_class_select)" in main
assert "menu.reopen()" in main
assert "func _input(ev: InputEvent)" in selector
assert 'class_id == "warrior"' in player or '"warrior":' in player
assert "HeroClasses.allows_melee" in player
assert 'if gs.class_id == "mage":' in player
assert 'if gs.class_id == "archer":' in player
assert 'if gs.class_id == "summoner":' in player
assert "SpiritPet.command(self)" in player
assert "SpiritPet.summon(self)" in player
assert "Projectile.arrow(" in player
assert "Projectile.spark(" in player
assert 'Fx.toast("Mana insuficiente"' in player
assert "class_name SpiritPet" in pet
assert "summoner.gs.class_id != \"summoner\"" in pet
assert "MAX_ACTIVE := 2" in pet

for item_id,typ in [("hunter_bow","bow"),("twin_daggers","dual_daggers")]:
    assert items[item_id]["weapon_type"] == typ
    assert items[item_id]["slot"] == 1

assert "PASS six distinct classes" in main
print("PASS: 6 class strengths and weaknesses, weapon locks, combat channels, pets, saving and UI wiring.")
print("PENDING: native Godot import, input/combat smoke, visual art gate, Android APK.")
