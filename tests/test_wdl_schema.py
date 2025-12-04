"""Tests for the WDL schema."""

from omniworld_builder.core.wdl_schema import (
    Color,
    EntityType,
    Lighting,
    LightType,
    Material,
    MaterialType,
    PhysicsSettings,
    Transform,
    Vector3,
    WDLEntity,
    WDLEnvironment,
    WDLMetadata,
    WDLWorld,
    WeatherType,
)


class TestVector3:
    """Tests for Vector3 model."""

    def test_default_values(self):
        """Test Vector3 default values."""
        v = Vector3()
        assert v.x == 0.0
        assert v.y == 0.0
        assert v.z == 0.0

    def test_custom_values(self):
        """Test Vector3 with custom values."""
        v = Vector3(x=1.0, y=2.0, z=3.0)
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0


class TestColor:
    """Tests for Color model."""

    def test_default_values(self):
        """Test Color default values (white)."""
        c = Color()
        assert c.r == 1.0
        assert c.g == 1.0
        assert c.b == 1.0
        assert c.a == 1.0

    def test_color_validation(self):
        """Test Color value validation."""
        c = Color(r=0.5, g=0.5, b=0.5, a=0.5)
        assert c.r == 0.5
        assert c.g == 0.5


class TestTransform:
    """Tests for Transform model."""

    def test_default_transform(self):
        """Test default transform values."""
        t = Transform()
        assert t.position.x == 0.0
        assert t.rotation.x == 0.0
        assert t.scale.x == 1.0


class TestWDLEntity:
    """Tests for WDLEntity model."""

    def test_entity_creation(self):
        """Test creating an entity."""
        entity = WDLEntity(name="TestEntity")
        assert entity.name == "TestEntity"
        assert entity.entity_type == EntityType.STATIC_MESH
        assert entity.id is not None

    def test_entity_with_transform(self):
        """Test entity with custom transform."""
        entity = WDLEntity(
            name="TestEntity",
            transform=Transform(
                position=Vector3(x=10, y=20, z=30),
            ),
        )
        assert entity.transform.position.x == 10
        assert entity.transform.position.y == 20
        assert entity.transform.position.z == 30

    def test_entity_with_material(self):
        """Test entity with material."""
        material = Material(
            name="TestMaterial",
            material_type=MaterialType.PBR,
            base_color=Color(r=0.5, g=0.5, b=0.5),
        )
        entity = WDLEntity(name="TestEntity", material=material)
        assert entity.material is not None
        assert entity.material.name == "TestMaterial"

    def test_entity_with_physics(self):
        """Test entity with physics settings."""
        physics = PhysicsSettings(enabled=True, mass=10.0)
        entity = WDLEntity(name="TestEntity", physics=physics)
        assert entity.physics.enabled is True
        assert entity.physics.mass == 10.0

    def test_entity_tags(self):
        """Test entity tags."""
        entity = WDLEntity(name="TestEntity", tags=["tag1", "tag2"])
        assert "tag1" in entity.tags
        assert "tag2" in entity.tags


class TestWDLEnvironment:
    """Tests for WDLEnvironment model."""

    def test_default_environment(self):
        """Test default environment values."""
        env = WDLEnvironment()
        assert env.weather == WeatherType.CLEAR
        assert env.fog_enabled is False

    def test_environment_with_fog(self):
        """Test environment with fog enabled."""
        env = WDLEnvironment(fog_enabled=True, fog_density=0.05)
        assert env.fog_enabled is True
        assert env.fog_density == 0.05


class TestLighting:
    """Tests for Lighting model."""

    def test_default_light(self):
        """Test default light values."""
        light = Lighting(name="TestLight")
        assert light.name == "TestLight"
        assert light.light_type == LightType.POINT
        assert light.intensity == 1.0
        assert light.cast_shadows is True

    def test_directional_light(self):
        """Test directional light."""
        light = Lighting(
            name="Sun",
            light_type=LightType.DIRECTIONAL,
            intensity=1.5,
        )
        assert light.light_type == LightType.DIRECTIONAL
        assert light.intensity == 1.5


class TestWDLWorld:
    """Tests for WDLWorld model."""

    def test_world_creation(self):
        """Test creating a world."""
        metadata = WDLMetadata(title="TestWorld", description="A test world")
        world = WDLWorld(metadata=metadata)
        assert world.metadata.title == "TestWorld"
        assert len(world.entities) == 0
        assert len(world.lights) == 0

    def test_add_entity(self):
        """Test adding an entity to the world."""
        metadata = WDLMetadata(title="TestWorld")
        world = WDLWorld(metadata=metadata)
        entity = WDLEntity(name="TestEntity")
        world.add_entity(entity)
        assert len(world.entities) == 1
        assert world.entities[0].name == "TestEntity"

    def test_add_light(self):
        """Test adding a light to the world."""
        metadata = WDLMetadata(title="TestWorld")
        world = WDLWorld(metadata=metadata)
        light = Lighting(name="TestLight")
        world.add_light(light)
        assert len(world.lights) == 1
        assert world.lights[0].name == "TestLight"

    def test_get_entity_by_id(self):
        """Test getting an entity by ID."""
        metadata = WDLMetadata(title="TestWorld")
        world = WDLWorld(metadata=metadata)
        entity = WDLEntity(name="TestEntity")
        world.add_entity(entity)
        found = world.get_entity_by_id(entity.id)
        assert found is not None
        assert found.name == "TestEntity"

    def test_get_entities_by_type(self):
        """Test getting entities by type."""
        metadata = WDLMetadata(title="TestWorld")
        world = WDLWorld(metadata=metadata)
        world.add_entity(WDLEntity(name="Mesh1", entity_type=EntityType.STATIC_MESH))
        world.add_entity(WDLEntity(name="Light1", entity_type=EntityType.LIGHT))
        world.add_entity(WDLEntity(name="Mesh2", entity_type=EntityType.STATIC_MESH))

        meshes = world.get_entities_by_type(EntityType.STATIC_MESH)
        assert len(meshes) == 2

    def test_get_entities_by_tag(self):
        """Test getting entities by tag."""
        metadata = WDLMetadata(title="TestWorld")
        world = WDLWorld(metadata=metadata)
        world.add_entity(WDLEntity(name="Entity1", tags=["vegetation"]))
        world.add_entity(WDLEntity(name="Entity2", tags=["structure"]))
        world.add_entity(WDLEntity(name="Entity3", tags=["vegetation"]))

        vegetation = world.get_entities_by_tag("vegetation")
        assert len(vegetation) == 2

    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        metadata = WDLMetadata(title="TestWorld", description="A test")
        world = WDLWorld(metadata=metadata)
        world.add_entity(WDLEntity(name="TestEntity"))

        json_str = world.to_json()
        assert "TestWorld" in json_str
        assert "TestEntity" in json_str

        # Deserialize
        loaded = WDLWorld.from_json(json_str)
        assert loaded.metadata.title == "TestWorld"
        assert len(loaded.entities) == 1
