# OmniWorld Builder

AI-powered universal world builder that converts natural language concepts into 3D environments across Unity, Unreal Engine, and Meta Horizon Worlds using a multi-agent system and World Description Language (WDL).

## Features

- **World Description Language (WDL)**: Platform-agnostic intermediate representation for 3D worlds
- **Multi-Agent System**: LangGraph-powered orchestration with specialized AI agents
- **Cross-Platform Export**: Generate code for Unity (C#), Unreal Engine (Python), and Meta Horizon Worlds (TypeScript)
- **Spatial Reasoning**: Built-in tools for entity placement and collision detection
- **Asset Management**: Registry system for tracking and organizing 3D assets

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OmniWorld Builder                            │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │   Vision    │───▶│   Systems   │───▶│  Technical  │             │
│  │  Architect  │    │  Designer   │    │  Director   │             │
│  └─────────────┘    └─────────────┘    └─────────────┘             │
│         │                                      │                    │
│         │           ┌─────────────┐            │                    │
│         │           │     QA      │◀───────────┤                    │
│         │◀──────────│    Agent    │            │                    │
│         │  revision └─────────────┘            │                    │
│         │                 │                    ▼                    │
│         │                 │           ┌─────────────┐               │
│         └─────────────────┴──────────▶│    WDL      │               │
│                                       │  Generator  │               │
│                                       └─────────────┘               │
│                                              │                      │
│                                              ▼                      │
│                                       ┌─────────────┐               │
│                                       │  WDL World  │               │
│                                       └─────────────┘               │
│                                              │                      │
│                    ┌─────────────────────────┼─────────────────┐    │
│                    ▼                         ▼                 ▼    │
│             ┌───────────┐             ┌───────────┐     ┌─────────┐│
│             │   Unity   │             │  Unreal   │     │ Horizon ││
│             │    C#     │             │  Python   │     │   TS    ││
│             └───────────┘             └───────────┘     └─────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

## Installation

### Requirements

- Python 3.10+
- pip or uv package manager

### Install

```bash
# Clone repository
git clone https://github.com/wildhash/omniworld-builder.git
cd omniworld-builder

# Install package
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

### Environment Setup

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Quick Start

### Generate a World with AI

```python
import asyncio
from omniworld_builder.agents import WorldBuilderOrchestrator

async def main():
    orchestrator = WorldBuilderOrchestrator()
    
    world = await orchestrator.build_world(
        "A mystical forest with ancient trees, glowing mushrooms, "
        "and a peaceful atmosphere at sunset"
    )
    
    print(world.to_json())

asyncio.run(main())
```

### Create a World Manually

```python
from omniworld_builder.core import (
    WDLWorld, WDLMetadata, WDLEntity, EntityType,
    Transform, Vector3, Lighting, LightType
)

# Create world
world = WDLWorld(
    metadata=WDLMetadata(
        title="My World",
        description="A simple world"
    )
)

# Add entities
world.add_entity(WDLEntity(
    name="Ground",
    entity_type=EntityType.TERRAIN,
    transform=Transform(scale=Vector3(x=100, y=1, z=100))
))

# Add lights
world.add_light(Lighting(
    name="Sun",
    light_type=LightType.DIRECTIONAL,
    intensity=1.0
))

# Export
print(world.to_json())
```

### Export to Game Engines

```python
from omniworld_builder.adapters import (
    UnityGenerator, UnrealGenerator, HorizonGenerator
)

# Export to Unity
UnityGenerator("output/unity").save(world)

# Export to Unreal
UnrealGenerator("output/unreal").save(world)

# Export to Horizon
HorizonGenerator("output/horizon").save(world)
```

## Project Structure

```
omniworld-builder/
├── src/omniworld_builder/
│   ├── core/               # WDL schema and validators
│   │   ├── wdl_schema.py   # Pydantic models for WDL
│   │   └── validators.py   # World validation logic
│   ├── agents/             # LangGraph multi-agent system
│   │   ├── orchestrator.py # Main workflow orchestration
│   │   ├── vision_architect.py
│   │   ├── systems_designer.py
│   │   ├── technical_director.py
│   │   ├── wdl_generator.py
│   │   └── qa_agent.py
│   ├── adapters/           # Platform-specific generators
│   │   ├── unity/          # Unity C# generator
│   │   ├── unreal/         # Unreal Python generator
│   │   └── horizon/        # Horizon TypeScript generator
│   ├── tools/              # Utilities
│   │   ├── asset_registry.py
│   │   └── spatial_reasoning.py
│   └── examples/           # Sample WDL worlds
├── docs/                   # Documentation
├── tests/                  # Test suite
└── pyproject.toml          # Project configuration
```

## Agents

| Agent | Role |
|-------|------|
| **Vision Architect** | Conceptualizes visual design, art style, and atmosphere |
| **Systems Designer** | Designs gameplay mechanics and interactions |
| **Technical Director** | Creates technical specifications and asset requirements |
| **WDL Generator** | Synthesizes all outputs into valid WDL |
| **QA Agent** | Validates and quality-checks the generated world |

## WDL Schema

WDL (World Description Language) is the core IR supporting:

- **Entities**: Static meshes, dynamic objects, characters, props, triggers
- **Materials**: PBR, standard, emissive, transparent
- **Lighting**: Directional, point, spot, area, ambient
- **Environment**: Weather, time of day, fog, skybox
- **Systems**: Interactions, triggers, gameplay mechanics

See [docs/wdl_specification.md](docs/wdl_specification.md) for full schema documentation.

## Dependencies

- **langgraph**: Multi-agent orchestration
- **langchain-anthropic**: Claude AI integration  
- **pydantic**: Data validation and serialization
- **langchain**: LLM framework

## Documentation

- [Getting Started](docs/getting_started.md)
- [WDL Specification](docs/wdl_specification.md)
- [Multi-Agent Architecture](docs/multi_agent_architecture.md)

## Examples

```python
from omniworld_builder.examples import create_forest_world, create_sci_fi_station

# Enchanted forest environment
forest = create_forest_world()

# Futuristic space station
station = create_sci_fi_station()
```

## License

MIT
