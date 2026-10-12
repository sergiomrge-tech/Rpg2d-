using UnityEngine;

namespace Aetheria
{
    /// <summary>Drop tables scale with demon level: more gold, better odds for rare materials.</summary>
    public static class Loot
    {
        public static void Drop(DemonDef def, int level, Vector2 at)
        {
            foreach (var (item, chance, min, max) in def.drops)
            {
                float c = chance * (item == "gold" ? 1f : 1f + 0.25f * (level - 1));
                if (Random.value > c) continue;
                int n = Random.Range(min, max + 1);
                if (item == "gold") n = Mathf.RoundToInt(n * (1 + 0.6f * (level - 1)));
                Pickup.Spawn(item, n, at);
            }
        }
    }

    public class Pickup : MonoBehaviour
    {
        public string item;
        public int count;
        float t, z, vz;
        Vector2 vxy;
        Transform spr;
        SpriteRenderer glow;
        bool collecting;

        public static void Spawn(string item, int count, Vector2 at)
        {
            var go = new GameObject("loot_" + item);
            go.transform.position = at;
            var p = go.AddComponent<Pickup>();
            p.item = item;
            p.count = count;
            p.vxy = Random.insideUnitCircle * 1.6f;
            p.vz = Random.Range(5f, 7f);
            var s = new GameObject("icon");
            s.transform.SetParent(go.transform, false);
            var sr = s.AddComponent<SpriteRenderer>();
            sr.sprite = Icons.Get(Data.Items[item].icon);
            s.transform.localScale = Vector3.one * 0.7f;
            p.spr = s.transform;
            var def = Data.Items[item];
            p.glow = Fx.Glow(go.transform, Data.RarityColors[(int)def.rarity], def.rarity >= Rarity.Rare ? 2.2f : 1.2f, def.rarity >= Rarity.Rare ? 0.6f : 0.3f);
            Util.Shadow(go.transform, 0.45f, 0.16f, 0.28f);
            var ys = go.AddComponent<YSort>();
            ys.renderers = new[] { sr };
            if (def.rarity >= Rarity.Rare) Fx.Toast(def.name + "!", Data.RarityColors[(int)def.rarity], at + Vector2.up * 2f);
        }

        void Update()
        {
            float dt = Time.deltaTime;
            t += dt;
            if (vz != 0 || z > 0)
            {
                vz -= 22f * dt;
                z += vz * dt;
                transform.position += (Vector3)(vxy * dt);
                if (z <= 0) { z = 0; vz = Mathf.Abs(vz) > 2f ? -vz * 0.35f : 0; vxy *= 0.5f; }
            }
            float bob = z + 0.12f + Mathf.Sin(t * 3f) * 0.06f;
            spr.localPosition = new Vector3(0, bob, 0);
            var p = Player.I;
            if (p == null || p.dead || t < 0.6f) return;
            Vector2 d = p.Pos + Vector2.up * 0.4f - (Vector2)transform.position;
            if (d.magnitude < 2.2f) collecting = true;
            if (collecting)
            {
                transform.position += (Vector3)(d.normalized * Mathf.Min(d.magnitude, (6f + t * 4f) * dt));
                if (d.magnitude < 0.3f)
                {
                    p.gs.Add(item, count);
                    var def = Data.Items[item];
                    Hud.I?.LootFeed(def, count);
                    Sfx.Play(item == "gold" ? "coin" : "pickup", 0.45f, Random.Range(0.95f, 1.1f));
                    Destroy(gameObject);
                }
            }
        }
    }
}
