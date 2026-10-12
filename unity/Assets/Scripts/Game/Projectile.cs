using UnityEngine;

namespace Aetheria
{
    public class Projectile : MonoBehaviour
    {
        public Vector2 vel;
        public float dmg, life = 2.2f, radius = 0.35f;
        public bool friendly;
        public bool inflictsHexSlow;
        public bool tealTrail;
        public bool inflictsVenom;
        public int tier;
        public string hitFx = "hit";
        SpriteAnim anim;
        SpriteRenderer glow;
        float trailT;

        static Projectile Make(string animName, Vector2 pos, Vector2 dir, float speed, float dmg, bool friendly, float scale, Color glowCol)
        {
            var go = new GameObject("proj_" + animName);
            go.transform.position = pos;
            var p = go.AddComponent<Projectile>();
            p.vel = dir.normalized * speed;
            p.dmg = dmg;
            p.friendly = friendly;
            var s = new GameObject("spr");
            s.transform.SetParent(go.transform, false);
            s.transform.localScale = Vector3.one * scale;
            s.transform.rotation = Quaternion.Euler(0, 0, Mathf.Atan2(dir.y, dir.x) * Mathf.Rad2Deg);
            var sr = s.AddComponent<SpriteRenderer>();
            sr.sharedMaterial = Util.AdditiveMaterial;
            p.anim = s.AddComponent<SpriteAnim>();
            p.anim.sheet = Fx.Sheet;
            p.anim.Play(animName, true);
            sr.sortingOrder = 20000;
            p.glow = Fx.Glow(go.transform, glowCol, 1.8f * scale, 0.55f);
            Util.Shadow(go.transform, 0.5f, 0.18f, 0.25f).transform.localPosition = new Vector3(0, -0.8f, 0);
            return p;
        }

        public static Projectile Spark(Vector2 pos, Vector2 dir, float dmg, int tier, bool friendly)
        {
            var col = tier == 1 ? new Color(0.45f, 0.8f, 1f) : tier == 2 ? new Color(1f, 0.55f, 0.15f) : new Color(0.75f, 0.45f, 1f);
            var p = Make("spark" + Mathf.Clamp(tier, 1, 3), pos, dir, 13f + tier, dmg, friendly, 1f + 0.15f * tier, col);
            p.tier = tier;
            p.hitFx = tier == 1 ? "hit_spark" : "hit_fire";
            p.radius = 0.4f + 0.1f * tier;
            return p;
        }

        public static Projectile Fireball(Vector2 pos, Vector2 dir, float dmg)
        {
            var p = Make("fireball", pos, dir, 6.2f, dmg, false, 0.9f, new Color(1f, 0.5f, 0.15f));
            p.hitFx = "hit_fire";
            p.life = 2.6f;
            return p;
        }

        // Moth's curse: distinct projectile color, flight speed and player debuff.
        public static Projectile HexSpore(Vector2 pos, Vector2 dir, float dmg)
        {
            var p = Make("fireball", pos, dir, 4.4f, dmg, false, .78f,
                new Color(.73f, .39f, .88f));
            p.hitFx = "hit_spark";
            p.life = 3.1f;
            p.radius = .46f;
            p.inflictsHexSlow = true;
            return p;
        }

        public static Projectile InsectNeedle(Vector2 pos, Vector2 dir, float dmg)
        {
            // Distinct rapid dragonfly lancet: not a fireball and no fire-colored trail.
            var p = Make("spark1", pos, dir, 15.5f, dmg, false, .67f,
                         new Color(.37f, .90f, .87f));
            p.hitFx = "hit_spark";
            p.radius = .25f;
            p.life = 1.3f;
            p.tealTrail = true;
            return p;
        }

        // Queen's actual venom bolt: separate colour, speed, damage and debuff.
        public static Projectile VenomDart(Vector2 pos, Vector2 dir, float dmg)
        {
            var p = Make("spark2", pos, dir, 10.4f, dmg, false, .86f,
                         new Color(.67f, .95f, .33f));
            p.radius = .34f;
            p.hitFx = "hit_spark";
            p.life = 2.3f;
            p.inflictsVenom = true;
            return p;
        }

        void Update()
        {
            float dt = Time.deltaTime;
            transform.position += (Vector3)(vel * dt);
            life -= dt;
            trailT -= dt;
            if (trailT <= 0)
            {
                trailT = 0.035f;
                Fx.Ember(transform.position, inflictsVenom ? new Color(.67f, .95f, .36f) :
                    tealTrail ? new Color(.36f, .96f, .90f) :
                    inflictsHexSlow ? new Color(.72f, .39f, .94f) :
                    friendly && tier == 1 ? new Color(0.6f, 0.9f, 1f) : new Color(1f, 0.6f, 0.2f));
            }
            if (glow != null) glow.transform.localScale = Vector3.one * (1.8f + Mathf.Sin(Time.time * 30) * 0.15f);
            Vector2 p = transform.position;
            if (friendly)
            {
                foreach (var e in Enemy.All)
                {
                    if (e.dead) continue;
                    if ((e.Pos + Vector2.up * 0.6f - p).magnitude < radius + 0.4f)
                    {
                        bool crit = Random.value < 0.1f;
                        e.Hurt(Mathf.Round(dmg * Random.Range(0.92f, 1.08f) * (crit ? 1.7f : 1f)), p - vel.normalized, 6f, 16, crit);
                        Explode();
                        return;
                    }
                }
            }
            else if (Player.I != null && !Player.I.dead)
            {
                if ((Player.I.Pos + Vector2.up * 0.6f - p).magnitude < radius + 0.3f)
                {
                    if (Player.I.Hurt(Mathf.Round(dmg), p - vel.normalized, 6f, 15))
                    {
                        if (inflictsHexSlow) Player.I.ApplyHexSlow(2.1f);
                        if (inflictsVenom) Player.I.ApplyVenom(3.0f);
                        Explode(); return;
                    }
                }
            }
            if (World.I != null && World.I.BlockedAt(p + Vector2.down * 0.8f, true)) { Explode(); return; }
            if (life <= 0) Explode();
        }

        void Explode()
        {
            Fx.Play(hitFx, transform.position, 0, 1.1f + 0.15f * tier, true);
            if (!friendly || tier > 1) CameraRig.Shake(0.07f, 0.1f);
            Sfx.Play("boom", 0.35f, Random.Range(0.9f, 1.15f));
            Destroy(gameObject);
        }
    }
}
