using UnityEngine;

namespace Aetheria
{
    /// <summary>Villager / guild staff: breathing idle, turns to face the hero, strolls a little, talks.</summary>
    public class Npc : Actor
    {
        public string id;
        public string displayName;
        Vector2 home;
        Facing homeFacing;
        float think;
        Vector2 stroll;
        public bool talking;

        public static Npc Spawn(MapNpc m)
        {
            var go = new GameObject("NPC_" + m.id);
            go.transform.position = Util.MapToWorld(m.x, m.y);
            var n = go.AddComponent<Npc>();
            n.id = m.id;
            n.displayName = Story.NameOf(m.id);
            n.Build("Sprites/Chars/" + m.look, 1.2f, 0.4f, 0.32f);
            n.rb.bodyType = RigidbodyType2D.Kinematic;
            n.home = go.transform.position;
            n.homeFacing = m.facing == "left" ? Facing.Left : m.facing == "right" ? Facing.Right : m.facing == "up" ? Facing.Up : Facing.Down;
            n.Face(n.homeFacing);
            n.anim.Play("idle");
            n.anim.speed = Random.Range(0.85f, 1.1f);
            n.maxHp = n.hp = 1;
            n.think = Random.Range(2f, 5f);
            return n;
        }

        protected override void Update()
        {
            base.Update();
            var p = Player.I;
            float dt = Time.deltaTime;
            bool near = p != null && (p.Pos - Pos).magnitude < 2.6f;
            if (near || talking)
            {
                rb.velocity = Vector2.zero;
                Face(Util.FacingFrom(p.Pos - Pos, facing));
                anim.Play("idle");
                return;
            }
            think -= dt;
            if (think <= 0)
            {
                think = Random.Range(3f, 7f);
                stroll = Random.value < 0.4f ? Random.insideUnitCircle.normalized : Vector2.zero;
                if ((Pos - home).magnitude > 1.5f) stroll = (home - Pos).normalized;
            }
            if (stroll.sqrMagnitude > 0.01f && think > 1.5f)
            {
                Face(Util.FacingFrom(stroll, facing));
                anim.Play("walk");
                rb.MovePosition(Pos + stroll * 1.4f * dt);
            }
            else
            {
                if (anim.Base == "walk") Face(homeFacing);
                anim.Play("idle");
            }
        }

        protected override void Die() { }
        public override bool Hurt(float dmg, Vector2 from, float knockback, float poiseDmg, bool crit = false) => false;
    }
}
