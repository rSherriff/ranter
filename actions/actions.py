from __future__ import annotations

import random
from typing import TYPE_CHECKING

import utils.color

if TYPE_CHECKING:
    from engine import Engine


class Action:
    def __init__(self, engine) -> None:
        super().__init__()
        self.engine = engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `engine` is the scope this action is being performed in.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self) -> None:
        self.engine.quit()


class CloseMenu(Action):
    def perform(self) -> None:
        self.engine.close_menu()


class OpenMenu(Action):
    def perform(self) -> None:
        self.engine.open_menu()

class NoAction(Action):
    def perform(self) -> None:
        print("No Action taken!")

class ShowTooltip(Action):
    def __init__(self, engine, tooltip_key: str) -> None:
        super().__init__(engine)
        self.tooltip_key = tooltip_key

    def perform(self):
        self.engine.show_tooltip(self.tooltip_key)


class HideTooltip(Action):
    def __init__(self, engine, tooltip_key: str) -> None:
        super().__init__(engine)
        self.tooltip_key = tooltip_key

    def perform(self):
        self.engine.hide_tooltip(self.tooltip_key)


class GameOver(Action):
    def perform(self) -> None:
        self.engine.game_over()

class AddEntity(Action):
    def __init__(self, engine, section, entity):
        super().__init__(engine)
        self.section = section
        self.entity = entity

    def perform(self):
        self.section.entities.append(self.entity)

class DeleteEntity(Action):
    def __init__(self, engine, section, entity):
        super().__init__(engine)
        self.section = section
        self.entity = entity

    def perform(self):
        self.section.remove_entity(self.entity)


class DisableSection(Action):
    def __init__(self, engine, section) -> None:
        super().__init__(engine)
        self.section = section

    def perform(self) -> None:
        return self.engine.disable_section(self.section)


class OpenConfirmationDialog(Action):
    def __init__(self, engine, text, confirmation_action, section) -> None:
        super().__init__(engine)
        self.text = text
        self.confirmation_action = confirmation_action
        self.section = section

    def perform(self) -> None:
        return self.engine.open_confirmation_dialog(self.text, self.confirmation_action, self.section)


class CloseConfirmationDialog(Action):
    def __init__(self, engine, section) -> None:
        super().__init__(engine)
        self.section = section

    def perform(self) -> None:
        return self.engine.close_confirmation_dialog(self.section)


class OpenNotificationDialog(Action):
    def __init__(self, engine, text, section) -> None:
        super().__init__(engine)
        self.text = text
        self.section = section

    def perform(self) -> None:
        return self.engine.open_notification_dialog(self.text, self.section)


class CloseNotificationDialog(Action):
    def __init__(self, engine, section) -> None:
        super().__init__(engine)
        self.section = section
        
    def perform(self) -> None:
        return self.engine.close_notification_dialog(self.section)


class ToggleFullScreenAction(Action):
    def __init__(self, engine) -> None:
        super().__init__(engine)

    def perform(self) -> None:
        self.engine.toggle_fullscreen()


class SliderAction(Action):
    def __init__(self, engine, action_type) -> None:
        super().__init__(engine)
        self.action_type = action_type
        
    def perform(self, value) -> None:
        action = self.action_type(self.engine, value)
        return action.perform(value)

class ChangeVolumeAction(Action):
    def __init__(self, engine, value) -> None:
        super().__init__(engine)
        self.value = value
        
    def perform(self, value) -> None:
        return self.engine.set_mixer_volume(value)



class QueueMusicAction(Action):
    def __init__(self, engine, stage) -> None:
        super().__init__(engine)
        self.stage = stage

    def perform(self) -> None:
        self.engine.queue_music(self.stage)

class EndMusicQueueAction(Action):
    def __init__(self, engine, fadeout_time) -> None:
        super().__init__(engine)
        self.fadeout_time = fadeout_time

    def perform(self) -> None:
        self.engine.end_music_queue( self.fadeout_time)

class IntroEndAction(Action):
    def perform(self) -> None:
        self.engine.end_intro()

class PlayMusicFileAction(Action):
    def __init__(self, engine, file) -> None:
        super().__init__(engine)
        self.file = file

    def perform(self) -> None:
        self.engine.play_music_file(self.file)

class PlayMenuMusicAction(Action):
    def __init__(self, engine, file="") -> None:
        super().__init__(engine)
        self.file = file

    def perform(self) -> None:
        self.engine.play_menu_music(self.file)

class EntityAction():
    def __init__(self, entity) -> None:
        self.entity = entity

    def perform(self, section) -> None:
        """Perform this action with the objects needed to determine its scope.

        `engine` is the scope this action is being performed in.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()

class EntityActionWithDirection(EntityAction):
    def __init__(self, entity, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self):
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) :
        """Return the blocking entity at this actions destination.."""
        return self.section.get_blocking_entity_at_location(*self.dest_xy)

    def perform(self, section) -> None:
        raise NotImplementedError()


class MovementAction(EntityActionWithDirection):
    def perform(self, section) -> None:  
        dest_x, dest_y = self.dest_xy

        if not section.in_rendered_map(dest_x, dest_y):
            print(f"{self.entity.name} is trying to move out of bounds!")
            return  # Destination is out of bounds.
        if not section.tiles["walkable"][dest_x, dest_y]:
            print(f"{self.entity.name}'s destination blocked by tile!")
            return  # Destination is blocked by a tile.
        if section.get_blocking_entity_at_location(dest_x, dest_y):
            print(f"{self.entity.name} destination blocked by an entity!")
            return  # Destination is blocked by an entity.

        MapRenderCageUpdateEntityAction(self.entity, self.dx, self.dy).perform(section)
        self.entity.move(self.dx, self.dy)

        # Tile is worn down as an actor moves on to it
        if section.tiles[dest_x, dest_y]["wearable"]:
            section.tiles[dest_x, dest_y]["wear"] = max(0, section.tiles[dest_x, dest_y]["wear"] - self.entity.weight * (random.random() * 0.0025))
            section.tiles[dest_x, dest_y]["graphic"]["bg"] = utils.color.color_lerp(utils.color.DRY_MUD_BROWN, section.tiles[dest_x, dest_y]["original_bg"], section.tiles[dest_x, dest_y]["wear"])

class BumpEntityAction(EntityActionWithDirection):
    def perform(self, section) -> None:
        dest_x = self.entity.x + self.dx
        dest_y = self.entity.y + self.dy

        if section.get_blocking_entity_at_location(dest_x, dest_y):
            return TouchEntityAction(self.entity,self.dx, self.dy).perform(section)

        else:
            return MovementAction(self.entity,self.dx, self.dy).perform(section)

class TouchEntityAction(EntityActionWithDirection):
   def perform(self, section) -> None:
        dest_x = self.entity.x + self.dx
        dest_y = self.entity.y + self.dy
        target = section.get_blocking_entity_at_location(dest_x, dest_y)
        if not target:
            return  # No entity to attack.
        
        target.on_touch.perform(target)

class MapRenderCageUpdateEntityAction(EntityActionWithDirection):
    def perform(self, section) -> None:
        dest_x, dest_y = self.dest_xy

        if not section.in_rendered_map(dest_x, dest_y):
            return  # Destination is out of bounds.
        if not section.tiles["walkable"][dest_x, dest_y]:
            return  # Destination is blocked by a tile.
        if section.get_blocking_entity_at_location(dest_x, dest_y):
            return  # Destination is blocked by an entity.

        section.update_movement_cage(self.dx, self.dy)
