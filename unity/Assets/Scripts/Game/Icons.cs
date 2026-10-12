using System.Collections.Generic;
using UnityEngine;

namespace Aetheria
{
    /// <summary>Item / skill icons from the "Sprites/Ui/icons" sheet (one frame per icon, anim name = icon id).</summary>
    public static class Icons
    {
        static Sheet sheet;
        static readonly Dictionary<string, Sprite> cache = new Dictionary<string, Sprite>();

        public static Sprite Get(string id)
        {
            if (cache.TryGetValue(id, out var s)) return s;
            if (sheet == null) sheet = Sheets.Load("Sprites/Ui/icons");
            var a = sheet?.Get(id);
            s = a != null ? sheet.frames[a.start] : Util.SoftCircle;
            cache[id] = s;
            return s;
        }
    }
}
