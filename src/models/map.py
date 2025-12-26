
import pygame
from src.models.factories import KeyAbstractFactory

class GameMap:
    def __init__(self, width, height, factory: KeyAbstractFactory, seed=None):
        self.width = width
        self.height = height
        self.factory = factory
        self.walls = []
        self.tiles_x = width // 40
        self.tiles_y = height // 40
        self.background_color = self.factory.create_background().get_color()
        self.seed = seed
        self._generate_map()

    def _generate_map(self):
        import random  
        if self.seed is not None:
             rng = random.Random(self.seed)
        else:
             rng = random
        
        safe_zones = [
            (1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 2),
            (self.tiles_x - 2, self.tiles_y - 2), 
            (self.tiles_x - 2, self.tiles_y - 3), 
            (self.tiles_x - 3, self.tiles_y - 2),
            (self.tiles_x - 2, self.tiles_y - 4),
            (self.tiles_x - 4, self.tiles_y - 2),
            (self.tiles_x - 3, self.tiles_y - 3)
        ]

        for y in range(self.tiles_y):
            for x in range(self.tiles_x):
                if x == 0 or x == self.tiles_x - 1 or y == 0 or y == self.tiles_y - 1:
                    self.walls.append(self.factory.create_wall(x * 40, y * 40))

                elif x % 2 == 0 and y % 2 == 0:
                    self.walls.append(self.factory.create_wall(x * 40, y * 40))

                else:
                    if (x, y) in safe_zones:
                        continue
                    roll = rng.random()
                    if roll < 0.05: 
                        self.walls.append(self.factory.create_hard_wall(x * 40, y * 40))
                    elif roll < 0.45: 
                        self.walls.append(self.factory.create_breakable_wall(x * 40, y * 40))

    def add_breakable_wall(self, tile_x, tile_y):
        self.walls.append(self.factory.create_breakable_wall(tile_x * 40, tile_y * 40))

    def add_hard_wall(self, tile_x, tile_y):
        self.walls.append(self.factory.create_hard_wall(tile_x * 40, tile_y * 40))

    def draw(self, surface):
        surface.fill(self.background_color)
        for wall in self.walls:
            wall.draw(surface)
