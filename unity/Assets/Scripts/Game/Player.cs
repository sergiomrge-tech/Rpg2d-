using UnityEngine;

namespace Aetheria
{
    /// <summary>The reincarnated hero. Stamina-gated melee combo, i-frame roll, Spark magic that evolves.</summary>
    public class Player : Actor
    {
        enum St { Free, Attack, Cast, Roll, Hurt, Dead }

        public static Player I;
        public GameState gs;
        public float mp, st;
        public bool inputLocked;
        public Vector2 scriptedMove;   // used by CI demo / cutscenes

        St state;
        int combo;
        bool bufferedAttack;
        float stRegenDelay;
        float stateT;
        Vector2 rollDir;
        Vector2 moveDir;
        float stepT;

        const float WalkSpeed = 4.0f, RunSpeed = 6.4f, RollSpeed = 10.5f;
        const float AttackCost = 14f, RollCost = 24f, RunDrain = 9f, CastCost = 12f;

        public static Player Spawn(Vector2 pos, GameState gs)
        {
            var go = new GameObject("Player");
            go.transform.position = pos;
            var p = go.AddComponent<Player>();
            p.gs = gs;
            p.Build("Sprites/Chars/hero", 1.25f, 0.42f, 0.32f);
            p.rb.mass = 1;
            p.maxHp = gs.maxHp;
            p.hp = gs.maxHp;
            p.mp = gs.maxMp;
            p.st = gs.maxSt;
            p.anim.OnHit += p.OnAnimHit;
            p.anim.OnEnd += p.OnAnimEnd;
            p.anim.Play("idle");
            I = p;
            return p;
        }

