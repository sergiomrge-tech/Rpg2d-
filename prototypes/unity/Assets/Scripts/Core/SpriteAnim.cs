using System;
using UnityEngine;

namespace Aetheria
{
    public enum Facing { Down, Up, Left, Right }

    /// <summary>Plays directional animations from a Sheet ("walk_down", "walk_up", "walk_side" + flipX).</summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class SpriteAnim : MonoBehaviour
    {
        public Sheet sheet;
        public SpriteRenderer sr;
        public string current;
        public Facing facing = Facing.Down;
        public float speed = 1f;
        public bool finished;
        public event Action<string> OnHit;
        public event Action<string> OnEnd;

        AnimInfo info;
        float t;
        int lastFrame = -1;
        string baseName;

        void Awake() { sr = GetComponent<SpriteRenderer>(); }

        public static string Suffix(Facing f) => f == Facing.Down ? "_down" : f == Facing.Up ? "_up" : "_side";

        public int Frame => info == null ? 0 : lastFrame;
        public float Normalized => info == null ? 1 : Mathf.Clamp01(t * info.fps / info.count);
        public string Base => baseName;

        public void Play(string name, bool restart = false)
        {
            string full = name + Suffix(facing);
            if (!restart && full == current) return;
            var a = sheet.Get(full) ?? sheet.Get(name);
            if (a == null) { Debug.LogWarning("anim missing " + full); return; }
            baseName = name;
            current = full;
            info = a;
            t = 0;
            lastFrame = -1;
            finished = false;
            Apply();
        }

        public void SetFacing(Facing f)
        {
            if (f == facing) return;
            facing = f;
            if (baseName != null)
            {
                // keep the phase when switching direction mid-loop
                float keep = t;
                string n = baseName;
                current = null;
                Play(n, true);
                t = keep;
                Apply();
            }
        }

        void Update()
        {
            if (info == null) return;
            t += Time.deltaTime * speed;
            Apply();
        }

        void Apply()
        {
            int f = Mathf.FloorToInt(t * info.fps);
            if (info.loop) f %= info.count;
            else if (f >= info.count)
            {
                f = info.count - 1;
                if (!finished) { finished = true; OnEnd?.Invoke(baseName); }
            }
            if (f != lastFrame)
            {
                if (info.hit >= 0 && lastFrame < info.hit && f >= info.hit) OnHit?.Invoke(baseName);
                lastFrame = f;
                sr.sprite = sheet.frames[info.start + f];
            }
            sr.flipX = facing == Facing.Left;
        }
    }
}
