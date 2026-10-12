using System.Collections.Generic;
using UnityEngine;

namespace Aetheria
{
    /// <summary>Demon AI: wander -> aggro -> telegraphed melee lunge / ranged fireball, staggers when poise breaks.</summary>
    public class Enemy : Actor
    {
        public static readonly List<Enemy> All = new List<Enemy>();
        enum St { Idle, Chase, Telegraph, Attack, Cast, Hurt, Dead, Retreat }

        public DemonDef def;
        public int level;
        public float dmg, speed;
        public float lastHurt = -99;
        Vector2 home;
        St state;
        float stateT;
        float think;
        float castCd;
        float attackCd;
        Vector2 wander;
        bool hitDone;
        bool nextIsCast;
        bool summoned;
        float tpCd = 3f;

        public static Enemy Spawn(string kind, Vector2 pos, int level)
        {
            var def = Data.Demons[kind];
            var go = new GameObject(def.name + " Nv" + level);
            go.transform.position = pos;
            var e = go.AddComponent<Enemy>();
            e.def = def;
            e.level = level;
            float s = Data.LevelScale(level);
            e.Build(def.sheet, 0.9f, 0.3f, 0.3f, def.scale + 0.05f * (level - 1));
            e.rb.mass = 0.6f;
            e.rb.drag = 0;
            e.maxHp = e.hp = Mathf.Round(def.hp * s);
            e.dmg = def.dmg * s;
            e.speed = def.speed;
            e.maxPoise = e.poise = def.poise * s;
            e.home = pos;
            e.castCd = Random.Range(1.5f, 3f);
            e.anim.OnHit += e.OnAnimHit;
            e.anim.OnEnd += e.OnAnimEnd;
            e.anim.Play("idle");
            e.anim.speed = Random.Range(0.92f, 1.08f);
            All.Add(e);
            return e;
        }

        void OnDestroy() { All.Remove(this); }

        public static Enemy Nearest(Vector2 p, float maxDist, Vector2? dir = null, float minDot = -2f)
        {
            Enemy best = null;
            float bd = maxDist;
            foreach (var e in All)
            {
                if (e.dead) continue;
                Vector2 d = e.Pos - p;
                float m = d.magnitude;
                if (m > bd) continue;
                if (dir.HasValue && m > 0.01f && Vector2.Dot(d / m, dir.Value) < minDot) continue;
                bd = m;
                best = e;
            }
            return best;
        }

        void Go(St s)
        {
            state = s;
            stateT = 0;
        }

        protected override void Update()
        {
            base.Update();
            if (dead) return;
            float dt = Time.deltaTime;
            stateT += dt;
            castCd -= dt;
            attackCd -= dt;
            var p = Player.I;
            Vector2 toP = p != null ? p.Pos - Pos : Vector2.zero;
            float dist = toP.magnitude;
            bool playerOk = p != null && !p.dead;

            switch (state)
            {
                case St.Idle:
                    think -= dt;
                    if (think <= 0)
                    {
                        think = Random.Range(1.2f, 2.8f);
                        wander = Random.value < 0.55f ? Random.insideUnitCircle.normalized * 0.9f : Vector2.zero;
                        if ((Pos - home).magnitude > 3f) wander = (home - Pos).normalized * 0.9f;
                    }
                    Move(wander, speed * 0.4f);
                    if (playerOk && dist < def.aggro)
                    {
                        Go(St.Chase);
                        Fx.Alert(this);
                        if (def.boss) { Hud.I?.Banner(def.name, def.title); CameraRig.Shake(0.25f, 0.4f); }
                        Sfx.Play("imp_cry", 0.35f, Random.Range(1.0f, 1.2f));
                    }
                    break;
                case St.Chase:
                {
                    if (!playerOk || dist > def.aggro * 1.8f) { Go(St.Idle); break; }
                    Face(Util.FacingFrom(toP, facing));
                    tpCd -= dt;
                    if (def.id == "assassin_shadow" && tpCd <= 0 && dist > 1.8f)
                    {
                        // shadow step: vanish and reappear behind the hero, then strike after a short tell
                        tpCd = Random.Range(3.6f, 5f);
                        Fx.DemonPoof(Pos + Vector2.up * 0.7f);
                        Vector2 behind = p.Pos - Util.FacingVec(p.facing) * 1.3f;
                        transform.position = behind;
                        Fx.DemonPoof(behind + Vector2.up * 0.7f);
                        Sfx.Play("roll", 0.4f, 0.7f);
                        nextIsCast = false;
                        attackCd = 0;
                        Go(St.Telegraph);
                        break;
                    }
                    // casters keep mid range and throw fire, melee when cornered
                    if (def.caster && castCd <= 0 && dist > 2.6f && dist < 7.5f) { nextIsCast = true; Go(St.Telegraph); break; }
                    if (dist < 1.55f && attackCd <= 0) { nextIsCast = false; Go(St.Telegraph); break; }
                    Vector2 want = toP.normalized;
                    // circle-strafe a little so groups surround the player instead of stacking
                    Vector2 side = new Vector2(-want.y, want.x) * Mathf.Sin(Time.time * 1.3f + GetInstanceID()) * 0.45f;
                    float sp = dist < 1.3f ? 0 : speed;
                    Move((want + side).normalized, sp);
                    Separate();
                    break;
                }
                case St.Telegraph:
                {
                    rb.velocity = knock;
                    Face(Util.FacingFrom(toP, facing));
                    // red pulse warns the player; the window is the time to roll
                    float pulse = Mathf.PingPong(stateT * 8f, 1f);
                    Flash(nextIsCast ? new Color(1f, 0.6f, 0.2f) : new Color(1f, 0.15f, 0.15f), 0.55f * pulse);
                    if (stateT > (nextIsCast ? 0.35f : 0.42f))
                    {
                        hitDone = false;
                        if (nextIsCast) { Go(St.Cast); anim.Play("cast", true); castCd = Random.Range(3.2f, 4.6f); }
                        else { Go(St.Attack); anim.Play("attack", true); attackCd = Random.Range(1.0f, 1.6f); }
                    }
                    break;
                }
                case St.Attack:
                {
                    float n = anim.Normalized;
                    // lunge burst right before the hit frame
                    Vector2 f = Util.FacingVec(facing);
                    rb.velocity = (n > 0.3f && n < 0.6f ? f * 7.5f : Vector2.zero) + knock;
                    break;
                }
                case St.Cast:
                    rb.velocity = knock;
                    break;
                case St.Hurt:
                    rb.velocity = knock;
                    if (stateT > 0.38f) { Go(St.Chase); anim.Play("move"); }
                    break;
            }
            knock = Vector2.MoveTowards(knock, Vector2.zero, 26f * dt);
        }

