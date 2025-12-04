# Getting Started with OmniWorld Builder

OmniWorld Builder is an AI-powered universal world builder that converts natural language descriptions into 3D environments across Unity, Unreal Engine, and Meta Horizon Worlds.

## Installation

### Requirements

- Python 3.10 or higher
- pip or uv package manager

### Install from Source

```bash
# Clone the repository
git clone https://github.com/wildhash/omniworld-builder.git
cd omniworld-builder

# Install with pip
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Environment Setup

Set your Anthropic API key for the AI agents:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Quick Start

### 1. Create a World Programmatically

```python
from omniworld_builder.core import (
    WDLWorld,
    WDLMetadata,
    WDLEntity,
    WDLEnvironment,
    EntityType,
    Transform,
    Vector3,
    WeatherType,
)

# Create world metadata
metadata = WDLMetadata(
    title="My First World",
    description="A simple test world",
    author="Your Name",
)

# Create environment
environment = WDLEnvironment(
    weather=WeatherType.CLEAR,
)

# Create world
world = WDLWorld(metadata=metadata, environment=environment)

# Add a ground plane
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
print(world.to_json())
```

### 2. Use AI Agents to Generate a World

```python
import asyncio
from omniworld_builder.agents import WorldBuilderOrchestrator

async def generate_world():
    orchestrator = WorldBuilderOrchestrator()
    
    world = await orchestrator.build_world(
        "Create a peaceful forest clearing with ancient oak trees, "
        "a small stream, and wildflowers. The lighting should be "
        "warm afternoon sunlight filtering through the leaves."
    )
    
    return world

# Run the async function
world = asyncio.run(generate_world())
print(world.to_json())
```

### 3. Export to Game Engines

```python
from omniworld_builder.adapters import (
    UnityGenerator,
    UnrealGenerator,
    HorizonGenerator,
)

# Export to Unity (C# scripts)
unity = UnityGenerator("output/unity")
unity_files = unity.save(world)
print(f"Unity files: {unity_files}")

# Export to Unreal (Python scripts)
unreal = UnrealGenerator("output/unreal")
unreal_files = unreal.save(world)
print(f"Unreal files: {unreal_files}")

# Export to Horizon (TypeScript)
horizon = HorizonGenerator("output/horizon")
horizon_files = horizon.save(world)
print(f"Horizon files: {horizon_files}")
```

## Using Example Worlds

OmniWorld Builder includes example worlds:

```python
from omniworld_builder.examples import create_forest_world, create_sci_fi_station

# Create an enchanted forest
forest = create_forest_world()
print(f"Forest has {len(forest.entities)} entities")

# Create a sci-fi space station
station = create_sci_fi_station()
print(f"Station has {len(station.entities)} entities")
```

## Working with Assets

### Asset Registry

```python
from omniworld_builder.tools import AssetRegistry, Asset, AssetType

# Create registry
registry = AssetRegistry()

# Register an asset
registry.register(
    Asset(
        id="tree_oak_01",
        name="Oak Tree",
        asset_type=AssetType.MODEL_3D,
        tags=["vegetation", "tree", "oak"],
        source_path="models/vegetation/oak_tree.fbx",
    )
)

# Search for assets
trees = registry.search(query="tree", asset_type=AssetType.MODEL_3D)

# Save registry
registry.save("assets/registry.json")
```

## Spatial Analysis

```python
from omniworld_builder.tools import SpatialReasoner

# Create reasoner for a world
reasoner = SpatialReasoner(world)

# Get spatial analysis
analysis = reasoner.get_spatial_analysis()
print(f"Entity count: {analysis['entity_count']}")
print(f"Collision count: {analysis['collision_count']}")

# Find entities in radius
from omniworld_builder.core import Vector3
nearby = reasoner.find_entities_in_radius(
    Vector3(x=0, y=0, z=0),
    radius=10.0
)
```

## Validation

```python
from omniworld_builder.core import WDLValidator

validator = WDLValidator()
result = validator.validate(world)

if result.is_valid:
    print("✓ World is valid")
else:
    print("✗ Validation failed:")
    for error in result.get_errors():
        print(f"  - {error.message}")
```

## Next Steps

- Read the [WDL Specification](wdl_specification.md) for schema details
- Learn about the [Multi-Agent Architecture](multi_agent_architecture.md)
- Explore example worlds in `src/omniworld_builder/examples/`
- Check out the Unity, Unreal, and Horizon adapters

## Troubleshooting

### API Key Issues

If you get authentication errors, ensure your API key is set:

```bash
echo $ANTHROPIC_API_KEY  # Should print your key
```

### Import Errors

Ensure the package is installed:

```bash
pip install -e .
```

### Async Issues

Remember that the orchestrator uses async/await. Use `asyncio.run()` or run in an async context:

```python
import asyncio

async def main():
    # Your async code here
    pass

asyncio.run(main())
```
