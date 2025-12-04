"""WDL Validators for ensuring world integrity and consistency."""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

from omniworld_builder.core.wdl_schema import (
    EntityType,
    WDLWorld,
)


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a WDL world."""

    severity: ValidationSeverity
    message: str
    entity_id: str | None = None
    field_path: str | None = None


@dataclass
class ValidationResult:
    """Result of validating a WDL world."""

    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue."""
        self.issues.append(issue)
        if issue.severity == ValidationSeverity.ERROR:
            self.is_valid = False

    def get_errors(self) -> list[ValidationIssue]:
        """Get all error-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    def get_warnings(self) -> list[ValidationIssue]:
        """Get all warning-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]


class WDLValidator:
    """Validator for WDL worlds."""

    def __init__(self) -> None:
        """Initialize the validator with default rules."""
        self._rules: list[Callable[[WDLWorld], list[ValidationIssue]]] = [
            self._validate_unique_entity_ids,
            self._validate_parent_references,
            self._validate_entity_bounds,
            self._validate_light_settings,
            self._validate_system_references,
            self._validate_physics_settings,
        ]

    def validate(self, world: WDLWorld) -> ValidationResult:
        """Validate a WDL world against all rules."""
        result = ValidationResult(is_valid=True)

        for rule in self._rules:
            issues = rule(world)
            for issue in issues:
                result.add_issue(issue)

        return result

    def add_rule(self, rule: Callable[[WDLWorld], list[ValidationIssue]]) -> None:
        """Add a custom validation rule."""
        self._rules.append(rule)

    def _validate_unique_entity_ids(self, world: WDLWorld) -> list[ValidationIssue]:
        """Ensure all entity IDs are unique."""
        issues: list[ValidationIssue] = []
        seen_ids: set[str] = set()

        for entity in world.entities:
            if entity.id in seen_ids:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Duplicate entity ID: {entity.id}",
                        entity_id=entity.id,
                    )
                )
            seen_ids.add(entity.id)

        return issues

    def _validate_parent_references(self, world: WDLWorld) -> list[ValidationIssue]:
        """Ensure parent references point to existing entities."""
        issues: list[ValidationIssue] = []
        entity_ids = {entity.id for entity in world.entities}

        for entity in world.entities:
            if entity.parent_id is not None and entity.parent_id not in entity_ids:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Entity '{entity.name}' references non-existent parent: {entity.parent_id}",
                        entity_id=entity.id,
                        field_path="parent_id",
                    )
                )

        return issues

    def _validate_entity_bounds(self, world: WDLWorld) -> list[ValidationIssue]:
        """Check if entities are within world bounds."""
        issues: list[ValidationIssue] = []
        min_b = world.bounds.min_bounds
        max_b = world.bounds.max_bounds

        for entity in world.entities:
            pos = entity.transform.position
            if (
                pos.x < min_b.x
                or pos.x > max_b.x
                or pos.y < min_b.y
                or pos.y > max_b.y
                or pos.z < min_b.z
                or pos.z > max_b.z
            ):
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Entity '{entity.name}' is outside world bounds",
                        entity_id=entity.id,
                        field_path="transform.position",
                    )
                )

        return issues

    def _validate_light_settings(self, world: WDLWorld) -> list[ValidationIssue]:
        """Validate light configuration."""
        issues: list[ValidationIssue] = []

        for light in world.lights:
            if light.intensity > 100:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Light '{light.name}' has unusually high intensity: {light.intensity}",
                        field_path="intensity",
                    )
                )

        return issues

    def _validate_system_references(self, world: WDLWorld) -> list[ValidationIssue]:
        """Validate that systems reference existing entities."""
        issues: list[ValidationIssue] = []
        entity_ids = {entity.id for entity in world.entities}

        for system in world.systems:
            for interaction in system.interactions:
                if (
                    interaction.target_entity_id is not None
                    and interaction.target_entity_id not in entity_ids
                ):
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            message=f"System '{system.name}' references non-existent entity: {interaction.target_entity_id}",
                            field_path="interactions.target_entity_id",
                        )
                    )

        return issues

    def _validate_physics_settings(self, world: WDLWorld) -> list[ValidationIssue]:
        """Validate physics settings for entities."""
        issues: list[ValidationIssue] = []

        for entity in world.entities:
            if entity.physics.enabled and entity.physics.mass == 0:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Entity '{entity.name}' has physics enabled but zero mass",
                        entity_id=entity.id,
                        field_path="physics.mass",
                    )
                )

            # Check if dynamic objects have physics enabled
            if entity.entity_type == EntityType.DYNAMIC_OBJECT and not entity.physics.enabled:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        message=f"Dynamic object '{entity.name}' does not have physics enabled",
                        entity_id=entity.id,
                        field_path="physics.enabled",
                    )
                )

        return issues


def validate_wdl(world: WDLWorld) -> ValidationResult:
    """Convenience function to validate a WDL world."""
    validator = WDLValidator()
    return validator.validate(world)
