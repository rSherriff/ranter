import gzip
import os.path
import random
from typing import TYPE_CHECKING, Iterator, Tuple

import numpy as np  # type: ignore
import tcod.noise
import tile_types
import utils.color
import xp_loader
from application_path import get_app_path
from utils.voronoi import Voronoi

from sections.section import Section

if TYPE_CHECKING:
    from engine import Engine

painted_grids = ('/images/gridTL.xp','/images/gridTR.xp','/images/gridBL.xp','/images/gridBR.xp')
painted_grid_width = 100
painted_grid_height = 75


class MapSection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, xp_filepath: str = "") -> None:
        super().__init__(engine, x, y, width, height, xp_filepath)

    def generate_landscape(self, engine, landscape, map_width, map_height):

        np.random.seed(1237)
        
        map_center = (int(map_width / 2), int(map_height / 2))

        # Generate and draw a voronoi diagram, then grab the points from a few of its sections to fill later
        vorgen = Voronoi(40, np.array([-1, map_width + 1, -1, map_height + 1]))
        self.draw_voronoi(vorgen, landscape, utils.color.WHITE)
        voronoi_fill_points = self.get_voronoi_fill_points(random.randrange(3, 6), vorgen, landscape)

        self.clear_landscape(landscape, utils.color.GRASS_GREEN, utils.color.DARK_GREEN)

        noise = tcod.noise.Noise(
            dimensions=2,
            algorithm=tcod.NOISE_PERLIN,
            implementation=tcod.noise.TURBULENCE,
            hurst=0.5,
            lacunarity=5.0,
            octaves=2,
            seed=None,
        )

        # Add a base layer of smooth, gradually changing noise to form base layer
        self.add_smooth_noise_to_landscape(landscape, noise, 0.05, utils.color.GRASS_GREEN, utils.color.DARK_GREEN)

        # Shade the voronoi sections we grabbed before now we have our base layer down
        #fill_regions(landscape, voronoi_fill_points, utils.color.DRY_MUD_BROWN, utils.color.WET_MUD_BROWN, utils.color.DARK_GREEN, utils.color.DRY_MUD_BROWN_B)

        # Add more granular noise on top to break things up
        self.add_noise_to_landscape(landscape, noise, 0.9, utils.color.GRASS_GREEN, utils.color.DARK_GREEN)

        self.add_painted_tiles(landscape)

        # Save this version of the map so effects can happen to it over the course of the game
        self.save_original_color(landscape)   


    def clear_landscape(self, landscape, bg_colour, fg_colour):
        for x in range(0, landscape.width):
            for y in range(0, landscape.height):
                landscape.tiles[x, y]["graphic"]["bg"] = bg_colour
                landscape.tiles[x, y]["graphic"]["ch"] = 9617
                landscape.tiles[x, y]["graphic"]["fg"] = utils.color.color_lerp(bg_colour, fg_colour, random.random())


    def draw_voronoi(self, vorgen, landscape, colour):
        for region in vorgen.vor.filtered_regions:
            vertices = vorgen.vor.vertices[region, :]
            for i in range(0, len(vertices)):
                nextVertex = i + 1
                if(i == len(vertices) - 1):
                    nextVertex = 0
                for x, y in self.line_between((int(vertices[i][0]), int(vertices[i][1])), (int(vertices[nextVertex][0]), int(vertices[nextVertex][1]))):
                    if x >= 0 and y >= 0 and x < landscape.width and y < landscape.height:
                        landscape.tiles[x, y]["graphic"]["bg"] = colour


    def get_voronoi_fill_points(self, num_regions, vorgen, landscape):
        dirt_patch_points = list()
        for i in range(0, num_regions):
            point = vorgen.vor.filtered_points[i]
            dirt_patch_points += [self.get_fill_points(landscape, point)]

        return dirt_patch_points


    def fill_regions(self, landscape, region_points, start_colour, end_colour, blend_colour, accent_colour):
        # Start colour, end colour - The range of color you want this tile to become
        # Blend colour - the colour this section blends into, tiles on the edge of the section will completely fade into it
        # accent colour - an extra dash for tiles that are completly surrounded by similar coloured tiles
        for i in region_points:
            for point in i:
                landscape.tiles[point[0], point[1]]["graphic"]["bg"] = start_colour

        for i in region_points:
            for point in i:
                x, y = point[0], point[1]
                score = 0
                if (x - 1, y) in i:
                    score += 1
                if (x + 1, y) in i:
                    score += 1
                if (x, y - 1) in i:
                    score += 1
                if (x, y + 1) in i:
                    score += 1
                if (x - 1, y + 1) in i:
                    score += 1
                if (x + 1, y + 1) in i:
                    score += 1
                if (x + 1, y - 1) in i:
                    score += 1
                if (x + 1, y + 1) in i:
                    score += 1

                if random.random() < 0.5:
                    landscape.tiles[x, y]["graphic"]["ch"] = 9617
                    landscape.tiles[x, y]["graphic"]["fg"] = utils.color.color_lerp(start_colour, end_colour, min(0.4, random.random()))

                landscape.tiles[x, y]["graphic"]["bg"] = utils.color.color_lerp(blend_colour, start_colour, score / 8)

                if score == 8:
                    landscape.tiles[x, y]["graphic"]["bg"] = utils.color.color_lerp(landscape.tiles[x, y]["graphic"]["bg"], accent_colour, random.random())

    def colour_point_fg(self, landscape, point, start_colour, end_colour):
            x,y = point[0], point[1]
            score = random.random() * 8

            landscape.tiles[x, y]["graphic"]["fg"] = utils.color.color_lerp(start_colour, end_colour, score / 8)

    def colour_point_bg(self, landscape, point, start_colour, end_colour):
            x,y = point[0], point[1]
            score = random.random() * 8

            landscape.tiles[x, y]["graphic"]["bg"] = utils.color.color_lerp(start_colour, end_colour, score / 8)

    def add_smooth_noise_to_landscape(self, landscape, noise, scale, start_colour, end_colour):
        # Create an open multi-dimensional mesh-grid.
        ogrid = [np.arange(landscape.width, dtype=np.float32),
                np.arange(landscape.height, dtype=np.float32)]

        ogrid[0] *= scale
        ogrid[1] *= scale

        # Return the sampled noise from this grid of points.
        samples = noise.sample_ogrid(ogrid)

        for x in range(0, landscape.width):
            for y in range(0, landscape.height):
                landscape.tiles[x, y]["graphic"]["bg"] = utils.color.color_lerp(landscape.tiles[x, y]["graphic"]["bg"], end_colour, samples[x, y] / 1.2)


    def add_noise_to_landscape(self, landscape, noise, threshold, start_colour, end_colour):
        # Create an open multi-dimensional mesh-grid.
        ogrid = [np.arange(landscape.width, dtype=np.float32),
                np.arange(landscape.height, dtype=np.float32)]

        # Return the sampled noise from this grid of points.
        samples = noise.sample_ogrid(ogrid)

        for x in range(0, landscape.width):
            for y in range(0, landscape.height):
                if samples[x, y] > threshold:
                    old_range = (1 - threshold)
                    new_value = ((samples[x, y] - threshold) / old_range)
                    colour = utils.color.color_lerp(start_colour, end_colour, max(0.5, random.random()))
                    landscape.tiles[x, y]["graphic"]["ch"] = 9617
                    landscape.tiles[x, y]["graphic"]["bg"] = colour
                    landscape.tiles[x, y]["graphic"]["fg"] = utils.color.color_lerp(colour, utils.color.DARK_GREEN, max(0.8, random.random()))


    def line_between(self, 
        start: Tuple[int, int], end: Tuple[int, int]
    ) -> Iterator[Tuple[int, int]]:
        """Return an L-shaped tunnel between these two points."""
        x1, y1 = start
        x2, y2 = end

        # Generate the coordinates for this tunnel.
        for x, y in tcod.los.bresenham((x1, y1), (x2, y2)).tolist():
            yield x, y


    def get_fill_points(self, landscape, start_coords: Tuple[int, int]):
        orig_value = (landscape.tiles[start_coords[0], start_coords[1]]["graphic"]["bg"]).copy()

        stack = set(((start_coords[0], start_coords[1]),))
        points = list()
        while stack:
            x, y = stack.pop()
            res = all(i == j for i, j in zip(landscape.tiles[x, y]["graphic"]["bg"], orig_value))
            if res:
                landscape.tiles[x, y]["graphic"]["bg"] = (255 - orig_value[0], 255 - orig_value[1], 255 - orig_value[2])
                points.append((x, y))
                if x > 0:
                    stack.add((x - 1, y))
                if x < (landscape.width - 1):
                    stack.add((x + 1, y))
                if y > 0:
                    stack.add((x, y - 1))
                if y < (landscape.height - 1):
                    stack.add((x, y + 1))

        return points


    def save_original_color(self, landscape):
        for x in range(0, landscape.width):
            for y in range(0, landscape.height):
                landscape.tiles[x, y]["original_bg"] = landscape.tiles[x, y]["graphic"]["bg"]

    def add_painted_tiles(self, landscape):
        count = 0 
        for y in range(0,2):
            for x in range(0,2):
                if os.path.isfile(get_app_path() + painted_grids[count]):
                    xp_file = gzip.open(get_app_path() + painted_grids[count])
                    raw_data = xp_file.read()
                    xp_file.close()
                    xp_data = xp_loader.load_xp_string(raw_data)

                    for w in range(0,painted_grid_width):
                        for h in range(0,painted_grid_height):
                            if xp_data['layer_data'][0]['cells'][w][h][0] != 32:
                                landscape.tiles[w + (x * painted_grid_width),h + (y * painted_grid_height)]['graphic']=  xp_data['layer_data'][0]['cells'][w][h]

                            if xp_data['layer_data'][1]['cells'][w][h][0] != 32:
                                landscape.artefact_tiles[w + (x * painted_grid_width),h + (y * painted_grid_height)] =  xp_data['layer_data'][1]['cells'][w][h][0]

                            if xp_data['layer_data'][2]['cells'][w][h][0] == 114: #r
                                self.colour_point_fg(landscape, (w + (x * painted_grid_width),h + (y * painted_grid_height)), utils.color.DRY_MUD_BROWN, utils.color.DRY_MUD_BROWN_B)
                            
                            if xp_data['layer_data'][2]['cells'][w][h][0] == 104: #h
                                self.colour_point_bg(landscape, (w + (x * painted_grid_width),h + (y * painted_grid_height)), utils.color.LIGHT_HEDGE, utils.color.DARK_HEDGE)
                                landscape.tiles[w + (x * painted_grid_width),h + (y * painted_grid_height)]["walkable"] = False

                            if xp_data['layer_data'][2]['cells'][w][h][0] == 103: #g
                                self.colour_point_bg(landscape, (w + (x * painted_grid_width),h + (y * painted_grid_height)),utils.color.GRASS_GREEN, utils.color.DARK_GREEN)

                            if xp_data['layer_data'][2]['cells'][w][h][0] == 99: #c
                                landscape.tiles[w + (x * painted_grid_width),h + (y * painted_grid_height)]['graphic']["ch"] = ord('ò')
                                self.colour_point_fg(landscape, (w + (x * painted_grid_width),h + (y * painted_grid_height)),utils.color.CROP_LIGHT, utils.color.CROP_DARK)
                                self.colour_point_bg(landscape, (w + (x * painted_grid_width),h + (y * painted_grid_height)),utils.color.CROP_LIGHT, utils.color.CROP_DARK)

                            if xp_data['layer_data'][2]['cells'][w][h][0] == 98: #b
                                landscape.tiles[w + (x * painted_grid_width),h + (y * painted_grid_height)]['walkable'] = False
                                self.colour_point_fg(landscape, (w + (x * painted_grid_width),h + (y * painted_grid_height)),utils.color.BLACK, utils.color.BLACK)
                                self.colour_point_bg(landscape, (w + (x * painted_grid_width),h + (y * painted_grid_height)),utils.color.WALL_BG, utils.color.GREY)

                            if xp_data['layer_data'][2]['cells'][w][h][0] == 119: #w
                                landscape.tiles[w + (x * painted_grid_width),h + (y * painted_grid_height)]['walkable'] = False
                                landscape.tiles[w + (x * painted_grid_width),h + (y * painted_grid_height)]['graphic']["ch"] = ord('ò')
                                self.colour_point_fg(landscape, (w + (x * painted_grid_width),h + (y * painted_grid_height)),utils.color.LIGHT_WATER, utils.color.DARK_WATER)
                                self.colour_point_bg(landscape, (w + (x * painted_grid_width),h + (y * painted_grid_height)),utils.color.LIGHT_WATER, utils.color.DARK_WATER)
                count += 1

    def get_surrounding_tiles(self, position: Tuple[int, int]):
        return ([position[0] - 1, position[1] - 1],
                [position[0] - 1, position[1] + 1],
                [position[0] + 1, position[1] - 1],
                [position[0] + 1, position[1] + 1],
                [position[0] - 1, position[1]],
                [position[0] + 1, position[1]],
                [position[0], position[1] - 1],
                [position[0], position[1] + 1],
                )




