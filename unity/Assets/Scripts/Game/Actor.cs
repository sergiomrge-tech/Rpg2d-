using UnityEngine;

namespace Aetheria
{
    /// <summary>Shared body for player / demons / NPCs: animated sprite, shadow, physics, hp, hit flash.</summary>
    public abstract class Actor : MonoBehaviour
    {
        public SpriteAnim anim;
        public SpriteRenderer body;
        public Rigidbody2D rb;
        public CircleCollider2D col;
        public float hp, maxHp;
        public bool dead;
        public Facing facing = Facing.Down;
        public float invuln;
        public float poise, maxPoise;

        protected Vector2 knock;
        float flash;
        float dissolve;
        MaterialPropertyBlock mpb;
        static readonly int FlashId = Shader.PropertyToID("_Flash");
        static readonly int FlashColId = Shader.PropertyToID("_FlashColor");
        static readonly int DissolveId = Shader.PropertyToID("_Dissolve");
        Color flashColor = Color.white;

        public Vector2 Pos => transform.position;

        protected void Build(string sheetPath, float shadowW, float shadowH, float radius, float scale = 1f)
        {
            var spriteGo = new GameObject("sprite");
            spriteGo.transform.SetParent(transform, false);
            spriteGo.transform.localScale = Vector3.one * scale;
            body = spriteGo.AddComponent<SpriteRenderer>();
            body.sharedMaterial = Util.FxMaterial;
            anim = spriteGo.AddComponent<SpriteAnim>();
            anim.sheet = Sheets.Load(sheetPath);
            Util.Shadow(transform, shadowW * scale, shadowH * scale);
            rb = gameObject.AddComponent<Rigidbody2D>();
            rb.gravityScale = 0;
            rb.freezeRotation = true;
            rb.interpolation = RigidbodyInterpolation2D.Interpolate;
            rb.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
            col = gameObject.AddComponent<CircleCollider2D>();
            col.radius = radius;
            col.offset = new Vector2(0, radius * 0.6f);
            var ys = gameObject.AddComponent<YSort>();
            ys.renderers = new[] { body };
            mpb = new MaterialPropertyBlock();
        }

        public void Flash(Color c, float amount = 1f)
        {
            flashColor = c;
            flash = amount;
        }

        public void StartDissolve() { dissolve = 0.001f; }

        protected virtual void Update()
        {
            if (invuln > 0) invuln -= Time.deltaTime;
            if (flash > 0) flash = Mathf.Max(0, flash - Time.deltaTime * 7f);
            if (dissolve > 0) dissolve = Mathf.Min(1, dissolve + Time.deltaTime * 0.9f);
            if (body != null && mpb != null)
            {
                body.GetPropertyBlock(mpb);
                mpb.SetFloat(FlashId, flash);
                mpb.SetColor(FlashColId, flashColor);
                mpb.SetFloat(DissolveId, dissolve);
                body.SetPropertyBlock(mpb);
            }
        }

        protected void Face(Facing f)
        {
            facing = f;
            anim.SetFacing(f);
        }

        /// <summary>Apply damage. Returns true if the hit landed.</summary>
        public virtual bool Hurt(float dmg, Vector2 from, float knockback, float poiseDmg, bool crit = false)
        {
            if (dead || invuln > 0) return false;
            hp -= dmg;
            Flash(Color.white);
            Vector2 dir = (Pos - from).normalized;
            if (dir.sqrMagnitude < 0.01f) dir = Vector2.down;
            knock = dir * knockback;
            poise -= poiseDmg;
            Fx.DamageNumber(Pos + Vector2.up * 1.6f, dmg, crit, this is Player);
            Fx.HitSpark(Pos + Vector2.up * 0.8f + dir * -0.2f, crit);
            if (hp <= 0)
            {
                hp = 0;
                Die();
            }
            return true;
        }

        protected abstract void Die();
    }
}
