using UnityEngine;

namespace Aetheria
{
    /// <summary>
    /// Actual gameplay abilities for the three insectoid pilots. Events fire only
    /// from the hit frames of their authored sprite atlases (Enemy.OnAnimHit).
    /// All damage checks use world-space positions and respect player i-frames.
    /// </summary>
    public static class InsectCombat
    {
        public static void Attack(Enemy e, Player player)
        {
            if (player == null || player.dead) return;
            Vector2 toward = player.Pos - e.Pos;
            Vector2 f = Util.FacingVec(e.facing);
            float dist = toward.magnitude;
            float facingDot = dist > .01f ? Vector2.Dot(toward / dist, f) : 1f;

            switch (e.def.combatStyle)
            {
                case "mantis":
                    // Double organic scythe strike, front arc, reach > imp claw.
                    Fx.Slash(e.Pos + Vector2.up * .5f, e.facing, 2);
                    if (dist <= 2.15f && facingDot > .25f)
                        player.Hurt(Mathf.Round(e.dmg * 1.10f), e.Pos, 7f, 21);
                    break;
                case "scarab":
                    // Horn impact: short range but heavy poise and push.
                    Fx.Shockwave(e.Pos + f * .55f, 1.05f);
                    CameraRig.Shake(.08f, .11f);
                    if (dist <= 1.8f && facingDot > .1f)
                        player.Hurt(Mathf.Round(e.dmg * 1.15f), e.Pos, 10f, 31);
                    break;
                case "moth":
                    // Wing-lash defensive melee.
                    Fx.Claw(e.Pos + f * .55f + Vector2.up * .65f, e.facing);
                    if (dist <= 1.6f && facingDot > .0f)
                        player.Hurt(Mathf.Round(e.dmg * .8f), e.Pos, 3f, 8);
                    break;
            }
        }

        public static void Skill(Enemy e, Player player)
        {
            if (player == null || player.dead) return;
            Vector2 f = Util.FacingVec(e.facing);
            Vector2 v = player.Pos - e.Pos;
            float d = v.magnitude;
            float angle = d < .01f ? 1f : Vector2.Dot(v / d, f);
            switch (e.def.combatStyle)
            {
                case "mantis":
                    // Lunge past the target. Independent from melee animation;
                    // no direct teleporting or unsafe transform jumps.
                    e.rb.velocity = f * 11f;
                    Fx.Slash(e.Pos + f + Vector2.up * .6f, e.facing, 3);
                    if (d < 3.15f && angle > .50f)
                        player.Hurt(Mathf.Round(e.dmg * 1.40f), e.Pos, 9f, 25);
                    break;
                case "scarab":
                    // Area shockwave; unlike the linear mantis cut, safe to
                    // dodge by leaving the marked radius during cast windup.
                    Fx.Shockwave(e.Pos, 1.8f);
                    CameraRig.Shake(.14f, .23f);
                    if (d < 2.6f)
                        player.Hurt(Mathf.Round(e.dmg * 1.25f), e.Pos, 12f, 32);
                    break;
                case "moth":
                    // Distinct cone hex. Drains stamina/mana only on a hit;
                    // damage goes through Player.Hurt so dodges still work.
                    Fx.MagicCircle(e.Pos, 1);
                    if (d <= 7.2f && angle > .53f)
                    {
                        if (player.Hurt(Mathf.Round(e.dmg * .75f), e.Pos, 2.5f, 10))
                        {
                            player.mp = Mathf.Max(0f, player.mp - 8f);
                            player.st = Mathf.Max(0f, player.st - 17f);
                            Fx.Toast("Poeira maldita!", new Color(.59f, .91f, 1f),
                                player.Pos + Vector2.up * 1.5f);
                        }
                    }
                    break;
            }
        }
    }
}
