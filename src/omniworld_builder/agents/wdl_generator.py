"""WDL Generator Agent for creating WDL schema from agent outputs."""

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from omniworld_builder.agents.base import AgentState, BaseAgent
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


class WDLGeneratorAgent(BaseAgent):
    """Agent responsible for generating WDL schema from all agent outputs.

    The WDL Generator synthesizes all previous agent outputs into a valid
    WDL world definition that can be exported to various game engines.
    """

    def __init__(self, model_name: str = "claude-sonnet-4-20250514") -> None:
        """Initialize the WDL Generator agent."""
        super().__init__(name="WDLGenerator", model_name=model_name)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the WDL Generator."""
        return """You are the WDL Generator, an expert in creating structured world definitions.
Your role is to synthesize all design outputs into a World Description Language (WDL) format.

You must create a structured JSON output that follows the WDL schema with:
1. metadata: Title, description, author, version, tags, target platforms
2. environment: Weather, time of day, ambient light, fog, skybox, gravity
3. entities: List of all entities with transforms, materials, physics, tags
4. lights: List of all light sources with types, colors, intensities
5. systems: List of interactive systems with triggers and actions

Each entity needs:
- name, entity_type, transform (position, rotation, scale)
- material (if applicable), physics settings, tags

Use the technical specifications for asset references and hierarchy.
Use the systems design for interactive elements.
Use the visual concept for materials and lighting.

Output ONLY valid JSON following the WDL schema."""

    async def process(self, state: AgentState) -> AgentState:
        """Process all agent outputs to generate WDL.

        Args:
            state: The current agent state with all previous outputs.

        Returns:
            Updated state with WDL output.
        """
        context = f"""
User Request: {state.user_prompt}

Visual Concept:
{state.vision_output}

Systems Design:
{state.systems_output}

Technical Specifications:
{state.technical_output}

