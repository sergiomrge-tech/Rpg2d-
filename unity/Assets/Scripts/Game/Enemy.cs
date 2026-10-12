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
        Vector2 skillDirection; // locked during telegraph; skill hit matches animation keyframe
        float chitinGuardLeft; // ant's active defensive cast buff

        public static Enemy Spawn(string kind, Vector2 pos, int level)
        {
            var def = Data.Demons[kind];
            var go = new GameObject(def.name + " Nv" + level);
            go.transform.position = pos;
            var e = go.AddComponent<Enemy>();
            e.def = def;
            e.level = level;
            float s = Data.LevelScale(level);
            e.Build(def.sheet, 0.9f, 0.3f, def.behavior == "scarab_shockwave" ? 0.56f :
                def.behavior == "termite_burrow" ? 0.46f :
                def.behavior == "ant_carapace" ? .43f :
                def.behavior == "spike_roll" ? .48f :
                def.behavior == "roach_plague" ? .42f :
                def.behavior == "cicada_sonic" ? .38f : 0.3f,
                def.scale + 0.05f * (level - 1));
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

        // Unity CI-only capture hook. Actual Enemy animation and ability logic,
        // not a mockup or a texture preview; only called from -ciShots.
        public void CiCastSkill(Vector2 target)
        {
            if (dead) return;
            var direction = target - Pos;
            skillDirection = direction.sqrMagnitude > .001f ? direction.normalized : Util.FacingVec(facing);
            Face(Util.FacingFrom(skillDirection, facing));
            hitDone = false;
            Go(St.Cast);
            anim.Play("cast", true);
        }

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
            if (chitinGuardLeft > 0f) chitinGuardLeft = Mathf.Max(0f, chitinGuardLeft - dt);
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
                        Sfx.Play("imp_cry", 0.35f, Random.Range(1.0f, 1.2f));
                    }
                    break;
                case St.Chase:
                {
                    if (!playerOk || dist > def.aggro * 1.8f) { Go(St.Idle); break; }
                    Face(Util.FacingFrom(toP, facing));
                    // Each Lote 2 species has its own combat range and skill windows.
                    bool mantis = def.behavior == "mantis_dash";
                    bool scarab = def.behavior == "scarab_shockwave";
                    bool moth = def.behavior == "moth_hex";
                    bool termite = def.behavior == "termite_burrow";
                    bool vespa = def.behavior == "vespa_sting";
                    bool cicada = def.behavior == "cicada_sonic";
                    bool ant = def.behavior == "ant_carapace";
                    bool roach = def.behavior == "roach_plague";
                    bool spike = def.behavior == "spike_roll";
                    bool dragonfly = def.behavior == "dragonfly_zigzag";
                    if (castCd <= 0 && ((mantis && dist > 1.9f && dist < 5.3f) ||
                                        (scarab && dist < 3.2f) ||
                                        (moth && dist > 2.2f && dist < 9f) ||
                                        (termite && dist > 1.5f && dist < 5.1f) ||
                                        (vespa && dist > 2.1f && dist < 6.4f) ||
                                        (cicada && dist < 3.8f) ||
                                        (ant && dist < 2.7f && chitinGuardLeft <= 0f) ||
                                        (roach && dist > 1.2f && dist < 5.4f) ||
                                        (spike && dist > 1.8f && dist < 5.5f) ||
                                        (dragonfly && dist > 2.8f && dist < 8.4f) ||
                                        (def.caster && !moth && dist > 2.6f && dist < 7.5f)))
                    {
                        nextIsCast = true; skillDirection = toP.sqrMagnitude > 0.01f ? toP.normalized : Util.FacingVec(facing);
                        Go(St.Telegraph); break;
                    }
                    if (dist < (scarab ? 1.85f : 1.55f) && attackCd <= 0)
                    {
                        nextIsCast = false; Go(St.Telegraph); break;
                    }
                    Vector2 want = toP.normalized;
                    Vector2 side = new Vector2(-want.y, want.x) * Mathf.Sin(Time.time * 1.3f + GetInstanceID()) * 0.45f;
                    if (moth || cicada || roach || dragonfly)
                    {
                        // Cicada circles near to build a sonic pulse; moth maintains longer casting range.
                        float tooNear = cicada ? 2.0f : roach ? 2.1f : dragonfly ? 3.3f : 4.0f;
                        float tooFar = cicada ? 3.2f : roach ? 4.1f : dragonfly ? 7.1f : 6.5f;
                        Vector2 kite = dist < tooNear ? -want : dist > tooFar ? want : side.normalized;
                        Move(kite, speed);
                    }
                    else
                    {
                        float sp = dist < (scarab ? 1.7f : termite ? 1.0f : spike ? 1.45f : 1.3f) ? 0 : speed;
                        Move((want + side * (mantis ? .8f : .45f)).normalized, sp);
                    }
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
                    float tell = nextIsCast
                        ? (def.behavior == "scarab_shockwave" ? 0.72f :
                           def.behavior == "termite_burrow" ? .78f :
                           def.behavior == "cicada_sonic" ? .72f :
                           def.behavior == "moth_hex" ? .65f :
                           def.behavior == "vespa_sting" ? .35f :
                           def.behavior == "spike_roll" ? .57f :
                           def.behavior == "roach_plague" ? .55f :
                           def.behavior == "ant_carapace" ? .48f :
                           def.behavior == "dragonfly_zigzag" ? .37f : .46f)
                        : (def.behavior == "scarab_shockwave" ? 0.52f : 0.42f);
                    if (stateT > tell)
                    {
                        hitDone = false;
                        if (nextIsCast)
                        {
                            Go(St.Cast); anim.Play("cast", true);
                            castCd = def.behavior == "scarab_shockwave" ? 6.2f :
                                     def.behavior == "termite_burrow" ? 5.1f :
                                     def.behavior == "cicada_sonic" ? 6.0f :
                                     def.behavior == "vespa_sting" ? 4.0f :
                                     def.behavior == "ant_carapace" ? 7.2f :
                                     def.behavior == "roach_plague" ? 6.3f :
                                     def.behavior == "spike_roll" ? 5.2f :
                                     def.behavior == "dragonfly_zigzag" ? 4.4f :
                                     def.behavior == "mantis_dash" ? 4.2f : Random.Range(3.6f, 5.4f);
                        }
                        else { Go(St.Attack); anim.Play("attack", true); attackCd = Random.Range(1.0f, 1.6f); }
                    }
                    break;
                }
                case St.Attack:
                {
                    float n = anim.Normalized;
                    // lunge burst right before the hit frame
                    Vector2 f = Util.FacingVec(facing);
                    float burst = def.behavior == "scarab_shockwave" ? 3.5f :
                                  def.behavior == "termite_burrow" ? 4f :
                                  def.behavior == "vespa_sting" ? 8.0f :
                                  def.behavior == "dragonfly_zigzag" ? 8.7f :
                                  def.behavior == "roach_plague" ? 6.3f :
                                  def.behavior == "mantis_dash" ? 9f : 5f;
                    rb.velocity = (n > 0.3f && n < 0.6f ? f * burst : Vector2.zero) + knock;
                    break;
                }
                case St.Cast:
                    // A real skill animation controls the strike window; this is not idle with recolor.
                    if (def.behavior == "mantis_dash")
                    {
                        float n = anim.Normalized;
                        rb.velocity = (n > 0.18f && n < 0.65f ? skillDirection * 10.5f : Vector2.zero) + knock;
                    }
                    else if (def.behavior == "termite_burrow" || def.behavior == "vespa_sting")
                    {
                        float n = anim.Normalized;
                        float burst = def.behavior == "vespa_sting" ? 12.5f : 6.0f;
                        float start = def.behavior == "vespa_sting" ? .20f : .29f;
                        rb.velocity = (n > start && n < .70f ? skillDirection * burst : Vector2.zero) + knock;
                    }
                    else if (def.behavior == "spike_roll" || def.behavior == "dragonfly_zigzag")
                    {
                        float n = anim.Normalized;
                        if (n > .22f && n < .70f)
                        {
                            float v = def.behavior == "spike_roll" ? 12.2f : 7.5f;
                            Vector2 cross = new Vector2(-skillDirection.y, skillDirection.x);
                            rb.velocity = skillDirection * v +
                                (def.behavior == "dragonfly_zigzag" ? cross * Mathf.Sin(Time.time * 27f) * 4f : Vector2.zero) + knock;
                        }
                        else rb.velocity = knock;
                    }
                    else rb.velocity = knock;
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
                Vector2 c = Pos + Util.FacingVec(facing) * (def.behavior == "mantis_dash" ? 1.05f : 0.7f);
                Fx.Claw(c + Vector2.up * 0.6f, facing);
                float radius = def.behavior == "scarab_shockwave" ? 1.55f :
                               def.behavior == "spike_roll" ? 1.38f :
                               def.behavior == "ant_carapace" ? 1.35f :
                               def.behavior == "termite_burrow" ? 1.3f :
                               def.behavior == "vespa_sting" ? 1.25f :
                               def.behavior == "mantis_dash" ? 1.35f : 1.05f;
                if ((p.Pos - c).magnitude < radius)
                    p.Hurt(Mathf.Round(dmg * Random.Range(0.9f, 1.1f)), Pos, 7f, 20);
                Sfx.Play("claw", 0.5f, Random.Range(1.0f, 1.15f));
            }
            else if (a == "cast" && !hitDone)
            {
                hitDone = true;
                if (def.behavior == "mantis_dash")
                {
                    // Scythe dash strike: damage is timed to frame 8, after a real forward movement.
                    Vector2 forward = skillDirection.sqrMagnitude > .01f ? skillDirection : Util.FacingVec(facing);
                    Vector2 center = Pos + forward * 0.7f;
                    Fx.Claw(center + Vector2.up * .65f, facing);
                    Fx.Slash(center + Vector2.up * .3f, facing, 3);
                    if ((p.Pos - center).magnitude < 1.65f)
                        p.Hurt(Mathf.Round(dmg * 1.45f), Pos, 8f, 25);
                    Sfx.Play("swing_heavy", .65f, 1.1f);
                }
                else if (def.behavior == "scarab_shockwave")
                {
                    // Heavy beetle releases a radial shockwave independent of normal melee.
                    Fx.Shockwave(Pos + Vector2.up * .18f, 2.35f);
                    CameraRig.Shake(.16f, .18f);
                    if ((p.Pos - Pos).magnitude <= 2.35f)
                        p.Hurt(Mathf.Round(dmg * 1.15f), Pos, 10f, 30);
                    Sfx.Play("boom", .55f, .85f);
                }
                else if (def.behavior == "termite_burrow")
                {
                    // Burrows forward during cast animation; rises at dig impact frame 10.
                    Fx.Dust(Pos, 1.9f);
                    Fx.Shockwave(Pos, 1.35f);
                    if ((p.Pos - Pos).magnitude < 1.55f)
                        p.Hurt(Mathf.Round(dmg * 1.2f), Pos, 7f, 25);
                    Sfx.Play("boom", .48f, .75f);
                }
                else if (def.behavior == "vespa_sting")
                {
                    // Flight dash + contact venom: animated sting on keyframe 10.
                    Vector2 center = Pos + skillDirection * .6f;
                    Fx.Claw(center + Vector2.up * .5f, facing);
                    for (int i = 0; i < 6; i++)
                    {
                        var e = Fx.Ember(center + Random.insideUnitCircle * .28f, new Color(.55f,.95f,.4f));
                        e.vel = Random.insideUnitCircle * 1.6f;
                    }
                    if ((p.Pos - center).magnitude < 1.6f &&
                        p.Hurt(Mathf.Round(dmg * 1.05f), Pos, 6f, 20))
                        p.ApplyVenom(3.2f);
                    Sfx.Play("claw", .62f, 1.4f);
                }
                else if (def.behavior == "cicada_sonic")
                {
                    // Radius and timing are coupled to the 10th frame of the shriek.
                    Fx.Shockwave(Pos + Vector2.up * .45f, 2.8f);
                    for (int i = 0; i < 9; i++)
                    {
                        Vector2 dir = new Vector2(Mathf.Cos(i * Mathf.PI * 2f / 9f),
                                                  Mathf.Sin(i * Mathf.PI * 2f / 9f));
                        var e = Fx.Ember(Pos + Vector2.up * .55f + dir * .9f, new Color(.36f,.86f,.95f));
                        e.vel = dir * 2.9f;
                    }
                    if ((p.Pos - Pos).magnitude < 2.8f &&
                        p.Hurt(Mathf.Round(dmg * .65f), Pos, 4f, 18))
                        p.ApplySonicDisrupt(.65f);
                    Sfx.Play("boom", .45f, 1.55f);
                }
                else if (def.behavior == "ant_carapace")
                {
                    // Mandibles interlock: temporary defensive carapace and real shield bash.
                    chitinGuardLeft = 3.1f;
                    Fx.MagicCircle(Pos, 1);
                    Fx.Shockwave(Pos, 1.5f);
                    if ((p.Pos - Pos).magnitude < 1.5f)
                        p.Hurt(Mathf.Round(dmg * .85f), Pos, 8f, 18);
                    Sfx.Play("claw", .54f, .70f);
                }
                else if (def.behavior == "roach_plague")
                {
                    // Moving, visible poison zone persists even after cast animation ends.
                    Vector2 center = Pos + skillDirection * 1.25f;
                    if (World.I != null && World.I.BlockedAt(center)) center = Pos;
                    InsectHazard.SpawnPoison(center, 2.25f, 3.6f, 3.4f);
                    Fx.DemonPoof(center);
                    Sfx.Play("fireball", .44f, .68f);
                }
                else if (def.behavior == "spike_roll")
                {
                    // Hit on the actual roll frame, after moving forward.
                    Fx.Shockwave(Pos + Vector2.up * .23f, 1.75f);
                    Fx.Claw(Pos + Vector2.up * .4f, facing);
                    if ((p.Pos - Pos).magnitude < 1.72f)
                        p.Hurt(Mathf.Round(dmg * 1.30f), Pos, 8f, 22);
                    Sfx.Play("boom", .47f, 1.16f);
                }
                else if (def.behavior == "dragonfly_zigzag")
                {
                    // Three slender real projectiles, with a visually different teal trail.
                    Vector2 start = Pos + Vector2.up * .6f;
                    Vector2 aim = (p.Pos + Vector2.up * .5f - start).normalized;
                    for (int k = -1; k <= 1; k++)
                    {
                        float ang = k * 0.13f;
                        Vector2 dir = new Vector2(aim.x * Mathf.Cos(ang) - aim.y * Mathf.Sin(ang),
                                                  aim.x * Mathf.Sin(ang) + aim.y * Mathf.Cos(ang));
                        Projectile.InsectNeedle(start + dir * .35f, dir, dmg * .70f);
                    }
                    Sfx.Play("spark", .56f, 1.5f);
                }
                else
                {
                    Vector2 from = Pos + Vector2.up * 0.9f;
                    Vector2 aim = (p.Pos + p.rb.velocity * 0.25f + Vector2.up * 0.5f - from).normalized;
                    if (def.behavior == "moth_hex")
                    {
                        Fx.MagicCircle(Pos, 2);
                        Projectile.HexSpore(from + aim * .4f, aim, dmg * .7f);
                    }
                    else Projectile.Fireball(from + aim * .4f, aim, dmg * .8f);
                    Sfx.Play("fireball", 0.5f, Random.Range(0.95f, 1.1f));
                }
            }
        }

        void OnAnimEnd(string a)
        {
            if ((a == "attack" && state == St.Attack) || (a == "cast" && state == St.Cast))
            {
                Go(St.Chase);
                anim.Play("move");
            }
            else if (a == "death") Destroy(gameObject, 0.1f);
        }

        public override bool Hurt(float d, Vector2 from, float knockback, float poiseDmg, bool crit = false)
        {
            if (def.behavior == "ant_carapace" && chitinGuardLeft > 0f)
            {
                d *= .36f; // actual temporary armour, not simply a bright shader pulse
                poiseDmg *= .45f;
                Fx.Dust(Pos, .2f);
            }
            if (!base.Hurt(d, from, knockback, poiseDmg, crit)) return false;
            lastHurt = Time.time;
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
