using UnityEngine;

namespace Aetheria
{
    /// <summary>Sylra, elven archer: follows the hero, keeps distance from demons and shoots arrows.</summary>
    public class Companion : Actor
    {
        public static Companion I;
        float shootCd = 1f;
        float shootT = -1;
        Enemy target;

        public static Companion Spawn(Vector2 at)
        {
            var go = new GameObject("Sylra");
            go.transform.position = at;
            var c = go.AddComponent<Companion>();
            c.Build("Sprites/Chars/sylra", 1.2f, 0.4f, 0.28f);
            c.rb.mass = 0.5f;
            c.col.isTrigger = true;   // never blocks the hero in corridors
            c.maxHp = c.hp = 1;
            c.anim.Play("idle");
            I = c;
            return c;
        }

        protected override void Update()
        {
            base.Update();
            var p = Player.I;
            if (p == null) return;
            float dt = Time.deltaTime;
            shootCd -= dt;
            Vector2 toP = p.Pos - Pos;
            float d = toP.magnitude;
            if (d > 14f) { transform.position = p.Pos + Random.insideUnitCircle * 1.5f; return; }   // catch up after travel

            target = Enemy.Nearest(Pos, 8.5f);
            if (shootT >= 0)
            {
                shootT += dt;
                rb.velocity = Vector2.zero;
                if (shootT > 0.32f && target != null && !target.dead)
                {
                    Vector2 dir = (target.Pos + Vector2.up * 0.5f - (Pos + Vector2.up * 0.8f)).normalized;
                    Projectile.Arrow(Pos + Vector2.up * 0.8f + dir * 0.4f, dir, 9f + 2.4f * p.gs.level);
                    Sfx.Play("swing", 0.25f, 1.6f);
                    shootT = -1;
                }
                else if (shootT > 0.6f) shootT = -1;
                return;
            }
            if (target != null && shootCd <= 0 && !p.dead)
            {
                shootCd = 1.35f;
                shootT = 0;
                Face(Util.FacingFrom(target.Pos - Pos, facing));
                anim.Play("cast", true);
                return;
            }
            // follow: stay ~2 tiles behind/side of the hero
            Vector2 want = p.Pos - Util.FacingVec(p.facing) * 1.6f + new Vector2(-Util.FacingVec(p.facing).y, Util.FacingVec(p.facing).x) * 0.9f;
            Vector2 to = want - Pos;
            if (to.magnitude > 0.5f)
            {
                bool run = to.magnitude > 3.5f;
                Face(Util.FacingFrom(to, facing));
                anim.Play(run ? "run" : "walk");
                rb.velocity = to.normalized * (run ? 6.6f : 4.1f);
            }
            else
            {
                rb.velocity = Vector2.zero;
                anim.Play("idle");
            }
        }

        public override bool Hurt(float dmg, Vector2 from, float knockback, float poiseDmg, bool crit = false) => false;
        protected override void Die() { }
    }
}
