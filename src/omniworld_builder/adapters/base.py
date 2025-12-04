"""Base adapter class for game engine code generators."""

from abc import ABC, abstractmethod
from pathlib import Path

from omniworld_builder.core.wdl_schema import WDLWorld


class BaseAdapter(ABC):
    """Base class for all game engine adapters."""

    def __init__(self, output_dir: str | Path) -> None:
        """Initialize the adapter.

        Args:
            output_dir: Directory to output generated files.
        """
        self.output_dir = Path(output_dir)

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Get the platform name for this adapter."""

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Get the file extension for generated code."""

    @abstractmethod
    def generate(self, world: WDLWorld) -> dict[str, str]:
        """Generate code from a WDL world.

        Args:
            world: The WDL world to generate code for.

        Returns:
            Dictionary mapping file paths to generated code content.
        """

    def save(self, world: WDLWorld) -> list[Path]:
        """Generate and save code files.

        Args:
            world: The WDL world to generate code for.

        Returns:
            List of paths to saved files.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        generated = self.generate(world)
        saved_files: list[Path] = []

        for file_path, content in generated.items():
            full_path = self.output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            saved_files.append(full_path)

        return saved_files
