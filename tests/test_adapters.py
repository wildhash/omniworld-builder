"""Tests for the adapters."""

import tempfile

import pytest

from omniworld_builder.adapters import (
    HorizonGenerator,
    UnityGenerator,
    UnrealGenerator,
)
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


@pytest.fixture
def sample_world():
    """Create a sample world for testing."""
    world = WDLWorld(
        metadata=WDLMetadata(
            title="Test World",
            description="A test world for adapter testing",
            author="Test Author",
            version="1.0.0",
        )
    )

    world.add_entity(
        WDLEntity(
            name="Ground",
            entity_type=EntityType.TERRAIN,
            transform=Transform(scale=Vector3(x=100, y=1, z=100)),
        )
    )

    world.add_entity(
        WDLEntity(
            name="TestObject",
            entity_type=EntityType.STATIC_MESH,
            transform=Transform(position=Vector3(x=10, y=0, z=10)),
            tags=["test", "static"],
        )
    )

    world.add_light(
        Lighting(
            name="Sun",
            light_type=LightType.DIRECTIONAL,
            intensity=1.0,
            transform=Transform(rotation=Vector3(x=45, y=-30, z=0)),
        )
    )

    return world


class TestUnityGenerator:
    """Tests for UnityGenerator."""

    def test_platform_name(self):
        """Test platform name property."""
        generator = UnityGenerator()
        assert generator.platform_name == "unity"

    def test_file_extension(self):
        """Test file extension property."""
        generator = UnityGenerator()
        assert generator.file_extension == ".cs"

    def test_generate(self, sample_world):
        """Test code generation."""
        generator = UnityGenerator()
        files = generator.generate(sample_world)

        assert "Scripts/WorldLoader.cs" in files
        assert "Scripts/EntitySpawner.cs" in files
        assert "Scripts/EnvironmentController.cs" in files
        assert "Scripts/WorldData.cs" in files
        assert "Data/world_data.json" in files

    def test_world_loader_content(self, sample_world):
        """Test WorldLoader.cs content."""
        generator = UnityGenerator()
        files = generator.generate(sample_world)

        content = files["Scripts/WorldLoader.cs"]
        assert "namespace OmniWorld.Generated" in content
        assert "class WorldLoader" in content
        assert "Test World" in content

    def test_entity_spawner_content(self, sample_world):
        """Test EntitySpawner.cs content."""
        generator = UnityGenerator()
        files = generator.generate(sample_world)

        content = files["Scripts/EntitySpawner.cs"]
        assert "class EntitySpawner" in content
        assert "Ground" in content
        assert "TestObject" in content

    def test_save(self, sample_world):
        """Test saving generated files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = UnityGenerator(tmpdir)
            saved_files = generator.save(sample_world)

            assert len(saved_files) > 0
            for file_path in saved_files:
                assert file_path.exists()


class TestUnrealGenerator:
    """Tests for UnrealGenerator."""

    def test_platform_name(self):
        """Test platform name property."""
        generator = UnrealGenerator()
        assert generator.platform_name == "unreal"

    def test_file_extension(self):
        """Test file extension property."""
        generator = UnrealGenerator()
        assert generator.file_extension == ".py"

    def test_generate(self, sample_world):
        """Test code generation."""
        generator = UnrealGenerator()
        files = generator.generate(sample_world)

        assert "Scripts/world_builder.py" in files
        assert "Scripts/entity_definitions.py" in files
        assert "Scripts/environment_setup.py" in files
        assert "Scripts/lighting_setup.py" in files
        assert "Data/world_data.json" in files

    def test_world_builder_content(self, sample_world):
        """Test world_builder.py content."""
        generator = UnrealGenerator()
        files = generator.generate(sample_world)

        content = files["Scripts/world_builder.py"]
        assert "class WorldBuilder" in content
        assert "Test World" in content
        assert "import unreal" in content

    def test_entity_definitions_content(self, sample_world):
        """Test entity_definitions.py content."""
        generator = UnrealGenerator()
        files = generator.generate(sample_world)

        content = files["Scripts/entity_definitions.py"]
        assert "class EntityData" in content
        assert "Ground" in content
        assert "TestObject" in content

    def test_save(self, sample_world):
        """Test saving generated files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = UnrealGenerator(tmpdir)
            saved_files = generator.save(sample_world)

            assert len(saved_files) > 0
            for file_path in saved_files:
                assert file_path.exists()


class TestHorizonGenerator:
    """Tests for HorizonGenerator."""

    def test_platform_name(self):
        """Test platform name property."""
        generator = HorizonGenerator()
        assert generator.platform_name == "horizon"

    def test_file_extension(self):
        """Test file extension property."""
        generator = HorizonGenerator()
        assert generator.file_extension == ".ts"

    def test_generate(self, sample_world):
        """Test code generation."""
        generator = HorizonGenerator()
        files = generator.generate(sample_world)

        assert "scripts/WorldManager.ts" in files
        assert "scripts/EntityFactory.ts" in files
        assert "scripts/EnvironmentController.ts" in files
        assert "scripts/types.ts" in files
        assert "data/worldData.ts" in files
        assert "data/world_data.json" in files

    def test_world_manager_content(self, sample_world):
        """Test WorldManager.ts content."""
        generator = HorizonGenerator()
        files = generator.generate(sample_world)

        content = files["scripts/WorldManager.ts"]
        assert "class WorldManager" in content
        assert "Test World" in content
        assert "import" in content

    def test_entity_factory_content(self, sample_world):
        """Test EntityFactory.ts content."""
        generator = HorizonGenerator()
        files = generator.generate(sample_world)

        content = files["scripts/EntityFactory.ts"]
        assert "class EntityFactory" in content
        assert "Ground" in content
        assert "TestObject" in content

    def test_types_content(self, sample_world):
        """Test types.ts content."""
        generator = HorizonGenerator()
        files = generator.generate(sample_world)

        content = files["scripts/types.ts"]
        assert "interface Vector3" in content
        assert "interface Color" in content
        assert "enum EntityType" in content
        assert "enum LightType" in content

    def test_save(self, sample_world):
        """Test saving generated files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = HorizonGenerator(tmpdir)
            saved_files = generator.save(sample_world)

            assert len(saved_files) > 0
            for file_path in saved_files:
                assert file_path.exists()
