"""Example: Export a world to Unity, Unreal, and Horizon.

This example demonstrates exporting a WDL world to all three supported engines:
- Unity (C#)
- Unreal Engine (Python)
- Meta Horizon Worlds (TypeScript)
"""

from pathlib import Path

from omniworld_builder.adapters.horizon import HorizonGenerator
from omniworld_builder.adapters.unity import UnityGenerator
from omniworld_builder.adapters.unreal import UnrealGenerator
from omniworld_builder.core.wdl_schema import (
    EntityType,
    Lighting,
    LightType,
    Transform,
    Vector3,
    WDLEntity,
    WDLMetadata,
    WDLWorld,
)


def create_simple_world() -> WDLWorld:
    """Create a simple world for export demonstration."""
    # Create world metadata
    metadata = WDLMetadata(
        title="Simple Export Demo",
        description="A minimal world for testing engine exports",
        author="OmniWorld Builder",
    )

    # Create the world
    world = WDLWorld(metadata=metadata)

    # Add a ground plane
    world.add_entity(
        WDLEntity(
            name="Ground",
            entity_type=EntityType.TERRAIN,
            transform=Transform(
                position=Vector3(x=0, y=0, z=0),
                scale=Vector3(x=50, y=1, z=50),
            ),
            tags=["terrain", "ground"],
        )
    )

    # Add a central prop (cube)
    world.add_entity(
        WDLEntity(
            name="CentralCube",
            entity_type=EntityType.PROP,
            transform=Transform(
                position=Vector3(x=0, y=2, z=0),
                scale=Vector3(x=2, y=2, z=2),
            ),
            tags=["prop", "interactive"],
        )
    )

    # Add a spawn point
    world.add_entity(
        WDLEntity(
            name="PlayerSpawn",
            entity_type=EntityType.SPAWN_POINT,
            transform=Transform(
                position=Vector3(x=0, y=1, z=-10),
                scale=Vector3(x=1, y=1, z=1),
            ),
            tags=["spawn"],
        )
    )

    # Add a directional light (sun)
    world.add_light(
        Lighting(
            name="Sun",
            light_type=LightType.DIRECTIONAL,
            intensity=1.2,
            transform=Transform(
                position=Vector3(x=0, y=10, z=0),
                rotation=Vector3(x=50, y=-30, z=0),
            ),
        )
    )

    # Add an ambient/point light
    world.add_light(
        Lighting(
            name="AmbientLight",
            light_type=LightType.POINT,
            intensity=0.5,
            transform=Transform(
                position=Vector3(x=0, y=5, z=0),
            ),
        )
    )

    return world


def main():
    """Export a world to all supported engines."""
    print("=" * 60)
    print("OmniWorld Builder - Export to Engines Example")
    print("=" * 60)
    print()

    # Create a simple world
    print("Creating simple world...")
    world = create_simple_world()
    print(f"✓ World created: {world.metadata.title}")
    print(f"  Entities: {len(world.entities)}")
    print(f"  Lights: {len(world.lights)}")
    print()

    # Define output directories
    base_output = Path("examples/output")
    unity_output = base_output / "unity"
    unreal_output = base_output / "unreal"
    horizon_output = base_output / "horizon"

    # Export to Unity
    print("Exporting to Unity (C#)...")
    try:
        unity_gen = UnityGenerator(unity_output)
        unity_gen.save(world)
        print(f"✓ Unity export saved to: {unity_output.absolute()}")
    except Exception as e:
        print(f"✗ Unity export failed: {e}")

    print()

    # Export to Unreal
    print("Exporting to Unreal Engine (Python)...")
    try:
        unreal_gen = UnrealGenerator(unreal_output)
        unreal_gen.save(world)
        print(f"✓ Unreal export saved to: {unreal_output.absolute()}")
    except Exception as e:
        print(f"✗ Unreal export failed: {e}")

    print()

    # Export to Horizon
    print("Exporting to Meta Horizon Worlds (TypeScript)...")
    try:
        horizon_gen = HorizonGenerator(horizon_output)
        horizon_gen.save(world)
        print(f"✓ Horizon export saved to: {horizon_output.absolute()}")
    except Exception as e:
        print(f"✗ Horizon export failed: {e}")

    print()
    print("=" * 60)
    print("Export complete!")
    print()
    print("Generated files:")
    print(f"  Unity:   {unity_output}/")
    print(f"  Unreal:  {unreal_output}/")
    print(f"  Horizon: {horizon_output}/")
    print()
    print("These generated files can be imported into their")
    print("respective game engines to build the world.")
    print("=" * 60)


if __name__ == "__main__":
    main()
