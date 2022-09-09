from __future__ import annotations

import copy
from enum import Enum, auto
from typing import TYPE_CHECKING, Iterable, Iterator, Optional, Tuple

import entities.entity_factories 
import numpy as np  # type: ignore
import tcod
from sections.section import Section
from sections.map_section import MapSection
import tile_types
import utils.color
from entities.entity import Actor, Entity, Prop
from tcod.console import Console
from utils.utils import Neighbourhood
from entities.player import Player

if TYPE_CHECKING:
    from engine import Engine


class TestMapSection(MapSection):
    def __init__(self, engine, x: int, y: int, width: int, height: int, xp_filepath: str = "") -> None:
        super().__init__(engine, x, y, width, height, xp_filepath)

        self.engine = engine
        self.width, self.height = width, height
        self.tiles = np.full((self.width, self.height), fill_value=tile_types.background_tile, order="F")
        self.artefact_tiles = np.full((self.width, self.height), fill_value=ord(" "), order="F")
        self.cost = None

        #Map Variables
        self.map_height = height
        self.map_width = width
        self.map_center = (int(self.map_width / 2), int(self.map_height / 2))
        self.map_render_width, self.map_render_height = 51,30
        self.map_render_x, self.map_render_y = 0,0
        self.map_movement_cage_x, self.map_movement_cage_y = 12,8
        self.initial_pawn, self.map_movement_pawn = [5,5], [5,5]
        self.map_x_offset = 0
        self.map_y_offset = 0
        self.map_mouse_location = (0, 0)

        self.player =  Player(self.engine, 12,8)
        self.add_entity(self.player)

        super().generate_landscape(self.engine, self, width, height)


    def update(self):
        self.cost = np.array(self.tiles["walkable"], dtype=np.int8)

        """ Very expensive!
        for x in range(0, self.width):
            for y in range(0, self.height):
                self.cost[x, y] += self.tiles[x, y]["cost"]
        """
        for entity in self.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and self.cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                if isinstance(entity, Actor):
                    self.cost[entity.x, entity.y] += 10
                if isinstance(entity, Prop):
                    self.cost[entity.x, entity.y] += 1000

        self.graph = tcod.path.SimpleGraph(cost=self.cost, cardinal=2, diagonal=3)

    def render(self, console: Console) -> None:
        """ Renders the game to console. """
        console.tiles_rgb[self.map_x_offset: self.map_render_width + self.map_x_offset, self.map_y_offset: self.map_render_height + self.map_y_offset] = self.tiles[self.map_render_x:self.map_render_x + self.map_render_width, self.map_render_y:self.map_render_y + self.map_render_height]["graphic"]

        entity_console = Console(console.width, console.height)
        for entity in self.entities_sorted_for_rendering():
            x = entity.x - self.map_render_x + self.map_x_offset
            y = entity.y - self.map_render_y + self.map_y_offset

            entity_console.print(x=x, y=y, string=entity.char, fg=entity.fg_colour, bg=self.get_tile_bg_colour(entity.x, entity.y))
            entity_console.blit(console, src_x=x, dest_x=x, src_y=y, dest_y=y, width=1, height=1)

        #self.message_log.render(console=console, x=0, y=self.map_height + self.map_y_offset + 2, width=40, height=10)
        #self.ui.render(console)

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def in_rendered_map(self, x: int, y: int) -> bool:
        return self.is_point_in_rendered_map((x,y))

    def is_mouse_in_map(self) -> bool:
        """ Is the mouse inside the bounds of the map """
        # This should perhaps move
        return self.map_x_offset <= self.mouse_location[0] < self.map_x_offset + self.map_render_width and self.map_y_offset <= self.mouse_location[1] < self.map_y_offset + self.map_render_height

    def convert_map_to_screen(self, map_position) -> Tuple[int,int]:
        return (map_position[0] - self.map_render_x, map_position[1] - self.map_render_y)

    def is_point_in_rendered_map(self, position) -> bool:
        screen_position = self.convert_map_to_screen(position)
        return screen_position[0] >= 0 and screen_position[0] < self.map_render_width and screen_position[1] >= 0 and screen_position[1] < self.map_render_height

    def get_neighbouring_tiles(self, position: Tuple[int, int], neighbourhood: Neighbourhood):
        if neighbourhood is Neighbourhood.VON_NEUMANN:
            neighbours = ([position[0] - 1, position[1]],
                          [position[0] + 1, position[1]],
                          [position[0], position[1] - 1],
                          [position[0], position[1] + 1]
                          )
        elif neighbourhood is Neighbourhood.MOORE:
            neighbours = ([position[0] - 1, position[1] - 1],
                          [position[0], position[1] - 1],
                          [position[0] + 1, position[1] - 1],
                          [position[0] - 1, position[1]],
                          [position[0] + 1, position[1]],
                          [position[0] - 1, position[1] + 1],
                          [position[0], position[1] + 1],
                          [position[0] + 1, position[1] + 1],
                          )

        return neighbours

    def can_place_prop_in_tile(self, x: int, y: int):
        if self.get_actor_at_location(x, y) is not None:
            return False
        if len(self.get_entities_at_location(x, y)) > 0:
            return False

        return True

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def get_surrounding_entities(self, position: Tuple[int, int], neighbourhood: Neighbourhood):
        entities = list()

        neighbours = self.get_neighbouring_tiles(position, neighbourhood)
        for neighbour in neighbours:
            entities.append(self.get_entities_at_location(neighbour[0], neighbour[1]))

        return entities

    def get_entities_at_location(self, x: int, y: int) -> list(Entity):
        entities = list()
        for entity in self.entities:
            if entity.x == x and entity.y == y:
                entities.append(entity)

        return entities

    def get_tile_bg_colour(self, x: int, y: int) -> Tuple[int, int, int]:
        for entity in reversed(sorted(self.get_entities_at_location(x, y), key=lambda x: x.render_order.value)):
            if entity.colours_bg:
                return entity.bg_colour

        np_colour_array = self.tiles[x, y]["graphic"]["bg"]
        return [np_colour_array[0], np_colour_array[1], np_colour_array[2]]

    def get_blocking_entity_at_location(self, location_x: int, location_y: int,) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity

        return None

    def replace_tile(self, x: int, y: int, tile: np.ndarray):
        self.tiles[x, y] = tile

    def update_movement_cage(self, dx,dy):
        self.map_movement_pawn[0] += dx
        self.map_movement_pawn[1] += dy

        #Right edge
        if (self.map_movement_pawn[0] > self.initial_pawn[0] + self.map_movement_cage_x) and self.map_render_x < self.map_width - self.map_render_width:
            self.map_render_x += 1
            self.map_movement_pawn[0] -= 1
        
        #Left edge
        elif (self.map_movement_pawn[0] < self.initial_pawn[0] - self.map_movement_cage_x) and self.map_render_x > 0:
            self.map_render_x -= 1
            self.map_movement_pawn[0] += 1

        #Top edge
        elif (self.map_movement_pawn[1] < self.initial_pawn[1] - self.map_movement_cage_y) and self.map_render_y > 0:
            self.map_render_y -= 1
            self.map_movement_pawn[1] += 1

        #Bottom edge
        elif (self.map_movement_pawn[1] > self.initial_pawn[1] + self.map_movement_cage_y) and self.map_render_y < self.map_height - self.map_render_height:
            self.map_render_y += 1
            self.map_movement_pawn[1] -= 1

            
