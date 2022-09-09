import numpy as np  # type: ignore
from typing import Tuple
import utils.color

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B")
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", np.bool),  # True if this tile can be walked over.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ("wearable", np.bool),  # True if this tile can be worn down
        ("wear", np.float),
        ("graphic", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("original_bg", "3B"),
        ("cost", np.int)
    ]
)

def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    graphic: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    wearable: bool,
    cost: int,
) -> np.ndarray:
    """Helper function for defining individual tile types """
    wear = 1
    return np.array((walkable, transparent, wearable, wear, graphic, graphic[2], cost), dtype=tile_dt)


floor = new_tile(
    walkable=True,
    transparent=True,
    wearable=True,
    graphic=(ord(" "), (255, 255, 255), utils.color.GRASS_GREEN),
    cost=0
)

background_tile = new_tile(
    walkable=True,
    transparent=True,
    wearable=True,
    graphic=(ord(" "), (255, 255, 255), (0,0,0)),
    cost=0
)
