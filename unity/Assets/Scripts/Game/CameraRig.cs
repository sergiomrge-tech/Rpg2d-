using UnityEngine;

namespace Aetheria
{
    /// <summary>Smooth follow with look-ahead, trauma-based shake, clamped to map bounds.</summary>
    public class CameraRig : MonoBehaviour
    {
        public static CameraRig I;
        public Camera cam;
        public Transform target;
        public float size = 8.4375f;   // 1080p -> 1 texel per pixel at 64 PPU
        Vector2 vel;
        Vector2 look;
        float trauma, traumaDecay = 1f;

        public static CameraRig Create()
        {
            var go = new GameObject("Main Camera");
            go.tag = "MainCamera";
            var c = go.AddComponent<Camera>();
            c.orthographic = true;
            c.orthographicSize = 8.4375f;
            c.clearFlags = CameraClearFlags.SolidColor;
            c.backgroundColor = new Color(0.36f, 0.6f, 0.3f);
            c.transform.position = new Vector3(0, 0, -10);
            go.AddComponent<AudioListener>();
            var r = go.AddComponent<CameraRig>();
            r.cam = c;
            I = r;
            return r;
        }

        public static void Shake(float amount, float duration)
        {
            if (I == null) return;
            I.trauma = Mathf.Min(1f, I.trauma + amount * 2.2f);
            I.traumaDecay = 1f / Mathf.Max(0.05f, duration * 2.5f);
        }

        public void Snap()
        {
            if (target == null) return;
            var p = (Vector2)target.position + Vector2.up * 0.8f;
            transform.position = Clamp(p);
        }

        Vector3 Clamp(Vector2 p)
        {
            var w = World.I;
            if (w != null)
            {
                float hh = cam.orthographicSize, hw = hh * cam.aspect;
                var b = w.bounds;
                p.x = b.width > hw * 2 ? Mathf.Clamp(p.x, b.xMin + hw, b.xMax - hw) : b.center.x;
                p.y = b.height > hh * 2 ? Mathf.Clamp(p.y, b.yMin + hh, b.yMax - hh) : b.center.y;
            }
            return new Vector3(p.x, p.y, -10);
        }

        void LateUpdate()
        {
            cam.orthographicSize = Mathf.Lerp(cam.orthographicSize, size, Time.unscaledDeltaTime * 4f);
            if (target == null) return;
            var rb = target.GetComponent<Rigidbody2D>();
            Vector2 lv = rb != null ? rb.velocity * 0.18f : Vector2.zero;
            look = Vector2.Lerp(look, Vector2.ClampMagnitude(lv, 1.2f), Time.deltaTime * 2.5f);
            Vector2 want = (Vector2)target.position + Vector2.up * 0.8f + look;
            Vector2 cur = Vector2.SmoothDamp((Vector2)transform.position - shakeOffset, want, ref vel, 0.16f);
            Vector3 c = Clamp(cur);
            trauma = Mathf.Max(0, trauma - traumaDecay * Time.unscaledDeltaTime);
            float s = trauma * trauma * 0.35f;
            shakeOffset = new Vector2((Mathf.PerlinNoise(Time.time * 25f, 0) - 0.5f) * 2 * s, (Mathf.PerlinNoise(0, Time.time * 25f) - 0.5f) * 2 * s);
            transform.position = c + (Vector3)shakeOffset;
        }

        Vector2 shakeOffset;
    }
}
