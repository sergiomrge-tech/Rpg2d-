using UnityEngine;

namespace Aetheria
{
    /// <summary>
    /// Concrete boss abilities on animation hit frames, not concept-only FX.
    /// Each of five optional insectoid bosses has TWO mechanically different skills.
    /// All damage uses actual Player.Hurt, projectiles or a timed hazard.
    /// </summary>
    public static class InsectBossSkills
    {
        public static void Execute(Enemy boss, int slot, Vector2 forward)
        {
            if (boss == null || boss.dead) return;
            Vector2 point = boss.Pos;
            Vector2 dir = forward.sqrMagnitude > 0.001f ? forward.normalized : Util.FacingVec(boss.facing);
            Player player = Player.I;
            if (player == null || player.dead) return;
            switch (boss.def.id)
            {
                case "mantis_high_reaper":
                    if (slot == 1)
                    {
                        // Scythe fan: closer and frontal, with lunge driven by Enemy.Cast.
                        Fx.Slash(point + Vector2.up * .65f, boss.facing, 3);
                        Fx.Claw(point + dir * 1.0f + Vector2.up * .7f, boss.facing);
                        Vector2 toward = player.Pos - point;
                        float dot = toward.sqrMagnitude > .01f ? Vector2.Dot(dir, toward.normalized) : 1f;
                        if (toward.magnitude < 3.1f && dot > .30f)
                            player.Hurt(boss.dmg * 1.40f, point, 9f, 30);
                    }
                    else
                    {
                        // Different signature: airborne execution dive at the locked direction.
                        Fx.Shockwave(point, 2.15f);
                        Fx.Slash(point + dir * 1.3f + Vector2.up * .5f, boss.facing, 3);
                        if ((player.Pos - point).magnitude < 2.45f)
                        {
                            if (player.Hurt(boss.dmg * 1.75f, point, 11f, 35))
                                player.ApplySonicDisrupt(.36f);
                        }
                        CameraRig.Shake(.28f, .24f);
                    }
                    break;

                case "scarab_colossus":
                    if (slot == 1)
                    {
                        // Seismic stomp with center-range AOE, independent of normal melee.
                        Fx.Shockwave(point, 3.2f);
                        for (int i = 0; i < 10; i++)
                        {
                            float a = i * Mathf.PI * 2f / 10f;
                            Vector2 edge = point + new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * 2.0f;
                            Fx.Dust(edge, 1.0f);
                        }
                        if ((player.Pos - point).magnitude < 3.2f)
                            player.Hurt(boss.dmg * 1.15f, point, 9f, 35);
                        CameraRig.Shake(.3f, .30f);
                    }
                    else
                    {
                        // Split shell acts as armour, while launching a radially spaced barrage.
                        boss.ActivateBossGuard(3.8f);
                        Fx.MagicCircle(point, 2);
                        for (int i = 0; i < 8; i++)
                        {
                            float a = i * Mathf.PI * 2f / 8f;
                            Vector2 shot = new Vector2(Mathf.Cos(a), Mathf.Sin(a));
                            Projectile.InsectNeedle(point + shot * 1f + Vector2.up * .55f,
                                                    shot, boss.dmg * .42f);
                        }
                        Fx.Shockwave(point, 1.6f);
                    }
                    break;

                case "moth_oracle":
                    if (slot == 1)
                    {
                        // Hex dust is a travelling projectile pattern and actually slows.
                        Fx.MagicCircle(point, 3);
                        Vector2 from = point + Vector2.up * .95f;
                        for (int i = -1; i <= 1; i++)
                        {
                            float angle = i * .18f;
                            Vector2 aim = Rot(dir, angle);
                            Projectile.HexSpore(from + aim * .5f, aim, boss.dmg * .65f);
                        }
                    }
                    else
                    {
                        // Ritual eye triggers close-range pulse; separate animation and hit-frame.
                        Fx.MagicCircle(point, 3);
                        Fx.Shockwave(point, 3.65f);
                        if ((player.Pos - point).magnitude < 3.65f)
                        {
                            if (player.Hurt(boss.dmg * 1.00f, point, 5f, 15))
                            {
                                player.ApplyHexSlow(2.8f);
                                player.ApplySonicDisrupt(.45f);
                            }
                        }
                        CameraRig.Shake(.11f, .20f);
                    }
                    break;

                case "queen_vespara":
                    if (slot == 1)
                    {
                        // Three organic venom darts, distinct from generic fireballs.
                        for (int i = -1; i <= 1; i++)
                        {
                            Vector2 aim = Rot(dir, i * .17f);
                            Projectile.VenomDart(point + Vector2.up * .85f + aim * .5f,
                                                 aim, boss.dmg * .56f);
                        }
                        for (int i = 0; i < 5; i++)
                        {
                            var e = Fx.Ember(point + Vector2.up * .8f + Random.insideUnitCircle * .35f,
                                             new Color(.54f, .93f, .42f));
                            e.vel = Random.insideUnitCircle * 2f;
                        }
                    }
                    else
                    {
                        // Royal stinger dive: Enemy Cast2 drives dash; this is the impact window.
                        Fx.Claw(point + Vector2.up * .8f, boss.facing);
                        Fx.Shockwave(point, 1.8f);
                        if ((player.Pos - point).magnitude < 2.1f)
                        {
                            if (player.Hurt(boss.dmg * 1.5f, point, 8f, 25))
                                player.ApplyVenom(3.8f);
                        }
                        InsectHazard.SpawnPoison(point, 1.6f, 2.4f, 2.3f);
                    }
                    break;

                case "brood_tyrant":
                    if (slot == 1)
                    {
                        // Summon a controlled number of real, independent ant minions.
                        Fx.MagicCircle(point, 1);
                        int living = 0;
                        foreach (var e in Enemy.All)
                            if (!e.dead && e.def.id == "ant_guard" &&
                                (e.Pos - point).sqrMagnitude < 120f) living++;
                        for (int i = 0; i < Mathf.Min(2, Mathf.Max(0, 4 - living)); i++)
                        {
                            Vector2 where = point + new Vector2(i == 0 ? -1.7f : 1.7f, -1.15f);
                            if (World.I != null && World.I.BlockedAt(where)) where = point;
                            Enemy.Spawn("ant_guard", where, Mathf.Max(1, boss.level - 1));
                            Fx.DemonPoof(where);
                        }
                    }
                    else
                    {
                        // Hive rupture: radial corrosion and actual persistent no-go zones.
                        Fx.Shockwave(point, 3.6f);
                        if ((player.Pos - point).magnitude < 3.4f)
                        {
                            if (player.Hurt(boss.dmg * 1.2f, point, 10f, 35))
                                player.ApplyVenom(2.1f);
                        }
                        for (int i = 0; i < 4; i++)
                        {
                            float a = i * Mathf.PI / 2f + .28f;
                            Vector2 pos = point + new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * 2.0f;
                            if (World.I != null && World.I.BlockedAt(pos)) continue;
                            InsectHazard.SpawnPoison(pos, 1.4f, 2.8f, 2.0f);
                        }
                        CameraRig.Shake(.36f, .32f);
                    }
                    break;
            }
            Sfx.Play(slot == 2 ? "boom" : "swing_heavy", .54f, slot == 2 ? .92f : 1.07f);
        }

        static Vector2 Rot(Vector2 v, float a)
        {
            float c = Mathf.Cos(a), s = Mathf.Sin(a);
            return new Vector2(v.x*c-v.y*s, v.x*s+v.y*c);
        }
    }
}
