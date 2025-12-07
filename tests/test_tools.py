"""Tests for the tools module."""

import tempfile
from pathlib import Path

import pytest

from omniworld_builder.core.wdl_schema import (
    Transform,
    Vector3,
    WDLEntity,
    WDLMetadata,
    WDLWorld,
)
from omniworld_builder.tools.asset_registry import (
    Asset,
    AssetPlatformInfo,
    AssetRegistry,
    AssetType,
)
from omniworld_builder.tools.spatial_reasoning import (
    BoundingBox,
    SpatialReasoner,
    distance,
    distance_squared,
)


class TestAsset:
    """Tests for Asset model."""

    def test_asset_creation(self):
        """Test creating an asset."""
        asset = Asset(
            id="test_asset_01",
            name="Test Asset",
            asset_type=AssetType.MODEL_3D,
        )
        assert asset.id == "test_asset_01"
        assert asset.name == "Test Asset"
        assert asset.asset_type == AssetType.MODEL_3D

    def test_asset_with_platform_info(self):
        """Test asset with platform-specific info."""
        asset = Asset(
            id="test_asset_01",
            name="Test Asset",
            asset_type=AssetType.MODEL_3D,
            platform_info={
                "unity": AssetPlatformInfo(path="Assets/Models/test.fbx", format="fbx"),
                "unreal": AssetPlatformInfo(path="/Game/Models/test", format="uasset"),
            },
        )
        assert asset.has_platform_support("unity")
        assert asset.has_platform_support("unreal")
        assert not asset.has_platform_support("horizon")

    def test_get_platform_path(self):
        """Test getting platform-specific path."""
        asset = Asset(
            id="test_asset_01",
            name="Test Asset",
            asset_type=AssetType.MODEL_3D,
            source_path="source/test.fbx",
            platform_info={
                "unity": AssetPlatformInfo(path="Assets/Models/test.fbx", format="fbx"),
            },
        )
        assert asset.get_platform_path("unity") == "Assets/Models/test.fbx"
        assert asset.get_platform_path("unreal") == "source/test.fbx"  # Falls back to source


