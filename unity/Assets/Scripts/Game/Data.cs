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
        public bool caster, boss;
        public string title;
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

            Demons["oni"] = new DemonDef
            {
                id = "oni", name = "Oni Soldado", sheet = "Sprites/Demons/oni", hp = 110, dmg = 24, speed = 2.1f, aggro = 6f,
                xp = 30, poise = 38, scale = 1.25f,
                drops = new[] { ("gold", 1f, 8, 18), ("potion", 0.2f, 1, 1), ("hell_ember", 0.12f, 1, 1), ("spark_tome", 0.02f, 1, 1) }
            };
            Demons["grakk"] = new DemonDef
            {
                id = "grakk", name = "Grakk", title = "Chefe dos Diabretes", sheet = "Sprites/Demons/grakk", hp = 420, dmg = 22,
                speed = 2.9f, aggro = 8f, xp = 160, caster = true, boss = true, poise = 70, scale = 1.9f,
                drops = new[] { ("gold", 1f, 120, 160), ("spark_tome", 1f, 1, 1), ("hell_ember", 1f, 2, 3), ("potion", 1f, 2, 2) }
            };

            // ---- Lote 1 (conceitos do catalogo refeitos no rig animado)
            D("imp_scout", "Diabrete Batedor", "Demons/imp_scout", 34, 13, 3.7f, 8f, 16, 6, 1.15f, false);
            D("imp_raider", "Diabrete Saqueador", "Demons/imp_raider", 72, 19, 2.3f, 6f, 22, 26, 1.2f, false);
            D("imp_pyro", "Diabrete Piromante", "Demons/imp_pyro", 46, 19, 2.4f, 8f, 20, 10, 1.15f, true);
            D("imp_hexer", "Diabrete Feiticeiro", "Demons/imp_hexer", 40, 17, 2.4f, 8.5f, 20, 8, 1.15f, true);
            D("imp_bomber", "Diabrete Bombardeiro", "Demons/imp_bomber", 48, 22, 2.5f, 7.5f, 20, 10, 1.15f, true);
            D("imp_howler", "Diabrete Uivador", "Demons/imp_howler", 58, 16, 2.6f, 9f, 22, 14, 1.2f, true);
            D("oni_lancer", "Oni Lanceiro", "Demons/oni_lancer", 100, 23, 2.4f, 6.5f, 32, 34, 1.25f, false);
            D("oni_shielder", "Oni Escudeiro", "Demons/oni_shielder", 165, 18, 1.7f, 5.5f, 38, 80, 1.3f, false);
            D("oni_executioner", "Oni Carrasco", "Demons/oni_executioner", 135, 34, 1.9f, 6f, 44, 50, 1.35f, false);
            D("morgash_ironhorn", "Morgash Chifre-de-Ferro", "Demons/morgash_ironhorn", 950, 36, 2.0f, 9f, 400, 140, 2.0f, false, "General Oni das Minas");
            D("velka_flamebeak", "Velka Bico-de-Fogo", "Demons/velka_flamebeak", 620, 28, 3.2f, 10f, 360, 90, 1.9f, true, "Rainha Harpia do Deserto");
            D("krull_chainlord", "Krull Senhor-das-Correntes", "Demons/krull_chainlord", 780, 32, 2.3f, 9f, 380, 120, 1.9f, false, "Carcereiro do Pantano");
            D("thornmaw_alpha", "Thornmaw Alfa", "Demons/thornmaw_alpha", 700, 30, 2.8f, 9f, 360, 110, 1.9f, false, "Fera Espinhosa de Velmoor");

            // ---- Etapa 2: Velmoor
            D("spirit_corrupt", "Espírito Corrompido", "Demons/spirit_corrupt", 58, 20, 3.0f, 8.5f, 26, 12, 1.2f, true);
            D("treant_demon", "Treant-Demônio", "Demons/treant_demon", 190, 30, 1.6f, 6f, 46, 90, 1.45f, false);
            D("dryad_profane", "Dríade Profanada", "Demons/dryad_profane", 1100, 30, 2.4f, 10f, 520, 120, 1.9f, true, "Guardiã Corrompida de Velmoor");

            // ---- Assets do GPT, como foram entregues (Bestiario F9)
            D("gpt_ant_guard", "Ant Guard (GPT)", "DemonsGpt/ant_guard", 70, 18, 2.3f, 8f, 20, 15, 1.39f, true);
            D("gpt_brood_tyrant", "Brood Tyrant (GPT)", "DemonsGpt/brood_tyrant", 600, 28, 2.3f, 8f, 200, 90, 1.04f, true, "Asset do GPT");
            D("gpt_cicada_screecher", "Cicada Screecher (GPT)", "DemonsGpt/cicada_screecher", 70, 18, 2.3f, 8f, 20, 15, 1.39f, true);
            D("gpt_dragonfly_skirmisher", "Dragonfly Skirmisher (GPT)", "DemonsGpt/dragonfly_skirmisher", 70, 18, 2.3f, 8f, 20, 15, 1.39f, true);
            D("gpt_grakk", "Grakk (GPT)", "DemonsGpt/grakk", 600, 28, 2.3f, 8f, 200, 90, 2.08f, true, "Asset do GPT");
            D("gpt_imp", "Imp (GPT)", "DemonsGpt/imp", 70, 18, 2.3f, 8f, 20, 15, 2.08f, true);
            D("gpt_imp_bomber", "Imp Bomber (GPT)", "DemonsGpt/imp_bomber", 70, 18, 2.3f, 8f, 20, 15, 2.08f, true);
            D("gpt_imp_hexer", "Imp Hexer (GPT)", "DemonsGpt/imp_hexer", 70, 18, 2.3f, 8f, 20, 15, 2.08f, true);
            D("gpt_imp_howler", "Imp Howler (GPT)", "DemonsGpt/imp_howler", 70, 18, 2.3f, 8f, 20, 15, 2.08f, true);
            D("gpt_imp_pyro", "Imp Pyro (GPT)", "DemonsGpt/imp_pyro", 70, 18, 2.3f, 8f, 20, 15, 2.08f, true);
            D("gpt_imp_raider", "Imp Raider (GPT)", "DemonsGpt/imp_raider", 70, 18, 2.3f, 8f, 20, 15, 2.08f, true);
            D("gpt_imp_scout", "Imp Scout (GPT)", "DemonsGpt/imp_scout", 70, 18, 2.3f, 8f, 20, 15, 2.08f, true);
            D("gpt_krull_chainlord", "Krull Chainlord (GPT)", "DemonsGpt/krull_chainlord", 600, 28, 2.3f, 8f, 200, 90, 1.56f, true, "Asset do GPT");
            D("gpt_mantis_high_reaper", "Mantis High Reaper (GPT)", "DemonsGpt/mantis_high_reaper", 600, 28, 2.3f, 8f, 200, 90, 1.04f, true, "Asset do GPT");
            D("gpt_mantis_reaver", "Mantis Reaver (GPT)", "DemonsGpt/mantis_reaver", 70, 18, 2.3f, 8f, 20, 15, 1.39f, true);
            D("gpt_morgash_ironhorn", "Morgash Ironhorn (GPT)", "DemonsGpt/morgash_ironhorn", 600, 28, 2.3f, 8f, 200, 90, 1.56f, true, "Asset do GPT");
            D("gpt_moth_hexer", "Moth Hexer (GPT)", "DemonsGpt/moth_hexer", 70, 18, 2.3f, 8f, 20, 15, 1.39f, true);
            D("gpt_moth_oracle", "Moth Oracle (GPT)", "DemonsGpt/moth_oracle", 600, 28, 2.3f, 8f, 200, 90, 1.04f, true, "Asset do GPT");
            D("gpt_oni_executioner", "Oni Executioner (GPT)", "DemonsGpt/oni_executioner", 70, 18, 2.3f, 8f, 20, 15, 1.78f, true);
            D("gpt_oni_lancer", "Oni Lancer (GPT)", "DemonsGpt/oni_lancer", 70, 18, 2.3f, 8f, 20, 15, 2.08f, true);
            D("gpt_oni_shielder", "Oni Shielder (GPT)", "DemonsGpt/oni_shielder", 70, 18, 2.3f, 8f, 20, 15, 1.92f, true);
            D("gpt_oni_soldier", "Oni Soldier (GPT)", "DemonsGpt/oni_soldier", 70, 18, 2.3f, 8f, 20, 15, 2.08f, true);
            D("gpt_queen_vespara", "Queen Vespara (GPT)", "DemonsGpt/queen_vespara", 600, 28, 2.3f, 8f, 200, 90, 1.04f, true, "Asset do GPT");
            D("gpt_roach_plaguebearer", "Roach Plaguebearer (GPT)", "DemonsGpt/roach_plaguebearer", 70, 18, 2.3f, 8f, 20, 15, 1.39f, true);
            D("gpt_scarab_brute", "Scarab Brute (GPT)", "DemonsGpt/scarab_brute", 70, 18, 2.3f, 8f, 20, 15, 1.39f, true);
            D("gpt_scarab_colossus", "Scarab Colossus (GPT)", "DemonsGpt/scarab_colossus", 600, 28, 2.3f, 8f, 200, 90, 1.04f, true, "Asset do GPT");
            D("gpt_spike_beetle", "Spike Beetle (GPT)", "DemonsGpt/spike_beetle", 70, 18, 2.3f, 8f, 20, 15, 1.39f, true);
            D("gpt_termite_burrower", "Termite Burrower (GPT)", "DemonsGpt/termite_burrower", 70, 18, 2.3f, 8f, 20, 15, 1.39f, true);
            D("gpt_thornmaw_alpha", "Thornmaw Alpha (GPT)", "DemonsGpt/thornmaw_alpha", 600, 28, 2.3f, 8f, 200, 90, 1.39f, true, "Asset do GPT");
            D("gpt_velka_flamebeak", "Velka Flamebeak (GPT)", "DemonsGpt/velka_flamebeak", 600, 28, 2.3f, 8f, 200, 90, 1.56f, true, "Asset do GPT");
            D("gpt_vespa_lancer", "Vespa Lancer (GPT)", "DemonsGpt/vespa_lancer", 70, 18, 2.3f, 8f, 20, 15, 1.39f, true);
        }

        static void D(string id, string name, string sheet, float hp, float dmg, float speed, float aggro, float xp, float poise,
                      float scale, bool caster, string bossTitle = null)
        {
            bool boss = bossTitle != null;
            Demons[id] = new DemonDef
            {
                id = id, name = name, sheet = "Sprites/" + sheet, hp = hp, dmg = dmg, speed = speed, aggro = aggro, xp = xp,
                poise = poise, scale = scale, caster = caster, boss = boss, title = bossTitle,
                drops = boss
                    ? new[] { ("gold", 1f, 150, 220), ("hell_ember", 1f, 2, 4), ("potion", 1f, 2, 3), ("spark_tome", 0.5f, 1, 1) }
                    : new[] { ("gold", 1f, 4, 12), ("imp_horn", 0.35f, 1, 1), ("potion", 0.12f, 1, 1), ("hell_ember", 0.06f, 1, 1),
                              ("spark_tome", 0.012f, 1, 1) }
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
