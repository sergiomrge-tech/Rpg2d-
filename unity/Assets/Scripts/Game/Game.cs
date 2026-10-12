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
            cam.target = player.transform;
            cam.Snap();
            hud = Hud.Create();
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
            if (Input.GetKeyDown(KeyCode.F5)) { Save(); Fx.Toast("Jogo salvo", Color.white); }
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
            return "◆ Rank E — aguarde novas missões\n<size=20>Floresta de Velmoor (em breve)</size>";
        }

        public void OnEnemyKilled(Enemy e)
        {
            if (quests.ContainsKey(Story.QuestImps) && e.def.id == "imp") quests[Story.QuestImps]++;
            int xp = Mathf.RoundToInt(e.def.xp * Data.LevelScale(e.level));
            Fx.Toast("+" + xp + " EXP", new Color(0.75f, 0.95f, 1f), e.Pos + Vector2.up * 2.6f);
            if (state.GainXp(xp))
            {
                player.maxHp = state.maxHp;
                player.hp = state.maxHp;
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
            // Deterministic shots of real Lote 2 creatures in the running Unity world.
            // No concept art or generated fake screenshots are ever used here.
            player.invuln = 15f;
            string[] pilotIds = { "mantis_reaver", "scarab_brute", "moth_hexer",
                                  "termite_burrower", "vespa_lancer", "cicada_screecher" };
            string[] pilotNames = { "06_mantis_skill", "07_scarab_skill", "08_moth_skill",
                                    "09_termite_burrow", "10_vespa_sting", "11_cicada_sonic" };
            for (int i = 0; i < pilotIds.Length; i++)
            {
                Enemy insect = Enemy.All.Find(e => !e.dead && e.def.id == pilotIds[i]);
                if (insect == null)
                {
                    Debug.LogWarning("[ci] missing insectoid: " + pilotIds[i]);
                    continue;
                }
                player.transform.position = insect.Pos + Vector2.down * 3.1f;
                player.rb.velocity = Vector2.zero;
                CameraRig.I.Snap();
                insect.CiCastSkill(player.Pos);
                yield return new WaitForSeconds(0.7f);
                yield return Shot(pilotNames[i]);
                yield return new WaitForSeconds(0.4f);
            }
            Debug.Log("[ci] done");
            yield return new WaitForSeconds(0.5f);
            Application.Quit();
        }
    }
}
