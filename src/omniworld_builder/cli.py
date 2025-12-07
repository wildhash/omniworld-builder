"""Command-line interface for OmniWorld Builder.

This CLI provides commands for building worlds from prompts and exporting
to game engines.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from omniworld_builder.adapters.horizon import HorizonGenerator
from omniworld_builder.adapters.unity import UnityGenerator
from omniworld_builder.adapters.unreal import UnrealGenerator
from omniworld_builder.agents.orchestrator import WorldBuilderOrchestrator
from omniworld_builder.core.wdl_schema import WDLWorld


def cmd_build_from_prompt(args):
    """Build a world from a natural language prompt."""
    print(f"Building world from prompt: {args.prompt}")
    print()

    async def build():
        orchestrator = WorldBuilderOrchestrator()
        world = await orchestrator.build_world(
            prompt=args.prompt, max_iterations=args.max_iterations
        )
        return world

    try:
        world = asyncio.run(build())

        # Save to JSON
        output_path = Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        json_data = world.to_json()
        with open(output_path, "w") as f:
            f.write(json_data)

        print(f"✓ World built successfully!")
        print(f"  Title: {world.metadata.title}")
        print(f"  Entities: {len(world.entities)}")
        print(f"  Lights: {len(world.lights)}")
        print(f"  Systems: {len(world.systems)}")
        print()
        print(f"Saved to: {output_path.absolute()}")

        return 0
    except Exception as e:
        print(f"✗ Error building world: {e}", file=sys.stderr)
        return 1


def cmd_build_from_json(args):
    """Build engine code from a WDL JSON file."""
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"✗ Error: File not found: {input_path}", file=sys.stderr)
        return 1

    print(f"Loading world from: {input_path}")

    try:
        # Load the world
        with open(input_path) as f:
            json_data = f.read()
        world = WDLWorld.from_json(json_data)

        print(f"✓ World loaded: {world.metadata.title}")
        print(f"  Entities: {len(world.entities)}")
        print(f"  Lights: {len(world.lights)}")
        print(f"  Systems: {len(world.systems)}")
        print()

        # Setup output directories
        out_root = Path(args.out_root)
        unity_out = out_root / "unity"
        unreal_out = out_root / "unreal"
        horizon_out = out_root / "horizon"

        # Export to Unity
        if args.unity or args.all:
            print("Exporting to Unity...")
            unity_gen = UnityGenerator(unity_out)
            unity_gen.save(world)
            print(f"✓ Unity export: {unity_out.absolute()}")

        # Export to Unreal
        if args.unreal or args.all:
            print("Exporting to Unreal...")
            unreal_gen = UnrealGenerator(unreal_out)
            unreal_gen.save(world)
            print(f"✓ Unreal export: {unreal_out.absolute()}")

        # Export to Horizon
        if args.horizon or args.all:
            print("Exporting to Horizon...")
            horizon_gen = HorizonGenerator(horizon_out)
            horizon_gen.save(world)
            print(f"✓ Horizon export: {horizon_out.absolute()}")

        print()
        print("Export complete!")
        return 0

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="omniworld",
        description="OmniWorld Builder - AI-powered universal world builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build a world from a prompt
  omniworld build-from-prompt "A mystical forest with ancient trees" --out world.json

  # Export a world to all engines
  omniworld build-from-json world.json --out-root output/

  # Export to specific engines only
  omniworld build-from-json world.json --out-root output/ --unity --unreal
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # build-from-prompt command
    prompt_parser = subparsers.add_parser(
        "build-from-prompt",
        help="Build a world from a natural language prompt",
        description="Generate a WDL world using AI from a natural language description",
    )
    prompt_parser.add_argument("prompt", help="Natural language description of the world")
    prompt_parser.add_argument(
        "--out",
        default="output/world.json",
        help="Output JSON file path (default: output/world.json)",
    )
    prompt_parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum agent revision iterations (default: 5)",
    )

    # build-from-json command
    json_parser = subparsers.add_parser(
        "build-from-json",
        help="Export a WDL world to game engines",
        description="Generate engine-specific code from a WDL JSON file",
    )
    json_parser.add_argument("input", help="Input WDL JSON file path")
    json_parser.add_argument(
        "--out-root", default="output/", help="Output root directory (default: output/)"
    )
    json_parser.add_argument(
        "--unity", action="store_true", help="Export to Unity (C#)"
    )
    json_parser.add_argument(
        "--unreal", action="store_true", help="Export to Unreal Engine (Python)"
    )
    json_parser.add_argument(
        "--horizon", action="store_true", help="Export to Meta Horizon Worlds (TypeScript)"
    )
    json_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="Export to all engines (default if no specific engine specified)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute the appropriate command
    if args.command == "build-from-prompt":
        # If any specific engine is selected, disable --all default
        if hasattr(args, "unity") and (args.unity or args.unreal or args.horizon):
            args.all = False
        return cmd_build_from_prompt(args)
    elif args.command == "build-from-json":
        # If any specific engine is selected, disable --all default
        if args.unity or args.unreal or args.horizon:
            args.all = False
        return cmd_build_from_json(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
