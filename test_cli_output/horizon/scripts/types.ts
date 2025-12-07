/**
 * Type definitions for OmniWorld Builder Horizon integration.
 */

/**
 * 3D Vector type.
 */
export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

/**
 * RGBA Color type.
 */
export interface Color {
  r: number;
  g: number;
  b: number;
  a: number;
}

/**
 * Entity types supported in Horizon.
 */
export enum EntityType {
  StaticMesh = 'static_mesh',
  DynamicObject = 'dynamic_object',
  Character = 'character',
  Prop = 'prop',
  Trigger = 'trigger',
  SpawnPoint = 'spawn_point',
  Waypoint = 'waypoint',
  Light = 'light',
  Camera = 'camera',
  AudioSource = 'audio_source',
  ParticleSystem = 'particle_system',
  Terrain = 'terrain',
}

/**
 * Light types supported in Horizon.
 */
export enum LightType {
  Directional = 'directional',
  Point = 'point',
  Spot = 'spot',
  Area = 'area',
  Ambient = 'ambient',
}

/**
 * Entity data structure.
 */
export interface EntityData {
  id: string;
  name: string;
  entityType: EntityType;
  position: Vector3;
  rotation: Vector3;
  scale: Vector3;
  tags: string[];
  assetReference?: string;
}

/**
 * Light data structure.
 */
export interface LightData {
  name: string;
  lightType: LightType;
  color: Color;
  intensity: number;
  position: Vector3;
  rotation: Vector3;
  castShadows: boolean;
}

/**
 * World metadata.
 */
export interface WorldMetadata {
  title: string;
  description: string;
  author: string;
  version: string;
  tags: string[];
  targetPlatforms: string[];
}