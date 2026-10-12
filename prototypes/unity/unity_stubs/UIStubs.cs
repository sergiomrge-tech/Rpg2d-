// Compile-check stubs for com.unity.ugui (UnityEngine.UI) — NOT shipped to Unity.
// Only the members used by the project are declared; signatures mirror the real package.
namespace UnityEngine.UI
{
    public abstract class UIBehaviour : MonoBehaviour { }

    public abstract class Graphic : UIBehaviour
    {
        public virtual Color color { get; set; }
        public bool raycastTarget { get; set; }
        public RectTransform rectTransform => null;
    }

    public abstract class MaskableGraphic : Graphic { }

    public class Image : MaskableGraphic
    {
        public enum Type { Simple, Sliced, Tiled, Filled }
        public enum FillMethod { Horizontal, Vertical, Radial90, Radial180, Radial360 }
        public enum Origin360 { Bottom, Right, Top, Left }
        public Sprite sprite { get; set; }
        public Type type { get; set; }
        public FillMethod fillMethod { get; set; }
        public int fillOrigin { get; set; }
        public bool fillClockwise { get; set; }
        public float fillAmount { get; set; }
        public bool preserveAspect { get; set; }
    }

    public class RawImage : MaskableGraphic
    {
        public Texture texture { get; set; }
    }

    public class Text : MaskableGraphic
    {
        public Font font { get; set; }
        public int fontSize { get; set; }
        public string text { get; set; }
        public TextAnchor alignment { get; set; }
        public HorizontalWrapMode horizontalOverflow { get; set; }
        public VerticalWrapMode verticalOverflow { get; set; }
        public FontStyle fontStyle { get; set; }
        public bool supportRichText { get; set; }
        public float lineSpacing { get; set; }
    }

    public abstract class BaseMeshEffect : UIBehaviour { }

    public class Shadow : BaseMeshEffect
    {
        public Color effectColor { get; set; }
        public Vector2 effectDistance { get; set; }
    }

    public class Outline : Shadow { }

    public class CanvasScaler : UIBehaviour
    {
        public enum ScaleMode { ConstantPixelSize, ScaleWithScreenSize, ConstantPhysicalSize }
        public ScaleMode uiScaleMode { get; set; }
        public Vector2 referenceResolution { get; set; }
        public float matchWidthOrHeight { get; set; }
    }

    public class GraphicRaycaster : UIBehaviour { }
}
