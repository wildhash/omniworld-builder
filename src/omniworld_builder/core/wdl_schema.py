"""World Description Language (WDL) Schema.

WDL is the core Intermediate Representation (IR) for describing 3D worlds
that can be translated to Unity, Unreal Engine, and Meta Horizon Worlds.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Vector3(BaseModel):
    """3D vector representation."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class Color(BaseModel):
    """RGBA color representation."""

    r: float = Field(ge=0.0, le=1.0, default=1.0)
    g: float = Field(ge=0.0, le=1.0, default=1.0)
    b: float = Field(ge=0.0, le=1.0, default=1.0)
    a: float = Field(ge=0.0, le=1.0, default=1.0)


class Transform(BaseModel):
    """Spatial transformation for entities."""

    position: Vector3 = Field(default_factory=Vector3)
    rotation: Vector3 = Field(default_factory=Vector3)
    scale: Vector3 = Field(default_factory=lambda: Vector3(x=1.0, y=1.0, z=1.0))


class MaterialType(str, Enum):
    """Supported material types."""

    STANDARD = "standard"
    PBR = "pbr"
    UNLIT = "unlit"
    TRANSPARENT = "transparent"
    EMISSIVE = "emissive"


class Material(BaseModel):
    """Material definition for visual appearance."""

    name: str
    material_type: MaterialType = MaterialType.STANDARD
    base_color: Color = Field(default_factory=Color)
    metallic: float = Field(ge=0.0, le=1.0, default=0.0)
    roughness: float = Field(ge=0.0, le=1.0, default=0.5)
    emission_color: Color | None = None
    emission_strength: float = Field(ge=0.0, default=0.0)
    texture_path: str | None = None
    normal_map_path: str | None = None


class LightType(str, Enum):
    """Supported light types."""

    DIRECTIONAL = "directional"
    POINT = "point"
    SPOT = "spot"
    AREA = "area"
    AMBIENT = "ambient"


class Lighting(BaseModel):
    """Light source definition."""

    name: str
    light_type: LightType = LightType.POINT
    color: Color = Field(default_factory=Color)
    intensity: float = Field(ge=0.0, default=1.0)
    range: float | None = None
    spot_angle: float | None = None
    cast_shadows: bool = True
    transform: Transform = Field(default_factory=Transform)


class EntityType(str, Enum):
    """Types of entities in the world."""

    STATIC_MESH = "static_mesh"
    DYNAMIC_OBJECT = "dynamic_object"
    CHARACTER = "character"
    PROP = "prop"
    TRIGGER = "trigger"
    SPAWN_POINT = "spawn_point"
    WAYPOINT = "waypoint"
    LIGHT = "light"
    CAMERA = "camera"
    AUDIO_SOURCE = "audio_source"
    PARTICLE_SYSTEM = "particle_system"
    TERRAIN = "terrain"


class PhysicsSettings(BaseModel):
    """Physics configuration for an entity."""

    enabled: bool = False
    is_kinematic: bool = False
    mass: float = Field(ge=0.0, default=1.0)
    drag: float = Field(ge=0.0, default=0.0)
    angular_drag: float = Field(ge=0.0, default=0.05)
    use_gravity: bool = True
    collision_enabled: bool = True


class ColliderType(str, Enum):
    """Types of collision shapes."""

    BOX = "box"
    SPHERE = "sphere"
    CAPSULE = "capsule"
    MESH = "mesh"
    CONVEX = "convex"


class Collider(BaseModel):
    """Collision shape definition."""

    collider_type: ColliderType = ColliderType.BOX
    is_trigger: bool = False
    center: Vector3 = Field(default_factory=Vector3)
    size: Vector3 = Field(default_factory=lambda: Vector3(x=1.0, y=1.0, z=1.0))
    radius: float | None = None
    height: float | None = None


