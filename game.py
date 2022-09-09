import json
from collections import OrderedDict
from threading import Timer

from pygame import mixer

from engine import Engine, GameState
from sections.confirmation import Confirmation
from sections.intro_section import IntroSection
from sections.notification import Notification
from sections.test_map_section import TestMapSection


class Game(Engine):
    def __init__(self, teminal_width: int, terminal_height: int):
        super().__init__(teminal_width, terminal_height)

    def create_new_save_data(self):
        pass

    def load_initial_data(self, data):
        pass

    def load_fonts(self):
        pass

    def setup_sections(self):
        self.intro_sections = OrderedDict()
        self.intro_sections["introSection"] = IntroSection(self,0,0,self.screen_width, self.screen_height)

        self.menu_sections = OrderedDict()

        self.game_sections = OrderedDict()
        self.game_sections["TestMapSection"] = TestMapSection(self, 0,0, 200, 150)
        
        self.misc_sections = OrderedDict()
        self.misc_sections["notificationDialog"] = Notification(self, 7, 9, 37, 10)
        self.misc_sections["confirmationDialog"] = Confirmation(self, 7, 9, 37, 10)

        self.completion_sections = OrderedDict()

        self.disabled_sections = ["confirmationDialog", "notificationDialog"]
        self.disabled_ui_sections = ["confirmationDialog", "notificationDialog"]
