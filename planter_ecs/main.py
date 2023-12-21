import esper
import pygame as pg

from planter_ecs.components import (
    CurrentPlayer,
    Position,
    Resources,
    Sprite,
    Velocity,
    PlayerControlled,
)
from planter_ecs.extras import GameResources, TileMap
from planter_ecs.processors import (
    Grid,
    Movement,
    Physics,
    Planter,
    PlayerInput,
    PlayerMovement,
    Renderer,
    ResourceTimers,
    Time,
)


def main(width: int, height: int, include_renderer=True):
    pg.init()

    esper.add_processor(PlayerInput())
    esper.add_processor(Planter())

    esper.add_processor(Time())
    esper.add_processor(ResourceTimers())

    esper.add_processor(Grid())
    esper.add_processor(Physics())
    esper.add_processor(PlayerMovement())
    esper.add_processor(Movement())

    if include_renderer:
        esper.add_processor(Renderer(width, height))

    esper.create_entity(CurrentPlayer(), Resources())

    ent = esper.create_entity(
        PlayerControlled(),
        Position(128),
        Velocity(128),
    )

    if renderer := esper.get_processor(Renderer):
        res = GameResources()
        tile_map = TileMap(res.surfs["dirt"], 32)
        renderer.tile_map = tile_map

        esper.add_component(ent, Sprite(surface=res.surfs["green_circle"]))

    while True:
        esper.process()
