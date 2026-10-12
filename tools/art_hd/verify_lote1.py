"""Validate Lote 1 specs and compare existing Oni/Grakk against REAL sprite JSON.

Standard library only. Does not run Unity, inspect render quality or claim that
not-yet-generated creatures have sprites or gameplay AI.
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "docs/asset_catalog/lote1_spec.json"
ATLAS = ROOT / "unity/Assets/Resources/Sprites/Demons"
BASE_TRACKS = ("idle", "move", "attack", "cast", "hurt", "death")
DIRECTIONS = ("down", "up", "side")
GENERATED = ("oni_soldier", "grakk")
EXPECTED_ENEMIES = (
    "imp_scout", "imp_raider", "imp_pyro", "imp_hexer", "imp_bomber",
    "imp_howler", "oni_soldier", "oni_lancer", "oni_shielder", "oni_executioner"
)
EXPECTED_BOSSES = (
    "grakk", "morgash_ironhorn", "velka_flamebeak", "krull_chainlord", "thornmaw_alpha"
)


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        data = f.read(24)
    assert len(data) == 24 and data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR", path
    return struct.unpack(">II", data[16:24])


def main() -> None:
    d = json.loads(SPEC.read_text(encoding="utf-8"))
    roster = d["roster"]
    assert d["schema_version"] == 1 and d["lot_id"] == "LOTE_01"
    assert len(roster) == 15
    assert tuple(r["id"] for r in roster[:10]) == EXPECTED_ENEMIES
    assert tuple(r["id"] for r in roster[10:]) == EXPECTED_BOSSES
    assert len({r["id"] for r in roster}) == len(roster)
    assert "HD cartoon" in d["visual_guard"]
    tracks_total, frames_total = 0, 0

    for index, record in enumerate(roster):
        id_ = record["id"]
        is_boss = index >= 10
        assert record["kind"] == ("boss" if is_boss else "demon")
        assert record["production"]["gameplay_registered"] is False
        assert record["production"]["unity_visual_approved"] is False
        assert record["production"]["skill_effects_implemented"] is False
        assert record["visual"]["sheet"] == "Sprites/Demons/" + id_
        assert record["visual"]["style"] == "approved_HD_cartoon_Cairo_cel_shading"

        v = record["visual"]
        w, h = v["frameW"], v["frameH"]
        assert 128 <= w <= 512 and 128 <= h <= 512
        assert 0 < v["pivotX"] < w and 0 < v["pivotY"] < h
        animations = record["animations"]
        assert tuple(animations["directions"]) == DIRECTIONS
        assert animations["mirror_left_from_side"] is True

        a = animations["tracks"]
        expected_states = BASE_TRACKS + (("skill_2",) if is_boss else ())
        assert tuple(x["id"] for x in a) == expected_states
        assert len(record["moves"]) == (3 if is_boss else 2)
        assert tuple(x["animation"] for x in record["moves"]) == ("attack", "cast") + (("skill_2",) if is_boss else ())

        for ability in record["moves"]:
            assert ability["status"] == "design_only"
            assert 0.15 <= ability["telegraph_s"] <= 1.5
            assert 0.5 <= ability["cooldown_s"] <= 30
            assert ability["visual_effect_id"].startswith(id_ + "_")

        for track in a:
            assert track["frames_per_direction"] >= 4
            assert 7 <= track["fps"] <= 30
            assert track["loop"] == (track["id"] in ("idle", "move"))
            ev = track["event_frame"]
            assert ev == -1 if track["id"] in ("idle", "move", "hurt", "death") else 0 <= ev < track["frames_per_direction"]
            tracks_total += 3
            frames_total += track["frames_per_direction"] * 3

        if id_ in GENERATED:
            assert record["production"]["art_status"] == "generated_pending_visual_gate"
            assert tuple(record["production"]["generated_tracks"]) == BASE_TRACKS
            data = json.loads((ATLAS / (id_ + ".json")).read_text(encoding="utf-8"))
            assert (data["frameW"], data["frameH"], data["pivotX"], data["pivotY"]) == (
                w, h, v["pivotX"], v["pivotY"]
            )
            real = {anim["name"]: anim for anim in data["anims"]}
            assert len(real) == 18
            for state in a:
                if state["id"] == "skill_2":
                    assert not any("skill_2_" + dr in real for dr in DIRECTIONS)
                    continue
                for dr in DIRECTIONS:
                    actual = real[state["id"] + "_" + dr]
                    assert actual["count"] == state["frames_per_direction"], (id_, state["id"], "count")
                    assert actual["fps"] == state["fps"], (id_, state["id"], "fps")
                    assert actual["loop"] == state["loop"], (id_, state["id"], "loop")
                    assert actual["hit"] == state["event_frame"], (id_, state["id"], "event_frame")
            width, height = png_dimensions(ATLAS / (id_ + ".png"))
            assert width == data["cols"] * w and height % h == 0
            assert width <= 8192 and height <= 8192
        else:
            assert record["production"]["art_status"] == "not_generated"
            assert record["production"]["generated_tracks"] == []

    assert tracks_total == 285 and frames_total == 3024, (tracks_total, frames_total)
    print("LOTE 1 VALIDADO: 10 demonios + 5 chefes; 285 trilhas propostas / 3024 frames planejados.")
    print("Oni/Grakk: JSONs e dimensoes PNG existentes conferidos. Demais sprites e habilidades pendentes.")
    print("Estilo existente intocado; ainda nao houve validacao do jogo Unity.")


if __name__ == "__main__":
    main()
