"""Example: Sci-Fi Space Station World.

This example demonstrates creating a futuristic space station
with metallic materials, neon lighting, and interactive elements.
"""

from omniworld_builder.core.wdl_schema import (
    ActionType,
    Color,
    EntityType,
    Interaction,
    InteractionType,
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
    WDLSystem,
    WDLWorld,
    WeatherType,
)


def create_sci_fi_station() -> WDLWorld:
    """Create a sci-fi space station world.

    Returns:
        A WDLWorld representing a futuristic space station.
    """
    # Create metadata
    metadata = WDLMetadata(
        title="Orbital Station Alpha",
        description="A sleek futuristic space station with neon accents and advanced technology",
        author="OmniWorld Builder",
        version="1.0.0",
        tags=["sci-fi", "space", "station", "futuristic"],
        target_platforms=["unity", "unreal", "horizon"],
    )

    # Create environment settings (space environment)
    environment = WDLEnvironment(
        weather=WeatherType.CLEAR,
        time_of_day=TimeOfDay(hour=0, minute=0, day_night_cycle=False),
        ambient_light=Color(r=0.05, g=0.05, b=0.1),
        fog_enabled=False,
        skybox=SkyboxSettings(
            skybox_type="cubemap",
            texture_path="skyboxes/space_nebula.hdr",
            tint_color=Color(r=0.1, g=0.1, b=0.15),
            exposure=1.0,
        ),
        gravity=Vector3(x=0.0, y=-3.0, z=0.0),  # Lower gravity for space station
    )

    # Create the world
    world = WDLWorld(metadata=metadata, environment=environment)

    # Add main floor
    world.add_entity(
        WDLEntity(
            name="MainFloor",
            entity_type=EntityType.STATIC_MESH,
            transform=Transform(
                position=Vector3(x=0, y=0, z=0),
                scale=Vector3(x=50, y=0.5, z=50),
            ),
            material=Material(
                name="MetalFloor",
                material_type=MaterialType.PBR,
                base_color=Color(r=0.15, g=0.15, b=0.18),
                metallic=0.9,
                roughness=0.3,
            ),
            physics=PhysicsSettings(enabled=False, collision_enabled=True),
            tags=["structure", "floor"],
            asset_reference="models/floor_panel.fbx",
        )
    )

    # Add walls
    wall_configs = [
        {"name": "NorthWall", "pos": (0, 5, 25), "scale": (50, 10, 0.5)},
        {"name": "SouthWall", "pos": (0, 5, -25), "scale": (50, 10, 0.5)},
        {"name": "EastWall", "pos": (25, 5, 0), "scale": (0.5, 10, 50)},
        {"name": "WestWall", "pos": (-25, 5, 0), "scale": (0.5, 10, 50)},
    ]

    for wall in wall_configs:
        pos = wall["pos"]
        scale = wall["scale"]
        world.add_entity(
            WDLEntity(
                name=wall["name"],
                entity_type=EntityType.STATIC_MESH,
                transform=Transform(
                    position=Vector3(x=pos[0], y=pos[1], z=pos[2]),
                    scale=Vector3(x=scale[0], y=scale[1], z=scale[2]),
                ),
                material=Material(
                    name="MetalWall",
                    material_type=MaterialType.PBR,
                    base_color=Color(r=0.2, g=0.2, b=0.25),
                    metallic=0.85,
                    roughness=0.35,
                ),
                physics=PhysicsSettings(enabled=False, collision_enabled=True),
                tags=["structure", "wall"],
            )
        )

    # Add control consoles
    console_positions = [
        (10, 1, 0),
        (-10, 1, 0),
        (0, 1, 10),
        (0, 1, -10),
    ]

    for i, (x, y, z) in enumerate(console_positions):
        world.add_entity(
            WDLEntity(
                name=f"ControlConsole_{i}",
                entity_type=EntityType.PROP,
                transform=Transform(
                    position=Vector3(x=x, y=y, z=z),
                    rotation=Vector3(x=0, y=i * 90, z=0),
                    scale=Vector3(x=2, y=1.5, z=1),
                ),
                material=Material(
                    name="ConsoleMaterial",
                    material_type=MaterialType.PBR,
                    base_color=Color(r=0.1, g=0.1, b=0.12),
                    metallic=0.8,
                    roughness=0.2,
                ),
                tags=["prop", "interactive", "console"],
                asset_reference="models/control_console.fbx",
            )
        )

    # Add holographic display in center
    world.add_entity(
        WDLEntity(
            name="HolographicDisplay",
            entity_type=EntityType.PROP,
            transform=Transform(
                position=Vector3(x=0, y=2, z=0),
                scale=Vector3(x=3, y=3, z=3),
            ),
            material=Material(
                name="HologramMaterial",
                material_type=MaterialType.EMISSIVE,
                base_color=Color(r=0.0, g=0.5, b=1.0, a=0.5),
                emission_color=Color(r=0.2, g=0.6, b=1.0),
                emission_strength=3.0,
            ),
            tags=["prop", "hologram", "interactive"],
            asset_reference="models/hologram_globe.fbx",
        )
    )

    # Add crates/containers
    crate_positions = [
        (18, 0.75, 18),
        (18, 0.75, 16),
        (-18, 0.75, 18),
        (-18, 0.75, -18),
    ]

    for i, (x, y, z) in enumerate(crate_positions):
        world.add_entity(
            WDLEntity(
                name=f"CargoCrate_{i}",
                entity_type=EntityType.DYNAMIC_OBJECT,
                transform=Transform(
                    position=Vector3(x=x, y=y, z=z),
                    scale=Vector3(x=1.5, y=1.5, z=1.5),
                ),
                material=Material(
                    name="CrateMaterial",
                    material_type=MaterialType.PBR,
                    base_color=Color(r=0.4, g=0.35, b=0.2),
                    metallic=0.3,
                    roughness=0.7,
                ),
                physics=PhysicsSettings(
                    enabled=True, mass=50.0, use_gravity=True, collision_enabled=True
                ),
                tags=["prop", "moveable", "crate"],
                asset_reference="models/cargo_crate.fbx",
            )
        )

    # Add spawn point
    world.add_entity(
        WDLEntity(
            name="PlayerSpawn",
            entity_type=EntityType.SPAWN_POINT,
            transform=Transform(position=Vector3(x=0, y=1, z=-15)),
            tags=["spawn", "player"],
        )
    )

    # Add trigger zone for door
    world.add_entity(
        WDLEntity(
            name="DoorTrigger",
            entity_type=EntityType.TRIGGER,
            transform=Transform(
                position=Vector3(x=0, y=2, z=24),
                scale=Vector3(x=5, y=4, z=2),
            ),
            tags=["trigger", "door"],
        )
    )

    # Add main overhead light
    world.add_light(
        Lighting(
            name="MainLight",
            light_type=LightType.AREA,
            color=Color(r=0.9, g=0.95, b=1.0),
            intensity=2.0,
            cast_shadows=True,
            transform=Transform(
                position=Vector3(x=0, y=9, z=0),
                rotation=Vector3(x=90, y=0, z=0),
            ),
        )
    )

    # Add neon accent lights
    neon_configs = [
        {"name": "NeonBlue_1", "pos": (24, 3, 0), "color": (0.2, 0.5, 1.0)},
        {"name": "NeonBlue_2", "pos": (-24, 3, 0), "color": (0.2, 0.5, 1.0)},
        {"name": "NeonCyan_1", "pos": (0, 3, 24), "color": (0.2, 1.0, 0.8)},
        {"name": "NeonCyan_2", "pos": (0, 3, -24), "color": (0.2, 1.0, 0.8)},
    ]

    for neon in neon_configs:
        pos = neon["pos"]
        color = neon["color"]
        world.add_light(
            Lighting(
                name=neon["name"],
                light_type=LightType.POINT,
                color=Color(r=color[0], g=color[1], b=color[2]),
                intensity=1.5,
                range=15.0,
                cast_shadows=False,
                transform=Transform(position=Vector3(x=pos[0], y=pos[1], z=pos[2])),
            )
        )

    # Add hologram light
    world.add_light(
        Lighting(
            name="HologramLight",
            light_type=LightType.POINT,
            color=Color(r=0.2, g=0.6, b=1.0),
            intensity=2.0,
            range=8.0,
            cast_shadows=False,
            transform=Transform(position=Vector3(x=0, y=3, z=0)),
        )
    )

    # Add interactive system for console
    world.add_system(
        WDLSystem(
            name="ConsoleInteraction",
            description="Handles player interaction with control consoles",
            interactions=[
                Interaction(
                    trigger_type=InteractionType.CLICK,
                    action_type=ActionType.TRIGGER_EVENT,
                    parameters={"event_name": "console_activated"},
                ),
                Interaction(
                    trigger_type=InteractionType.PROXIMITY,
                    action_type=ActionType.ANIMATE,
                    parameters={"animation": "console_idle_highlight", "radius": 3.0},
                ),
            ],
            enabled=True,
            priority=1,
        )
    )

    # Add door system
    world.add_system(
        WDLSystem(
            name="DoorSystem",
            description="Automatic door that opens when player approaches",
            interactions=[
                Interaction(
                    trigger_type=InteractionType.PROXIMITY,
                    action_type=ActionType.ANIMATE,
                    target_entity_id=None,  # Would reference door entity
                    parameters={"animation": "door_open", "radius": 4.0},
                ),
            ],
            enabled=True,
            priority=2,
        )
    )

    return world


# Create a standalone JSON file when run as script
if __name__ == "__main__":
    world = create_sci_fi_station()
    print(world.to_json())
