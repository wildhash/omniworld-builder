using UnityEngine;
using System.Collections.Generic;

namespace OmniWorld.Generated
{
    [System.Serializable]
    public class EntityData
    {
        public string id;
        public string name;
        public string entityType;
        public Vector3 position;
        public Vector3 rotation;
        public Vector3 scale;
        public string[] tags;
        public string assetReference;
    }

    /// <summary>
    /// Spawns entities for the generated world.
    /// Total entities: 3
    /// </summary>
    public class EntitySpawner : MonoBehaviour
    {
        [Header("Entity Prefabs")]
        public GameObject defaultPrefab;
        public Dictionary<string, GameObject> prefabLookup = new Dictionary<string, GameObject>();

        private List<GameObject> spawnedEntities = new List<GameObject>();

        private EntityData[] entityDataList = new EntityData[]
        {
            new EntityData {
        id = "8b1d62fc-9a93-4432-8825-6b9d96623ada",
        name = "Ground",
        entityType = "terrain",
        position = new Vector3(0.0f, 0.0f, 0.0f),
        rotation = new Vector3(0.0f, 0.0f, 0.0f),
        scale = new Vector3(50.0f, 1.0f, 50.0f),
        tags = new string[] { "terrain", "ground" },
        assetReference = ""
    },
new EntityData {
        id = "f4b02161-6554-4bed-8e3c-15b73af0da54",
        name = "CentralCube",
        entityType = "prop",
        position = new Vector3(0.0f, 2.0f, 0.0f),
        rotation = new Vector3(0.0f, 0.0f, 0.0f),
        scale = new Vector3(2.0f, 2.0f, 2.0f),
        tags = new string[] { "prop", "interactive" },
        assetReference = ""
    },
new EntityData {
        id = "135a5229-5eb0-4b56-914b-8fa4c4c8e7a5",
        name = "PlayerSpawn",
        entityType = "spawn_point",
        position = new Vector3(0.0f, 1.0f, -10.0f),
        rotation = new Vector3(0.0f, 0.0f, 0.0f),
        scale = new Vector3(1.0f, 1.0f, 1.0f),
        tags = new string[] { "spawn" },
        assetReference = ""
    }
        };

        public void SpawnAll()
        {
            foreach (var data in entityDataList)
            {
                SpawnEntity(data);
            }
            Debug.Log($"Spawned {entityDataList.Length} entities");
        }

        public GameObject SpawnEntity(EntityData data)
        {
            GameObject prefab = defaultPrefab;
            if (!string.IsNullOrEmpty(data.assetReference) && prefabLookup.ContainsKey(data.assetReference))
            {
                prefab = prefabLookup[data.assetReference];
            }

            if (prefab == null)
            {
                // Create primitive as fallback
                prefab = GameObject.CreatePrimitive(GetPrimitiveType(data.entityType));
            }

            GameObject instance = Instantiate(prefab, data.position, Quaternion.Euler(data.rotation));
            instance.name = data.name;
            instance.transform.localScale = data.scale;

            spawnedEntities.Add(instance);
            return instance;
        }

        public void DestroyAll()
        {
            foreach (var entity in spawnedEntities)
            {
                if (entity != null)
                {
                    Destroy(entity);
                }
            }
            spawnedEntities.Clear();
        }

        private PrimitiveType GetPrimitiveType(string entityType)
        {
            return entityType switch
            {
                "terrain" => PrimitiveType.Plane,
                "light" => PrimitiveType.Sphere,
                _ => PrimitiveType.Cube
            };
        }
    }
}