using System;
using System.Collections.Generic;
using UnityEngine;

namespace Aetheria
{
    [Serializable] public class MapProp { public string kind; public float x, y; }
    [Serializable] public class MapSpawn { public string kind; public float x, y; public int level; }
    [Serializable] public class MapNpc { public string id; public float x, y; public string look; public string facing; }
    [Serializable] public class MapExit { public string to; public float x, y, w, h; }

    [Serializable]
    public class MapData
    {
        public string name;
        public int w, h, tile, chunk, chunksX, chunksY;
        public string blocked;
        public float playerX, playerY;
        public MapProp[] props;
        public MapSpawn[] spawns;
        public MapNpc[] npcs;
        public MapExit[] exits;
    }

    /// <summary>Builds a map: baked ground chunks, y-sorted props with colliders, water blockers, spawns.</summary>
    public class World : MonoBehaviour
    {
        public static World I;
        public MapData data;
        public Rect bounds;
        bool[] blocked;
        readonly List<GameObject> spawned = new List<GameObject>();
        readonly List<Transform> swaying = new List<Transform>();

        public static World Load(string name)
        {
            var go = new GameObject("World_" + name);
            var w = go.AddComponent<World>();
            I = w;
            var txt = Resources.Load<TextAsset>("Maps/" + name);
            w.data = JsonUtility.FromJson<MapData>(txt.text);
            w.Build();
            return w;
        }

        void Build()
        {
            var d = data;
            float u = d.tile / Sheets.PPU;   // world units per tile (=1)
            bounds = new Rect(0, -d.h * u, d.w * u, d.h * u);
            // ground
            for (int j = 0; j < d.chunksY; j++)
            for (int i = 0; i < d.chunksX; i++)
            {
                var tex = Sheets.Tex($"Maps/{d.name}/g_{i}_{j}");
                if (tex == null) continue;
                var sp = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0, 1), Sheets.PPU, 0, SpriteMeshType.FullRect);
                var g = new GameObject($"ground_{i}_{j}");
                g.transform.SetParent(transform, false);
                g.transform.position = Util.MapToWorld(i * d.chunk, j * d.chunk);
                var sr = g.AddComponent<SpriteRenderer>();
                sr.sprite = sp;
                sr.sortingOrder = Util.GroundOrder;
            }
            // collision grid (water)
            blocked = new bool[d.w * d.h];
            for (int k = 0; k < blocked.Length && k < d.blocked.Length; k++) blocked[k] = d.blocked[k] == '1';
            BuildWaterColliders();
            BuildBorders();
            // props
            foreach (var p in d.props) SpawnProp(p);
        }

        void BuildWaterColliders()
        {
            var d = data;
            // merge horizontal runs of blocked tiles into boxes
            for (int y = 0; y < d.h; y++)
            {
                int x = 0;
                while (x < d.w)
                {
                    if (!blocked[y * d.w + x]) { x++; continue; }
                    int x0 = x;
                    while (x < d.w && blocked[y * d.w + x]) x++;
                    var bc = gameObject.AddComponent<BoxCollider2D>();
                    bc.size = new Vector2(x - x0, 1) * 0.92f;
                    bc.offset = new Vector2((x0 + x) * 0.5f, -(y + 0.5f));
                }
            }
        }

        void BuildBorders()
        {
            var b = bounds;
            void Box(Vector2 c, Vector2 s)
            {
                var bc = gameObject.AddComponent<BoxCollider2D>();
                bc.offset = c;
                bc.size = s;
            }
            Box(new Vector2(b.center.x, b.yMax + 0.5f), new Vector2(b.width + 2, 1));
            Box(new Vector2(b.center.x, b.yMin - 0.5f), new Vector2(b.width + 2, 1));
            Box(new Vector2(b.xMin - 0.5f, b.center.y), new Vector2(1, b.height + 2));
            Box(new Vector2(b.xMax + 0.5f, b.center.y), new Vector2(1, b.height + 2));
        }

        void SpawnProp(MapProp p)
        {
            var info = Sheets.Prop(p.kind);
            var go = new GameObject(p.kind);
            go.transform.SetParent(transform, false);
            go.transform.position = Util.MapToWorld(p.x, p.y);
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = Sheets.PropSprite(p.kind);
            bool flat = p.kind == "bridge" || p.kind == "flowers";
            sr.sortingOrder = flat ? -30800 : Util.SortOrder(go.transform.position.y);
            if (p.kind == "tuft") sr.sortingOrder = Util.SortOrder(go.transform.position.y) - 1;
            if (info != null && info.colW > 0)
            {
                var bc = go.AddComponent<BoxCollider2D>();
                bc.size = new Vector2(info.colW, info.colH) / Sheets.PPU;
                bc.offset = new Vector2(0, (info.colH * 0.5f - info.colY) / Sheets.PPU);
            }
            if (p.kind.StartsWith("tree") || p.kind.StartsWith("bush") || p.kind == "tuft") swaying.Add(go.transform);
            if (p.kind == "lamp") Fx.Glow(go.transform, new Color(1f, 0.82f, 0.45f), 2.6f, 0.22f).transform.localPosition = new Vector3(0, 1.55f, 0);
        }

        void Update()
        {
            // gentle wind: shear-like sway via small rotation + scale around the base
            float t = Time.time;
            for (int i = 0; i < swaying.Count; i++)
            {
                var tr = swaying[i];
                float ph = tr.position.x * 0.35f + tr.position.y * 0.2f;
                float a = Mathf.Sin(t * 1.3f + ph) * 0.9f + Mathf.Sin(t * 2.9f + ph * 1.7f) * 0.35f;
                tr.localRotation = Quaternion.Euler(0, 0, a);
                tr.localScale = new Vector3(1 + Mathf.Sin(t * 1.1f + ph) * 0.006f, 1 + Mathf.Sin(t * 1.7f + ph) * 0.01f, 1);
            }
        }

        public bool BlockedAt(Vector2 w, bool forProjectile = false)
        {
            if (!bounds.Contains(w)) return true;
            if (forProjectile) return false;   // projectiles fly over water
            int x = Mathf.FloorToInt(w.x), y = Mathf.FloorToInt(-w.y);
            if (x < 0 || y < 0 || x >= data.w || y >= data.h) return true;
            return blocked[y * data.w + x];
        }

        public void SpawnActors()
        {
            foreach (var s in data.spawns)
                spawned.Add(Enemy.Spawn(s.kind, Util.MapToWorld(s.x, s.y), s.level).gameObject);
            foreach (var n in data.npcs)
                spawned.Add(Npc.Spawn(n).gameObject);
        }

        public void RespawnEnemies()
        {
            foreach (var s in data.spawns)
            {
                bool alive = false;
                var at = Util.MapToWorld(s.x, s.y);
                foreach (var e in Enemy.All) if (!e.dead && (e.Pos - at).magnitude < 4f) alive = true;
                if (!alive) Enemy.Spawn(s.kind, at, s.level);
            }
        }
    }
}
