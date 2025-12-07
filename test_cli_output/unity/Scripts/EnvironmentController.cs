using UnityEngine;
using System.Collections.Generic;

namespace OmniWorld.Generated
{
    [System.Serializable]
    public class LightData
    {
        public string name;
        public LightType lightType;
        public Color color;
        public float intensity;
        public Vector3 position;
        public Vector3 rotation;
        public bool castShadows;
    }

    /// <summary>
    /// Controls environment settings for the generated world.
    /// </summary>
    public class EnvironmentController : MonoBehaviour
    {
        [Header("Environment Settings")]
        public Color ambientColor = new Color(0.2f, 0.2f, 0.2f, 1.0f);
        public bool fogEnabled = false;
        public Color fogColor = new Color(0.5f, 0.5f, 0.5f);
        public float fogDensity = 0.01f;

        [Header("Time Settings")]
        public int timeHour = 12;
        public int timeMinute = 0;
        public bool dayNightCycle = false;

        private List<Light> createdLights = new List<Light>();

        private LightData[] lightDataList = new LightData[]
        {
            new LightData {
        name = "Sun",
        lightType = LightType.Directional,
        color = new Color(1.0f, 1.0f, 1.0f),
        intensity = 1.2f,
        position = new Vector3(0.0f, 10.0f, 0.0f),
        rotation = new Vector3(50.0f, -30.0f, 0.0f),
        castShadows = true
    },
new LightData {
        name = "AmbientLight",
        lightType = LightType.Point,
        color = new Color(1.0f, 1.0f, 1.0f),
        intensity = 0.5f,
        position = new Vector3(0.0f, 5.0f, 0.0f),
        rotation = new Vector3(0.0f, 0.0f, 0.0f),
        castShadows = true
    }
        };

        public void Initialize()
        {
            SetupAmbient();
            SetupFog();
            CreateLights();
        }

        private void SetupAmbient()
        {
            RenderSettings.ambientLight = ambientColor;
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
        }

        private void SetupFog()
        {
            RenderSettings.fog = fogEnabled;
            RenderSettings.fogColor = fogColor;
            RenderSettings.fogDensity = fogDensity;
            RenderSettings.fogMode = FogMode.Exponential;
        }

        private void CreateLights()
        {
            foreach (var data in lightDataList)
            {
                CreateLight(data);
            }
            Debug.Log($"Created {lightDataList.Length} lights");
        }

        private void CreateLight(LightData data)
        {
            GameObject lightObj = new GameObject(data.name);
            lightObj.transform.position = data.position;
            lightObj.transform.rotation = Quaternion.Euler(data.rotation);
            lightObj.transform.SetParent(transform);

            Light light = lightObj.AddComponent<Light>();
            light.type = data.lightType;
            light.color = data.color;
            light.intensity = data.intensity;
            light.shadows = data.castShadows ? LightShadows.Soft : LightShadows.None;

            createdLights.Add(light);
        }
    }
}