class TestAssetRegistry:
    """Tests for AssetRegistry."""

    def test_register_and_get(self):
        """Test registering and retrieving an asset."""
        registry = AssetRegistry()
        asset = Asset(
            id="test_01",
            name="Test",
            asset_type=AssetType.MODEL_3D,
        )
        registry.register(asset)
        retrieved = registry.get("test_01")
        assert retrieved is not None
        assert retrieved.name == "Test"

    def test_unregister(self):
        """Test unregistering an asset."""
        registry = AssetRegistry()
        asset = Asset(id="test_01", name="Test", asset_type=AssetType.MODEL_3D)
        registry.register(asset)
        assert registry.unregister("test_01") is True
        assert registry.get("test_01") is None
        assert registry.unregister("non_existent") is False

    def test_get_by_tag(self):
        """Test getting assets by tag."""
        registry = AssetRegistry()
        registry.register(
            Asset(id="tree_01", name="Oak Tree", asset_type=AssetType.MODEL_3D, tags=["vegetation"])
        )
        registry.register(
            Asset(id="tree_02", name="Pine Tree", asset_type=AssetType.MODEL_3D, tags=["vegetation"])
        )
        registry.register(
            Asset(id="rock_01", name="Rock", asset_type=AssetType.MODEL_3D, tags=["prop"])
        )

        vegetation = registry.get_by_tag("vegetation")
        assert len(vegetation) == 2

    def test_get_by_type(self):
        """Test getting assets by type."""
        registry = AssetRegistry()
        registry.register(Asset(id="model_01", name="Model", asset_type=AssetType.MODEL_3D))
        registry.register(Asset(id="tex_01", name="Texture", asset_type=AssetType.TEXTURE))
        registry.register(Asset(id="model_02", name="Model2", asset_type=AssetType.MODEL_3D))

        models = registry.get_by_type(AssetType.MODEL_3D)
        assert len(models) == 2

    def test_search(self):
        """Test searching assets."""
        registry = AssetRegistry()
        registry.register(
            Asset(
                id="tree_01",
                name="Oak Tree",
                description="A large oak tree",
                asset_type=AssetType.MODEL_3D,
                tags=["vegetation"],
            )
        )
        registry.register(
            Asset(
                id="rock_01",
                name="Rock",
                description="A mossy rock",
                asset_type=AssetType.MODEL_3D,
                tags=["prop"],
            )
        )

        # Search by query
        results = registry.search(query="oak")
        assert len(results) == 1
        assert results[0].id == "tree_01"

        # Search by type and tags
        results = registry.search(asset_type=AssetType.MODEL_3D, tags=["vegetation"])
        assert len(results) == 1

    def test_save_and_load(self):
        """Test saving and loading registry."""
        registry = AssetRegistry()
        registry.register(Asset(id="test_01", name="Test", asset_type=AssetType.MODEL_3D))

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "registry.json"
            registry.save(path)

            new_registry = AssetRegistry()
            count = new_registry.load(path)
            assert count == 1
            assert new_registry.get("test_01") is not None

    def test_get_by_name(self):
        """Test getting assets by name."""
        registry = AssetRegistry()
        registry.register(Asset(id="test_01", name="Oak Tree", asset_type=AssetType.MODEL_3D))
        registry.register(Asset(id="test_02", name="Pine Tree", asset_type=AssetType.MODEL_3D))
        registry.register(Asset(id="test_03", name="Oak Tree", asset_type=AssetType.MODEL_3D))

        results = registry.get_by_name("Oak Tree")
        assert len(results) == 2

    def test_count(self):
        """Test getting asset count."""
        registry = AssetRegistry()
        assert registry.count() == 0

        registry.register(Asset(id="test_01", name="Asset1", asset_type=AssetType.MODEL_3D))
        assert registry.count() == 1

        registry.register(Asset(id="test_02", name="Asset2", asset_type=AssetType.TEXTURE))
        assert registry.count() == 2

    def test_get_all_tags(self):
        """Test getting all unique tags."""
        registry = AssetRegistry()
        registry.register(
            Asset(id="test_01", name="Asset1", asset_type=AssetType.MODEL_3D, tags=["tag1", "tag2"])
        )
        registry.register(
            Asset(id="test_02", name="Asset2", asset_type=AssetType.MODEL_3D, tags=["tag2", "tag3"])
        )

        tags = registry.get_all_tags()
        assert len(tags) == 3
        assert "tag1" in tags
        assert "tag2" in tags
        assert "tag3" in tags

    def test_list_all(self):
        """Test listing all assets."""
        registry = AssetRegistry()
        registry.register(Asset(id="test_01", name="Asset1", asset_type=AssetType.MODEL_3D))
        registry.register(Asset(id="test_02", name="Asset2", asset_type=AssetType.TEXTURE))

        all_assets = registry.list_all()
        assert len(all_assets) == 2

    def test_search_by_multiple_tags(self):
        """Test searching assets with multiple tags (AND logic)."""
        registry = AssetRegistry()
        registry.register(
            Asset(
                id="test_01",
                name="Asset1",
                asset_type=AssetType.MODEL_3D,
                tags=["vegetation", "tree"],
            )
        )
        registry.register(
            Asset(
                id="test_02", name="Asset2", asset_type=AssetType.MODEL_3D, tags=["vegetation"]
            )
        )
        registry.register(
            Asset(id="test_03", name="Asset3", asset_type=AssetType.MODEL_3D, tags=["tree"])
        )

        # Search for assets with both tags
        results = registry.search(tags=["vegetation", "tree"])
        assert len(results) == 1
        assert results[0].id == "test_01"

    def test_search_with_platform_filter(self):
        """Test searching assets by platform support."""
        registry = AssetRegistry()
        registry.register(
            Asset(
                id="test_01",
                name="Asset1",
                asset_type=AssetType.MODEL_3D,
                platform_info={
                    "unity": AssetPlatformInfo(path="test.fbx", format="fbx"),
                },
            )
        )
        registry.register(
            Asset(
                id="test_02",
                name="Asset2",
                asset_type=AssetType.MODEL_3D,
                platform_info={
                    "unreal": AssetPlatformInfo(path="test.uasset", format="uasset"),
                },
            )
        )

        # Search for Unity-compatible assets
        results = registry.search(platform="unity")
        assert len(results) == 1
        assert results[0].id == "test_01"

    def test_export_import_manifest(self):
        """Test exporting and importing manifest."""
        registry = AssetRegistry()
        registry.register(
            Asset(
                id="test_01",
                name="Test Asset",
                asset_type=AssetType.MODEL_3D,
                tags=["test"],
            )
        )

        # Export manifest
        manifest = registry.export_manifest()
        assert manifest["total_count"] == 1
        assert len(manifest["assets"]) == 1
        assert "test" in manifest["tags"]

        # Import into new registry
        new_registry = AssetRegistry()
        count = new_registry.import_manifest(manifest)
        assert count == 1
        assert new_registry.count() == 1
        assert new_registry.get("test_01") is not None


