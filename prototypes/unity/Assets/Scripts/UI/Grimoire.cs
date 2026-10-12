using UnityEngine;
using UnityEngine.UI;

namespace Aetheria
{
    /// <summary>Inventory / skills menu drawn as an open leather book (Tab). Pauses the game.</summary>
    public class Grimoire : MonoBehaviour
    {
        public static Grimoire I;
        public bool open;
        public int lastToggleFrame = -1;
        Hud hud;
        RectTransform root, page;
        int sel;
        float prevScale = 1;

        static readonly string[] SparkNames = { "", "Centelha", "Lança de Chamas", "Cometa Arcano" };
        static readonly string[] SparkDesc =
        {
            "",
            "Uma faísca elétrica. Fraca, rápida, sua.",
            "A centelha vira fogo: dano maior e explosão.",
            "Magia arcana pura que atravessa demônios."
        };

        public static Grimoire Create(Hud h)
        {
            var g = h.gameObject.AddComponent<Grimoire>();
            g.hud = h;
            I = g;
            g.root = h.Rect("grimoire", h.root, new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(1920, 1080));
            var dim = h.Img("dim", g.root, Util.SoftCircle, new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(2600, 1800));
            dim.color = new Color(0.02f, 0.01f, 0.04f, 0.75f);
            h.Img("book", g.root, Hud.Ui("book"), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(1400, 860));
            g.root.gameObject.SetActive(false);
            return g;
        }

        public void Toggle()
        {
            if (lastToggleFrame == Time.frameCount) return;
            lastToggleFrame = Time.frameCount;
            open = !open;
            root.gameObject.SetActive(open);
            if (open)
            {
                prevScale = Time.timeScale;
                Time.timeScale = 0;
                sel = 0;
                Refresh();
                Sfx.Play("ui", 0.3f, 0.8f);
            }
            else Time.timeScale = prevScale <= 0 ? 1 : prevScale;
            if (Player.I != null) Player.I.inputLocked = open;
        }

