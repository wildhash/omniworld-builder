"""
        Entity definitions for the generated world.
        Total entities: 3
        """

        import unreal
        from dataclasses import dataclass
        from typing import List, Optional


        @dataclass
        class EntityData:
            """Data class for entity information."""
            id: str
            name: str
            entity_type: str
            position: tuple
            rotation: tuple
            scale: tuple
            tags: List[str]
            asset_reference: Optional[str] = None


        ENTITY_DATA: List[EntityData] = [
            EntityData(
        id="f5f9254d-317f-41b0-9620-8d06f6551c3e",
        name="Ground",
        entity_type="terrain",
        position=(0.0, 0.0, 0.0),
        rotation=(0.0, 0.0, 0.0),
        scale=(50.0, 1.0, 50.0),
        tags=["terrain", "ground"],
        asset_reference=None
    ),
EntityData(
        id="fc25d648-1ad6-4987-bf33-db46b938b76b",
        name="CentralCube",
        entity_type="prop",
        position=(0.0, 2.0, 0.0),
        rotation=(0.0, 0.0, 0.0),
        scale=(2.0, 2.0, 2.0),
        tags=["prop", "interactive"],
        asset_reference=None
    ),
EntityData(
        id="1de4a1b6-283e-4c7b-ba47-df009294ea58",
        name="PlayerSpawn",
        entity_type="spawn_point",
        position=(0.0, 1.0, -10.0),
        rotation=(0.0, 0.0, 0.0),
        scale=(1.0, 1.0, 1.0),
        tags=["spawn"],
        asset_reference=None
    )
        ]


        def get_actor_class(entity_type: str):
            """Get the appropriate Unreal actor class for an entity type."""
            type_mapping = {
                "static_mesh": unreal.StaticMeshActor,
                "dynamic_object": unreal.Actor,
                "character": unreal.Character,
                "light": unreal.PointLight,
                "camera": unreal.CameraActor,
                "terrain": unreal.Landscape,
                "trigger": unreal.TriggerBox,
                "spawn_point": unreal.PlayerStart,
            }
            return type_mapping.get(entity_type, unreal.Actor)


        def spawn_entity(data: EntityData) -> unreal.Actor:
            """Spawn a single entity in the world."""
            actor_class = get_actor_class(data.entity_type)

            # Create spawn location
            location = unreal.Vector(data.position[0], data.position[1], data.position[2])
            rotation = unreal.Rotator(data.rotation[0], data.rotation[1], data.rotation[2])

            # Spawn the actor
            spawn_params = unreal.SpawnActorParameters()
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                actor_class,
                location,
                rotation
            )

            if actor:
                # Set name and scale
                actor.set_actor_label(data.name)
                actor.set_actor_scale3d(unreal.Vector(data.scale[0], data.scale[1], data.scale[2]))

                # Add tags
                for tag in data.tags:
                    actor.tags.append(tag)

            return actor


        def spawn_entities() -> List[unreal.Actor]:
            """Spawn all entities defined in ENTITY_DATA."""
            spawned = []
            for data in ENTITY_DATA:
                actor = spawn_entity(data)
                if actor:
                    spawned.append(actor)
                    unreal.log(f"Spawned: {data.name}")
                else:
                    unreal.log_warning(f"Failed to spawn: {data.name}")
            return spawned