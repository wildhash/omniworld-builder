# World Description Language (WDL) Specification

WDL (World Description Language) is the core Intermediate Representation (IR) used by OmniWorld Builder to describe 3D worlds in a platform-agnostic format.

## Overview

WDL provides a structured way to define:
- **Metadata**: World title, description, author, version, and target platforms
- **Environment**: Weather, lighting, fog, skybox, and physics settings
- **Entities**: All objects in the world with transforms, materials, and physics
- **Lights**: Light sources with type, color, intensity, and shadows
- **Systems**: Interactive behaviors and gameplay mechanics

## Schema Structure

### WDLWorld (Root)

```python
WDLWorld:
  metadata: WDLMetadata
  environment: WDLEnvironment
  entities: list[WDLEntity]
  lights: list[Lighting]
  systems: list[WDLSystem]
  bounds: WorldBounds
```

### WDLMetadata

```python
WDLMetadata:
  title: str                    # World name
  description: str              # Brief description
  author: str                   # Creator name
  version: str                  # Semantic version (e.g., "1.0.0")
  created_at: datetime          # Creation timestamp
  updated_at: datetime          # Last update timestamp
  tags: list[str]               # Categorization tags
  target_platforms: list[str]   # ["unity", "unreal", "horizon"]
```

### WDLEnvironment

```python
WDLEnvironment:
  weather: WeatherType          # clear, cloudy, rainy, stormy, snowy, foggy
  time_of_day: TimeOfDay        # Hour, minute, day/night cycle
  ambient_light: Color          # Global ambient lighting
  fog_enabled: bool             # Enable/disable fog
  fog_color: Color              # Fog color
  fog_density: float            # 0.0 to 1.0
  skybox: SkyboxSettings        # Skybox configuration
  gravity: Vector3              # World gravity vector
  audio_reverb_preset: str      # Optional reverb preset name
```

### WDLEntity

```python
WDLEntity:
  id: str                       # Unique identifier (UUID)
  name: str                     # Display name
  entity_type: EntityType       # static_mesh, dynamic_object, etc.
  transform: Transform          # Position, rotation, scale
  material: Material            # Optional material definition
  physics: PhysicsSettings      # Physics configuration
  collider: Collider            # Optional collision shape
  parent_id: str                # Optional parent entity ID
  children_ids: list[str]       # Child entity IDs
  tags: list[str]               # Entity tags
  metadata: dict                # Custom metadata
  asset_reference: str          # Path to 3D asset
  prefab_reference: str         # Optional prefab reference
```

### Entity Types

| Type | Description |
|------|-------------|
| `static_mesh` | Non-moving geometry |
| `dynamic_object` | Physics-enabled object |
| `character` | NPC or player character |
| `prop` | Interactive prop |
| `trigger` | Trigger volume |
| `spawn_point` | Player/entity spawn location |
| `waypoint` | Navigation waypoint |
| `light` | Light source (use Lighting instead) |
| `camera` | Camera viewpoint |
| `audio_source` | Sound emitter |
| `particle_system` | Particle effect |
| `terrain` | Terrain/landscape |

### Transform

```python
Transform:
  position: Vector3             # World position (x, y, z)
  rotation: Vector3             # Euler angles in degrees
  scale: Vector3                # Scale factors
```

### Material

```python
Material:
  name: str                     # Material name
  material_type: MaterialType   # standard, pbr, unlit, transparent, emissive
  base_color: Color             # Base/albedo color
  metallic: float               # 0.0 to 1.0
  roughness: float              # 0.0 to 1.0
  emission_color: Color         # Optional emission color
  emission_strength: float      # Emission intensity
  texture_path: str             # Diffuse/albedo texture path
  normal_map_path: str          # Normal map texture path
```

### Lighting

```python
Lighting:
  name: str                     # Light name
  light_type: LightType         # directional, point, spot, area, ambient
  color: Color                  # Light color
  intensity: float              # Light intensity
  range: float                  # For point/spot lights
  spot_angle: float             # For spot lights
  cast_shadows: bool            # Enable shadow casting
  transform: Transform          # Position and rotation
```

### WDLSystem

```python
WDLSystem:
  id: str                       # Unique identifier
  name: str                     # System name
  description: str              # System description
  interactions: list[Interaction]  # Interaction definitions
  enabled: bool                 # Is system active
  priority: int                 # Execution priority
  conditions: dict              # Activation conditions
```

### Interaction

```python
Interaction:
  trigger_type: InteractionType # click, hover, collision, proximity, grab, use
  action_type: ActionType       # spawn, destroy, move, animate, etc.
  target_entity_id: str         # Target entity for action
  parameters: dict              # Action-specific parameters
```

## JSON Format

WDL worlds can be serialized to JSON for storage and transfer:

```json
{
  "metadata": {
    "title": "My World",
    "description": "A sample world",
    "version": "1.0.0"
  },
  "environment": {
    "weather": "clear",
    "time_of_day": {
      "hour": 12,
      "minute": 0
    }
  },
  "entities": [
    {
      "id": "uuid-here",
      "name": "Ground",
      "entity_type": "terrain",
      "transform": {
        "position": {"x": 0, "y": 0, "z": 0},
        "rotation": {"x": 0, "y": 0, "z": 0},
        "scale": {"x": 100, "y": 1, "z": 100}
      }
    }
  ],
  "lights": [],
  "systems": []
}
```

## Usage

### Creating a World Programmatically

```python
from omniworld_builder.core import (
    WDLWorld,
    WDLMetadata,
    WDLEntity,
    EntityType,
    Transform,
    Vector3,
)

# Create metadata
metadata = WDLMetadata(
    title="My World",
    description="A simple world",
)

# Create world
world = WDLWorld(metadata=metadata)

# Add entity
world.add_entity(
    WDLEntity(
        name="Ground",
        entity_type=EntityType.TERRAIN,
        transform=Transform(
            scale=Vector3(x=100, y=1, z=100)
        ),
    )
)

# Export to JSON
json_str = world.to_json()
```

### Loading from JSON

```python
world = WDLWorld.from_json(json_str)
```

## Validation

WDL worlds can be validated using the `WDLValidator`:

```python
from omniworld_builder.core import WDLValidator

validator = WDLValidator()
result = validator.validate(world)

if result.is_valid:
    print("World is valid!")
else:
    for error in result.get_errors():
        print(f"Error: {error.message}")
```

## Platform Export

WDL worlds can be exported to platform-specific formats using adapters:

```python
from omniworld_builder.adapters import (
    UnityGenerator,
    UnrealGenerator,
    HorizonGenerator,
)

# Export to Unity C#
unity = UnityGenerator("output/unity")
unity.save(world)

# Export to Unreal Python
unreal = UnrealGenerator("output/unreal")
unreal.save(world)

# Export to Horizon TypeScript
horizon = HorizonGenerator("output/horizon")
horizon.save(world)
```
