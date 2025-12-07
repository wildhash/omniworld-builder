"""
        Lighting setup for the generated world.
        Total lights: 2
        """

        import unreal
        from dataclasses import dataclass
        from typing import List


        @dataclass
        class LightData:
            """Data class for light information."""
            name: str
            light_type: str
            color: tuple
            intensity: float
            position: tuple
            rotation: tuple
            cast_shadows: bool


        LIGHT_DATA: List[LightData] = [
            LightData(
        name="Sun",
        light_type="directional",
        color=(1.0, 1.0, 1.0),
        intensity=1.2,
        position=(0.0, 10.0, 0.0),
        rotation=(50.0, -30.0, 0.0),
        cast_shadows=True
    ),
LightData(
        name="AmbientLight",
        light_type="point",
        color=(1.0, 1.0, 1.0),
        intensity=0.5,
        position=(0.0, 5.0, 0.0),
        rotation=(0.0, 0.0, 0.0),
        cast_shadows=True
    )
        ]


        def get_light_class(light_type: str):
            """Get the appropriate Unreal light class."""
            type_mapping = {
                "directional": unreal.DirectionalLight,
                "point": unreal.PointLight,
                "spot": unreal.SpotLight,
                "area": unreal.RectLight,
            }
            return type_mapping.get(light_type, unreal.PointLight)


        def spawn_light(data: LightData) -> unreal.Actor:
            """Spawn a single light in the world."""
            light_class = get_light_class(data.light_type)

            location = unreal.Vector(data.position[0], data.position[1], data.position[2])
            rotation = unreal.Rotator(data.rotation[0], data.rotation[1], data.rotation[2])

            light_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                light_class,
                location,
                rotation
            )

            if light_actor:
                light_actor.set_actor_label(data.name)

                # Configure light component
                light_component = light_actor.get_component_by_class(unreal.LightComponent)
                if light_component:
                    light_component.set_intensity(data.intensity)
                    light_component.set_light_color(
                        unreal.LinearColor(data.color[0], data.color[1], data.color[2])
                    )
                    light_component.set_cast_shadows(data.cast_shadows)

            return light_actor


        def setup_lighting() -> List[unreal.Actor]:
            """Setup all lights defined in LIGHT_DATA."""
            unreal.log("Setting up lighting...")
            lights = []

            for data in LIGHT_DATA:
                light = spawn_light(data)
                if light:
                    lights.append(light)
                    unreal.log(f"Created light: {data.name}")

            unreal.log(f"Lighting setup complete: {len(lights)} lights created")
            return lights