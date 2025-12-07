"""Example: Build a world from a natural language prompt.

This example demonstrates the end-to-end pipeline:
1. Take a natural language description
2. Use WorldBuilderOrchestrator with multi-agent system
3. Generate a WDLWorld
4. Save to JSON
"""

import asyncio
import json
from pathlib import Path

from omniworld_builder.agents.orchestrator import WorldBuilderOrchestrator


async def main():
    """Build a world from a prompt and save it."""
    print("=" * 60)
    print("OmniWorld Builder - Build World from Prompt Example")
    print("=" * 60)
    print()

    # Define the prompt
    prompt = "A small floating sky island with a tree, a shrine, and warm sunset light."
    print(f"Prompt: {prompt}")
    print()

    # Initialize orchestrator
    print("Initializing WorldBuilderOrchestrator...")
    orchestrator = WorldBuilderOrchestrator()
    print()

    # Build the world
    print("Building world (this may take a moment)...")
    try:
        world = await orchestrator.build_world(prompt=prompt, max_iterations=3)
        print("✓ World built successfully!")
        print()

        # Print world summary
        print("World Summary:")
        print(f"  Title: {world.metadata.title}")
        print(f"  Description: {world.metadata.description}")
        print(f"  Entities: {len(world.entities)}")
        print(f"  Lights: {len(world.lights)}")
        print(f"  Systems: {len(world.systems)}")
        print()

        # Save to JSON
        output_dir = Path("examples/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "sky_island_world.json"

        print(f"Saving to: {output_path}")
        json_data = world.to_json()

        with open(output_path, "w") as f:
            f.write(json_data)

        print("✓ World saved successfully!")
        print()

        # Print a preview of the JSON
        print("JSON Preview (first 500 chars):")
        print("-" * 60)
        print(json_data[:500] + "...")
        print("-" * 60)
        print()

        print("Example complete!")
        print(f"Output saved to: {output_path.absolute()}")

    except Exception as e:
        print(f"✗ Error building world: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
