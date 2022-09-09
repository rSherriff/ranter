

import random
from enum import Enum, auto

import utils.color

from entities.animal import Animal
from entities.entity import Actor, Prop, Touchable


class EntityID(Enum):
    NONE = -1
    WALL = auto()
    FLOOR = auto()
    PENDING_JOB = auto()
    DOOR = auto()
    FIELD = auto()
    CLUE_GIVER = auto()

player = Actor(
    char="@",
    fg_colour=(255, 255, 255),
    name="Player",
    animal=Animal(hp=30,),
    weight=80,
)

wall = Prop(
    id=EntityID.WALL,
    char="═",
    fg_colour=utils.color.WALL_FG,
    bg_colour=utils.color.GREY,
    name="Wall",
    weight=500,
    colours_bg=True
)

stone_floor = Prop(
    id=EntityID.FLOOR,
    char=" ",
    fg_colour=utils.color.WHITE,
    bg_colour=utils.color.GREY,
    name="Stone Floor",
    weight=200,
    blocks_movement=False,
    colours_bg=True
)

cloister_grass = Prop(
    id=EntityID.FLOOR,
    char=" ",
    fg_colour=utils.color.DARK_GREEN,
    bg_colour=utils.color.GRASS_GREEN,
    name="Cloister Grass",
    weight=0,
    blocks_movement=True,
    colours_bg=False
)

pending_job = Prop(
    id=EntityID.PENDING_JOB,
    char=".",
    fg_colour=utils.color.WHITE,
    name="Pending Job",
    weight=0,
    blocks_movement=False,
)

door = Prop(
    id=EntityID.DOOR,
    char="∩",
    fg_colour=utils.color.WALL_FG,
    name="Door",
    weight=80,
    blocks_movement=False
)

stone_pillar = Prop(
    id=EntityID.DOOR,
    char="o",
    fg_colour=utils.color.WALL_FG,
    bg_colour=utils.color.GREY,
    name="Stone Pillar",
    weight=80,
    blocks_movement=False,
    colours_bg=True
)

placeable_props = [door, stone_pillar]
