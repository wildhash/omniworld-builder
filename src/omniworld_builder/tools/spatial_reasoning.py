"""Spatial reasoning utilities for world layout and entity placement."""

import math
from dataclasses import dataclass
from typing import Any

from omniworld_builder.core.wdl_schema import Vector3, WDLEntity, WDLWorld


@dataclass
class BoundingBox:
    """Axis-aligned bounding box for spatial calculations."""

    min_point: Vector3
    max_point: Vector3

    @property
    def center(self) -> Vector3:
        """Get the center point of the bounding box."""
        return Vector3(
            x=(self.min_point.x + self.max_point.x) / 2,
            y=(self.min_point.y + self.max_point.y) / 2,
            z=(self.min_point.z + self.max_point.z) / 2,
        )

    @property
    def size(self) -> Vector3:
        """Get the size of the bounding box."""
        return Vector3(
            x=self.max_point.x - self.min_point.x,
            y=self.max_point.y - self.min_point.y,
            z=self.max_point.z - self.min_point.z,
        )

    @property
    def volume(self) -> float:
        """Get the volume of the bounding box."""
        size = self.size
        return size.x * size.y * size.z

    def contains_point(self, point: Vector3) -> bool:
        """Check if a point is inside the bounding box."""
        return (
            self.min_point.x <= point.x <= self.max_point.x
            and self.min_point.y <= point.y <= self.max_point.y
            and self.min_point.z <= point.z <= self.max_point.z
        )

    def intersects(self, other: "BoundingBox") -> bool:
        """Check if this bounding box intersects with another."""
        return (
            self.min_point.x <= other.max_point.x
            and self.max_point.x >= other.min_point.x
            and self.min_point.y <= other.max_point.y
            and self.max_point.y >= other.min_point.y
            and self.min_point.z <= other.max_point.z
            and self.max_point.z >= other.min_point.z
        )

    def expand(self, amount: float) -> "BoundingBox":
        """Create an expanded bounding box."""
        return BoundingBox(
            min_point=Vector3(
                x=self.min_point.x - amount,
                y=self.min_point.y - amount,
                z=self.min_point.z - amount,
            ),
            max_point=Vector3(
                x=self.max_point.x + amount,
                y=self.max_point.y + amount,
                z=self.max_point.z + amount,
            ),
        )


def distance(p1: Vector3, p2: Vector3) -> float:
    """Calculate Euclidean distance between two points."""
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    dz = p2.z - p1.z
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def distance_squared(p1: Vector3, p2: Vector3) -> float:
    """Calculate squared Euclidean distance (faster, no sqrt)."""
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    dz = p2.z - p1.z
    return dx * dx + dy * dy + dz * dz