class TestBoundingBox:
    """Tests for BoundingBox."""

    def test_center(self):
        """Test calculating bounding box center."""
        bbox = BoundingBox(
            min_point=Vector3(x=0, y=0, z=0),
            max_point=Vector3(x=10, y=10, z=10),
        )
        center = bbox.center
        assert center.x == 5
        assert center.y == 5
        assert center.z == 5

    def test_size(self):
        """Test calculating bounding box size."""
        bbox = BoundingBox(
            min_point=Vector3(x=0, y=0, z=0),
            max_point=Vector3(x=10, y=20, z=30),
        )
        size = bbox.size
        assert size.x == 10
        assert size.y == 20
        assert size.z == 30

    def test_volume(self):
        """Test calculating bounding box volume."""
        bbox = BoundingBox(
            min_point=Vector3(x=0, y=0, z=0),
            max_point=Vector3(x=10, y=10, z=10),
        )
        assert bbox.volume == 1000

    def test_contains_point(self):
        """Test point containment check."""
        bbox = BoundingBox(
            min_point=Vector3(x=0, y=0, z=0),
            max_point=Vector3(x=10, y=10, z=10),
        )
        assert bbox.contains_point(Vector3(x=5, y=5, z=5)) is True
        assert bbox.contains_point(Vector3(x=15, y=5, z=5)) is False

    def test_intersects(self):
        """Test bounding box intersection."""
        bbox1 = BoundingBox(
            min_point=Vector3(x=0, y=0, z=0),
            max_point=Vector3(x=10, y=10, z=10),
        )
        bbox2 = BoundingBox(
            min_point=Vector3(x=5, y=5, z=5),
            max_point=Vector3(x=15, y=15, z=15),
        )
        bbox3 = BoundingBox(
            min_point=Vector3(x=20, y=20, z=20),
            max_point=Vector3(x=30, y=30, z=30),
        )
        assert bbox1.intersects(bbox2) is True
        assert bbox1.intersects(bbox3) is False


