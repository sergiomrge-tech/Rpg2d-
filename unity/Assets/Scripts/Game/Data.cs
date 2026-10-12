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
        public int slot;                 // 0 = not gear, 1 weapon, 2 armor, 3 charm
        public float atk, def, mag, hp;  // gear bonuses
    }

    public class Recipe
    {
        public string result;
        public int gold;
        public (string item, int n)[] needs;
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
            Add(new ItemDef { id = "demon_hide", name = "Couro Demoníaco", desc = "Material. Resistente, o ferreiro adora.", icon = "horn", value = 20, rarity = Rarity.Uncommon });
            Add(new ItemDef { id = "spirit_dust", name = "Pó de Espírito", desc = "Material élfico que brilha no escuro.", icon = "ember", value = 30, rarity = Rarity.Uncommon });
            Add(new ItemDef { id = "sword_tome", name = "Tomo: Corte Crescente", desc = "O 3º golpe da espada lança uma lâmina de energia.", icon = "scroll", value = 300, rarity = Rarity.Epic });
            Gear("rusty_sword", "Espada Enferrujada", "A espada com que você acordou.", 1, Rarity.Common, atk: 0);
            Gear("horn_blade", "Lâmina de Chifre", "Forjada com chifres de diabrete. +6 ATQ.", 1, Rarity.Uncommon, atk: 6);
            Gear("velmoor_blade", "Espada de Velmoor", "Madeira-de-prata élfica. +10 ATQ, +4 MAG.", 1, Rarity.Rare, atk: 10, mag: 4);
            Gear("ember_blade", "Lâmina Infernal", "Temperada em brasas do inferno. +14 ATQ.", 1, Rarity.Rare, atk: 14);
            Gear("oni_cleaver", "Cutelo do General Oni", "Pesado, brutal. +20 ATQ.", 1, Rarity.Epic, atk: 20);
            Gear("leather_vest", "Colete de Couro", "Leve e barato. +5 DEF.", 2, Rarity.Common, def: 5);
            Gear("iron_mail", "Cota de Couro Demoníaco", "Reforçada com couro de oni. +12 DEF.", 2, Rarity.Uncommon, def: 12);
            Gear("elven_robe", "Manto Élfico", "Tecido de Velmoor. +9 DEF, +8 MAG.", 2, Rarity.Rare, def: 9, mag: 8);
            Gear("sand_blade", "Cimitarra do Escorpião", "Lâmina curva de quitina. +18 ATQ.", 1, Rarity.Epic, atk: 18);
            Gear("dwarf_plate", "Couraça Anã de Durnhold", "Aço de forja anã. +20 DEF.", 2, Rarity.Epic, def: 20);
            Gear("swamp_charm", "Coração de Mirael", "Pulsa em tom rosado. +16 MAG, +20 PV.", 3, Rarity.Epic, mag: 16, hp: 20);
            Gear("frost_blade", "Lâmina do Inverno Eterno", "Congela o ar ao redor. +26 ATQ, +6 MAG.", 1, Rarity.Legendary, atk: 26, mag: 6);
            Gear("ice_mail", "Manto de Cristal Gélido", "Quase impenetrável. +24 DEF.", 2, Rarity.Legendary, def: 24);
            Gear("luma_charm", "Amuleto de Lumia", "A deusa vigia. +25 PV.", 3, Rarity.Rare, hp: 25);
            Gear("ember_charm", "Brasa Eterna", "Um coração de chama. +10 MAG.", 3, Rarity.Rare, mag: 10);
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

            // ---- Etapa 3: Valemont
            D("assassin_shadow", "Assassino Sombrio", "Demons/assassin_shadow", 1450, 40, 3.4f, 9f, 700, 110, 1.45f, false, "Lâmina do Rei Demônio");

            // ---- Etapa 3: Kharis, Durnhold, Mirewail, Picos
            D("sand_imp", "Diabrete das Dunas", "Demons/sand_imp", 95, 30, 3.1f, 8f, 36, 14, 1.2f, true);
            D("sand_wraith", "Espectro de Areia", "Demons/sand_wraith", 115, 32, 3.0f, 8.5f, 40, 14, 1.2f, true);
            D("oni_nomad", "Oni Nômade", "Demons/oni_nomad", 230, 42, 2.7f, 6.5f, 64, 60, 1.3f, false);
            D("scorpion_demon", "Demônio Escorpião", "Demons/scorpion_demon", 2600, 60, 3.0f, 10f, 900, 220, 1.9f, false, "Ferrão do Deserto de Kharis");
            D("mine_imp", "Diabrete Minerador", "Demons/mine_imp", 140, 38, 3.0f, 7.5f, 50, 20, 1.2f, false);
            D("rock_oni", "Oni de Rocha", "Demons/rock_oni", 340, 54, 2.0f, 6f, 90, 130, 1.4f, false);
            D("ember_golem", "Golem de Brasa", "Demons/ember_golem", 4300, 72, 2.2f, 10f, 1300, 320, 2.0f, true, "Coração da Forja de Durnhold");
            D("witch_imp", "Diabrete Bruxo", "Demons/witch_imp", 160, 48, 2.8f, 9f, 76, 20, 1.2f, true);
            D("bog_wraith", "Espectro do Brejo", "Demons/bog_wraith", 185, 50, 3.0f, 9f, 80, 22, 1.2f, true);
            D("succubus_mirael", "Mirael, a Súcubo", "Demons/succubus_mirael", 5400, 80, 3.2f, 11f, 1700, 300, 1.8f, true, "Rainha do Pântano de Mirewail");
            D("frost_imp", "Diabrete Gélido", "Demons/frost_imp", 205, 58, 3.1f, 9f, 98, 24, 1.25f, true);
            D("ice_oni", "Oni de Gelo", "Demons/ice_oni", 480, 68, 2.4f, 6.5f, 130, 170, 1.4f, false);
            D("ice_demon", "Demônio de Gelo", "Demons/ice_demon", 7600, 95, 2.8f, 11f, 2400, 380, 2.0f, true, "Senhor dos Picos Gelados");

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

            foreach (var k in new List<string>(Demons.Keys))
            {
                if (k == "oni" || k.StartsWith("oni_")) AddDrop(k, "demon_hide", 0.4f, 1, 2);
                if (k == "spirit_corrupt") AddDrop(k, "spirit_dust", 0.5f, 1, 2);
                if (k == "treant_demon") AddDrop(k, "spirit_dust", 0.7f, 1, 3);
            }
            AddDrop("dryad_profane", "velmoor_blade", 1f);
            AddDrop("dryad_profane", "luma_charm", 0.5f);
            AddDrop("morgash_ironhorn", "oni_cleaver", 1f);
            AddDrop("morgash_ironhorn", "sword_tome", 0.6f);
            AddDrop("oni_executioner", "sword_tome", 0.03f);
            AddDrop("assassin_shadow", "sword_tome", 0.5f);
            AddDrop("scorpion_demon", "sand_blade", 1f);
            AddDrop("ember_golem", "dwarf_plate", 1f);
            AddDrop("succubus_mirael", "swamp_charm", 1f);
            AddDrop("ice_demon", "frost_blade", 1f);
            AddDrop("ice_demon", "ice_mail", 1f);
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

        static void Gear(string id, string name, string desc, int slot, Rarity r, float atk = 0, float def = 0, float mag = 0, float hp = 0)
        {
            Add(new ItemDef { id = id, name = name, desc = desc, slot = slot, rarity = r, atk = atk, def = def, mag = mag, hp = hp,
                              icon = slot == 1 ? "gear_sword" : slot == 2 ? "gear_armor" : "gear_charm", value = 40 + (int)r * 80 });
        }

        public static void AddDrop(string demon, string item, float chance, int min = 1, int max = 1)
        {
            if (!Demons.TryGetValue(demon, out var d)) return;
            var list = new List<(string, float, int, int)>(d.drops) { (item, chance, min, max) };
            d.drops = list.ToArray();
        }

        public static readonly Recipe[] Recipes =
        {
            new Recipe { result = "horn_blade", gold = 80, needs = new[] { ("imp_horn", 5) } },
            new Recipe { result = "iron_mail", gold = 180, needs = new[] { ("demon_hide", 4) } },
            new Recipe { result = "ember_charm", gold = 120, needs = new[] { ("hell_ember", 3), ("spirit_dust", 1) } },
            new Recipe { result = "elven_robe", gold = 150, needs = new[] { ("spirit_dust", 4) } },
            new Recipe { result = "ember_blade", gold = 260, needs = new[] { ("hell_ember", 4), ("imp_horn", 6) } },
        };

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
        public int sparkTier = 1, swordTier = 1;
        public string eqWeapon = "rusty_sword", eqArmor = "", eqCharm = "";
        public string guildRank = "F";
        public List<string> invIds = new List<string> { "potion", "potion" };
        public List<int> invCounts = new List<int> { 1, 1 };

        float Gear(System.Func<ItemDef, float> f)
        {
            float t = 0;
            foreach (var id in new[] { eqWeapon, eqArmor, eqCharm })
                if (!string.IsNullOrEmpty(id) && Data.Items.TryGetValue(id, out var d)) t += f(d);
            return t;
        }

        public float TotalAtk => atk + Gear(d => d.atk);
        public float TotalMag => mag + Gear(d => d.mag);
        public float TotalDef => Gear(d => d.def);
        public float HpMax => maxHp + Gear(d => d.hp);

        public string Equipped(int slot) => slot == 1 ? eqWeapon : slot == 2 ? eqArmor : eqCharm;

        /// <summary>Equip a bag item; the previous piece goes back to the bag.</summary>
        public bool Equip(string id)
        {
            if (!Data.Items.TryGetValue(id, out var d) || d.slot == 0 || !Take(id)) return false;
            string old = Equipped(d.slot);
            if (d.slot == 1) eqWeapon = id; else if (d.slot == 2) eqArmor = id; else eqCharm = id;
            if (!string.IsNullOrEmpty(old) && old != "rusty_sword") Add(old, 1);
            return true;
        }

        public bool CanCraft(Recipe r)
        {
            if (gold < r.gold) return false;
            foreach (var (item, n) in r.needs) if (Count(item) < n) return false;
            return true;
        }

        public void Craft(Recipe r)
        {
            gold -= r.gold;
            foreach (var (item, n) in r.needs) for (int i = 0; i < n; i++) Take(item);
            Add(r.result, 1);
        }

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
