from __future__ import annotations

import sys

import esper
import glm
import pygame as pg
from glm import vec2

from planter_ecs.components import (
    Acceleration,
    AddResource,
    CurrentPlayer,
    Position,
    Resources,
    ResourceTimer,
    Sprite,
    Velocity,
    PlayerControlled,
)
from planter_ecs.extras import GameResources

# ==============================
# PROCESSORS


class Time(esper.Processor):
    def __init__(self):
        self.clock = pg.time.Clock()
        self.dt = 0.0
        self.fps = 0.0

    def process(self):
        self.dt = self.clock.tick(60) * 0.001
        self.fps = self.clock.get_fps()
        pg.display.set_caption(f"{self.fps:0.2f}")


class PlayerInput(esper.Processor):
    def __init__(self):
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False
        self.mpos = vec2()
        self.left_click = False

    def process(self):
        self.reset()

        for event in pg.event.get():
            if event.type == pg.QUIT or (
                event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
            ):
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.left_click = event.button == 1

        keys = pg.key.get_pressed()

        self.move_left = keys[pg.K_a]
        self.move_right = keys[pg.K_d]
        self.move_up = keys[pg.K_w]
        self.move_down = keys[pg.K_s]

        self.mpos = vec2(pg.mouse.get_pos())

    def reset(self):
        self.left_click = False


class Grid(esper.Processor):
    def __init__(self, cell_size: int = 32):
        self.cell_size = cell_size
        self.cells = {}

    def process(self):
        self.cells = {}
        for ent, pos in esper.get_component(Position):
            key = tuple(map(lambda i: int(i) // self.cell_size, pos))
            self.cells.setdefault(key, []).append(ent)

    def query(self, pos):
        key = tuple(map(lambda i: int(i) // self.cell_size, pos))
        return self.cells.get(key, [])

    def query_rect(self, pos, size):
        entities = set()
        for x in range(pos.x // self.cell_size, (pos.x + size.x) // self.cell_size):
            for y in range(pos.y // self.cell_size, (pos.y + size.y) // self.cell_size):
                entities.update(self.cells.get((x, y), []))
        return entities


class Renderer(esper.Processor):
    def __init__(self, width: int, height: int):
        self.window = pg.display.set_mode((width, height))
        self.win_size = vec2(width, height)
        self.tile_map = None
        self.font = pg.font.SysFont(pg.font.get_default_font(), 48)
        self.res = GameResources()

    def process(self):
        self.window.fill((30, 20, 20))

        if self.tile_map:
            tile_size = self.tile_map.tile_size
            for y, row in enumerate(self.tile_map.tiles):
                for x, tile in enumerate(row):
                    self.window.blit(tile, (x * tile_size, y * tile_size))

        for _, (pos, spr) in esper.get_components(Position, Sprite):
            self.window.blit(spr.surface, (pos - (spr.size * 0.5)).to_list())

        for _, (pos, res) in esper.get_components(Position, ResourceTimer):
            # draw a progress bar
            progress = res.time / res.timeout
            surf = pg.Surface((32, 4))
            surf.fill((0, 0, 0))
            surf.fill((255, 255, 255), (0, 0, 32 * progress, 4))
            self.window.blit(surf, (pos + (-16, 16)).to_list())

        for _, res in esper.get_component(Resources):
            shadow = self.font.render(f"{res.r1}", True, (0, 0, 0))
            self.window.blit(shadow, (18, 18))
            string = self.font.render(f"{res.r1}", True, (255, 255, 255))
            self.window.blit(string, (16, 16))

        pg.display.update()


class PlayerMovement(esper.Processor):
    def __init__(self):
        self.input = esper.get_processor(PlayerInput)
        assert (
            self.input
        ), "PlayerInput processor must be added before PlayerMovement processor"

    def process(self):
        for _, (vel, _) in esper.get_components(Velocity, PlayerControlled):
            direction = vec2()
            if self.input.move_left:
                direction += vec2(-1, 0)
            if self.input.move_right:
                direction += vec2(1, 0)
            if self.input.move_up:
                direction += vec2(0, -1)
            if self.input.move_down:
                direction += vec2(0, 1)
            if not direction == vec2():
                norm = glm.normalize(direction)
                vel += norm * 20


class Planter(esper.Processor):
    def __init__(self):
        self.input = esper.get_processor(PlayerInput)
        assert (
            self.input
        ), "PlayerInput processor must be added before Planter processor"

    def process(self):
        if self.input.left_click:
            print("planter clicked")
            renderer = esper.get_processor(Renderer)
            for ent, _ in esper.get_component(CurrentPlayer):
                new_ent = esper.create_entity(
                    ResourceTimer(
                        owner=ent,
                        timeout=3.0,
                        repeat=True,
                        resource="r1",
                        amount=10,
                    ),
                    Position(self.input.mpos),
                )
                if renderer:
                    esper.add_component(
                        new_ent, Sprite(surface=renderer.res.surfs["cog"])
                    )


class Movement(esper.Processor):
    def __init__(self):
        self.time = esper.get_processor(Time)
        assert self.time, "Time processor must be added before Movement processor"

    def process(self):
        for _, (pos, vel) in esper.get_components(Position, Velocity):
            pos += vel * self.time.dt
            vel *= 0.9


class Physics(esper.Processor):
    def __init__(self):
        self.time = esper.get_processor(Time)
        assert self.time, "Time processor must be added before Physics processor"

    def process(self):
        for _, (vel, acc) in esper.get_components(Velocity, Acceleration):
            vel += acc * self.time.dt
            acc *= 0.0


class ResourceTimers(esper.Processor):
    def __init__(self):
        self.time = esper.get_processor(Time)
        assert self.time, "Time processor must be added before ResourceTimers processor"

    def process(self):
        for ent, timer in esper.get_component(ResourceTimer):
            if not timer.paused:
                timer.time += self.time.dt
                if timer.time >= timer.timeout:
                    esper.add_component(
                        timer.owner,
                        AddResource(
                            owner=timer.owner, kind=timer.resource, amount=timer.amount
                        ),
                    )
                    if timer.repeat:
                        timer.time = 0
                    else:
                        esper.remove_component(ent, ResourceTimer)

        for ent, add in esper.get_component(AddResource):
            if res := esper.component_for_entity(ent, Resources):
                res[add.kind] += add.amount
                esper.remove_component(ent, AddResource)
                print(res)
