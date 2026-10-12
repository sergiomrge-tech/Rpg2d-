using System.Collections.Generic;
using UnityEngine;

namespace Aetheria
{
    public static class Util
    {
        public const int GroundOrder = -32000;

        public static Vector2 MapToWorld(float px, float py) => new Vector2(px / Sheets.PPU, -py / Sheets.PPU);

        public static int SortOrder(float worldY) => Mathf.Clamp(Mathf.RoundToInt(-worldY * 100f), -30000, 30000);

        public static Facing FacingFrom(Vector2 d, Facing fallback)
        {
            if (d.sqrMagnitude < 1e-4f) return fallback;
            if (Mathf.Abs(d.x) > Mathf.Abs(d.y) * 0.9f) return d.x > 0 ? Facing.Right : Facing.Left;
            return d.y > 0 ? Facing.Up : Facing.Down;
        }

        public static Vector2 FacingVec(Facing f)
        {
            switch (f)
            {
                case Facing.Up: return Vector2.up;
                case Facing.Left: return Vector2.left;
                case Facing.Right: return Vector2.right;
                default: return Vector2.down;
            }
        }

        static Material fxMat;
        public static Material FxMaterial
        {
            get
            {
                if (fxMat == null)
                {
                    var sh = Shader.Find("Aetheria/SpriteFx");
                    if (sh == null) sh = Shader.Find("Sprites/Default");
                    fxMat = new Material(sh);
                }
                return fxMat;
            }
        }

        static Material addMat;
        /// <summary>Additive material for glows / magic.</summary>
        public static Material AdditiveMaterial
        {
            get
            {
                if (addMat == null)
                {
                    var sh = Shader.Find("Aetheria/SpriteAdd");
                    if (sh == null) sh = Shader.Find("Sprites/Default");
                    addMat = new Material(sh);
                }
                return addMat;
            }
        }

        static Sprite softCircle;
        /// <summary>Procedural soft round blob (shadows, glows).</summary>
        public static Sprite SoftCircle
        {
            get
            {
                if (softCircle != null) return softCircle;
                const int n = 128;
                var tex = new Texture2D(n, n, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp };
                var px = new Color32[n * n];
                for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    float dx = (x + 0.5f) / n * 2 - 1, dy = (y + 0.5f) / n * 2 - 1;
                    float d = Mathf.Sqrt(dx * dx + dy * dy);
                    float a = Mathf.Clamp01(1 - d);
                    a = a * a * (3 - 2 * a);
                    px[y * n + x] = new Color32(255, 255, 255, (byte)(a * 255));
                }
                tex.SetPixels32(px);
                tex.Apply();
                softCircle = Sprite.Create(tex, new Rect(0, 0, n, n), new Vector2(0.5f, 0.5f), n);
                return softCircle;
            }
        }

        public static SpriteRenderer Shadow(Transform parent, float w, float h, float alpha = 0.32f)
        {
            var go = new GameObject("shadow");
            go.transform.SetParent(parent, false);
            go.transform.localScale = new Vector3(w, h, 1);
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = SoftCircle;
            sr.color = new Color(0.08f, 0.12f, 0.1f, alpha);
            sr.sortingOrder = -31000;
            return sr;
        }

        public static T Pick<T>(IList<T> list) => list[Random.Range(0, list.Count)];

        public static float Approach(float v, float target, float delta) =>
            v < target ? Mathf.Min(v + delta, target) : Mathf.Max(v - delta, target);
    }

    /// <summary>Keeps a renderer's sorting order in sync with its y position (top-down depth).</summary>
    public class YSort : MonoBehaviour
    {
        public SpriteRenderer[] renderers;
        public float offset;
        public bool isStatic;

        void Start()
        {
            if (renderers == null || renderers.Length == 0) renderers = GetComponentsInChildren<SpriteRenderer>();
            Apply();
            if (isStatic) enabled = false;
        }

        void LateUpdate() { Apply(); }

        void Apply()
        {
            int o = Util.SortOrder(transform.position.y + offset);
            foreach (var r in renderers)
                if (r != null && r.sortingOrder > -31000) r.sortingOrder = o;
        }
    }
}