        Vector2 ReadMove()
        {
            if (inputLocked) return scriptedMove;
            Vector2 v = Vector2.zero;
            if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) v.x -= 1;
            if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) v.x += 1;
            if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow)) v.y += 1;
            if (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow)) v.y -= 1;
            return v.sqrMagnitude > 1 ? v.normalized : v;
        }

        bool Pressed(params KeyCode[] keys)
        {
            if (inputLocked) return false;
            foreach (var k in keys) if (Input.GetKeyDown(k)) return true;
            return false;
        }

        protected override void Update()
        {
            base.Update();
            if (dead) return;
            float dt = Time.deltaTime;
            stateT += dt;
            moveDir = ReadMove();
            bool run = !inputLocked && Input.GetKey(KeyCode.LeftShift);

            // regen
            stRegenDelay -= dt;
            if (stRegenDelay <= 0 && state != St.Roll) st = Mathf.Min(gs.maxSt, st + 38f * dt);
            mp = Mathf.Min(gs.maxMp, mp + 1.2f * dt);

            if (Pressed(KeyCode.J, KeyCode.Mouse0)) TryAttack();
            if (Pressed(KeyCode.K, KeyCode.Mouse1)) TryCast();
            if (Pressed(KeyCode.Space)) TryRoll();
            if (Pressed(KeyCode.Q)) UsePotion();
            if (Pressed(KeyCode.E)) Game.I.Interact(this);

            switch (state)
            {
                case St.Free:
                {
                    if (moveDir.sqrMagnitude > 0.01f)
                    {
                        bool canRun = run && st > 1;
                        if (canRun) { st -= RunDrain * dt; stRegenDelay = 0.4f; }
                        Face(Util.FacingFrom(moveDir, facing));
                        anim.Play(canRun ? "run" : "walk");
                        rb.velocity = moveDir * (canRun ? RunSpeed : WalkSpeed) + knock;
                        stepT -= dt * (canRun ? 1.5f : 1f);
                        if (stepT <= 0) { stepT = 0.36f; Sfx.Play("step", 0.18f, Random.Range(0.9f, 1.1f)); if (canRun) Fx.Dust(Pos, 0.5f); }
                    }
                    else
                    {
                        anim.Play("idle");
                        rb.velocity = knock;
                    }
                    break;
                }
                case St.Attack:
                {
                    // small forward lunge during wind-up -> strike
                    float n = anim.Normalized;
                    float lunge = n < 0.45f ? (combo == 3 ? 5.5f : 3.2f) * (1 - n / 0.45f) : 0;
                    var steer = moveDir.sqrMagnitude > 0.01f && n < 0.2f ? moveDir : Util.FacingVec(facing);
                    if (n < 0.2f && moveDir.sqrMagnitude > 0.01f) Face(Util.FacingFrom(steer, facing));
                    rb.velocity = Util.FacingVec(facing) * lunge + knock;
                    if (bufferedAttack && n > 0.58f && combo < 3) { bufferedAttack = false; StartAttack(combo + 1); }
                    break;
                }
                case St.Cast:
                    rb.velocity = knock;
                    break;
                case St.Roll:
                {
                    float k = Mathf.Clamp01(1 - stateT / 0.48f);
                    rb.velocity = rollDir * RollSpeed * (0.35f + 0.65f * k);
                    if (stateT > 0.46f) invuln = Mathf.Min(invuln, 0);
                    break;
                }
                case St.Hurt:
                    rb.velocity = knock;
                    if (stateT > 0.32f) ToFree();
                    break;
            }
            knock = Vector2.MoveTowards(knock, Vector2.zero, 30f * dt);
        }

        void ToFree()
        {
            state = St.Free;
            stateT = 0;
            anim.Play("idle", true);
        }

        public void CiAttack() => TryAttack();
        public void CiCast() => TryCast();

        void TryAttack()
        {
            if (state == St.Attack) { bufferedAttack = true; return; }
            if (state != St.Free) return;
            if (st < AttackCost * 0.5f) { Fx.Toast("Sem fôlego!", new Color(1f, 0.85f, 0.4f)); return; }
            StartAttack(1);
        }

        void StartAttack(int n)
        {
            if (st < AttackCost * 0.5f) { ToFree(); return; }
            combo = n;
            state = St.Attack;
            stateT = 0;
            st -= AttackCost * (n == 3 ? 1.5f : 1f);
            stRegenDelay = 0.7f;
            // aim assist: snap facing to the nearest demon in front
            var target = Enemy.Nearest(Pos, 2.6f);
            if (target != null && moveDir.sqrMagnitude < 0.01f) Face(Util.FacingFrom(target.Pos - Pos, facing));
            anim.Play("attack" + n, true);
            Sfx.Play(n == 3 ? "swing_heavy" : "swing", 0.55f, Random.Range(0.95f, 1.08f));
        }

        void OnAnimHit(string a)
        {
            if (a.StartsWith("attack"))
            {
                Vector2 f = Util.FacingVec(facing);
                Vector2 c = Pos + Vector2.up * 0.55f + f * (combo == 3 ? 1.0f : 0.85f);
                float r = combo == 3 ? 1.55f : 1.25f;
                Fx.Slash(Pos + Vector2.up * 0.6f, facing, combo);
                if (combo == 3) { Fx.Shockwave(c, 1.2f); CameraRig.Shake(0.22f, 0.25f); }
                int hits = 0;
                foreach (var e in Enemy.All.ToArray())
                {
                    if (e.dead) continue;
                    Vector2 d = e.Pos + Vector2.up * 0.4f - c;
                    if (d.magnitude > r + 0.35f) continue;
                    bool crit = Random.value < 0.08f;
                    float dmg = gs.atk * (combo == 3 ? 1.9f : combo == 2 ? 1.15f : 1f) * Random.Range(0.9f, 1.1f) * (crit ? 1.8f : 1f);
                    if (e.Hurt(Mathf.Round(dmg), Pos, combo == 3 ? 9f : 5f, combo == 3 ? 30 : 12, crit)) hits++;
                }
                if (hits > 0)
                {
                    Game.HitStop(combo == 3 ? 0.09f : 0.05f);
                    Sfx.Play("hit", 0.7f, Random.Range(0.92f, 1.06f));
                    if (combo != 3) CameraRig.Shake(0.08f, 0.12f);
                }
            }
            else if (a == "cast")
            {
                Vector2 dir = Util.FacingVec(facing);
                var t = Enemy.Nearest(Pos, 9f, dir, 0.45f);
                if (t != null) dir = ((t.Pos + Vector2.up * 0.5f) - (Pos + Vector2.up * 0.8f)).normalized;
                Projectile.Spark(Pos + Vector2.up * 0.8f + dir * 0.5f, dir, gs.mag * (1 + 0.35f * (gs.sparkTier - 1)), gs.sparkTier, true);
                Sfx.Play("spark", 0.6f, 1f);
            }
        }

        void OnAnimEnd(string a)
        {
            if (state == St.Attack && a.StartsWith("attack"))
            {
                if (bufferedAttack && combo < 3) { bufferedAttack = false; StartAttack(combo + 1); return; }
                bufferedAttack = false;
                combo = 0;
                ToFree();
            }
            else if (state == St.Cast && a == "cast") ToFree();
            else if (state == St.Roll && a == "roll") ToFree();
        }

        void TryCast()
        {
            if (state != St.Free) return;
            if (mp < CastCost) { Fx.Toast("Mana insuficiente", new Color(0.5f, 0.75f, 1f)); return; }
            mp -= CastCost;
            state = St.Cast;
            stateT = 0;
            var target = Enemy.Nearest(Pos, 9f);
            if (target != null && moveDir.sqrMagnitude < 0.01f) Face(Util.FacingFrom(target.Pos - Pos, facing));
            else if (moveDir.sqrMagnitude > 0.01f) Face(Util.FacingFrom(moveDir, facing));
            anim.Play("cast", true);
            Fx.MagicCircle(Pos, gs.sparkTier);
            Sfx.Play("charge", 0.4f, 1f);
        }

        void TryRoll()
        {
            if (state == St.Roll || state == St.Dead) return;
            if (state == St.Attack && anim.Normalized < 0.5f) return;
            if (st < RollCost * 0.6f) { Fx.Toast("Sem fôlego!", new Color(1f, 0.85f, 0.4f)); return; }
            st -= RollCost;
            stRegenDelay = 0.6f;
            rollDir = moveDir.sqrMagnitude > 0.01f ? moveDir.normalized : Util.FacingVec(facing);
            Face(Util.FacingFrom(rollDir, facing));
            state = St.Roll;
            stateT = 0;
            invuln = 0.36f;
            combo = 0;
            bufferedAttack = false;
            anim.Play("roll", true);
            Fx.Dust(Pos, 1f);
            Sfx.Play("roll", 0.4f, 1f);
        }

        void UsePotion()
        {
            if (hp >= gs.maxHp) return;
            if (!gs.Take("potion")) { Fx.Toast("Sem poções", new Color(1f, 0.5f, 0.5f)); return; }
            hp = Mathf.Min(gs.maxHp, hp + Data.Items["potion"].heal);
            Fx.Heal(Pos);
            Sfx.Play("potion", 0.5f, 1f);
        }

        public override bool Hurt(float dmg, Vector2 from, float knockback, float poiseDmg, bool crit = false)
        {
            if (state == St.Roll && invuln > 0) { Fx.Toast("Esquiva!", new Color(0.7f, 0.95f, 1f)); return false; }
            bool ok = base.Hurt(dmg, from, knockback, poiseDmg, crit);
            if (!ok) return false;
            invuln = 0.6f;
            Sfx.Play("hurt", 0.6f, 1f);
            CameraRig.Shake(0.18f, 0.2f);
            Hud.I?.HurtPulse();
            if (!dead)
            {
                state = St.Hurt;
                stateT = 0;
                combo = 0;
                bufferedAttack = false;
                anim.Play("hurt", true);
            }
            return true;
        }

        protected override void Die()
        {
            dead = true;
            state = St.Dead;
            rb.velocity = Vector2.zero;
            anim.Play("death", true);
            Sfx.Play("death", 0.7f, 0.9f);
            Game.I.OnPlayerDied();
        }

        public void Revive(Vector2 at)
        {
            dead = false;
            transform.position = at;
            hp = gs.maxHp;
            mp = gs.maxMp;
            st = gs.maxSt;
            ToFree();
        }
    }
}
