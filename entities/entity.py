import copy
import random
from typing import Tuple, Type, TypeVar

from entities.action_component import ActionComponent
from entities.animal import Animal
from entities.render_order import RenderOrder

T = TypeVar("T", bound="Entity")

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    def __init__(
        self,
        id: int = -1,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        bg_colour: Tuple[int, int, int] = (255, 255, 255),
        fg_colour: Tuple[int, int, int] = (255, 255, 255),
        colours_bg: bool = False,
        name: str = "<unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
        physical_properties: list = [],
        weight: int = 0
    ):
        self.id = id
        self.x = x
        self.y = y
        self.char = char
        self.bg_colour = bg_colour
        self.fg_colour = fg_colour
        self.colours_bg = colours_bg
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        self.weight = weight

        self.physical_properties = []
        for component in physical_properties:
            self.physical_properties.append(component(self))

    def spawn(self: T, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y

        return clone



    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy

    def place(self, x: int, y: int) -> None:
        #Place this entitiy at a new location.  Handles moving across GameMaps.
        self.x = x
        self.y = y

    def update(self):
        for component in self.physical_properties:
            component.perform()

    def late_update(self):
        pass
    
    def keydown(self, key):
        pass

    def mousedown(self, button):
        pass


class Actor(Entity):
    def __init__(
        self,
        *,
        id: int = -1,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        bg_colour: Tuple[int, int, int] = (255, 255, 255),
        fg_colour: Tuple[int, int, int] = (255, 255, 255),
        colours_bg: bool = False,
        name: str = "<unnamed>",
        animal: Animal,
        weight: int = 0,
        physical_properties: list = [],
    ):
        super().__init__(
            id=id,
            x=x,
            y=y,
            char=char,
            name=name,
            bg_colour=bg_colour,
            fg_colour=fg_colour,
            colours_bg=colours_bg,
            blocks_movement=False,
            render_order=RenderOrder.ACTOR,
            weight=weight,
            physical_properties=physical_properties
        )


        self.animal = animal
        self.animal.entity = self

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)

    def update(self):
        super().update()


    def get_effort(self):
        # TODO: Return effort based on the job and the actors abilities
        return 1

class Prop(Entity):
    def __init__(
        self,
        id: int = -1,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        bg_colour: Tuple[int, int, int] = (255, 255, 255),
        fg_colour: Tuple[int, int, int] = (255, 255, 255),
        colours_bg: bool = False,
        weight: int = 0,
        name: str = "<unnamed>",
        blocks_movement: bool = False,
        physical_properties: list = [],
    ):
        super().__init__(
            id=id,
            x=x,
            y=y,
            char=char,
            bg_colour=bg_colour,
            fg_colour=fg_colour,
            colours_bg=colours_bg,
            name=name,
            blocks_movement=blocks_movement,
            render_order=RenderOrder.PROP,
            weight=weight,
            physical_properties=physical_properties
        )

class Touchable(Prop):
    def __init__(
        self,
        id: int = -1,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        bg_colour: Tuple[int, int, int] = (255, 255, 255),
        fg_colour: Tuple[int, int, int] = (255, 255, 255),
        colours_bg: bool = False,
        weight: int = 0,
        name: str = "<unnamed>",
        blocks_movement: bool = True,
        physical_properties: list = [],
        on_touch: Type[ActionComponent]
    ):
        super().__init__(
            id=id,
            x=x,
            y=y,
            char=char,
            bg_colour=bg_colour,
            fg_colour=fg_colour,
            colours_bg=colours_bg,
            name=name,
            blocks_movement=blocks_movement,
            weight=weight,
            physical_properties=physical_properties
        )

        self.on_touch = on_touch
