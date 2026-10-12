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
        // Optional combat archetype; empty preserves the original imp behaviour.
        public string behavior = "";
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

            // Pilot Lote 2: three distinct insectoid species, with existing loot IDs.
            // Additional demons are not substituted for the prologue's imp quest targets.
            Demons["mantis_reaver"] = new DemonDef
            {
                id = "mantis_reaver", name = "Mantis Reaver", sheet = "Sprites/Demons/mantis_reaver",
                behavior = "mantis_dash", hp = 95, dmg = 19, speed = 3.5f, aggro = 8.5f,
                xp = 33, poise = 16, scale = 0.86f,
                drops = new[] { ("gold", 1f, 7, 14), ("imp_horn", 0.25f, 1, 1), ("hell_ember", 0.13f, 1, 1) }
            };
            Demons["scarab_brute"] = new DemonDef
            {
                id = "scarab_brute", name = "Escaravelho Infernal", sheet = "Sprites/Demons/scarab_brute",
                behavior = "scarab_shockwave", hp = 240, dmg = 24, speed = 1.65f, aggro = 7.2f,
                xp = 55, poise = 48, scale = 0.91f,
                drops = new[] { ("gold", 1f, 12, 24), ("hell_ember", 0.24f, 1, 1), ("potion", 0.15f, 1, 1) }
            };
            Demons["moth_hexer"] = new DemonDef
            {
                id = "moth_hexer", name = "Mariposa Ocultista", sheet = "Sprites/Demons/moth_hexer",
                behavior = "moth_hex", hp = 75, dmg = 15, speed = 2.75f, aggro = 9f,
                xp = 37, poise = 12, caster = true, scale = 0.78f,
                drops = new[] { ("gold", 1f, 6, 14), ("ether", 0.3f, 1, 1), ("hell_ember", 0.10f, 1, 1) }
            };
            // Lote 2 Set A: new anatomy families, not reskins or weapon-swaps.
            Demons["termite_burrower"] = new DemonDef
            {
                id = "termite_burrower", name = "Térmita Escavadora", sheet = "Sprites/Demons/termite_burrower",
                behavior = "termite_burrow", hp = 118, dmg = 20, speed = 2.0f, aggro = 7.5f,
                xp = 39, poise = 27, scale = 0.84f,
                drops = new[] { ("gold", 1f, 8, 16), ("potion", 0.10f, 1, 1), ("hell_ember", 0.17f, 1, 1) }
            };
            Demons["vespa_lancer"] = new DemonDef
            {
                id = "vespa_lancer", name = "Vespa Perfuradora", sheet = "Sprites/Demons/vespa_lancer",
                behavior = "vespa_sting", hp = 81, dmg = 19, speed = 4.1f, aggro = 9.0f,
                xp = 42, poise = 12, scale = 0.80f,
                drops = new[] { ("gold", 1f, 6, 17), ("ether", 0.15f, 1, 1), ("hell_ember", 0.11f, 1, 1) }
            };
            Demons["cicada_screecher"] = new DemonDef
            {
                id = "cicada_screecher", name = "Cigarra Estridente", sheet = "Sprites/Demons/cicada_screecher",
                behavior = "cicada_sonic", hp = 105, dmg = 16, speed = 2.9f, aggro = 8.0f,
                xp = 40, poise = 21, scale = 0.77f,
                drops = new[] { ("gold", 1f, 7, 16), ("ether", 0.15f, 1, 1), ("hell_ember", 0.12f, 1, 1) }
            };
            // Set B: four new independent bodies and actual combat archetypes.
            Demons["ant_guard"] = new DemonDef
            {
                id = "ant_guard", name = "Formiga Sentinela", sheet = "Sprites/Demons/ant_guard",
                behavior = "ant_carapace", hp = 145, dmg = 18, speed = 2.6f, aggro = 7.7f,
                xp = 45, poise = 34, scale = .86f,
                drops = new[] { ("gold", 1f, 9, 17), ("potion", .12f, 1, 1), ("hell_ember", .11f, 1, 1) }
            };
            Demons["roach_plaguebearer"] = new DemonDef
            {
                id = "roach_plaguebearer", name = "Barata Pestilenta", sheet = "Sprites/Demons/roach_plaguebearer",
                behavior = "roach_plague", hp = 108, dmg = 14, speed = 3.45f, aggro = 8.3f,
                xp = 41, poise = 16, scale = .78f,
                drops = new[] { ("gold", 1f, 8, 17), ("ether", .12f, 1, 1), ("hell_ember", .14f, 1, 1) }
            };
            Demons["spike_beetle"] = new DemonDef
            {
                id = "spike_beetle", name = "Besouro Ouriço", sheet = "Sprites/Demons/spike_beetle",
                behavior = "spike_roll", hp = 160, dmg = 20, speed = 2.1f, aggro = 7.5f,
                xp = 48, poise = 35, scale = .82f,
                drops = new[] { ("gold", 1f, 9, 18), ("potion", .08f, 1, 1), ("hell_ember", .15f, 1, 1) }
            };
            Demons["dragonfly_skirmisher"] = new DemonDef
            {
                id = "dragonfly_skirmisher", name = "Libélula Caçadora", sheet = "Sprites/Demons/dragonfly_skirmisher",
                behavior = "dragonfly_zigzag", hp = 80, dmg = 17, speed = 4.2f, aggro = 9f,
                xp = 47, poise = 12, scale = .82f,
                drops = new[] { ("gold", 1f, 9, 20), ("ether", .14f, 1, 1), ("hell_ember", .12f, 1, 1) }
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
