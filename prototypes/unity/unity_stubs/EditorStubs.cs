// Compile-check stubs for the UnityEditor API surface used by Assets/Editor — NOT shipped to Unity.
using System;
using UnityEngine;

namespace UnityEditor
{
    [AttributeUsage(AttributeTargets.Method)]
    public class MenuItem : Attribute { public MenuItem(string path) { } }

    public enum BuildTarget { StandaloneLinux64 = 24, StandaloneWindows64 = 19 }
    public enum BuildTargetGroup { Standalone = 1 }
    [Flags] public enum BuildOptions { None = 0, Development = 1 }
    public enum ApiCompatibilityLevel { NET_Standard_2_0 = 6, NET_Unity_4_8 = 3 }

    public struct BuildPlayerOptions
    {
        public string[] scenes;
        public string locationPathName;
        public BuildTarget target;
        public BuildOptions options;
    }

    public static class BuildPipeline
    {
        public static Build.Reporting.BuildReport BuildPlayer(BuildPlayerOptions o) => null;
    }

    public class EditorBuildSettingsScene
    {
        public EditorBuildSettingsScene(string path, bool enabled) { }
    }

    public static class EditorBuildSettings
    {
        public static EditorBuildSettingsScene[] scenes { get; set; }
    }

    public static class PlayerSettings
    {
        public static string productName { get; set; }
        public static string companyName { get; set; }
        public static int defaultScreenWidth { get; set; }
        public static int defaultScreenHeight { get; set; }
        public static FullScreenMode fullScreenMode { get; set; }
        public static ColorSpace colorSpace { get; set; }
        public static void SetApiCompatibilityLevel(BuildTargetGroup g, ApiCompatibilityLevel l) { }
    }

    public static class AssetDatabase { public static void Refresh() { } }
    public static class EditorApplication { public static void Exit(int code) { } }

    public class AssetImporter : UnityEngine.Object { }

    public enum TextureImporterType { Default = 0, Sprite = 8 }
    public enum TextureImporterNPOTScale { None = 0 }
    public enum TextureImporterCompression { Uncompressed = 0, Compressed = 1, CompressedHQ = 2, CompressedLQ = 3 }

    public class TextureImporter : AssetImporter
    {
        public TextureImporterType textureType { get; set; }
        public TextureImporterNPOTScale npotScale { get; set; }
        public bool mipmapEnabled { get; set; }
        public bool isReadable { get; set; }
        public bool alphaIsTransparency { get; set; }
        public TextureWrapMode wrapMode { get; set; }
        public FilterMode filterMode { get; set; }
        public int maxTextureSize { get; set; }
        public TextureImporterCompression textureCompression { get; set; }
        public bool sRGBTexture { get; set; }
        public bool crunchedCompression { get; set; }
    }

    public class AssetPostprocessor
    {
        public string assetPath => null;
        public AssetImporter assetImporter => null;
    }
}

namespace UnityEditor.Build.Reporting
{
    public enum BuildResult { Unknown, Succeeded, Failed, Cancelled }
    public struct BuildSummary
    {
        public BuildResult result;
        public ulong totalSize;
    }
    public class BuildReport { public BuildSummary summary; }
}

namespace UnityEditor.SceneManagement
{
    public enum NewSceneSetup { EmptyScene, DefaultGameObjects }
    public enum NewSceneMode { Single, Additive }

    public static class EditorSceneManager
    {
        public static UnityEngine.SceneManagement.Scene NewScene(NewSceneSetup s, NewSceneMode m) => default;
        public static bool SaveScene(UnityEngine.SceneManagement.Scene s, string path) => true;
    }
}
