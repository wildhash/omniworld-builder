"""Example: Enchanted Forest World.

This example demonstrates creating a nature-themed world with
terrain, vegetation, and atmospheric lighting.
"""

from omniworld_builder.core.wdl_schema import (
    Color,
    EntityType,
    Lighting,
    LightType,
    Material,
    MaterialType,
    PhysicsSettings,
    SkyboxSettings,
    TimeOfDay,
    Transform,
    Vector3,
    WDLEntity,
    WDLEnvironment,
    WDLMetadata,
    WDLWorld,
    WeatherType,
)


def create_forest_world() -> WDLWorld:
    """Create an enchanted forest world.

    Returns:
        A WDLWorld representing an enchanted forest environment.
    """
    # Create metadata
    metadata = WDLMetadata(
        title="Enchanted Forest",
        description="A mystical forest with ancient trees, glowing mushrooms, and a serene atmosphere",
        author="OmniWorld Builder",
        version="1.0.0",
        tags=["nature", "fantasy", "forest", "peaceful"],
        target_platforms=["unity", "unreal", "horizon"],
    )

    # Create environment settings
    environment = WDLEnvironment(
        weather=WeatherType.FOGGY,
        time_of_day=TimeOfDay(hour=17, minute=30, day_night_cycle=True, cycle_duration_seconds=600),
        ambient_light=Color(r=0.15, g=0.2, b=0.15),
        fog_enabled=True,
        fog_color=Color(r=0.4, g=0.5, b=0.4),
        fog_density=0.02,
        skybox=SkyboxSettings(
            skybox_type="procedural",
            tint_color=Color(r=0.6, g=0.7, b=0.8),
            exposure=0.8,
        ),
        gravity=Vector3(x=0.0, y=-9.81, z=0.0),
    )

    # Create the world
    world = WDLWorld(metadata=metadata, environment=environment)

    # Add terrain
    world.add_entity(
        WDLEntity(
            name="ForestGround",
            entity_type=EntityType.TERRAIN,
            transform=Transform(
                position=Vector3(x=0, y=0, z=0),
                scale=Vector3(x=200, y=1, z=200),
            ),
            material=Material(
                name="ForestFloor",
                material_type=MaterialType.PBR,
                base_color=Color(r=0.2, g=0.15, b=0.1),
                roughness=0.9,
                texture_path="textures/forest_floor_diffuse.png",
                normal_map_path="textures/forest_floor_normal.png",
            ),
            tags=["terrain", "ground"],
        )
    )

    # Add ancient trees
    tree_positions = [
        (10, 0, 10),
        (-15, 0, 5),
        (20, 0, -10),
        (-25, 0, 15),
        (5, 0, -20),
        (-10, 0, -15),
        (30, 0, 5),
        (-5, 0, 25),
    ]

    for i, (x, y, z) in enumerate(tree_positions):
        world.add_entity(
            WDLEntity(
                name=f"AncientTree_{i}",
                entity_type=EntityType.STATIC_MESH,
                transform=Transform(
                    position=Vector3(x=x, y=y, z=z),
                    rotation=Vector3(x=0, y=i * 45, z=0),
                    scale=Vector3(x=1.5, y=2.0, z=1.5),
                ),
                material=Material(
                    name="TreeBark",
                    material_type=MaterialType.PBR,
                    base_color=Color(r=0.3, g=0.2, b=0.15),
                    roughness=0.85,
                ),
                physics=PhysicsSettings(enabled=False, collision_enabled=True),
                tags=["vegetation", "tree", "static"],
                asset_reference="models/ancient_tree.fbx",
            )
        )

    # Add glowing mushrooms
    mushroom_positions = [
        (3, 0, 3),
        (-8, 0, 2),
        (12, 0, -5),
        (-3, 0, -8),
        (7, 0, 15),
    ]

    for i, (x, y, z) in enumerate(mushroom_positions):
        world.add_entity(
            WDLEntity(
                name=f"GlowingMushroom_{i}",
                entity_type=EntityType.STATIC_MESH,
                transform=Transform(
                    position=Vector3(x=x, y=y, z=z),
                    scale=Vector3(x=0.3, y=0.4, z=0.3),
                ),
                material=Material(
                    name="GlowingMushroom",
                    material_type=MaterialType.EMISSIVE,
                    base_color=Color(r=0.2, g=0.8, b=0.6),
                    emission_color=Color(r=0.3, g=1.0, b=0.7),
                    emission_strength=2.0,
                ),
                tags=["vegetation", "mushroom", "glowing"],
                asset_reference="models/mushroom.fbx",
            )
        )

    # Add rocks
    rock_positions = [
        (8, 0, -3),
        (-12, 0, 8),
        (18, 0, 12),
    ]

    for i, (x, y, z) in enumerate(rock_positions):
        world.add_entity(
            WDLEntity(
                name=f"MossyRock_{i}",
                entity_type=EntityType.STATIC_MESH,
                transform=Transform(
                    position=Vector3(x=x, y=y, z=z),
                    rotation=Vector3(x=0, y=i * 60, z=0),
                    scale=Vector3(x=1.0 + i * 0.3, y=0.8 + i * 0.2, z=1.0 + i * 0.3),
                ),
                material=Material(
                    name="MossyRock",
                    material_type=MaterialType.PBR,
                    base_color=Color(r=0.35, g=0.35, b=0.3),
                    roughness=0.95,
                ),
                physics=PhysicsSettings(enabled=False, collision_enabled=True),
                tags=["prop", "rock", "static"],
                asset_reference="models/rock.fbx",
            )
        )

    # Add spawn point
    world.add_entity(
        WDLEntity(
            name="PlayerSpawn",
            entity_type=EntityType.SPAWN_POINT,
            transform=Transform(position=Vector3(x=0, y=1, z=0)),
            tags=["spawn", "player"],
        )
    )

    # Add sun/directional light
    world.add_light(
        Lighting(
            name="Sun",
            light_type=LightType.DIRECTIONAL,
            color=Color(r=1.0, g=0.9, b=0.7),
            intensity=0.6,
            cast_shadows=True,
            transform=Transform(rotation=Vector3(x=45, y=-30, z=0)),
        )
    )

    # Add ambient fill light
    world.add_light(
        Lighting(
            name="AmbientFill",
            light_type=LightType.AMBIENT,
            color=Color(r=0.2, g=0.25, b=0.2),
            intensity=0.3,
            cast_shadows=False,
        )
    )

    # Add point lights near mushrooms for glow effect
    for i, (x, y, z) in enumerate(mushroom_positions):
        world.add_light(
            Lighting(
                name=f"MushroomGlow_{i}",
                light_type=LightType.POINT,
                color=Color(r=0.3, g=1.0, b=0.7),
                intensity=0.5,
                range=5.0,
                cast_shadows=False,
                transform=Transform(position=Vector3(x=x, y=y + 0.5, z=z)),
            )
        )

    return world


# Create a standalone JSON file when run as script
if __name__ == "__main__":
    world = create_forest_world()
    print(world.to_json())
