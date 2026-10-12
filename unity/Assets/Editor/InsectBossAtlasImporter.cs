using UnityEditor;
using UnityEngine;

namespace Aetheria.Editor
{
    /// <summary>
    /// Prevent Unity's default 2K import limit from silently shrinking the
    /// 3840x8064 boss atlases and degrading their hand-painted details.
    /// Only new Lote 2 boss PNGs are affected; prior approved art is untouched.
    /// </summary>
    public sealed class InsectBossAtlasImporter : AssetPostprocessor
    {
        void OnPreprocessTexture()
        {
            string prefix = "Assets/Resources/Sprites/Demons/";
            if (!assetPath.StartsWith(prefix)) return;
            string name = assetPath.Substring(prefix.Length);
            if (name != "mantis_high_reaper.png" &&
                name != "scarab_colossus.png" &&
                name != "moth_oracle.png" &&
                name != "queen_vespara.png" &&
                name != "brood_tyrant.png") return;
            var importer = assetImporter as TextureImporter;
            if (importer == null) return;
            importer.maxTextureSize = 8192;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.textureCompression = TextureImporterCompression.Compressed;
            importer.compressionQuality = 100;
            importer.mipmapEnabled = false;
            importer.alphaIsTransparency = true;
            importer.isReadable = false;
            importer.filterMode = FilterMode.Bilinear;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.sRGBTexture = true;
        }
    }
}