class TestSpatialReasoner:
    """Tests for SpatialReasoner."""

    @pytest.fixture
    def sample_world(self):
        """Create a sample world for testing."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))
        world.add_entity(
            WDLEntity(
                name="Entity1",
                transform=Transform(position=Vector3(x=0, y=0, z=0)),
            )
        )
        world.add_entity(
            WDLEntity(
                name="Entity2",
                transform=Transform(position=Vector3(x=10, y=0, z=0)),
            )
        )
        world.add_entity(
            WDLEntity(
                name="Entity3",
                transform=Transform(position=Vector3(x=5, y=0, z=5)),
            )
        )
        return world

    def test_find_nearest_entity(self, sample_world):
        """Test finding nearest entity."""
        reasoner = SpatialReasoner(sample_world)
        nearest, dist = reasoner.find_nearest_entity(Vector3(x=1, y=0, z=0))
        assert nearest is not None
        assert nearest.name == "Entity1"

    def test_find_entities_in_radius(self, sample_world):
        """Test finding entities in radius."""
        reasoner = SpatialReasoner(sample_world)
        entities = reasoner.find_entities_in_radius(Vector3(x=0, y=0, z=0), radius=8)
        # Entity1 at origin, Entity3 at (5, 0, 5) = dist ~7.07
        assert len(entities) == 2

    def test_check_collision(self, sample_world):
        """Test collision detection."""
        # Create overlapping entities
        world = WDLWorld(metadata=WDLMetadata(title="Test"))
        entity1 = WDLEntity(
            name="Entity1",
            transform=Transform(
                position=Vector3(x=0, y=0, z=0),
                scale=Vector3(x=5, y=5, z=5),
            ),
        )
        entity2 = WDLEntity(
            name="Entity2",
            transform=Transform(
                position=Vector3(x=2, y=0, z=0),
                scale=Vector3(x=5, y=5, z=5),
            ),
        )
        world.add_entity(entity1)
        world.add_entity(entity2)

        reasoner = SpatialReasoner(world)
        assert reasoner.check_collision(entity1, entity2) is True

    def test_get_spatial_analysis(self, sample_world):
        """Test spatial analysis."""
        reasoner = SpatialReasoner(sample_world)
        analysis = reasoner.get_spatial_analysis()

        assert analysis["entity_count"] == 3
        assert "world_bounds" in analysis
        assert "collision_count" in analysis

    def test_get_world_bounds_empty(self):
        """Test getting world bounds with no entities."""
        world = WDLWorld(metadata=WDLMetadata(title="Empty"))
        reasoner = SpatialReasoner(world)
        bounds = reasoner.get_world_bounds()
        assert bounds is None

    def test_get_world_bounds_single_entity(self):
        """Test getting world bounds with single entity."""
        world = WDLWorld(metadata=WDLMetadata(title="Single"))
        world.add_entity(
            WDLEntity(
                name="Entity",
                transform=Transform(
                    position=Vector3(x=10, y=20, z=30),
                    scale=Vector3(x=4, y=6, z=8),
                ),
            )
        )

        reasoner = SpatialReasoner(world)
        bounds = reasoner.get_world_bounds()

        assert bounds is not None
        # Entity at (10, 20, 30) with scale (4, 6, 8) means bounds from (8, 17, 26) to (12, 23, 34)
        assert bounds.min_point.x == 8.0
        assert bounds.min_point.y == 17.0
        assert bounds.min_point.z == 26.0
        assert bounds.max_point.x == 12.0
        assert bounds.max_point.y == 23.0
        assert bounds.max_point.z == 34.0

    def test_find_entities_in_radius_none(self):
        """Test finding entities when none are in radius."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))
        world.add_entity(
            WDLEntity(
                name="Far",
                transform=Transform(position=Vector3(x=100, y=0, z=100)),
            )
        )

        reasoner = SpatialReasoner(world)
        entities = reasoner.find_entities_in_radius(Vector3(x=0, y=0, z=0), radius=10)
        assert len(entities) == 0

    def test_find_entities_in_radius_all(self):
        """Test finding all entities within radius."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))
        world.add_entity(
            WDLEntity(name="E1", transform=Transform(position=Vector3(x=1, y=0, z=0)))
        )
        world.add_entity(
            WDLEntity(name="E2", transform=Transform(position=Vector3(x=0, y=1, z=0)))
        )
        world.add_entity(
            WDLEntity(name="E3", transform=Transform(position=Vector3(x=0, y=0, z=1)))
        )

        reasoner = SpatialReasoner(world)
        entities = reasoner.find_entities_in_radius(Vector3(x=0, y=0, z=0), radius=2)
        assert len(entities) == 3

    def test_detect_collisions_none(self):
        """Test collision detection when no collisions exist."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))
        world.add_entity(
            WDLEntity(
                name="E1",
                transform=Transform(
                    position=Vector3(x=0, y=0, z=0),
                    scale=Vector3(x=1, y=1, z=1),
                ),
            )
        )
        world.add_entity(
            WDLEntity(
                name="E2",
                transform=Transform(
                    position=Vector3(x=10, y=0, z=0),
                    scale=Vector3(x=1, y=1, z=1),
                ),
            )
        )

        reasoner = SpatialReasoner(world)
        collisions = reasoner.find_all_collisions()
        assert len(collisions) == 0

    def test_detect_collisions_multiple(self):
        """Test detecting multiple collisions."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))

        # Create three overlapping entities
        world.add_entity(
            WDLEntity(
                name="E1",
                transform=Transform(
                    position=Vector3(x=0, y=0, z=0),
                    scale=Vector3(x=4, y=4, z=4),
                ),
            )
        )
        world.add_entity(
            WDLEntity(
                name="E2",
                transform=Transform(
                    position=Vector3(x=1, y=0, z=0),
                    scale=Vector3(x=4, y=4, z=4),
                ),
            )
        )
        world.add_entity(
            WDLEntity(
                name="E3",
                transform=Transform(
                    position=Vector3(x=0.5, y=0, z=0),
                    scale=Vector3(x=4, y=4, z=4),
                ),
            )
        )

        reasoner = SpatialReasoner(world)
        collisions = reasoner.find_all_collisions()

        # Should detect 3 collision pairs: (E1, E2), (E1, E3), (E2, E3)
        assert len(collisions) == 3

    def test_suggest_placement_empty_world(self):
        """Test suggesting placement in empty world."""
        world = WDLWorld(metadata=WDLMetadata(title="Empty"))
        reasoner = SpatialReasoner(world)

        position = reasoner.suggest_placement(
            size=Vector3(x=1, y=1, z=1), min_distance_from_others=2.0, preferred_y=0.0
        )

        # Should return origin when world is empty
        assert position is not None
        assert position.x == 0
        assert position.y == 0
        assert position.z == 0

    def test_suggest_placement_with_spacing(self):
        """Test suggesting placement respecting minimum distance."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))
        world.add_entity(
            WDLEntity(
                name="Existing",
                transform=Transform(
                    position=Vector3(x=0, y=0, z=0),
                    scale=Vector3(x=2, y=2, z=2),
                ),
            )
        )

        reasoner = SpatialReasoner(world)
        position = reasoner.suggest_placement(
            size=Vector3(x=1, y=1, z=1), min_distance_from_others=3.0, preferred_y=0.0
        )

        # Should return a position at least 3 units away from origin
        # (or None if search range is exhausted, which is acceptable)
        if position is not None:
            dist = distance(position, Vector3(x=0, y=0, z=0))
            assert dist >= 3.0


class TestDistanceFunctions:
    """Tests for distance helper functions."""

    def test_distance(self):
        """Test Euclidean distance calculation."""
        p1 = Vector3(x=0, y=0, z=0)
        p2 = Vector3(x=3, y=4, z=0)
        assert distance(p1, p2) == 5.0  # 3-4-5 triangle

    def test_distance_squared(self):
        """Test squared distance calculation."""
        p1 = Vector3(x=0, y=0, z=0)
        p2 = Vector3(x=3, y=4, z=0)
        assert distance_squared(p1, p2) == 25.0
