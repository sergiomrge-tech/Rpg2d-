"""Static regression contracts for the latest Godot Android source.

Native full UI/input verification is performed separately by the
Godot UI smoke GitHub Actions job. Static checks don't equal runtime tests.
"""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/"godot/scripts/ui"
CORE=ROOT/"godot/scripts/core"
GAME=ROOT/"godot/scripts/game"
BOOK=(UI/"grimoire.gd").read_text(encoding="utf-8")
TOUCH=(UI/"touch_controls.gd").read_text(encoding="utf-8")
GAME_SRC=(GAME/"game.gd").read_text(encoding="utf-8")
MUSIC=(CORE/"music.gd").read_text(encoding="utf-8")


def check():
    for p in [
        "close_button = Button.new()",
        'close_button.text = "X"',
        "close_button.pressed.connect(_on_close_pressed)",
        "close_button.mouse_filter = Control.MOUSE_FILTER_STOP",
        "close_button.process_mode = Node.PROCESS_MODE_ALWAYS",
        "func _on_close_pressed() -> void:",
        "InputEventScreenTouch",
        "func toggle() -> void:",
        "root.move_child(close_button, root.get_child_count() - 1)"
    ]:
        assert p in BOOK, ("book missing",p)
    assert 'Sheets.ui("book")' in BOOK
    assert "func _use(id: String)" in BOOK
    assert "func _refresh() -> void:" in BOOK
    assert "get_tree().paused = open or Game.in_menu" in BOOK

    assert re.search(r"if not in_menu and not grimoire\.open.*consume\(KEY_ESCAPE\)", GAME_SRC)
    assert re.search(r"if not in_menu and not options\.open and not grimoire\.open.*consume\(KEY_TAB\)", GAME_SRC)
    assert "func _ui_smoke_test() -> void:" in GAME_SRC
    for text in [
        "PASS controls hidden in prologue",
        "PASS controls appear when gameplay begins",
        "PASS X touchscreen closes and unpauses grimoire",
        "PASS Escape closes book",
        "PASS Tab closes book",
        "PASS cutscenes hide controls after prologue",
    ]:
        assert text in GAME_SRC

    for p in [
        'var playing := Game.flags.has("prologue")',
        "hud.in_dialogue() or hud.in_credits() or hud.scene_img.visible",
        "layer.visible = not Game.in_menu and not cinematic and (menu or playing)",
        "menu_pad.visible = menu and layer.visible",
        "game_buttons.visible = playing and not menu and layer.visible",
        "stick_base.visible = game_buttons.visible",
        "stick_knob.visible = game_buttons.visible",
    ]:
        assert p in TOUCH, ("touch missing",p)
    assert 'if kind == "flute":' in MUSIC
    assert 'var lead := "pluck" if int(spec["drums"]) == 2 else "flute"' in MUSIC
    assert 'var volume := 0.23' in MUSIC
    assert '"bpm": 76' in MUSIC
    assert '"boss":' in MUSIC
    print("PASS source contracts: book close, Escape/Tab, cutscene touch, gentle flute, original visuals.")
    print("PENDING: real Godot runtime smoke action and actual Android build.")


if __name__=="__main__":
    check()