        void Move(Vector2 dir, float sp)
        {
            if (dir.sqrMagnitude > 0.01f && sp > 0.01f)
            {
                Face(Util.FacingFrom(dir, facing));
                anim.Play("move");
            }
            else anim.Play("idle");
            rb.velocity = dir * sp + knock;
        }

        void Separate()
        {
            foreach (var o in All)
            {
                if (o == this || o.dead) continue;
                Vector2 d = Pos - o.Pos;
                float m = d.magnitude;
                if (m < 0.9f && m > 0.001f) rb.velocity += d / m * (0.9f - m) * 4f;
            }
        }

        void OnAnimHit(string a)
        {
            var p = Player.I;
            if (p == null || p.dead) return;
            if (a == "attack" && !hitDone)
            {
                hitDone = true;
                Vector2 c = Pos + Util.FacingVec(facing) * 0.7f;
                Fx.Claw(c + Vector2.up * 0.6f, facing);
                if ((p.Pos - c).magnitude < 1.05f)
                    p.Hurt(Mathf.Round(dmg * Random.Range(0.9f, 1.1f)), Pos, 7f, 20);
                Sfx.Play("claw", 0.5f, Random.Range(1.0f, 1.15f));
            }
            else if (a == "cast")
            {
                Vector2 from = Pos + Vector2.up * 0.9f;
                // lead the target slightly
                Vector2 aim = (p.Pos + p.rb.velocity * 0.25f + Vector2.up * 0.5f - from).normalized;
                if (def.boss)
                    for (int k = -1; k <= 1; k++)
                    {
                        Vector2 a2 = Quaternion.Euler(0, 0, k * 18f) * aim;
                        Projectile.Fireball(from + a2 * 0.5f, a2, dmg * 0.7f);
                    }
                else if (def.caster) Projectile.Fireball(from + aim * 0.4f, aim, dmg * 0.8f);
                Sfx.Play("fireball", 0.5f, Random.Range(0.95f, 1.1f));
            }
        }

        void OnAnimEnd(string a)
        {
            if (a == "attack" || a == "cast")
            {
                Go(St.Chase);
                anim.Play("move");
            }
            else if (a == "death") Destroy(gameObject, 0.1f);
        }

        public override bool Hurt(float d, Vector2 from, float knockback, float poiseDmg, bool crit = false)
        {
            if (!base.Hurt(d, from, knockback, poiseDmg, crit)) return false;
            lastHurt = Time.time;
            if (def.boss && !summoned && hp < maxHp * 0.5f && hp > 0)
            {
                summoned = true;
                string minion = def.id == "dryad_profane" ? "spirit_corrupt" : def.id == "grakk" ? "imp" : def.id == "assassin_shadow" ? "imp_scout" : null;
                if (minion != null)
                {
                    Hud.I?.Banner(def.name + " se enfurece", "Reforços demoníacos!");
                    CameraRig.Shake(0.3f, 0.5f);
                    for (int k = 0; k < 3; k++)
                        Enemy.Spawn(minion, Pos + (Vector2)(Quaternion.Euler(0, 0, k * 120f) * Vector2.right) * 2.2f, Mathf.Max(1, level - 2));
                    speed *= 1.25f;
                }
            }
            Sfx.Play("imp_hurt", 0.4f, Random.Range(1.0f, 1.25f));
            if (dead) return true;
            if (state == St.Idle) Go(St.Chase);
            if (poise <= 0)
            {
                // poise break: stagger + interrupts telegraph
                poise = maxPoise;
                Go(St.Hurt);
                anim.Play("hurt", true);
                Fx.Toast("Quebra!", new Color(1f, 0.9f, 0.5f), Pos + Vector2.up * 2.1f);
            }
            return true;
        }

        protected override void Die()
        {
            dead = true;
            Go(St.Dead);
            rb.velocity = Vector2.zero;
            col.enabled = false;
            anim.Play("death", true);
            StartDissolve();
            Sfx.Play("imp_die", 0.5f, Random.Range(0.95f, 1.1f));
            Fx.DemonPoof(Pos + Vector2.up * 0.7f);
            Loot.Drop(def, level, Pos);
            Game.I.OnEnemyKilled(this);
        }
    }
}
