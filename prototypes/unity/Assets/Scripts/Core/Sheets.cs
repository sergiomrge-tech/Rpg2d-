using System;
using System.Collections.Generic;
using UnityEngine;

namespace Aetheria
{
    [Serializable]
    public class AnimInfo
    {
        public string name;
        public int start;
        public int count;
        public float fps;
        public bool loop;
        public int hit;
    }

    [Serializable]
    public class SheetData
    {
        public int frameW, frameH, pivotX, pivotY, cols;
        public AnimInfo[] anims;
    }

    /// <summary>A sliced sprite sheet (frames + named animations).</summary>
    public class Sheet
    {
        public SheetData data;
        public Sprite[] frames;
        public readonly Dictionary<string, AnimInfo> anims = new Dictionary<string, AnimInfo>();

        public AnimInfo Get(string name)
        {
            anims.TryGetValue(name, out var a);
            return a;
        }
    }

    [Serializable]
    public class PropInfo
    {
        public string name;
        public int w, h, pivotX, pivotY, colW, colH, colY;
    }

    [Serializable]
    class PropList
    {
        public PropInfo[] props;
    }

    /// <summary>Loads PNG+JSON art produced by tools/art_hd from Resources and caches sprites.</summary>
    public static class Sheets
    {
        public const float PPU = 64f;
        static readonly Dictionary<string, Sheet> cache = new Dictionary<string, Sheet>();
        static readonly Dictionary<string, Sprite> sprites = new Dictionary<string, Sprite>();
        static Dictionary<string, PropInfo> props;

        public static Texture2D Tex(string path)
        {
            var t = Resources.Load<Texture2D>(path);
            if (t == null) { Debug.LogError("Missing texture " + path); return null; }
            t.filterMode = FilterMode.Bilinear;
            t.wrapMode = TextureWrapMode.Clamp;
            return t;
        }

        public static Sheet Load(string path)
        {
            if (cache.TryGetValue(path, out var s)) return s;
            var json = Resources.Load<TextAsset>(path);
            var tex = Tex(path);
            if (json == null || tex == null) { Debug.LogError("Missing sheet " + path); return null; }
            s = new Sheet { data = JsonUtility.FromJson<SheetData>(json.text) };
            var d = s.data;
            int total = 0;
            foreach (var a in d.anims) { s.anims[a.name] = a; total = Mathf.Max(total, a.start + a.count); }
            s.frames = new Sprite[total];
            var pivot = new Vector2(d.pivotX / (float)d.frameW, d.pivotY / (float)d.frameH);
            for (int i = 0; i < total; i++)
            {
                int cx = i % d.cols, cy = i / d.cols;
                // texture origin is bottom-left; sheet rows go top-down
                var r = new Rect(cx * d.frameW, tex.height - (cy + 1) * d.frameH, d.frameW, d.frameH);
                s.frames[i] = Sprite.Create(tex, r, pivot, PPU, 0, SpriteMeshType.FullRect);
                s.frames[i].name = path + "#" + i;
            }
            cache[path] = s;
            return s;
        }

        public static PropInfo Prop(string name)
        {
            if (props == null)
            {
                props = new Dictionary<string, PropInfo>();
                var j = Resources.Load<TextAsset>("Sprites/Env/props");
                if (j != null)
                    foreach (var p in JsonUtility.FromJson<PropList>(j.text).props) props[p.name] = p;
            }
            props.TryGetValue(name, out var info);
            return info;
        }

        /// <summary>Single sprite from a PNG; pivot in pixels from bottom-left (or centre when null).</summary>
        public static Sprite Single(string path, Vector2? pivotPx = null)
        {
            string key = path + (pivotPx.HasValue ? pivotPx.Value.ToString() : "c");
            if (sprites.TryGetValue(key, out var sp)) return sp;
            var tex = Tex(path);
            if (tex == null) return null;
            var pv = pivotPx.HasValue ? new Vector2(pivotPx.Value.x / tex.width, pivotPx.Value.y / tex.height) : new Vector2(0.5f, 0.5f);
            sp = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), pv, PPU, 0, SpriteMeshType.FullRect);
            sprites[key] = sp;
            return sp;
        }

        public static Sprite PropSprite(string name)
        {
            var p = Prop(name);
            if (p == null) return Single("Sprites/Env/" + name);
            return Single("Sprites/Env/" + name, new Vector2(p.pivotX, p.pivotY));
        }
    }
}
