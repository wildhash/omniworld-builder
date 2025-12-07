using UnityEngine;

namespace OmniWorld.Generated
{
    /// <summary>
    /// Scriptable object containing world metadata.
    /// </summary>
    [CreateAssetMenu(fileName = "WorldData", menuName = "OmniWorld/World Data")]
    public class WorldData : ScriptableObject
    {
        [Header("Metadata")]
        public string worldTitle = "Simple Export Demo";
        public string description = "A minimal world for testing engine exports";
        public string author = "OmniWorld Builder";
        public string version = "1.0.0";

        [Header("Bounds")]
        public Vector3 minBounds = new Vector3(-1000.0f, -100.0f, -1000.0f);
        public Vector3 maxBounds = new Vector3(1000.0f, 500.0f, 1000.0f);

        [Header("Statistics")]
        public int entityCount = 3;
        public int lightCount = 2;
        public int systemCount = 0;
    }
}