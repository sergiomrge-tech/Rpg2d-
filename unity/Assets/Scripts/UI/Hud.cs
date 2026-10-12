using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Aetheria
{
    /// <summary>Non-boxy HUD: ornate portrait medallion wrapped by curved HP / MP / stamina arcs, skill orbs fanned
    /// along an arc, floating world text, loot feed without panels, cinematic dialogue band.</summary>
    public class Hud : MonoBehaviour
    {
        public static Hud I;
        public Canvas canvas;
        public RectTransform root;
        public static Font Serif, Sans, SansBold;

        Image hpFill, hpTrail, mpFill, stFill;
        Text hpText, levelText, goldText, questText, rankText;
        float hpShown, hpTrailShown, mpShown, stShown;
        RectTransform medallion;
        float hurtPulse;
        Image vignette;

        class Orb { public Image cd; public Text count; public string item; }
        readonly List<Orb> orbs = new List<Orb>();

        class Floater { public RectTransform rt; public Text txt; public Vector2 world; public float t, life; public Vector2 vel; public float scale; }
        readonly List<Floater> floaters = new List<Floater>();

        class Feed { public RectTransform rt; public CanvasGroup cg; public float t; }
        readonly List<Feed> feeds = new List<Feed>();

        class Plate { public Enemy e; public RectTransform rt; public Image fill; public Image trail; public Text name; public float shown; }
        readonly Dictionary<Enemy, Plate> plates = new Dictionary<Enemy, Plate>();

        // dialogue
        RectTransform dlg;
        Text dlgName, dlgText, dlgHint;
        Image dlgPortrait;
        Story.Line[] lines;
        int lineIdx;
        float typeT;
        Action onDone;
        public bool InDialogue => lines != null;

        // banner
        RectTransform banner;
        Text bannerTitle, bannerSub;
        float bannerT = -1;

        const float ArcSpan = 240f / 360f;

        public static Hud Create()
        {
            var go = new GameObject("HUD");
            var h = go.AddComponent<Hud>();
            I = h;
            h.Build();
            return h;
        }

        public static Sprite Ui(string n) => Sheets.Single("Sprites/Ui/" + n);

        public RectTransform Rect(string name, Transform parent, Vector2 anchor, Vector2 pos, Vector2 size)
        {
            var go = new GameObject(name, typeof(RectTransform));
            var rt = go.GetComponent<RectTransform>();
            rt.SetParent(parent, false);
            rt.anchorMin = rt.anchorMax = anchor;
            rt.pivot = new Vector2(0.5f, 0.5f);
            rt.anchoredPosition = pos;
            rt.sizeDelta = size;
            return rt;
        }

        public Image Img(string name, Transform parent, Sprite sp, Vector2 anchor, Vector2 pos, Vector2 size)
        {
            var rt = Rect(name, parent, anchor, pos, size);
            var im = rt.gameObject.AddComponent<Image>();
            im.sprite = sp;
            im.raycastTarget = false;
            return im;
        }

        public Text Txt(string name, Transform parent, string s, Font f, int size, Color c, Vector2 anchor, Vector2 pos, Vector2 box,
                 TextAnchor align = TextAnchor.MiddleCenter, bool outline = true)
        {
            var rt = Rect(name, parent, anchor, pos, box);
            var t = rt.gameObject.AddComponent<Text>();
            t.font = f;
            t.fontSize = size;
            t.color = c;
            t.text = s;
            t.alignment = align;
            t.raycastTarget = false;
            t.horizontalOverflow = HorizontalWrapMode.Overflow;
            t.verticalOverflow = VerticalWrapMode.Overflow;
            if (outline)
            {
                var o = rt.gameObject.AddComponent<Outline>();
                o.effectColor = new Color(0.12f, 0.06f, 0.08f, 0.9f);
                o.effectDistance = new Vector2(1.6f, -1.6f);
                var sh = rt.gameObject.AddComponent<Shadow>();
                sh.effectColor = new Color(0, 0, 0, 0.45f);
                sh.effectDistance = new Vector2(2f, -3f);
            }
            return t;
        }

        Image Arc(string name, Transform parent, string tex, float size, Color tint)
        {
            var im = Img(name, parent, Ui(tex), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(size, size));
            im.type = Image.Type.Filled;
            im.fillMethod = Image.FillMethod.Radial360;
            im.fillOrigin = (int)Image.Origin360.Left;
            im.fillClockwise = true;
            im.fillAmount = ArcSpan;
            im.color = tint;
            return im;
        }

        void Build()
        {
            Serif = Resources.Load<Font>("Fonts/Cinzel-700");
            Sans = Resources.Load<Font>("Fonts/AlegreyaSans-400");
            SansBold = Resources.Load<Font>("Fonts/AlegreyaSans-700");
            canvas = gameObject.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 10;
            var sc = gameObject.AddComponent<CanvasScaler>();
            sc.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            sc.referenceResolution = new Vector2(1920, 1080);
            sc.matchWidthOrHeight = 0.5f;
            gameObject.AddComponent<GraphicRaycaster>();
            root = GetComponent<RectTransform>();

            // soft vignette (screen-edge darkening, flashes red when hurt)
            vignette = Img("vignette", root, Ui("vignette"), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(1920, 1080));
            vignette.rectTransform.anchorMin = Vector2.zero;
            vignette.rectTransform.anchorMax = Vector2.one;
            vignette.rectTransform.sizeDelta = Vector2.zero;
            vignette.color = new Color(0.05f, 0.02f, 0.08f, 0.55f);

            // ---- portrait medallion + arcs (bottom-left)
            medallion = Rect("medallion", root, new Vector2(0, 0), new Vector2(190, 190), new Vector2(460, 460));
            Img("smear", medallion, Ui("smear"), new Vector2(0.5f, 0.5f), new Vector2(40, -10), new Vector2(620, 420)).color = new Color(0, 0, 0, 0.38f);
            Arc("hp_track", medallion, "arc_hp_track", 440, Color.white);
            hpTrail = Arc("hp_trail", medallion, "arc_hp_fill", 440, new Color(1f, 0.92f, 0.75f, 0.9f));
            hpFill = Arc("hp_fill", medallion, "arc_hp_fill", 440, Color.white);
            Arc("mp_track", medallion, "arc_mp_track", 440, Color.white);
            mpFill = Arc("mp_fill", medallion, "arc_mp_fill", 440, Color.white);
            Arc("st_track", medallion, "arc_st_track", 440, Color.white);
            stFill = Arc("st_fill", medallion, "arc_st_fill", 440, Color.white);
            Img("portrait", medallion, Ui("portrait"), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(196, 196));
            Img("frame", medallion, Ui("medallion"), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(300, 300));
            levelText = Txt("level", medallion, "1", Serif, 30, new Color(1f, 0.93f, 0.7f), new Vector2(0.5f, 0.5f), new Vector2(0, -128), new Vector2(80, 40));
            hpText = Txt("hp", medallion, "", Serif, 26, new Color(1f, 0.9f, 0.85f), new Vector2(0.5f, 0.5f), new Vector2(232, 72), new Vector2(200, 40), TextAnchor.MiddleLeft);
            rankText = Txt("rank", medallion, "Aventureiro · Rank F", SansBold, 22, new Color(0.95f, 0.88f, 0.7f), new Vector2(0.5f, 0.5f), new Vector2(150, 230), new Vector2(380, 30), TextAnchor.MiddleLeft);

            // ---- gold (top-left, no box): coin icon + number
            var goldIcon = Img("goldIcon", root, null, new Vector2(0, 1), new Vector2(58, -52), new Vector2(46, 46));
            goldIcon.sprite = Icons.Get("coin");
            goldText = Txt("gold", root, "0", Serif, 30, new Color(1f, 0.88f, 0.45f), new Vector2(0, 1), new Vector2(170, -52), new Vector2(160, 40), TextAnchor.MiddleLeft);

            // ---- quest tracker (top-right): flourish + text on a soft smear
            var q = Rect("quest", root, new Vector2(1, 1), new Vector2(-250, -90), new Vector2(460, 140));
            Img("smear", q, Ui("smear"), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(520, 200)).color = new Color(0, 0, 0, 0.42f);
            Img("flourish", q, Ui("flourish"), new Vector2(0.5f, 0.5f), new Vector2(0, 44), new Vector2(360, 36));
            questText = Txt("qtext", q, "", Sans, 25, new Color(0.98f, 0.95f, 0.88f), new Vector2(0.5f, 0.5f), new Vector2(0, -8), new Vector2(420, 90), TextAnchor.UpperCenter);

            // ---- skill orbs fanned along an arc (bottom-right)
            var fan = Rect("skills", root, new Vector2(1, 0), new Vector2(-170, 150), new Vector2(10, 10));
            string[] icons = { "skill_sword", "skill_spark", "skill_roll", "potion" };
            string[] keys = { "J", "K", "Espaço", "Q" };
            for (int i = 0; i < icons.Length; i++)
            {
                float a = Mathf.Deg2Rad * (200f - i * 34f);
                Vector2 p = new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * 190f + new Vector2(120, -40);
                float sz = i == 0 ? 132 : 104;
                var o = Img("orb" + i, fan, Ui("orb"), new Vector2(0.5f, 0.5f), p, new Vector2(sz, sz));
                Img("icon", o.transform, Icons.Get(icons[i]), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(sz * 0.56f, sz * 0.56f));
                var cd = Img("cd", o.transform, Ui("orb_shade"), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(sz * 0.8f, sz * 0.8f));
                cd.type = Image.Type.Filled;
                cd.fillMethod = Image.FillMethod.Radial360;
                cd.fillOrigin = (int)Image.Origin360.Top;
                cd.fillAmount = 0;
                Txt("key", o.transform, keys[i], SansBold, 20, new Color(1f, 0.95f, 0.8f), new Vector2(0.5f, 0f), new Vector2(0, -6), new Vector2(100, 24));
                var cnt = i == 3 ? Txt("count", o.transform, "", Serif, 24, Color.white, new Vector2(1f, 1f), new Vector2(-14, -14), new Vector2(40, 30)) : null;
                orbs.Add(new Orb { cd = cd, count = cnt, item = i == 3 ? "potion" : null });
            }
            // central large orb gets the "main" spot
            Txt("hint", root, "WASD mover · Shift correr · E falar", Sans, 20, new Color(1, 1, 1, 0.7f), new Vector2(1, 0), new Vector2(-250, 26), new Vector2(480, 28));

            // ---- dialogue band (bottom, full width gradient, no box)
            dlg = Rect("dialogue", root, new Vector2(0.5f, 0), new Vector2(0, 170), new Vector2(1920, 340));
            Img("band", dlg, Ui("dialogue_band"), new Vector2(0.5f, 0.5f), new Vector2(0, -20), new Vector2(1920, 380));
            dlgPortrait = Img("dportrait", dlg, Ui("portrait"), new Vector2(0.5f, 0.5f), new Vector2(-700, 30), new Vector2(230, 230));
            Img("dframe", dlg, Ui("medallion"), new Vector2(0.5f, 0.5f), new Vector2(-700, 30), new Vector2(340, 340));
            Img("nameplate", dlg, Ui("nameplate"), new Vector2(0.5f, 0.5f), new Vector2(-330, 118), new Vector2(480, 70));
            dlgName = Txt("dname", dlg, "", Serif, 32, new Color(1f, 0.92f, 0.7f), new Vector2(0.5f, 0.5f), new Vector2(-330, 120), new Vector2(460, 50));
            dlgText = Txt("dtext", dlg, "", Sans, 34, new Color(1f, 0.98f, 0.94f), new Vector2(0.5f, 0.5f), new Vector2(130, 20), new Vector2(1250, 160), TextAnchor.UpperLeft);
            dlgText.horizontalOverflow = HorizontalWrapMode.Wrap;
            dlgHint = Txt("dhint", dlg, "E / Enter ▸", SansBold, 22, new Color(1f, 0.9f, 0.6f, 0.9f), new Vector2(0.5f, 0.5f), new Vector2(700, -90), new Vector2(200, 30));
            dlg.gameObject.SetActive(false);

            // ---- zone banner
            banner = Rect("banner", root, new Vector2(0.5f, 1), new Vector2(0, -170), new Vector2(900, 160));
            Img("bflourish", banner, Ui("flourish"), new Vector2(0.5f, 0.5f), new Vector2(0, -36), new Vector2(560, 48));
            bannerTitle = Txt("btitle", banner, "", Serif, 64, new Color(1f, 0.95f, 0.82f), new Vector2(0.5f, 0.5f), new Vector2(0, 20), new Vector2(900, 80));
            bannerSub = Txt("bsub", banner, "", Sans, 28, new Color(1f, 0.9f, 0.7f), new Vector2(0.5f, 0.5f), new Vector2(0, -78), new Vector2(900, 40));
            banner.gameObject.SetActive(false);
        }

        public void Banner(string title, string sub)
        {
            bannerTitle.text = title;
            bannerSub.text = sub;
            bannerT = 0;
            banner.gameObject.SetActive(true);
        }

        public void HurtPulse() { hurtPulse = 1f; }

        public void Number(Vector2 world, string s, bool crit, bool onPlayer)
        {
            var c = onPlayer ? new Color(1f, 0.38f, 0.35f) : crit ? new Color(1f, 0.82f, 0.25f) : Color.white;
            var f = MakeFloater(world, s, c, crit ? 54 : 40, Serif);
            f.vel = new Vector2(UnityEngine.Random.Range(-60f, 60f), 260f);
            f.scale = crit ? 1.5f : 1.15f;
            f.life = 0.9f;
        }

        public void Float(Vector2 world, string s, Color c)
        {
            var f = MakeFloater(world, s, c, 30, SansBold);
            f.vel = new Vector2(0, 70f);
            f.life = 1.3f;
            f.scale = 1f;
        }

        Floater MakeFloater(Vector2 world, string s, Color c, int size, Font font)
        {
            var t = Txt("float", root, s, font, size, c, new Vector2(0, 0), Vector2.zero, new Vector2(300, 60));
            var f = new Floater { rt = t.rectTransform, txt = t, world = world };
            floaters.Add(f);
            return f;
        }

        public void LootFeed(ItemDef def, int count)
        {
            var rt = Rect("feed", root, new Vector2(1, 0.5f), new Vector2(-230, -40), new Vector2(420, 52));
            var cg = rt.gameObject.AddComponent<CanvasGroup>();
            Img("smear", rt, Ui("smear"), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(440, 80)).color = new Color(0, 0, 0, 0.35f);
            Img("ic", rt, Icons.Get(def.icon), new Vector2(0.5f, 0.5f), new Vector2(-150, 0), new Vector2(46, 46));
            Txt("t", rt, (count > 1 ? count + "× " : "") + def.name, SansBold, 26, Data.RarityColors[(int)def.rarity], new Vector2(0.5f, 0.5f), new Vector2(30, 0), new Vector2(320, 40), TextAnchor.MiddleLeft);
            foreach (var f in feeds) f.rt.anchoredPosition += new Vector2(0, 56);
            feeds.Add(new Feed { rt = rt, cg = cg });
        }

        public void ShowDialogue(Story.Line[] l, Action done)
        {
            lines = l;
            lineIdx = 0;
            typeT = 0;
            onDone = done;
            dlg.gameObject.SetActive(true);
            ShowLine();
        }

        void ShowLine()
        {
            var ln = lines[lineIdx];
            bool narr = string.IsNullOrEmpty(ln.who);
            dlgName.text = narr ? "" : Story.NameOf(ln.who);
            dlgName.transform.parent.Find("nameplate").gameObject.SetActive(!narr);
            dlgPortrait.transform.parent.Find("dframe").gameObject.SetActive(!narr);
            dlgPortrait.gameObject.SetActive(!narr);
            if (!narr) dlgPortrait.sprite = PortraitFor(ln.who);
            dlgText.fontStyle = narr ? FontStyle.Italic : FontStyle.Normal;
            typeT = 0;
            Sfx.Play("ui", 0.2f, 1.2f);
        }

        Sprite PortraitFor(string who)
        {
            var sp = Resources.Load<Texture2D>("Sprites/Ui/portrait_" + who) != null ? Ui("portrait_" + who) : Ui("portrait");
            return sp;
        }

        void AdvanceDialogue()
        {
            var full = lines[lineIdx].text;
            int shown = Mathf.FloorToInt(typeT * 55f);
            if (shown < full.Length) { typeT = 999; return; }
            lineIdx++;
            if (lineIdx >= lines.Length)
            {
                lines = null;
                dlg.gameObject.SetActive(false);
                var d = onDone;
                onDone = null;
                d?.Invoke();
                return;
            }
            ShowLine();
        }

        public void Advance() { if (InDialogue) AdvanceDialogue(); }

        void Update()
        {
            float dt = Time.unscaledDeltaTime;
            var p = Player.I;
            var g = Game.I;
            if (p != null)
            {
                var gs = p.gs;
                float hpN = p.hp / gs.HpMax, mpN = p.mp / gs.maxMp, stN = p.st / gs.maxSt;
                hpShown = Mathf.Lerp(hpShown, hpN, dt * 12f);
                hpTrailShown = hpTrailShown < hpShown ? hpShown : Mathf.MoveTowards(hpTrailShown, hpShown, dt * 0.35f);
                mpShown = Mathf.Lerp(mpShown, mpN, dt * 10f);
                stShown = Mathf.Lerp(stShown, stN, dt * 14f);
                hpFill.fillAmount = ArcSpan * hpShown;
                hpTrail.fillAmount = ArcSpan * hpTrailShown;
                mpFill.fillAmount = ArcSpan * mpShown;
                stFill.fillAmount = ArcSpan * stShown;
                // low hp heartbeat
                float low = hpN < 0.3f ? (0.5f + 0.5f * Mathf.Sin(Time.time * 8f)) : 0;
                hpFill.color = Color.Lerp(Color.white, new Color(1f, 0.6f, 0.6f), low);
                hpText.text = Mathf.CeilToInt(p.hp) + " / " + Mathf.RoundToInt(gs.HpMax);
                levelText.text = gs.level.ToString();
                goldText.text = gs.gold.ToString();
                rankText.text = "Aventureiro · Rank " + gs.guildRank;
                orbs[3].count.text = gs.Count("potion").ToString();
                orbs[1].cd.fillAmount = p.mp < 12 ? 1 - p.mp / 12f : 0;
                orbs[2].cd.fillAmount = p.st < 24 ? 1 - p.st / 24f : 0;
                orbs[0].cd.fillAmount = p.st < 7 ? 1 - p.st / 7f : 0;
            }
            if (g != null) questText.text = g.QuestLine();
            hurtPulse = Mathf.Max(0, hurtPulse - dt * 2.2f);
            vignette.color = Color.Lerp(new Color(0.05f, 0.02f, 0.08f, 0.5f), new Color(0.75f, 0.05f, 0.05f, 0.85f), hurtPulse);

            var cam = CameraRig.I != null ? CameraRig.I.cam : null;
            float scale = root.rect.height / Screen.height;
            for (int i = floaters.Count - 1; i >= 0; i--)
            {
                var f = floaters[i];
                f.t += dt;
                if (cam != null)
                {
                    Vector2 sp = cam.WorldToScreenPoint(f.world);
                    f.rt.anchoredPosition = sp * scale + f.vel * f.t * (1 - f.t * 0.5f);
                }
                float pop = f.t < 0.12f ? Mathf.Lerp(f.scale * 1.6f, f.scale, f.t / 0.12f) : f.scale;
                f.rt.localScale = Vector3.one * pop;
                var c = f.txt.color;
                c.a = Mathf.Clamp01((f.life - f.t) / 0.3f);
                f.txt.color = c;
                if (f.t >= f.life) { Destroy(f.rt.gameObject); floaters.RemoveAt(i); }
            }
            for (int i = feeds.Count - 1; i >= 0; i--)
            {
                var f = feeds[i];
                f.t += dt;
                f.cg.alpha = Mathf.Clamp01(f.t * 6f) * Mathf.Clamp01((3.2f - f.t) / 0.5f);
                if (f.t > 3.2f) { Destroy(f.rt.gameObject); feeds.RemoveAt(i); }
            }
            UpdatePlates(cam, scale);

            if (InDialogue)
            {
                typeT += dt;
                var full = lines[lineIdx].text;
                int n = Mathf.Min(full.Length, Mathf.FloorToInt(typeT * 55f));
                dlgText.text = full.Substring(0, n);
                dlgHint.color = new Color(1f, 0.9f, 0.6f, n >= full.Length ? 0.6f + 0.4f * Mathf.Sin(Time.time * 5) : 0);
                if (Input.GetKeyDown(KeyCode.E) || Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.Mouse0))
                    AdvanceDialogue();
            }
            if (bannerT >= 0)
            {
                bannerT += dt;
                float a = Mathf.Clamp01(bannerT / 0.6f) * Mathf.Clamp01((4f - bannerT) / 0.8f);
                foreach (var gr in banner.GetComponentsInChildren<Graphic>())
                {
                    var c = gr.color;
                    c.a = a;
                    gr.color = c;
                }
                banner.anchoredPosition = new Vector2(0, -170 + (1 - Mathf.Clamp01(bannerT / 0.6f)) * 20);
                if (bannerT > 4f) { bannerT = -1; banner.gameObject.SetActive(false); }
            }
        }

        void UpdatePlates(Camera cam, float scale)
        {
            if (cam == null) return;
            foreach (var e in Enemy.All)
            {
                bool show = !e.dead && (Time.time - e.lastHurt < 6f || (Player.I != null && (Player.I.Pos - e.Pos).magnitude < 5f));
                plates.TryGetValue(e, out var pl);
                if (show && pl == null)
                {
                    var rt = Rect("plate", root, Vector2.zero, Vector2.zero, new Vector2(120, 30));
                    pl = new Plate { e = e, rt = rt, shown = 1 };
                    Img("track", rt, Ui("pill_track"), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(104, 16));
                    pl.trail = Img("trail", rt, Ui("pill_fill"), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(98, 10));
                    pl.trail.type = Image.Type.Filled;
                    pl.trail.fillMethod = Image.FillMethod.Horizontal;
                    pl.trail.color = new Color(1f, 0.9f, 0.7f);
                    pl.fill = Img("fill", rt, Ui("pill_fill"), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(98, 10));
                    pl.fill.type = Image.Type.Filled;
                    pl.fill.fillMethod = Image.FillMethod.Horizontal;
                    pl.name = Txt("lv", rt, "Nv " + e.level, SansBold, 18, e.level > (Player.I != null ? Player.I.gs.level : 1) ? new Color(1f, 0.5f, 0.4f) : new Color(1f, 0.95f, 0.85f),
                        new Vector2(0.5f, 0.5f), new Vector2(0, 18), new Vector2(120, 22));
                    plates[e] = pl;
                }
                if (pl == null) continue;
                pl.rt.gameObject.SetActive(show);
                if (!show) continue;
                Vector2 sp = cam.WorldToScreenPoint(e.Pos + Vector2.up * (2.1f * e.body.transform.localScale.y));
                pl.rt.anchoredPosition = sp * scale;
                float n = e.hp / e.maxHp;
                pl.fill.fillAmount = n;
                pl.shown = pl.shown < n ? n : Mathf.MoveTowards(pl.shown, n, Time.deltaTime * 0.6f);
                pl.trail.fillAmount = pl.shown;
            }
            var dead = new List<Enemy>();
            foreach (var kv in plates)
                if (kv.Key == null || kv.Key.dead) { if (kv.Value.rt != null) Destroy(kv.Value.rt.gameObject); dead.Add(kv.Key); }
            foreach (var k in dead) plates.Remove(k);
        }
    }
}
