"""Regression contracts for removal of stamina costs in the Godot RPG.

Legacy max_st remains serializable to avoid corrupting existing user saves.
The runtime Godot smoke test proves attack/roll/run with legacy stamina == 0.
"""
from pathlib import Path

root=Path(__file__).resolve().parents[1]
game=root/"godot/scripts/game"
ui=root/"godot/scripts/ui"
player=(game/"player.gd").read_text(encoding="utf-8")
state=(game/"game_state.gd").read_text(encoding="utf-8")
main=(game/"game.gd").read_text(encoding="utf-8")
hud=(ui/"hud.gd").read_text(encoding="utf-8")
book=(ui/"grimoire.gd").read_text(encoding="utf-8")

forbidden_player=[
    "var st :=", "st_regen_delay", "RUN_DRAIN", "ATTACK_COST",
    "ROLL_COST", "gs.max_st", '"Sem fôlego!"',
]
for fragment in forbidden_player:
    assert fragment not in player, ("stamina gating remains",fragment)
for expected in [
    "var can_run := run",
    'anim.play("run" if can_run else "walk")',
    "func _try_attack() -> void:",
    "func _start_attack(n: int) -> void:",
    "func _try_roll() -> void:",
    "if state == St.ATTACK and anim.normalized() < 0.5:",
    "invuln = 0.36",
    # Costs are class-specific now; mana must still gate magical abilities.
    "if mp < cost:",
]:
    assert expected in player, ("lost essential combat behaviour",expected)
assert "arc_st_track" not in hud
assert "arc_st_fill" not in hud
assert "st_fill" not in hud
assert "st_shown" not in hud
assert "p.st" not in hud
assert "orb_cd[0].value = 0.0" in hud
assert "orb_cd[2].value = 0.0" in hud
assert '"Fôlego' not in book
assert "player.st =" not in main
assert "player.gs.max_st = 0.0" in main
assert "PASS unlimited sprint animation at zero legacy stamina" in main
assert "PASS unlimited attack and dodge with zero legacy stamina" in main
assert "max_st" in state and '"max_st": max_st' in state
assert 'if k in self:' in state
assert "max_st += " not in state
print("PASS: combat unrestricted, stamina HUD removed, mana/roll protections intact.")
print("PASS: old-save max_st retained (legacy field), runtime regression wired.")
print("PENDING: actual Godot runtime smoke and Android APK build.")
