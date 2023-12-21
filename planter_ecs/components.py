from __future__ import annotations

from dataclasses import dataclass
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
