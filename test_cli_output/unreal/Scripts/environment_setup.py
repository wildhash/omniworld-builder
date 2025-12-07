"""
Environment setup for the generated world.
"""

import unreal


# Environment configuration
ENVIRONMENT_CONFIG = {
    "weather": "clear",
    "time_hour": 12,
    "time_minute": 0,
    "day_night_cycle": False,
    "ambient_color": (0.2, 0.2, 0.2),
    "fog_enabled": False,
    "fog_color": (0.5, 0.5, 0.5),
    "fog_density": 0.01,
    "gravity": (0.0, -9.81, 0.0),
    "skybox_type": "procedural",
}


def setup_environment():
    """Configure the world environment settings."""
    unreal.log("Setting up environment...")

    # Get world settings
    world = unreal.EditorLevelLibrary.get_editor_world()
    if not world:
        unreal.log_error("No world found!")
        return

    # Setup fog
    if ENVIRONMENT_CONFIG["fog_enabled"]:
        setup_fog()

    # Setup sky
    setup_sky()

    unreal.log("Environment setup complete")


def setup_fog():
    """Configure exponential height fog."""
    fog_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.ExponentialHeightFog,
        unreal.Vector(0, 0, 0)
    )

    if fog_actor:
        fog_component = fog_actor.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if fog_component:
            fog_color = ENVIRONMENT_CONFIG["fog_color"]
            fog_component.set_fog_inscattering_color(
                unreal.LinearColor(fog_color[0], fog_color[1], fog_color[2])
            )
            fog_component.set_fog_density(ENVIRONMENT_CONFIG["fog_density"])


def setup_sky():
    """Configure sky atmosphere and clouds."""
    # Spawn sky atmosphere
    sky_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyAtmosphere,
        unreal.Vector(0, 0, 0)
    )

    if sky_actor:
        unreal.log("Sky atmosphere created")

    # Spawn sky light
    sky_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyLight,
        unreal.Vector(0, 0, 100)
    )

    if sky_light:
        sky_light_component = sky_light.get_component_by_class(unreal.SkyLightComponent)
        if sky_light_component:
            ambient = ENVIRONMENT_CONFIG["ambient_color"]
            sky_light_component.set_intensity(1.0)