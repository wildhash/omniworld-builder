# OmniWorld Builder - Quick Start Guide

This guide demonstrates the end-to-end pipeline for building worlds with OmniWorld Builder.

## Installation

```bash
# Clone repository
git clone https://github.com/wildhash/omniworld-builder.git
cd omniworld-builder

# Install package
pip install -e .

# Set up API key for AI generation
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Usage

### 1. Command-Line Interface (CLI)

The `omniworld` CLI provides convenient commands for building and exporting worlds.

#### Build a World from a Prompt

```bash
# Generate a world from natural language
omniworld build-from-prompt "A mystical forest with ancient trees and glowing mushrooms" --out my_world.json

# With custom iteration limit
omniworld build-from-prompt "A sci-fi space station" --out station.json --max-iterations 3
```

#### Export a World to Game Engines

```bash
# Export to all engines (Unity, Unreal, Horizon)
omniworld build-from-json my_world.json --out-root output/

# Export to specific engines only
omniworld build-from-json my_world.json --out-root output/ --unity --unreal

# Single engine export
omniworld build-from-json my_world.json --out-root output/ --unity
```

### 2. Python Examples

#### Example 1: Build World from Prompt

```python
import asyncio
from omniworld_builder.agents.orchestrator import WorldBuilderOrchestrator

async def main():
    orchestrator = WorldBuilderOrchestrator()
    
    world = await orchestrator.build_world(
        prompt="A floating sky island with a tree and shrine",
        max_iterations=3
    )
    
    # Save to JSON
    with open("sky_island.json", "w") as f:
        f.write(world.to_json())
    
    print(f"World created: {world.metadata.title}")
    print(f"Entities: {len(world.entities)}")
    print(f"Lights: {len(world.lights)}")

asyncio.run(main())
```

#### Example 2: Export to Game Engines

```python
from omniworld_builder.core.wdl_schema import (
    WDLWorld, WDLMetadata, WDLEntity, EntityType,
    Transform, Vector3, Lighting, LightType
)
from omniworld_builder.adapters import (
    UnityGenerator, UnrealGenerator, HorizonGenerator
)

# Create a simple world
world = WDLWorld(metadata=WDLMetadata(title="My World"))

# Add a ground plane
world.add_entity(WDLEntity(
    name="Ground",
    entity_type=EntityType.TERRAIN,
    transform=Transform(scale=Vector3(x=100, y=1, z=100))
))

# Add a light
world.add_light(Lighting(
    name="Sun",
    light_type=LightType.DIRECTIONAL,
    intensity=1.0
))

# Export to all engines
UnityGenerator("output/unity").save(world)
UnrealGenerator("output/unreal").save(world)
HorizonGenerator("output/horizon").save(world)

print("Export complete!")
```

### 3. Running Provided Examples

```bash
# Export a simple demo world to all engines
python -m omniworld_builder.examples.export_to_engines

# Build a world from a prompt (requires API key)
python -m omniworld_builder.examples.build_world_from_prompt
```

## Output Structure

After exporting, you'll find the following structure:

```
output/
├── unity/
│   ├── Scripts/
│   │   ├── WorldLoader.cs
│   │   ├── EntitySpawner.cs
│   │   ├── EnvironmentController.cs
│   │   └── WorldData.cs
│   └── Data/
│       └── world_data.json
├── unreal/
│   ├── Scripts/
│   │   ├── world_builder.py
│   │   ├── entity_definitions.py
│   │   ├── environment_setup.py
│   │   └── lighting_setup.py
│   └── Data/
│       └── world_data.json
└── horizon/
    ├── scripts/
    │   ├── WorldManager.ts
    │   ├── EntityFactory.ts
    │   ├── EnvironmentController.ts
    │   └── types.ts
    └── data/
        ├── worldData.ts
        └── world_data.json
```

## Testing

Run the test suite to verify your installation:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_wdl_schema.py
pytest tests/test_tools.py
pytest tests/test_adapters.py
```

## Next Steps

- See [WDL Specification](docs/wdl_specification.md) for detailed schema documentation
- See [Multi-Agent Architecture](docs/multi_agent_architecture.md) for how the AI system works
- See [Getting Started](docs/getting_started.md) for more detailed tutorials

## Troubleshooting

### No API Key

If you see errors about missing API keys when using `build-from-prompt`:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Import Errors

If you see module import errors:
```bash
pip install -e .
```

### CLI Not Found

If `omniworld` command is not found:
```bash
pip install -e .
# or use:
python -m omniworld_builder.cli <command>
```