        void Update()
        {
            if (!open) return;
            var gs = Player.I.gs;
            int n = gs.invIds.Count;
            if (Input.GetKeyDown(KeyCode.Tab) || Input.GetKeyDown(KeyCode.Escape)) { Toggle(); return; }
            if (n > 0 && (Input.GetKeyDown(KeyCode.S) || Input.GetKeyDown(KeyCode.DownArrow))) { sel = (sel + 1) % n; Refresh(); }
            if (n > 0 && (Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.UpArrow))) { sel = (sel + n - 1) % n; Refresh(); }
            if (n > 0 && (Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.E))) { Use(gs.invIds[sel]); Refresh(); }
        }

        static string Name(string id) => string.IsNullOrEmpty(id) ? "—" : Data.Items[id].name;

        void Use(string id)
        {
            var p = Player.I;
            var gs = p.gs;
            var d = Data.Items[id];
            if (id == "sword_tome")
            {
                if (gs.swordTier >= 2) { Fx.Toast("O Corte Crescente já foi aprendido", Color.white); return; }
                gs.Take(id);
                gs.swordTier = 2;
                Sfx.Play("levelup", 0.6f, 1.2f);
                hud.Banner("Corte Crescente", "O 3º golpe lança uma lâmina de energia");
                return;
            }
            if (d.slot > 0)
            {
                gs.Equip(id);
                Sfx.Play("pickup", 0.5f, 0.9f);
                if (p.hp > gs.HpMax) p.hp = gs.HpMax;
                return;
            }
            if (id == "spark_tome")
            {
                if (gs.sparkTier >= 3) { Fx.Toast("A Centelha já está no máximo", Color.white); return; }
                gs.Take(id);
                gs.sparkTier++;
                Sfx.Play("levelup", 0.6f, 1.1f);
                hud.Banner("A Centelha evoluiu", SparkNames[gs.sparkTier]);
                return;
            }
            if (!d.consumable) { Sfx.Play("ui", 0.2f, 0.6f); return; }
            if (d.heal > 0 && p.hp >= gs.HpMax) return;
            if (d.mana > 0 && p.mp >= gs.maxMp) return;
            gs.Take(id);
            p.hp = Mathf.Min(gs.HpMax, p.hp + (d.heal > 0 ? Mathf.Max(d.heal, 0.35f * gs.HpMax) : 0));
            p.mp = Mathf.Min(gs.maxMp, p.mp + (d.mana > 0 ? Mathf.Max(d.mana, 0.4f * gs.maxMp) : 0));
            Sfx.Play("potion", 0.5f, 1f);
        }

        void Refresh()
        {
            if (page != null) Destroy(page.gameObject);
            page = hud.Rect("page", root, new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(1400, 860));
            var gs = Player.I.gs;
            var ink = new Color(0.27f, 0.16f, 0.1f);
            var faint = new Color(0.45f, 0.32f, 0.2f);
            var c = new Vector2(0.5f, 0.5f);
            Font serif = Hud.Serif, sans = Hud.Sans, bold = Hud.SansBold;

            // ---- left page: the hero
            hud.Txt("name", page, "Ren Takamura", serif, 44, ink, c, new Vector2(-335, 300), new Vector2(500, 60), TextAnchor.MiddleCenter, false);
            hud.Txt("sub", page, $"Nível {gs.level}  ·  Aventureiro Rank {gs.guildRank}", sans, 26, faint, c, new Vector2(-335, 236), new Vector2(500, 40), TextAnchor.MiddleCenter, false);
            hud.Img("por", page, Hud.Ui("portrait"), c, new Vector2(-500, 120), new Vector2(130, 130));
            hud.Img("fr", page, Hud.Ui("medallion"), c, new Vector2(-500, 120), new Vector2(200, 200));
            var p = Player.I;
            string stats =
                $"Vida          {Mathf.CeilToInt(p.hp)} / {Mathf.RoundToInt(gs.HpMax)}\n" +
                $"Mana          {Mathf.FloorToInt(p.mp)} / {Mathf.RoundToInt(gs.maxMp)}\n" +
                $"Fôlego        {Mathf.RoundToInt(gs.maxSt)}\n" +
                $"Ataque        {gs.TotalAtk:0}   Defesa  {gs.TotalDef:0}\n" +
                $"Magia          {gs.TotalMag:0}\n" +
                $"Experiência  {gs.xp} / {Data.XpToNext(gs.level)}\n" +
                $"Ouro            {gs.gold}\n" +
                $"Arma: {Name(gs.eqWeapon)}\n" +
                $"Armadura: {Name(gs.eqArmor)}\n" +
                $"Amuleto: {Name(gs.eqCharm)}";
            hud.Txt("stats", page, stats, bold, 22, ink, c, new Vector2(-300, 82), new Vector2(380, 320), TextAnchor.MiddleLeft, false).lineSpacing = 1.1f;
            hud.Img("flo", page, Hud.Ui("flourish"), c, new Vector2(-335, -60), new Vector2(380, 30));
            hud.Txt("skt", page, "Grimório de Magias", serif, 30, ink, c, new Vector2(-335, -100), new Vector2(500, 40), TextAnchor.MiddleCenter, false);
            for (int t = 1; t <= 3; t++)
            {
                bool have = gs.sparkTier >= t;
                float y = -150 - (t - 1) * 62;
                var ic = hud.Img("sp" + t, page, Icons.Get("skill_spark"), c, new Vector2(-560, y), new Vector2(52, 52));
                ic.color = have ? (t == 1 ? new Color(0.6f, 0.85f, 1f) : t == 2 ? new Color(1f, 0.6f, 0.3f) : new Color(0.8f, 0.55f, 1f)) : new Color(0.3f, 0.25f, 0.2f, 0.5f);
                hud.Txt("spn" + t, page, SparkNames[t] + (gs.sparkTier == t ? "  ◆" : ""), bold, 26, have ? ink : faint, c, new Vector2(-300, y + 12), new Vector2(440, 30), TextAnchor.MiddleLeft, false);
                hud.Txt("spd" + t, page, have ? SparkDesc[t] : "Requer um Tomo da Centelha", sans, 21, faint, c, new Vector2(-300, y - 14), new Vector2(440, 26), TextAnchor.MiddleLeft, false);
            }

            // ---- right page: the bag
            hud.Txt("bag", page, "Bolsa", serif, 44, ink, c, new Vector2(335, 300), new Vector2(500, 60), TextAnchor.MiddleCenter, false);
            if (gs.invIds.Count == 0)
                hud.Txt("empty", page, "Vazia. Os demônios carregam coisas valiosas...", sans, 24, faint, c, new Vector2(335, 150), new Vector2(500, 40), TextAnchor.MiddleCenter, false);
            sel = Mathf.Clamp(sel, 0, Mathf.Max(0, gs.invIds.Count - 1));
            for (int i = 0; i < gs.invIds.Count && i < 9; i++)
            {
                var d = Data.Items[gs.invIds[i]];
                float y = 220 - i * 56;
                if (i == sel)
                {
                    var hl = hud.Img("hl", page, Hud.Ui("smear"), c, new Vector2(335, y), new Vector2(560, 70));
                    hl.color = new Color(0.85f, 0.6f, 0.2f, 0.35f);
                    hud.Txt("mk", page, "◆", serif, 22, new Color(0.75f, 0.5f, 0.15f), c, new Vector2(100, y), new Vector2(30, 30), TextAnchor.MiddleCenter, false);
                }
                hud.Img("ic" + i, page, Icons.Get(d.icon), c, new Vector2(150, y), new Vector2(48, 48));
                var rc = Data.RarityColors[(int)d.rarity];
                var nameCol = d.rarity == Rarity.Common ? ink : Color.Lerp(rc, ink, 0.45f);
                hud.Txt("n" + i, page, d.name, bold, 27, nameCol, c, new Vector2(370, y), new Vector2(380, 34), TextAnchor.MiddleLeft, false);
                hud.Txt("c" + i, page, "×" + gs.invCounts[i], serif, 26, faint, c, new Vector2(590, y), new Vector2(80, 34), TextAnchor.MiddleRight, false);
            }
            if (gs.invIds.Count > 0)
            {
                var d = Data.Items[gs.invIds[sel]];
                hud.Img("flo2", page, Hud.Ui("flourish"), c, new Vector2(335, -250), new Vector2(380, 30));
                string stat = d.slot > 0 ? "\n" + (d.atk > 0 ? $"ATQ +{d.atk:0}  " : "") + (d.def > 0 ? $"DEF +{d.def:0}  " : "") + (d.mag > 0 ? $"MAG +{d.mag:0}  " : "") + (d.hp > 0 ? $"PV +{d.hp:0}  " : "") + "· Enter: equipar" : "";
                var desc = hud.Txt("desc", page, (d.desc ?? "") + stat, sans, 22, ink, c, new Vector2(335, -292), new Vector2(520, 60), TextAnchor.UpperCenter, false);
                desc.horizontalOverflow = HorizontalWrapMode.Wrap;
            }
            hud.Txt("hint", page, "W/S escolher  ·  Enter usar  ·  Tab fechar", sans, 21, faint, c, new Vector2(335, -340), new Vector2(560, 30), TextAnchor.MiddleCenter, false);
        }
    }
}