Generate a complete WDL world definition that synthesizes all these inputs.
Include appropriate entities, lights, materials, and systems based on the designs.
"""
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=context),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            wdl_data = self._parse_response(response.content)
            # Convert the raw data to proper WDL objects
            wdl_world = self._create_wdl_world(wdl_data, state)
            state.wdl_output = {"wdl_world": wdl_world.model_dump(), "raw_data": wdl_data}
            state.current_stage = "wdl_complete"
        except Exception as e:
            state.errors.append(f"WDLGenerator error: {str(e)}")
            wdl_world = self._create_default_world(state)
            state.wdl_output = {"wdl_world": wdl_world.model_dump(), "raw_data": {}}

        return state

    def _parse_response(self, content: str) -> dict[str, Any]:
        """Parse the LLM response into structured output."""
        import json

        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content.strip())
        except json.JSONDecodeError:
            return {}

    def _create_wdl_world(self, data: dict[str, Any], state: AgentState) -> WDLWorld:
        """Create a WDLWorld from parsed data."""
        # Extract metadata
        metadata_data = data.get("metadata", {})
        metadata = WDLMetadata(
            title=metadata_data.get("title", state.user_prompt[:50]),
            description=metadata_data.get("description", state.user_prompt),
            author=metadata_data.get("author", "OmniWorld Builder"),
            version=metadata_data.get("version", "1.0.0"),
            tags=metadata_data.get("tags", []),
            target_platforms=metadata_data.get("target_platforms", ["unity", "unreal", "horizon"]),
        )

        # Extract environment
        env_data = data.get("environment", {})
        vision = state.vision_output

        weather_str = env_data.get("weather", "clear").lower()
        weather = WeatherType.CLEAR
        for w in WeatherType:
            if w.value == weather_str:
                weather = w
                break

        environment = WDLEnvironment(
            weather=weather,
            time_of_day=TimeOfDay(
                hour=env_data.get("time_of_day", {}).get("hour", 12),
                minute=env_data.get("time_of_day", {}).get("minute", 0),
            ),
            fog_enabled=env_data.get("fog_enabled", False),
            skybox=SkyboxSettings(
                skybox_type=env_data.get("skybox", {}).get("type", "procedural"),
            ),
        )

        # Apply vision mood to lighting
        if vision.get("mood") == "serene":
            environment.ambient_light = Color(r=0.3, g=0.35, b=0.4)
        elif vision.get("mood") == "ominous":
            environment.ambient_light = Color(r=0.15, g=0.12, b=0.18)

        # Create world
        world = WDLWorld(metadata=metadata, environment=environment)

        # Add entities from data
        entities_data = data.get("entities", [])
        for entity_data in entities_data:
            entity = self._create_entity(entity_data)
            world.add_entity(entity)

        # Add lights from data
        lights_data = data.get("lights", [])
        for light_data in lights_data:
            light = self._create_light(light_data)
            world.add_light(light)

        # Add default sun light if no lights defined
        if not world.lights:
            world.add_light(
                Lighting(
                    name="Sun",
                    light_type=LightType.DIRECTIONAL,
                    color=Color(r=1.0, g=0.95, b=0.9),
                    intensity=1.0,
                    transform=Transform(rotation=Vector3(x=50, y=-30, z=0)),
                )
            )

        return world

    def _create_entity(self, data: dict[str, Any]) -> WDLEntity:
        """Create a WDLEntity from data."""
        entity_type_str = data.get("entity_type", "static_mesh")
        entity_type = EntityType.STATIC_MESH
        for et in EntityType:
            if et.value == entity_type_str:
                entity_type = et
                break

        transform_data = data.get("transform", {})
        pos = transform_data.get("position", {})
        rot = transform_data.get("rotation", {})
        scale = transform_data.get("scale", {})

        transform = Transform(
            position=Vector3(x=pos.get("x", 0), y=pos.get("y", 0), z=pos.get("z", 0)),
            rotation=Vector3(x=rot.get("x", 0), y=rot.get("y", 0), z=rot.get("z", 0)),
            scale=Vector3(x=scale.get("x", 1), y=scale.get("y", 1), z=scale.get("z", 1)),
        )

        material = None
        if "material" in data:
            mat_data = data["material"]
            material = Material(
                name=mat_data.get("name", "default"),
                material_type=MaterialType.STANDARD,
            )

        physics_data = data.get("physics", {})
        physics = PhysicsSettings(
            enabled=physics_data.get("enabled", False),
            mass=physics_data.get("mass", 1.0),
            use_gravity=physics_data.get("use_gravity", True),
        )

        return WDLEntity(
            name=data.get("name", "Entity"),
            entity_type=entity_type,
            transform=transform,
            material=material,
            physics=physics,
            tags=data.get("tags", []),
            asset_reference=data.get("asset_reference"),
        )

    def _create_light(self, data: dict[str, Any]) -> Lighting:
        """Create a Lighting from data."""
        light_type_str = data.get("light_type", "point")
        light_type = LightType.POINT
        for lt in LightType:
            if lt.value == light_type_str:
                light_type = lt
                break

        color_data = data.get("color", {})
        color = Color(
            r=color_data.get("r", 1.0),
            g=color_data.get("g", 1.0),
            b=color_data.get("b", 1.0),
        )

        transform_data = data.get("transform", {})
        pos = transform_data.get("position", {})
        rot = transform_data.get("rotation", {})

        return Lighting(
            name=data.get("name", "Light"),
            light_type=light_type,
            color=color,
            intensity=data.get("intensity", 1.0),
            cast_shadows=data.get("cast_shadows", True),
            transform=Transform(
                position=Vector3(x=pos.get("x", 0), y=pos.get("y", 0), z=pos.get("z", 0)),
                rotation=Vector3(x=rot.get("x", 0), y=rot.get("y", 0), z=rot.get("z", 0)),
            ),
        )

    def _create_default_world(self, state: AgentState) -> WDLWorld:
        """Create a default WDL world on error."""
        metadata = WDLMetadata(
            title=state.user_prompt[:50] if state.user_prompt else "New World",
            description=state.user_prompt or "A new world created with OmniWorld Builder",
            author="OmniWorld Builder",
        )

        environment = WDLEnvironment()

        world = WDLWorld(metadata=metadata, environment=environment)

        # Add default ground plane
        world.add_entity(
            WDLEntity(
                name="Ground",
                entity_type=EntityType.TERRAIN,
                transform=Transform(scale=Vector3(x=100, y=1, z=100)),
            )
        )

        # Add default sun
        world.add_light(
            Lighting(
                name="Sun",
                light_type=LightType.DIRECTIONAL,
                intensity=1.0,
                transform=Transform(rotation=Vector3(x=50, y=-30, z=0)),
            )
        )

        return world
