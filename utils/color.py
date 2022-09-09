
import random
from typing import Tuple

GRASS_GREEN = (17, 41, 6)
DARK_GREEN = (40, 50, 6)
LIGHT_HEDGE = (30, 40, 0)
DARK_HEDGE = (20, 30, 0)
DRY_MUD_BROWN = (102, 82, 51)
DRY_MUD_BROWN_B = (75, 65, 35)
WET_MUD_BROWN = (39, 27, 10)

CROP_LIGHT = (100,84,15)
CROP_DARK = (72,64,12)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
DARK_GREY = (96, 96, 96)

LIGHT_WATER = (0,108,217)
DARK_WATER = (3,72,143)

WALL_BG = DARK_GREY
WALL_FG = DARK_GREEN


red =  (255,0,0)
green = (0,255,0)
blue = (0,0,255)
yellow = (255,255,0)

colors = []
colors.append(red)
colors.append(green)
colors.append(blue)
colors.append(yellow)

def get_random_color():
    return colors[random.randrange(0, len(colors))]

def blend_color(self, lc, rc, t):
        r = lc[0] * t + rc[0] * (1 - t) 
        g = lc[1] * t + rc[1] * (1 - t) 
        b = lc[2] * t + rc[2] * (1 - t)

        return (int(r),int(g),int(b))

def color_lerp(colour1: Tuple[int, int, int], colour2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    return (int(colour1[0] + t * (colour2[0] - colour1[0])), int(colour1[1] + t * (colour2[1] - colour1[1])), int(colour1[2] + t * (colour2[2] - colour1[2])))

