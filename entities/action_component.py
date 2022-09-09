from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

from actions.actions import Action
from entities.base_component import BaseComponent

class ActionComponent(Action, BaseComponent):
    def perform(self) -> None:
        raise NotImplementedError()

