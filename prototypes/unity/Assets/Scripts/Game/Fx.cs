using UnityEngine;

namespace Aetheria
{
    /// <summary>One-shot animated effect (destroys itself at the end).</summary>
    public class FxSprite : MonoBehaviour
    {
        public SpriteAnim anim;
        public SpriteRenderer sr;
        public Vector2 vel;
        public float fadeAfter = -1, life = -1, spin, grow;
        float t;
        Color baseCol;

        void Start() { baseCol = sr.color; }

        void Update()
        {
            float dt = Time.deltaTime;
            t += dt;
            transform.position += (Vector3)(vel * dt);
            vel *= 1f - 3f * dt;
            if (spin != 0) transform.Rotate(0, 0, spin * dt);
            if (grow != 0) transform.localScale *= 1f + grow * dt;
            if (fadeAfter >= 0 && life > 0 && t > fadeAfter)
            {
                float k = 1 - Mathf.Clamp01((t - fadeAfter) / Mathf.Max(0.01f, life - fadeAfter));
                sr.color = new Color(baseCol.r, baseCol.g, baseCol.b, baseCol.a * k);
            }
            if (life > 0 && t >= life) Destroy(gameObject);
            else if (life < 0 && anim != null && anim.finished) Destroy(gameObject);
        }
    }

    /// <summary>Visual effects facade (sheet "Sprites/Fx/fx").</summary>
    public static class Fx
    {
        static Sheet sheet;
        public static Sheet Sheet => sheet ?? (sheet = Sheets.Load("Sprites/Fx/fx"));

        public static FxSprite Play(string name, Vector2 pos, float angle = 0, float scale = 1, bool additive = false, int order = 21000)
        {
            var go = new GameObject("fx_" + name);
            go.transform.position = pos;
            go.transform.rotation = Quaternion.Euler(0, 0, angle);
            go.transform.localScale = Vector3.one * scale;
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sharedMaterial = additive ? Util.AdditiveMaterial : Util.FxMaterial;
            sr.sortingOrder = order;
            var a = go.AddComponent<SpriteAnim>();
            a.sheet = Sheet;
            a.Play(name, true);
            var f = go.AddComponent<FxSprite>();
            f.anim = a;
            f.sr = sr;
            return f;
        }

        static float AngleOf(Facing f) => f == Facing.Right ? 0 : f == Facing.Up ? 90 : f == Facing.Left ? 180 : -90;

        public static void Slash(Vector2 pos, Facing f, int combo)
        {
            string n = combo == 3 ? "slash_heavy" : "slash";
            float ang = AngleOf(f);
            int order = Util.SortOrder(pos.y - 0.6f) + (f == Facing.Up ? -5 : 5);
            var fx = Play(n, pos + Util.FacingVec(f) * 0.25f, ang, combo == 3 ? 1.25f : 1.05f, true, order);
            // second swing mirrors the arc
            if (combo == 2) fx.transform.localScale = new Vector3(1.05f, -1.05f, 1);
        }

        public static void Claw(Vector2 pos, Facing f)
        {
            Play("claw", pos, AngleOf(f), 0.9f, false, Util.SortOrder(pos.y - 0.6f) + 5);
        }

        public static void HitSpark(Vector2 pos, bool crit)
        {
            Play(crit ? "hit_crit" : "hit", pos, Random.Range(0, 360f), crit ? 1.3f : 1f, true);
        }

        public static void Dust(Vector2 pos, float amount)
        {
            var f = Play("dust", pos + Random.insideUnitCircle * 0.1f, 0, 0.7f + amount * 0.4f, false, Util.SortOrder(pos.y) + 1);
            f.vel = Random.insideUnitCircle * 0.4f;
        }

        public static void Shockwave(Vector2 pos, float scale)
        {
            var f = Play("shock", pos, 0, scale, true, Util.SortOrder(pos.y) - 2);
            f.transform.localScale = new Vector3(scale, scale * 0.55f, 1);
        }

        public static void MagicCircle(Vector2 pos, int tier)
        {
            var f = Play("circle" + Mathf.Clamp(tier, 1, 3), pos + Vector2.up * 0.05f, 0, 1f, true, -30500);
            f.transform.localScale = new Vector3(1.1f, 0.55f, 1);
        }

        public static void Heal(Vector2 pos)
        {
            var f = Play("heal", pos + Vector2.up * 0.8f, 0, 1.2f, true, 22000);
        }

        public static void DemonPoof(Vector2 pos)
        {
            Play("poof", pos, 0, 1.3f, false, Util.SortOrder(pos.y) - 3);
            for (int i = 0; i < 10; i++)
            {
                var e = Ember(pos + Random.insideUnitCircle * 0.4f, new Color(0.85f, 0.35f, 1f));
                e.vel = Random.insideUnitCircle * 2.5f + Vector2.up * 1.5f;
            }
        }

        public static FxSprite Ember(Vector2 pos, Color c)
        {
            var go = new GameObject("ember");
            go.transform.position = pos;
            go.transform.localScale = Vector3.one * Random.Range(0.12f, 0.24f);
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = Util.SoftCircle;
            sr.sharedMaterial = Util.AdditiveMaterial;
            sr.color = c;
            sr.sortingOrder = 21500;
            var f = go.AddComponent<FxSprite>();
            f.sr = sr;
            f.life = Random.Range(0.3f, 0.55f);
            f.fadeAfter = 0.05f;
            f.vel = Random.insideUnitCircle * 0.6f + Vector2.up * 0.4f;
            f.grow = -1.2f;
            return f;
        }

        public static SpriteRenderer Glow(Transform parent, Color c, float size, float alpha)
        {
            var go = new GameObject("glow");
            go.transform.SetParent(parent, false);
            go.transform.localScale = Vector3.one * size;
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = Util.SoftCircle;
            sr.sharedMaterial = Util.AdditiveMaterial;
            sr.color = new Color(c.r, c.g, c.b, alpha);
            sr.sortingOrder = 20500;
            return sr;
        }

        public static void Alert(Actor a)
        {
            var f = Play("alert", a.Pos + Vector2.up * 2.0f, 0, 0.8f, false, 23000);
            f.transform.SetParent(a.transform, true);
        }

        public static void DamageNumber(Vector2 pos, float dmg, bool crit, bool onPlayer)
        {
            Hud.I?.Number(pos, Mathf.RoundToInt(dmg).ToString(), crit, onPlayer);
        }

        public static void Toast(string text, Color c, Vector2? at = null)
        {
            Vector2 p = at ?? (Player.I != null ? Player.I.Pos + Vector2.up * 2.4f : Vector2.zero);
            Hud.I?.Float(p, text, c);
        }
    }
}