class SpatialReasoner:
    """Utility class for spatial reasoning and entity placement.

    Provides methods for analyzing spatial relationships between entities,
    calculating optimal placements, and validating spatial constraints.
    """

    def __init__(self, world: WDLWorld | None = None) -> None:
        """Initialize the spatial reasoner.

        Args:
            world: Optional WDL world to analyze.
        """
        self.world = world
        self._entity_bounds: dict[str, BoundingBox] = {}

    def set_world(self, world: WDLWorld) -> None:
        """Set or update the world to analyze."""
        self.world = world
        self._entity_bounds.clear()

    def get_entity_bounds(self, entity: WDLEntity) -> BoundingBox:
        """Get the bounding box for an entity.

        Args:
            entity: The entity to get bounds for.

        Returns:
            The entity's bounding box.
        """
        if entity.id in self._entity_bounds:
            return self._entity_bounds[entity.id]

        pos = entity.transform.position
        scale = entity.transform.scale

        # Calculate bounds based on position and scale
        half_size = Vector3(x=scale.x / 2, y=scale.y / 2, z=scale.z / 2)

        bounds = BoundingBox(
            min_point=Vector3(
                x=pos.x - half_size.x,
                y=pos.y - half_size.y,
                z=pos.z - half_size.z,
            ),
            max_point=Vector3(
                x=pos.x + half_size.x,
                y=pos.y + half_size.y,
                z=pos.z + half_size.z,
            ),
        )

        self._entity_bounds[entity.id] = bounds
        return bounds

    def get_world_bounds(self) -> BoundingBox | None:
        """Get the overall bounds of the world based on entities.

        Returns:
            Bounding box containing all entities, or None if no entities.
        """
        if not self.world or not self.world.entities:
            return None

        min_x = float("inf")
        min_y = float("inf")
        min_z = float("inf")
        max_x = float("-inf")
        max_y = float("-inf")
        max_z = float("-inf")

        for entity in self.world.entities:
            bounds = self.get_entity_bounds(entity)
            min_x = min(min_x, bounds.min_point.x)
            min_y = min(min_y, bounds.min_point.y)
            min_z = min(min_z, bounds.min_point.z)
            max_x = max(max_x, bounds.max_point.x)
            max_y = max(max_y, bounds.max_point.y)
            max_z = max(max_z, bounds.max_point.z)

        return BoundingBox(
            min_point=Vector3(x=min_x, y=min_y, z=min_z),
            max_point=Vector3(x=max_x, y=max_y, z=max_z),
        )

    def find_nearest_entity(self, position: Vector3) -> tuple[WDLEntity | None, float]:
        """Find the nearest entity to a given position.

        Args:
            position: The reference position.

        Returns:
            Tuple of (nearest entity, distance) or (None, inf).
        """
        if not self.world:
            return None, float("inf")

        nearest = None
        nearest_dist = float("inf")

        for entity in self.world.entities:
            dist = distance(position, entity.transform.position)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = entity

        return nearest, nearest_dist

    def find_entities_in_radius(self, center: Vector3, radius: float) -> list[WDLEntity]:
        """Find all entities within a radius of a point.

        Args:
            center: The center point.
            radius: The search radius.

        Returns:
            List of entities within the radius.
        """
        if not self.world:
            return []

        radius_sq = radius * radius
        return [
            e
            for e in self.world.entities
            if distance_squared(center, e.transform.position) <= radius_sq
        ]

    def find_entities_in_bounds(self, bounds: BoundingBox) -> list[WDLEntity]:
        """Find all entities within a bounding box.

        Args:
            bounds: The bounding box to search within.

        Returns:
            List of entities within the bounds.
        """
        if not self.world:
            return []

        return [e for e in self.world.entities if bounds.contains_point(e.transform.position)]

    def check_collision(self, entity1: WDLEntity, entity2: WDLEntity) -> bool:
        """Check if two entities collide (their bounds intersect).

        Args:
            entity1: First entity.
            entity2: Second entity.

        Returns:
            True if entities collide, False otherwise.
        """
        bounds1 = self.get_entity_bounds(entity1)
        bounds2 = self.get_entity_bounds(entity2)
        return bounds1.intersects(bounds2)

    def find_colliding_entities(self, entity: WDLEntity) -> list[WDLEntity]:
        """Find all entities that collide with a given entity.

        Args:
            entity: The entity to check collisions for.

        Returns:
            List of colliding entities.
        """
        if not self.world:
            return []

        return [
            e for e in self.world.entities if e.id != entity.id and self.check_collision(entity, e)
        ]

    def find_all_collisions(self) -> list[tuple[WDLEntity, WDLEntity]]:
        """Find all pairs of colliding entities in the world.

        Returns:
            List of tuples containing colliding entity pairs.
        """
        if not self.world:
            return []

        collisions = []
        entities = self.world.entities

        for i, entity1 in enumerate(entities):
            for entity2 in entities[i + 1 :]:
                if self.check_collision(entity1, entity2):
                    collisions.append((entity1, entity2))

        return collisions

    def suggest_placement(
        self,
        size: Vector3,
        min_distance_from_others: float = 1.0,
        preferred_y: float = 0.0,
    ) -> Vector3 | None:
        """Suggest a placement position for a new entity.

        Args:
            size: The size of the entity to place.
            min_distance_from_others: Minimum distance from existing entities.
            preferred_y: Preferred Y coordinate (height).

        Returns:
            Suggested position, or None if no valid position found.
        """
        if not self.world:
            return Vector3(x=0, y=preferred_y, z=0)

        world_bounds = self.get_world_bounds()
        if not world_bounds:
            return Vector3(x=0, y=preferred_y, z=0)

        # Try positions in a grid pattern
        search_range = max(world_bounds.size.x, world_bounds.size.z) * 2
        step = min_distance_from_others

        for r in range(int(search_range / step)):
            radius = r * step
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                x = radius * math.cos(rad)
                z = radius * math.sin(rad)
                candidate = Vector3(x=x, y=preferred_y, z=z)

                # Check if position is valid
                is_valid = True
                for entity in self.world.entities:
                    if distance(candidate, entity.transform.position) < min_distance_from_others:
                        is_valid = False
                        break

                if is_valid:
                    return candidate

        return None

    def calculate_density(self, region: BoundingBox) -> float:
        """Calculate entity density in a region.

        Args:
            region: The region to calculate density for.

        Returns:
            Number of entities per unit volume.
        """
        entities_in_region = self.find_entities_in_bounds(region)
        volume = region.volume
        if volume == 0:
            return 0
        return len(entities_in_region) / volume

    def get_spatial_analysis(self) -> dict[str, Any]:
        """Get a comprehensive spatial analysis of the world.

        Returns:
            Dictionary with spatial statistics and analysis.
        """
        if not self.world:
            return {"error": "No world set"}

        world_bounds = self.get_world_bounds()
        if not world_bounds:
            return {
                "entity_count": 0,
                "world_bounds": None,
                "collisions": [],
                "density": 0,
            }

        collisions = self.find_all_collisions()

        return {
            "entity_count": len(self.world.entities),
            "world_bounds": {
                "min": {
                    "x": world_bounds.min_point.x,
                    "y": world_bounds.min_point.y,
                    "z": world_bounds.min_point.z,
                },
                "max": {
                    "x": world_bounds.max_point.x,
                    "y": world_bounds.max_point.y,
                    "z": world_bounds.max_point.z,
                },
                "size": {
                    "x": world_bounds.size.x,
                    "y": world_bounds.size.y,
                    "z": world_bounds.size.z,
                },
                "volume": world_bounds.volume,
            },
            "collisions": [
                {"entity1": c[0].name, "entity2": c[1].name} for c in collisions
            ],
            "collision_count": len(collisions),
            "density": self.calculate_density(world_bounds),
        }
