"""Tests for the WDL validators."""

from omniworld_builder.core.validators import (
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    WDLValidator,
    validate_wdl,
)
from omniworld_builder.core.wdl_schema import (
    EntityType,
    Lighting,
    PhysicsSettings,
    Transform,
    Vector3,
    WDLEntity,
    WDLMetadata,
    WDLWorld,
)


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_initial_state(self):
        """Test initial validation result state."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert len(result.issues) == 0

    def test_add_error(self):
        """Test adding an error issue."""
        result = ValidationResult(is_valid=True)
        result.add_issue(
            ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Test error",
            )
        )
        assert result.is_valid is False
        assert len(result.get_errors()) == 1

    def test_add_warning(self):
        """Test adding a warning issue."""
        result = ValidationResult(is_valid=True)
        result.add_issue(
            ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Test warning",
            )
        )
        # Warnings don't invalidate
        assert result.is_valid is True
        assert len(result.get_warnings()) == 1


class TestWDLValidator:
    """Tests for WDLValidator."""

    def test_validate_empty_world(self):
        """Test validating an empty world."""
        world = WDLWorld(metadata=WDLMetadata(title="Empty"))
        validator = WDLValidator()
        result = validator.validate(world)
        assert result.is_valid is True

    def test_validate_duplicate_entity_ids(self):
        """Test detecting duplicate entity IDs."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))

        # Create two entities with same ID
        entity1 = WDLEntity(name="Entity1")
        entity2 = WDLEntity(name="Entity2")
        entity2.id = entity1.id  # Force duplicate ID

        world.add_entity(entity1)
        world.add_entity(entity2)

        validator = WDLValidator()
        result = validator.validate(world)

        assert result.is_valid is False
        assert any("Duplicate entity ID" in e.message for e in result.get_errors())

    def test_validate_invalid_parent_reference(self):
        """Test detecting invalid parent references."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))
        entity = WDLEntity(name="Child", parent_id="non-existent-id")
        world.add_entity(entity)

        validator = WDLValidator()
        result = validator.validate(world)

        assert result.is_valid is False
        assert any("non-existent parent" in e.message for e in result.get_errors())

    def test_validate_entity_out_of_bounds(self):
        """Test detecting entities outside world bounds."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))
        entity = WDLEntity(
            name="FarAway",
            transform=Transform(
                position=Vector3(x=10000, y=0, z=0)  # Beyond default bounds
            ),
        )
        world.add_entity(entity)

        validator = WDLValidator()
        result = validator.validate(world)

        # Should have warning about bounds
        assert any("outside world bounds" in w.message for w in result.get_warnings())

    def test_validate_high_light_intensity(self):
        """Test detecting unusually high light intensity."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))
        world.add_light(
            Lighting(
                name="BrightLight",
                intensity=200,  # Very high
            )
        )

        validator = WDLValidator()
        result = validator.validate(world)

        assert any("unusually high intensity" in w.message for w in result.get_warnings())

    def test_validate_physics_zero_mass(self):
        """Test detecting zero mass with physics enabled."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))
        entity = WDLEntity(
            name="ZeroMass",
            physics=PhysicsSettings(enabled=True, mass=0),
        )
        world.add_entity(entity)

        validator = WDLValidator()
        result = validator.validate(world)

        assert any("zero mass" in w.message for w in result.get_warnings())

    def test_validate_dynamic_without_physics(self):
        """Test detecting dynamic objects without physics."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))
        entity = WDLEntity(
            name="DynamicNoPhysics",
            entity_type=EntityType.DYNAMIC_OBJECT,
            physics=PhysicsSettings(enabled=False),
        )
        world.add_entity(entity)

        validator = WDLValidator()
        result = validator.validate(world)

        # Should have info about dynamic object without physics
        assert any(
            "does not have physics enabled" in i.message
            for i in result.issues
            if i.severity == ValidationSeverity.INFO
        )

    def test_add_custom_rule(self):
        """Test adding a custom validation rule."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))
        world.add_entity(WDLEntity(name="TestEntity"))

        def custom_rule(w):
            return [
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Custom rule triggered",
                )
            ]

        validator = WDLValidator()
        validator.add_rule(custom_rule)
        result = validator.validate(world)

        assert any("Custom rule triggered" in w.message for w in result.get_warnings())

    def test_validate_wdl_convenience_function(self):
        """Test the convenience validate_wdl function."""
        world = WDLWorld(metadata=WDLMetadata(title="Test"))
        result = validate_wdl(world)
        assert result.is_valid is True
