using UnityEngine;

namespace Aetheria
{
    /// <summary>Timed, visible poison cloud left by a plague roach.
    /// Runs in the actual Unity world; applies venom only when the player is inside.
    /// Uses existing glow materials, no fake sprite or editor screenshot.</summary>
    public sealed class InsectHazard : MonoBehaviour
    {
        float life, totalLife, radius, damage, tickLeft;
        SpriteRenderer cloud;
        float particleClock;

        public static InsectHazard SpawnPoison(Vector2 point, float size, float seconds, float tickDamage)
        {
            var obj = new GameObject("roach_poison_cloud");
            obj.transform.position = point;
            var h = obj.AddComponent<InsectHazard>();
            h.radius = size;
            h.life = h.totalLife = seconds;
            h.damage = tickDamage;
            h.tickLeft = .2f;
            var display = new GameObject("toxic_area");
            display.transform.SetParent(obj.transform, false);
            display.transform.localScale = new Vector3(size * 2.0f, size * 1.15f, 1);
            h.cloud = display.AddComponent<SpriteRenderer>();
            h.cloud.sprite = Util.SoftCircle;
            h.cloud.sharedMaterial = Util.AdditiveMaterial;
            h.cloud.color = new Color(.32f, .72f, .29f, .32f);
            h.cloud.sortingOrder = Util.SortOrder(point.y) - 4;
            return h;
        }

        void Update()
        {
            float dt = Time.deltaTime;
            life -= dt;
            if (life <= 0f) { Destroy(gameObject); return; }
            float fade = Mathf.Clamp01(life / Mathf.Max(.01f, totalLife));
            cloud.color = new Color(.32f, .72f, .29f, .32f * fade);
            var p = Player.I;
            tickLeft -= dt;
            if (tickLeft <= 0f)
            {
                tickLeft = .85f;
                if (p != null && !p.dead && (p.Pos - (Vector2)transform.position).magnitude < radius)
                {
                    if (p.Hurt(damage, transform.position, 0f, 0f))
                        p.ApplyVenom(1.15f);
                }
            }
            particleClock -= dt;
            if (particleClock <= 0)
            {
                particleClock = .2f;
                var e = Fx.Ember((Vector2)transform.position + Random.insideUnitCircle * radius * .65f,
                                 new Color(.48f, .83f, .32f));
                e.vel = Vector2.up * .5f + Random.insideUnitCircle * .3f;
            }
        }
    }
}
