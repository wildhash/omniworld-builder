/**
           * Entity factory for spawning world entities.
           * Total entities: 3
           */

          import { Entity, World, Vec3 } from 'horizon/core';
          import { EntityData, EntityType } from './types';

          /**
           * Pre-defined entity data for the world.
           */
          export const ENTITY_DATA: EntityData[] = [
            {
  id: "f5f9254d-317f-41b0-9620-8d06f6551c3e",
  name: "Ground",
  entityType: EntityType.Terrain,
  position: { x: 0.0, y: 0.0, z: 0.0 },
  rotation: { x: 0.0, y: 0.0, z: 0.0 },
  scale: { x: 50.0, y: 1.0, z: 50.0 },
  tags: ["terrain", "ground"],
  assetReference: undefined,
},
{
  id: "fc25d648-1ad6-4987-bf33-db46b938b76b",
  name: "CentralCube",
  entityType: EntityType.Prop,
  position: { x: 0.0, y: 2.0, z: 0.0 },
  rotation: { x: 0.0, y: 0.0, z: 0.0 },
  scale: { x: 2.0, y: 2.0, z: 2.0 },
  tags: ["prop", "interactive"],
  assetReference: undefined,
},
{
  id: "1de4a1b6-283e-4c7b-ba47-df009294ea58",
  name: "PlayerSpawn",
  entityType: EntityType.SpawnPoint,
  position: { x: 0.0, y: 1.0, z: -10.0 },
  rotation: { x: 0.0, y: 0.0, z: 0.0 },
  scale: { x: 1.0, y: 1.0, z: 1.0 },
  tags: ["spawn"],
  assetReference: undefined,
}
          ];

          /**
           * Factory class for creating entities in Horizon Worlds.
           */
          export class EntityFactory {
            private world: World;

            constructor() {
              this.world = World.getWorld();
            }

            /**
             * Spawn all entities from the data list.
             */
            async spawnAll(): Promise<Entity[]> {
              const spawned: Entity[] = [];

              for (const data of ENTITY_DATA) {
                const entity = await this.spawnEntity(data);
                if (entity) {
                  spawned.push(entity);
                }
              }

              console.log(`Spawned ${spawned.length} entities`);
              return spawned;
            }

            /**
             * Spawn a single entity from data.
             */
            async spawnEntity(data: EntityData): Promise<Entity | null> {
              try {
                const entity = await this.world.spawnEntity({
                  position: new Vec3(data.position.x, data.position.y, data.position.z),
                  rotation: new Vec3(data.rotation.x, data.rotation.y, data.rotation.z),
                  scale: new Vec3(data.scale.x, data.scale.y, data.scale.z),
                });

                if (entity) {
                  entity.name.set(data.name);

                  // Set up based on entity type
                  this.configureEntity(entity, data);

                  console.log(`Spawned: ${data.name}`);
                }

                return entity;
              } catch (error) {
                console.error(`Failed to spawn ${data.name}:`, error);
                return null;
              }
            }

            /**
             * Configure entity based on its type.
             */
            private configureEntity(entity: Entity, data: EntityData): void {
              switch (data.entityType) {
                case EntityType.StaticMesh:
                  // Configure as static mesh
                  break;
                case EntityType.DynamicObject:
                  // Enable physics
                  break;
                case EntityType.Trigger:
                  // Setup trigger zone
                  break;
                case EntityType.SpawnPoint:
                  // Mark as spawn point
                  break;
                default:
                  break;
              }
            }

            /**
             * Spawn entity by ID from the data list.
             */
            async spawnById(id: string): Promise<Entity | null> {
              const data = ENTITY_DATA.find(e => e.id === id);
              if (data) {
                return this.spawnEntity(data);
              }
              console.warn(`Entity not found: ${id}`);
              return null;
            }
          }