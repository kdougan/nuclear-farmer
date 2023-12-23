from __future__ import annotations

from dataclasses import field, dataclass
from typing import Callable
from typing import Union

from glm import vec2
from pygame import Surface

# ==============================
# COMPONENTS


class Position(vec2):
    pass


class Velocity(vec2):
    pass


class Acceleration(vec2):
    pass


@dataclass
class Timer:
    timeout: float
    time: float = 0.0
    paused: bool = False
    repeat: bool = False


@dataclass(kw_only=True)
class ResourceTimer(Timer):
    owner: int
    resource: str
    amount: int


@dataclass
class Sprite:
    surface: Surface

    @property
    def size(self):
        return vec2(self.surface.get_size())


@dataclass
class Animation:
    surface: Surface
    frame_size: vec2
    frame_count: int
    frame_time: float
    time: float = 0.0
    frame: int = 0
    frames: list[Surface] = field(default_factory=list)
    paused: bool = False
    repeat: bool = False

    def __post_init__(self):
        self.frames = []
        for i in range(self.frame_count):
            x = i * self.frame_size.x
            y = 0
            self.frames.append(
                self.surface.subsurface((x, y), self.frame_size.to_list())
            )


class PlayerControlled:
    pass


class CurrentPlayer:
    pass


@dataclass
class HighlightRect:
    pos: vec2
    size: vec2


@dataclass
class Resources:
    r1: int = 0

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


@dataclass
class AddResource:
    owner: int
    kind: str
    amount: int
