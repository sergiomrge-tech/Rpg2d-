using System;
using System.Collections.Generic;
using UnityEngine;

namespace Aetheria
{
    public enum Rarity { Common, Uncommon, Rare, Epic, Legendary }

    public class ItemDef
    {
        public string id, name, desc, icon;
        public Rarity rarity;
        public int value;
        public bool consumable;
        public int heal, mana;
    }

    public class DemonDef
    {
        public string id, name, sheet;
        public float hp, dmg, speed, aggro, xp, scale = 1f, poise;
        public bool caster;
        // Unique insectoid combat logic; default preserves original Imp AI.
        public string combatStyle = "imp";
        public float attackReach = 1.55f;
        public float castReach = 7.5f;
        public float bodyRadius = 0.3f;
        public (string item, float chance, int min, int max)[] drops;
    }

    /// <summary>Static game data (items, demons). Balance: enemies scale ~22%/level, early game is lethal if careless.</summary>
    public static class Data
    {
        public static readonly Dictionary<string, ItemDef> Items = new Dictionary<string, ItemDef>();
        public static readonly Dictionary<string, DemonDef> Demons = new Dictionary<string, DemonDef>();

        public static readonly Color[] RarityColors =
        {
            new Color(0.92f, 0.9f, 0.85f), new Color(0.45f, 0.9f, 0.45f), new Color(0.35f, 0.65f, 1f),
            new Color(0.78f, 0.45f, 1f), new Color(1f, 0.68f, 0.2f)
        };

        static Data()
        {
            Add(new ItemDef { id = "gold", name = "Moedas de Ouro", icon = "coin", value = 1 });
            Add(new ItemDef { id = "potion", name = "Poção de Vida", desc = "Restaura 40 PV.", icon = "potion", value = 25, consumable = true, heal = 40 });
            Add(new ItemDef { id = "ether", name = "Éter Azul", desc = "Restaura 30 PM.", icon = "ether", value = 30, consumable = true, mana = 30, rarity = Rarity.Uncommon });
            Add(new ItemDef { id = "imp_horn", name = "Chifre de Diabrete", desc = "Material. A Guilda paga bem.", icon = "horn", value = 12 });
            Add(new ItemDef { id = "hell_ember", name = "Brasa Infernal", desc = "Material raro para forjar armas de fogo.", icon = "ember", value = 60, rarity = Rarity.Rare });
            Add(new ItemDef { id = "spark_tome", name = "Tomo: Centelha II", desc = "Evolui a Centelha em Lança de Chamas.", icon = "tome", value = 250, rarity = Rarity.Epic });

            Demons["imp"] = new DemonDef
            {
                id = "imp", name = "Diabrete", sheet = "Sprites/Demons/imp", hp = 46, dmg = 15, speed = 2.6f, aggro = 7f,
                xp = 14, caster = true, poise = 10, scale = 1.15f,
                drops = new[] { ("gold", 1f, 3, 9), ("imp_horn", 0.45f, 1, 1), ("potion", 0.12f, 1, 1), ("ether", 0.06f, 1, 1),
                                ("hell_ember", 0.05f, 1, 1), ("spark_tome", 0.012f, 1, 1) }
            };

            // Lote 2 pilot: real in-game enemies, loaded from independently animated
            // PNG/JSON Resources sheets. No changes to the approved hero/map art.
            Demons["mantis_reaver"] = new DemonDef
            {
                id = "mantis_reaver", name = "Ceifador Mantídeo",
                sheet = "Sprites/Demons/mantis_reaver", combatStyle = "mantis",
                hp = 75, dmg = 16, speed = 3.5f, aggro = 9f, xp = 31,
                caster = true, attackReach = 1.9f, castReach = 5.2f,
                bodyRadius = 0.35f, poise = 15f, scale = 1.08f,
                drops = new[] { ("gold", 1f, 6, 14), ("imp_horn", .2f, 1, 1),
                                 ("hell_ember", .06f, 1, 1) }
            };
            Demons["scarab_brute"] = new DemonDef
            {
                id = "scarab_brute", name = "Escaravelho Abissal",
                sheet = "Sprites/Demons/scarab_brute", combatStyle = "scarab",
                hp = 165, dmg = 19, speed = 1.75f, aggro = 7f, xp = 45,
                caster = true, attackReach = 2.0f, castReach = 4f,
                bodyRadius = .48f, poise = 50f, scale = 1.16f,
                drops = new[] { ("gold", 1f, 11, 24), ("imp_horn", .15f, 1, 2),
                                 ("hell_ember", .09f, 1, 1) }
            };
            Demons["moth_hexer"] = new DemonDef
            {
                id = "moth_hexer", name = "Mariposa Maldita",
                sheet = "Sprites/Demons/moth_hexer", combatStyle = "moth",
                hp = 63, dmg = 11, speed = 2.5f, aggro = 10f, xp = 36,
                caster = true, attackReach = 1.45f, castReach = 8.2f,
                bodyRadius = .27f, poise = 13f, scale = 1.04f,
                drops = new[] { ("gold", 1f, 7, 17), ("ether", .15f, 1, 1),
                                 ("hell_ember", .07f, 1, 1) }
            };
        }

        static void Add(ItemDef d) => Items[d.id] = d;

        public static float LevelScale(int lv) => Mathf.Pow(1.22f, lv - 1);
        public static int XpToNext(int lv) => Mathf.RoundToInt(90 * Mathf.Pow(1.38f, lv - 1));
    }

    /// <summary>Persistent player progress.</summary>
    [Serializable]
    public class GameState
    {
        public int level = 1, xp, gold = 10;
        public float maxHp = 100, maxMp = 50, maxSt = 100;
        public float atk = 11, mag = 14;
        public int sparkTier = 1;
        public string guildRank = "F";
        public List<string> invIds = new List<string> { "potion", "potion" };
        public List<int> invCounts = new List<int> { 1, 1 };

        public int Count(string id)
        {
            int n = 0;
            for (int i = 0; i < invIds.Count; i++) if (invIds[i] == id) n += invCounts[i];
            return n;
        }

        public void Add(string id, int n)
        {
            if (id == "gold") { gold += n; return; }
            int i = invIds.IndexOf(id);
            if (i < 0) { invIds.Add(id); invCounts.Add(n); }
            else invCounts[i] += n;
        }

        public bool Take(string id)
        {
            int i = invIds.IndexOf(id);
            if (i < 0) return false;
            invCounts[i]--;
            if (invCounts[i] <= 0) { invIds.RemoveAt(i); invCounts.RemoveAt(i); }
            return true;
        }

        /// <returns>true when leveled up</returns>
        public bool GainXp(int amount)
        {
            xp += amount;
            bool up = false;
            while (xp >= Data.XpToNext(level))
            {
                xp -= Data.XpToNext(level);
                level++;
                maxHp += 14; maxMp += 6; maxSt += 4; atk += 2.2f; mag += 2.6f;
                up = true;
            }
            return up;
        }
    }
}
