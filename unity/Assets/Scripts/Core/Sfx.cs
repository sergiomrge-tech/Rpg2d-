using System.Collections.Generic;
using UnityEngine;

namespace Aetheria
{
    /// <summary>Procedurally synthesised sound effects (no audio files needed) + simple ambient pad.</summary>
    public static class Sfx
    {
        const int Rate = 44100;
        static readonly Dictionary<string, AudioClip> clips = new Dictionary<string, AudioClip>();
        static AudioSource[] pool;
        static int next;
        static GameObject host;

        static void Init()
        {
            if (host != null) return;
            host = new GameObject("Sfx");
            Object.DontDestroyOnLoad(host);
            pool = new AudioSource[16];
            for (int i = 0; i < pool.Length; i++)
            {
                pool[i] = host.AddComponent<AudioSource>();
                pool[i].playOnAwake = false;
            }
        }

        public static void Play(string name, float vol = 0.5f, float pitch = 1f)
        {
            Init();
            var c = Get(name);
            if (c == null) return;
            var s = pool[next];
            next = (next + 1) % pool.Length;
            s.pitch = pitch;
            s.PlayOneShot(c, vol);
        }

        public static AudioSource Loop(string name, float vol)
        {
            Init();
            var s = host.AddComponent<AudioSource>();
            s.clip = Get(name);
            s.loop = true;
            s.volume = vol;
            s.Play();
            return s;
        }

        static AudioClip Get(string name)
        {
            if (clips.TryGetValue(name, out var c)) return c;
            float[] d = Synth(name);
            if (d == null) return null;
            c = AudioClip.Create(name, d.Length, 1, Rate, false);
            c.SetData(d, 0);
            clips[name] = c;
            return c;
        }

        static float[] Buf(float sec) => new float[Mathf.CeilToInt(sec * Rate)];
        static float Env(float t, float a, float dcy) => t < a ? t / a : Mathf.Exp(-(t - a) / dcy);
        static System.Random rng = new System.Random(7);
        static float N() => (float)(rng.NextDouble() * 2 - 1);

        // simple one-pole filtered noise
        static float[] Noise(float sec, float cutoff, float a, float dcy, float gain = 1f)
        {
            var b = Buf(sec);
            float y = 0, k = Mathf.Clamp01(cutoff);
            for (int i = 0; i < b.Length; i++)
            {
                float t = i / (float)Rate;
                y += (N() - y) * k;
                b[i] = y * Env(t, a, dcy) * gain;
            }
            return b;
        }