class WDLEntity(BaseModel):
    """Entity definition in the world."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    entity_type: EntityType = EntityType.STATIC_MESH
    transform: Transform = Field(default_factory=Transform)
    material: Material | None = None
    physics: PhysicsSettings = Field(default_factory=PhysicsSettings)
    collider: Collider | None = None
    parent_id: str | None = None
    children_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    asset_reference: str | None = None
    prefab_reference: str | None = None


class WeatherType(str, Enum):
    """Weather condition types."""

    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"
    SNOWY = "snowy"
    FOGGY = "foggy"


class TimeOfDay(BaseModel):
    """Time of day configuration."""

    hour: int = Field(ge=0, le=23, default=12)
    minute: int = Field(ge=0, le=59, default=0)
    day_night_cycle: bool = False
    cycle_duration_seconds: float = Field(ge=0.0, default=3600.0)


class SkyboxSettings(BaseModel):
    """Skybox configuration."""

    skybox_type: str = "procedural"
    texture_path: str | None = None
    tint_color: Color = Field(default_factory=Color)
    exposure: float = Field(ge=0.0, default=1.0)
    rotation: float = 0.0


class WDLEnvironment(BaseModel):
    """Environment settings for the world."""

    weather: WeatherType = WeatherType.CLEAR
    time_of_day: TimeOfDay = Field(default_factory=TimeOfDay)
    ambient_light: Color = Field(default_factory=lambda: Color(r=0.2, g=0.2, b=0.2))
    fog_enabled: bool = False
    fog_color: Color = Field(default_factory=lambda: Color(r=0.5, g=0.5, b=0.5))
    fog_density: float = Field(ge=0.0, le=1.0, default=0.01)
    skybox: SkyboxSettings = Field(default_factory=SkyboxSettings)
    gravity: Vector3 = Field(default_factory=lambda: Vector3(x=0.0, y=-9.81, z=0.0))
    audio_reverb_preset: str | None = None


class InteractionType(str, Enum):
    """Types of interactions."""

    CLICK = "click"
    HOVER = "hover"
    COLLISION = "collision"
    PROXIMITY = "proximity"
    GRAB = "grab"
    USE = "use"


class ActionType(str, Enum):
    """Types of actions in response to interactions."""

    SPAWN = "spawn"
    DESTROY = "destroy"
    MOVE = "move"
    ROTATE = "rotate"
    ANIMATE = "animate"
    PLAY_SOUND = "play_sound"
    TRIGGER_EVENT = "trigger_event"
    SET_PROPERTY = "set_property"
    TELEPORT = "teleport"


class Interaction(BaseModel):
    """Interaction definition."""

    trigger_type: InteractionType
    action_type: ActionType
    target_entity_id: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)


class WDLSystem(BaseModel):
    """System definition for gameplay logic and mechanics."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    interactions: list[Interaction] = Field(default_factory=list)
    enabled: bool = True
    priority: int = 0
    conditions: dict[str, Any] = Field(default_factory=dict)


class WorldBounds(BaseModel):
    """World boundary definition."""

    min_bounds: Vector3 = Field(default_factory=lambda: Vector3(x=-1000.0, y=-100.0, z=-1000.0))
    max_bounds: Vector3 = Field(default_factory=lambda: Vector3(x=1000.0, y=500.0, z=1000.0))


class WDLMetadata(BaseModel):
    """Metadata for the WDL world."""

    title: str
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)
    target_platforms: list[str] = Field(default_factory=lambda: ["unity", "unreal", "horizon"])


class WDLWorld(BaseModel):
    """Root WDL world definition.

    This is the main schema for describing a complete 3D world that can be
    translated to various game engines and platforms.
    """

    metadata: WDLMetadata
    environment: WDLEnvironment = Field(default_factory=WDLEnvironment)
    entities: list[WDLEntity] = Field(default_factory=list)
    lights: list[Lighting] = Field(default_factory=list)
    systems: list[WDLSystem] = Field(default_factory=list)
    bounds: WorldBounds = Field(default_factory=WorldBounds)

    def add_entity(self, entity: WDLEntity) -> None:
        """Add an entity to the world."""
        self.entities.append(entity)

    def add_light(self, light: Lighting) -> None:
        """Add a light to the world."""
        self.lights.append(light)

    def add_system(self, system: WDLSystem) -> None:
        """Add a system to the world."""
        self.systems.append(system)

    def get_entity_by_id(self, entity_id: str) -> WDLEntity | None:
        """Get an entity by its ID."""
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        return None

    def get_entities_by_type(self, entity_type: EntityType) -> list[WDLEntity]:
        """Get all entities of a specific type."""
        return [e for e in self.entities if e.entity_type == entity_type]

    def get_entities_by_tag(self, tag: str) -> list[WDLEntity]:
        """Get all entities with a specific tag."""
        return [e for e in self.entities if tag in e.tags]

    def to_json(self) -> str:
        """Export the world to JSON format."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "WDLWorld":
        """Load a world from JSON format."""
        return cls.model_validate_json(json_str)
