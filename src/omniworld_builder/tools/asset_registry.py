"""Asset registry for managing and referencing 3D assets."""

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class AssetType(str, Enum):
    """Types of assets that can be registered."""

    MODEL_3D = "model_3d"
    TEXTURE = "texture"
    MATERIAL = "material"
    AUDIO = "audio"
    ANIMATION = "animation"
    PREFAB = "prefab"
    PARTICLE = "particle"
    SHADER = "shader"
    SCRIPT = "script"


class AssetPlatformInfo(BaseModel):
    """Platform-specific asset information."""

    path: str
    format: str
    optimized: bool = False
    lod_levels: int = 1


class Asset(BaseModel):
    """Represents a registered asset."""

    id: str
    name: str
    asset_type: AssetType
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    source_path: str | None = None
    thumbnail_path: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    platform_info: dict[str, AssetPlatformInfo] = Field(default_factory=dict)

    def get_platform_path(self, platform: str) -> str | None:
        """Get the asset path for a specific platform."""
        if platform in self.platform_info:
            return self.platform_info[platform].path
        return self.source_path

    def has_platform_support(self, platform: str) -> bool:
        """Check if the asset supports a specific platform."""
        return platform in self.platform_info


class AssetRegistry:
    """Registry for managing and querying 3D assets.

    The asset registry provides a centralized way to manage assets
    that can be referenced by WDL entities and exported to different
    game engine formats.
    """

    def __init__(self) -> None:
        """Initialize the asset registry."""
        self._assets: dict[str, Asset] = {}
        self._tags_index: dict[str, set[str]] = {}
        self._type_index: dict[AssetType, set[str]] = {}

    def register(self, asset: Asset) -> None:
        """Register a new asset.

        Args:
            asset: The asset to register.
        """
        self._assets[asset.id] = asset

        # Index by tags
        for tag in asset.tags:
            if tag not in self._tags_index:
                self._tags_index[tag] = set()
            self._tags_index[tag].add(asset.id)

        # Index by type
        if asset.asset_type not in self._type_index:
            self._type_index[asset.asset_type] = set()
        self._type_index[asset.asset_type].add(asset.id)

    def unregister(self, asset_id: str) -> bool:
        """Unregister an asset.

        Args:
            asset_id: The ID of the asset to unregister.

        Returns:
            True if the asset was unregistered, False if not found.
        """
        if asset_id not in self._assets:
            return False

        asset = self._assets[asset_id]

        # Remove from tag index
        for tag in asset.tags:
            if tag in self._tags_index:
                self._tags_index[tag].discard(asset_id)

        # Remove from type index
        if asset.asset_type in self._type_index:
            self._type_index[asset.asset_type].discard(asset_id)

        del self._assets[asset_id]
        return True

    def get(self, asset_id: str) -> Asset | None:
        """Get an asset by ID.

        Args:
            asset_id: The ID of the asset.

        Returns:
            The asset if found, None otherwise.
        """
        return self._assets.get(asset_id)

    def get_by_name(self, name: str) -> list[Asset]:
        """Get assets by name.

        Args:
            name: The name to search for.

        Returns:
            List of assets with matching name.
        """
        return [a for a in self._assets.values() if a.name == name]

    def get_by_tag(self, tag: str) -> list[Asset]:
        """Get all assets with a specific tag.

        Args:
            tag: The tag to search for.

        Returns:
            List of assets with the tag.
        """
        if tag not in self._tags_index:
            return []
        return [self._assets[aid] for aid in self._tags_index[tag] if aid in self._assets]

    def get_by_type(self, asset_type: AssetType) -> list[Asset]:
        """Get all assets of a specific type.

        Args:
            asset_type: The type to filter by.

        Returns:
            List of assets of the specified type.
        """
        if asset_type not in self._type_index:
            return []
        return [self._assets[aid] for aid in self._type_index[asset_type] if aid in self._assets]

    def search(
        self,
        query: str | None = None,
        asset_type: AssetType | None = None,
        tags: list[str] | None = None,
        platform: str | None = None,
    ) -> list[Asset]:
        """Search for assets with multiple criteria.

        Args:
            query: Text search in name and description.
            asset_type: Filter by asset type.
            tags: Filter by tags (AND logic).
            platform: Filter by platform support.

        Returns:
            List of matching assets.
        """
        results = list(self._assets.values())

        if query:
            query_lower = query.lower()
            results = [
                a
                for a in results
                if query_lower in a.name.lower() or query_lower in a.description.lower()
            ]

        if asset_type:
            results = [a for a in results if a.asset_type == asset_type]

        if tags:
            results = [a for a in results if all(t in a.tags for t in tags)]

        if platform:
            results = [a for a in results if a.has_platform_support(platform)]

        return results

    def list_all(self) -> list[Asset]:
        """List all registered assets.

        Returns:
            List of all assets.
        """
        return list(self._assets.values())

    def count(self) -> int:
        """Get the total number of registered assets.

        Returns:
            Number of registered assets.
        """
        return len(self._assets)

    def get_all_tags(self) -> list[str]:
        """Get all unique tags in the registry.

        Returns:
            List of all tags.
        """
        return list(self._tags_index.keys())

    def export_manifest(self) -> dict[str, Any]:
        """Export the registry as a manifest dictionary.

        Returns:
            Dictionary representation of all assets.
        """
        return {
            "assets": [a.model_dump() for a in self._assets.values()],
            "total_count": len(self._assets),
            "tags": self.get_all_tags(),
            "types": [t.value for t in self._type_index.keys()],
        }

    def import_manifest(self, manifest: dict[str, Any]) -> int:
        """Import assets from a manifest dictionary.

        Args:
            manifest: Dictionary containing asset data.

        Returns:
            Number of assets imported.
        """
        count = 0
        for asset_data in manifest.get("assets", []):
            try:
                asset = Asset.model_validate(asset_data)
                self.register(asset)
                count += 1
            except (ValueError, TypeError, KeyError):
                # Skip invalid asset data but continue importing others
                continue
        return count

    def save(self, path: str | Path) -> None:
        """Save the registry to a JSON file.

        Args:
            path: Path to save the registry.
        """
        import json

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.export_manifest(), f, indent=2)

    def load(self, path: str | Path) -> int:
        """Load the registry from a JSON file.

        Args:
            path: Path to load the registry from.

        Returns:
            Number of assets loaded.
        """
        import json

        path = Path(path)
        if not path.exists():
            return 0

        with open(path) as f:
            manifest = json.load(f)
        return self.import_manifest(manifest)
