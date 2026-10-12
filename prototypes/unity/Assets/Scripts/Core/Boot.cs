using UnityEngine;

namespace Aetheria
{
    /// <summary>Entry point: the scene is empty; everything is built from code.</summary>
    public static class Boot
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Start()
        {
            if (Object.FindObjectOfType<Game>() != null) return;
            Application.targetFrameRate = 60;
            QualitySettings.vSyncCount = 1;
            Physics2D.gravity = Vector2.zero;
            var go = new GameObject("Game");
            Object.DontDestroyOnLoad(go);
            go.AddComponent<Game>();
        }
    }
}