        static float[] Synth(string n)
        {
            switch (n)
            {
                case "swing":
                case "swing_heavy":
                {
                    bool h = n == "swing_heavy";
                    var b = Buf(h ? 0.38f : 0.26f);
                    float y = 0;
                    for (int i = 0; i < b.Length; i++)
                    {
                        float t = i / (float)Rate, u = t / (b.Length / (float)Rate);
                        float k = Mathf.Lerp(0.05f, 0.45f, Mathf.Sin(u * Mathf.PI));
                        y += (N() - y) * k;
                        b[i] = y * Mathf.Sin(u * Mathf.PI) * (h ? 0.9f : 0.7f);
                    }
                    return b;
                }
                case "hit":
                {
                    var b = Noise(0.22f, 0.6f, 0.001f, 0.04f, 0.9f);
                    for (int i = 0; i < b.Length; i++)
                    {
                        float t = i / (float)Rate;
                        b[i] += Mathf.Sin(2 * Mathf.PI * (140 - 260 * t) * t) * Env(t, 0.001f, 0.07f) * 0.8f;
                    }
                    return b;
                }
                case "claw": return Noise(0.18f, 0.75f, 0.002f, 0.035f, 0.8f);
                case "step": return Noise(0.07f, 0.15f, 0.001f, 0.015f, 0.6f);
                case "roll": return Noise(0.3f, 0.08f, 0.02f, 0.09f, 0.9f);
                case "boom":
                {
                    var b = Noise(0.5f, 0.12f, 0.002f, 0.12f, 1f);
                    for (int i = 0; i < b.Length; i++)
                    {
                        float t = i / (float)Rate;
                        b[i] += Mathf.Sin(2 * Mathf.PI * (90 - 60 * t) * t) * Env(t, 0.002f, 0.15f) * 0.7f;
                    }
                    return b;
                }
                case "spark":
                case "charge":
                case "fireball":
                {
                    float len = n == "charge" ? 0.45f : 0.35f;
                    var b = Buf(len);
                    float f0 = n == "spark" ? 900 : n == "charge" ? 300 : 220;
                    float f1 = n == "spark" ? 2200 : n == "charge" ? 900 : 120;
                    float ph = 0;
                    for (int i = 0; i < b.Length; i++)
                    {
                        float t = i / (float)Rate, u = t / len;
                        float f = Mathf.Lerp(f0, f1, u);
                        ph += f / Rate;
                        float tone = Mathf.Sin(2 * Mathf.PI * ph) + 0.4f * Mathf.Sin(2 * Mathf.PI * ph * 2.01f);
                        float env = n == "charge" ? Mathf.Sin(u * Mathf.PI) : Env(t, 0.005f, len * 0.35f);
                        b[i] = (tone * 0.35f + N() * (n == "fireball" ? 0.5f : 0.15f)) * env;
                    }
                    return b;
                }
                case "imp_cry":
                case "imp_hurt":
                case "imp_die":
                {
                    float len = n == "imp_die" ? 0.6f : 0.28f;
                    var b = Buf(len);
                    float ph = 0;
                    for (int i = 0; i < b.Length; i++)
                    {
                        float t = i / (float)Rate, u = t / len;
                        float f = n == "imp_cry" ? 700 + 500 * Mathf.Sin(u * 9) : n == "imp_hurt" ? 900 - 400 * u : 600 - 450 * u;
                        f += 40 * Mathf.Sin(t * 2 * Mathf.PI * 35);   // raspy vibrato
                        ph += f / Rate;
                        float saw = 2 * (ph - Mathf.Floor(ph + 0.5f));
                        b[i] = (saw * 0.35f + N() * 0.12f) * Env(t, 0.01f, len * 0.4f);
                    }
                    return b;
                }
                case "hurt":
                {
                    var b = Noise(0.25f, 0.35f, 0.001f, 0.06f, 0.8f);
                    for (int i = 0; i < b.Length; i++)
                    {
                        float t = i / (float)Rate;
                        b[i] += Mathf.Sin(2 * Mathf.PI * (220 - 120 * t) * t) * Env(t, 0.001f, 0.08f) * 0.6f;
                    }
                    return b;
                }
                case "coin":
                case "pickup":
                case "potion":
                case "levelup":
                case "ui":
                {
                    float[] notes = n == "coin" ? new[] { 1318f, 1975f } : n == "pickup" ? new[] { 660f, 990f } :
                        n == "potion" ? new[] { 523f, 659f, 784f } : n == "levelup" ? new[] { 523f, 659f, 784f, 1046f } : new[] { 880f };
                    float step = n == "levelup" ? 0.11f : 0.07f;
                    var b = Buf(step * notes.Length + 0.35f);
                    for (int k = 0; k < notes.Length; k++)
                    {
                        int s0 = (int)(k * step * Rate);
                        for (int i = s0; i < b.Length; i++)
                        {
                            float t = (i - s0) / (float)Rate;
                            b[i] += (Mathf.Sin(2 * Mathf.PI * notes[k] * t) + 0.3f * Mathf.Sin(4 * Mathf.PI * notes[k] * t)) * Env(t, 0.003f, 0.12f) * 0.3f;
                        }
                    }
                    return b;
                }
                case "death":
                {
                    var b = Buf(1.2f);
                    for (int i = 0; i < b.Length; i++)
                    {
                        float t = i / (float)Rate;
                        b[i] = (Mathf.Sin(2 * Mathf.PI * 220 * t) + Mathf.Sin(2 * Mathf.PI * 261 * t) + Mathf.Sin(2 * Mathf.PI * 311 * t)) * 0.15f * Env(t, 0.05f, 0.5f);
                    }
                    return b;
                }
                case "ambience":
                {
                    // 8s seamless loop: soft wind + distant birds
                    float len = 8f;
                    var b = Buf(len);
                    float y = 0;
                    for (int i = 0; i < b.Length; i++)
                    {
                        float t = i / (float)Rate;
                        y += (N() - y) * 0.02f;
                        float wind = y * (0.5f + 0.5f * Mathf.Sin(2 * Mathf.PI * t / len * 2)) * 0.6f;
                        b[i] = wind;
                    }
                    for (int k = 0; k < 7; k++)
                    {
                        float t0 = (float)rng.NextDouble() * (len - 0.5f);
                        float f = 2600 + (float)rng.NextDouble() * 1400;
                        int s0 = (int)(t0 * Rate);
                        for (int i = 0; i < Rate * 0.18f && s0 + i < b.Length; i++)
                        {
                            float t = i / (float)Rate;
                            b[s0 + i] += Mathf.Sin(2 * Mathf.PI * (f + 900 * Mathf.Sin(t * 60)) * t) * Env(t, 0.01f, 0.05f) * 0.05f;
                        }
                    }
                    return b;
                }
            }
            return null;
        }
    }
}
