using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Aetheria
{
    [Serializable]
    class SaveData
    {
        public GameState state;
        public List<string> flags = new List<string>();
        public List<string> questIds = new List<string>();
        public List<int> questVals = new List<int>();
    }

    /// <summary>Top-level orchestrator: world, player, HUD, quests, saves, CI screenshot mode.</summary>
    public class Game : MonoBehaviour
    {
        public static Game I;
        public GameState state = new GameState();
        public HashSet<string> flags = new HashSet<string>();
        readonly Dictionary<string, int> quests = new Dictionary<string, int>();
        public Player player;
        World world;
        Hud hud;
        float hitStop;
        string ciDir;

        static string SavePath => Path.Combine(Application.persistentDataPath, "aetheria_save.json");

        void Awake()
        {
            I = this;
            var args = Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length - 1; i++)
                if (args[i] == "-ciShots") ciDir = args[i + 1];
        }

        void Start()
        {
            if (ciDir == null) Load();
            var cam = CameraRig.Create();
            world = World.Load("village");
            var spawn = Util.MapToWorld(world.data.playerX, world.data.playerY);
            player = Player.Spawn(spawn, state);
            world.SpawnActors();
            if (flags.Contains("sylra_joined")) Companion.Spawn(spawn + Vector2.left);
            cam.target = player.transform;
            cam.Snap();
            hud = Hud.Create();
            Grimoire.Create(hud);
            Sfx.Loop("ambience", 0.25f);
            if (ciDir != null) { StartCoroutine(CiShots()); return; }
            if (!flags.Contains("prologue"))
            {
                player.inputLocked = true;
                hud.ShowDialogue(Story.Prologue, () =>
                {
                    flags.Add("prologue");
                    player.inputLocked = false;
                    hud.Banner("Vila de Aurora", "Capítulo I — A Centelha");
                    Save();
                });
            }
            else hud.Banner("Vila de Aurora", "Rank " + state.guildRank);
        }

        void Update()
        {
            if (hitStop > 0)
            {
                hitStop -= Time.unscaledDeltaTime;
                Time.timeScale = hitStop > 0 ? 0.05f : 1f;
            }
            if (Input.GetKeyDown(KeyCode.Tab) && Grimoire.I != null && !Grimoire.I.open && !hud.InDialogue && player != null && !player.dead && !player.inputLocked)
                Grimoire.I.Toggle();
            if (player != null && !player.dead && travelCd <= 0)
            {
                var ex = world.ExitAt(player.Pos);
                if (ex != null) Travel(ex.to);
            }
            travelCd -= Time.deltaTime;
            if (Input.GetKeyDown(KeyCode.F9) && player != null && !player.dead) SpawnBestiary();
            if (Input.GetKeyDown(KeyCode.F5)) { Save(); Fx.Toast("Jogo salvo", Color.white); }
        }

        // Bestiary: F9 spawns the next demon (ours + the GPT-delivered assets) next to the hero for review.
        List<string> bestiary;
        int bestiaryIdx;

        void SpawnBestiary()
        {
            if (bestiary == null) { bestiary = new List<string>(Data.Demons.Keys); bestiary.Sort(); }
            var id = bestiary[bestiaryIdx % bestiary.Count];
            bestiaryIdx++;
            var e = Enemy.Spawn(id, player.Pos + Util.FacingVec(player.facing) * 3.5f, Mathf.Max(1, state.level));
            Fx.Toast($"Bestiário {bestiaryIdx}/{bestiary.Count}: {e.def.name}", new Color(1f, 0.9f, 0.6f), e.Pos + Vector2.up * 2.8f);
        }

        float travelCd = 1f;
        public string mapName = "village";

        static readonly System.Collections.Generic.Dictionary<string, string[]> MapTitles = new System.Collections.Generic.Dictionary<string, string[]>
        {
            { "village", new[] { "Vila de Aurora", "Capítulo I — A Centelha" } },
            { "velmoor", new[] { "Floresta de Velmoor", "Capítulo II — Raízes Profanas" } },
            { "valemont", new[] { "Cidade de Valemont", "Capítulo III — Sombras na Capital" } },
            { "kharis", new[] { "Deserto de Kharis", "Capítulo IV — O Ferrão do Deserto" } },
            { "mines", new[] { "Minas de Durnhold", "Capítulo V — O Coração da Forja" } },
            { "mirewail", new[] { "Pântano de Mirewail", "Capítulo VI — A Rainha do Brejo" } },
            { "peaks", new[] { "Picos Gelados", "Capítulo VII — A Nascente Congelada" } },
        };

        static readonly System.Collections.Generic.Dictionary<string, (string flag, string msg)> Gates = new System.Collections.Generic.Dictionary<string, (string, string)>
        {
            { "velmoor", ("rank_e", "O portal rejeita você. A Guilda exige Rank E.") },
            { "valemont", ("rank_d", "Os guardas barram você. Valemont exige Rank D.") },
            { "kharis", ("rank_c", "A caravana recusa: o deserto exige Rank C (derrote o Assassino Sombrio).") },
            { "mines", ("kharis_done", "O túnel está bloqueado. Ajude Hasim contra o Escorpião primeiro.") },
            { "mirewail", ("mines_done", "A bruma repele você. Ajude Durnok contra o Golem primeiro.") },
            { "peaks", ("mirewail_done", "A nevasca é forte demais. Ajude Morgana contra Mirael primeiro.") },
        };

        public void Travel(string to)
        {
            if (Gates.TryGetValue(to, out var gate) && !flags.Contains(gate.flag))
            {
                Fx.Toast(gate.msg, new Color(1f, 0.88f, 0.55f));
                travelCd = 2f;
                player.transform.position += (Vector3)(Vector2)(Util.MapToWorld(world.data.w * 32, world.data.h * 32) - player.Pos).normalized * 1.6f;
                return;
            }
            string from = mapName;
            mapName = to;
            world = World.Load(to);
            // arrive at the exit that leads back to where we came from
            Vector2 at = Util.MapToWorld(world.data.playerX, world.data.playerY);
            foreach (var e in world.data.exits)
                if (e.to == from)
                {
                    Vector2 ep = Util.MapToWorld(e.x, e.y), centre = Util.MapToWorld(world.data.w * 32, world.data.h * 32);
                    at = ep + (centre - ep).normalized * 2.4f;   // step inside, away from the exit trigger
                }
            player.transform.position = at;
            world.SpawnActors();
            if (Companion.I != null) Companion.I.transform.position = at + Vector2.left;
            CameraRig.I.Snap();
            travelCd = 1.5f;
            if (MapTitles.TryGetValue(to, out var t)) hud.Banner(t[0], t[1]);
            Save();
        }

        public static void HitStop(float t)
        {
            if (I == null) return;
            I.hitStop = Mathf.Max(I.hitStop, t);
        }

        public void Interact(Player p)
        {
            if (hud.InDialogue) return;
            Npc best = null;
            float bd = 2.2f;
            foreach (var n in FindObjectsOfType<Npc>())
            {
                float d = (n.Pos - p.Pos).magnitude;
                if (d < bd) { bd = d; best = n; }
            }
            if (best == null) return;
            var npc = best;
            npc.talking = true;
            p.inputLocked = true;
            p.rb.velocity = Vector2.zero;
            hud.ShowDialogue(Story.Talk(npc.id, this), () =>
            {
                npc.talking = false;
                p.inputLocked = false;
                if (npc.id == "sylra" && flags.Contains("sylra_joined") && Companion.I == null)
                {
                    Companion.Spawn(npc.Pos);
                    Destroy(npc.gameObject);
                    hud.Banner("Sylra entrou no grupo", "Arqueira de Velmoor");
                }
                Save();
            });
        }

        public void StartQuest(string id)
        {
            if (!quests.ContainsKey(id)) quests[id] = 0;
        }

        public int QuestProgress(string id) => quests.TryGetValue(id, out var v) ? v : 0;

        public string QuestLine()
        {
            if (!flags.Contains("guild_joined")) return "◆ Procure a Guilda dos Aventureiros\n<size=20>ao norte da praça</size>";
            if (!flags.Contains("q_imps_done"))
            {
                int n = Mathf.Min(QuestProgress(Story.QuestImps), Story.QuestImpsGoal);
                return n >= Story.QuestImpsGoal
                    ? "◆ Volte à Guilda e fale com Elina"
                    : $"◆ Purgar o Bosque dos Chifres\n<size=22>Diabretes {n}/{Story.QuestImpsGoal}</size>";
            }
            if (!flags.Contains("grakk_dead")) return "◆ Derrote Grakk, Chefe dos Diabretes\n<size=22>sul do Bosque dos Chifres</size>";
            if (!flags.Contains("rank_e")) return "◆ Volte à Guilda e fale com Elina";
            if (!flags.Contains("sylra_joined")) return "◆ Entre no portal ao sul do Bosque\n<size=22>e encontre o santuário élfico de Velmoor</size>";
            if (!flags.Contains("dryad_profane_dead")) return "◆ Purifique o bosque sagrado\n<size=22>derrote a Dríade Profanada (sul de Velmoor)</size>";
            if (!flags.Contains("rank_d")) return "◆ Volte à Guilda de Aurora";
            if (!flags.Contains("val_started")) return "◆ Viaje a Valemont\n<size=22>saída leste de Velmoor — fale com o Mestre da Guilda</size>";
            if (!flags.Contains("assassin_shadow_dead")) return "◆ Cace o Assassino Sombrio\n<size=22>beco ao sul de Valemont</size>";
            if (!flags.Contains("rank_c")) return "◆ Volte ao Mestre Aldric, na Guilda";
            foreach (var r in Story.Regions)
            {
                if (flags.Contains(r.done)) continue;
                if (!flags.Contains(r.start)) return $"◆ Viaje a {r.title}\n<size=22>fale com {Story.NameOf(r.npc)}</size>";
                if (!flags.Contains(r.boss + "_dead")) return $"◆ Derrote {r.bossName}\n<size=22>{r.title}</size>";
                return $"◆ Volte a {Story.NameOf(r.npc)}\n<size=22>{r.title}</size>";
            }
            return "◆ Rank A — Castelo de Valemont tomado\n<size=20>(Capítulo VIII em breve)</size>";
        }

        public void OnEnemyKilled(Enemy e)
        {
            if (quests.ContainsKey(Story.QuestImps) && e.def.id == "imp") quests[Story.QuestImps]++;
            if (e.def.boss)
            {
                flags.Add(e.def.id + "_dead");
                hud.Banner(e.def.name + " foi derrotado", "Volte à Guilda");
                Save();
            }
            int xp = Mathf.RoundToInt(e.def.xp * Data.LevelScale(e.level));
            Fx.Toast("+" + xp + " EXP", new Color(0.75f, 0.95f, 1f), e.Pos + Vector2.up * 2.6f);
            if (state.GainXp(xp))
            {
                player.maxHp = state.HpMax;
                player.hp = state.HpMax;
                player.mp = state.maxMp;
                Fx.Heal(player.Pos);
                Sfx.Play("levelup", 0.6f, 1f);
                hud.Banner("Nível " + state.level, "Sua centelha arde mais forte");
            }
        }

        public void OnPlayerDied() { StartCoroutine(DeathRoutine()); }

        IEnumerator DeathRoutine()
        {
            yield return new WaitForSeconds(1.6f);
            hud.Banner("Você caiu", "A deusa Lumia o traz de volta... mas metade do ouro ficou para trás");
            yield return new WaitForSeconds(1.8f);
            state.gold /= 2;
            player.Revive(Util.MapToWorld(world.data.playerX, world.data.playerY));
            CameraRig.I.Snap();
            world.RespawnEnemies();
        }

        public void Save()
        {
            if (ciDir != null) return;
            try
            {
                var s = new SaveData { state = state, flags = new List<string>(flags) };
                foreach (var kv in quests) { s.questIds.Add(kv.Key); s.questVals.Add(kv.Value); }
                File.WriteAllText(SavePath, JsonUtility.ToJson(s));
            }
            catch (Exception ex) { Debug.LogWarning("save failed: " + ex.Message); }
        }

        void Load()
        {
            try
            {
                if (!File.Exists(SavePath)) return;
                var s = JsonUtility.FromJson<SaveData>(File.ReadAllText(SavePath));
                if (s?.state == null) return;
                state = s.state;
                flags = new HashSet<string>(s.flags);
                for (int i = 0; i < s.questIds.Count; i++) quests[s.questIds[i]] = s.questVals[i];
            }
            catch (Exception ex) { Debug.LogWarning("load failed: " + ex.Message); }
        }

        // ------------------------------------------------------------ CI: scripted tour + screenshots
        IEnumerator Shot(string name)
        {
            yield return new WaitForEndOfFrame();
            Directory.CreateDirectory(ciDir);
            ScreenCapture.CaptureScreenshot(Path.Combine(ciDir, name + ".png"));
            Debug.Log("[ci] shot " + name);
            yield return null;
        }

        IEnumerator CiShots()
        {
            player.inputLocked = true;
            hud.Banner("Vila de Aurora", "Capítulo I — A Centelha");
            yield return new WaitForSeconds(1.5f);
            yield return Shot("01_village");
            hud.ShowDialogue(Story.Talk("receptionist", this), null);
            yield return new WaitForSeconds(2.5f);
            yield return Shot("02_dialogue");
            while (hud.InDialogue) { hud.Advance(); hud.Advance(); yield return null; }
            // walk into the woods
            player.transform.position = Util.MapToWorld(27 * 64, 39 * 64);
            CameraRig.I.Snap();
            player.scriptedMove = Vector2.down;
            yield return new WaitForSeconds(1.2f);
            player.scriptedMove = Vector2.zero;
            yield return new WaitForSeconds(1.2f);
            yield return Shot("03_woods");
            var e = Enemy.Nearest(player.Pos, 30f);
            if (e != null)
            {
                player.transform.position = e.Pos + Vector2.up * 1.3f;
                CameraRig.I.Snap();
                yield return new WaitForSeconds(0.8f);
            }
            player.CiAttack();
            yield return new WaitForSeconds(0.12f);
            yield return Shot("04_combat");
            yield return new WaitForSeconds(0.6f);
            player.CiCast();
            yield return new WaitForSeconds(0.35f);
            yield return Shot("05_combat2");
            Debug.Log("[ci] done");
            yield return new WaitForSeconds(0.5f);
            Application.Quit();
        }
    }
}
