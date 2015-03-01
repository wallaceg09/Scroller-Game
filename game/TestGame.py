'''
Created on Feb 28, 2015

@author: Glen
'''

import os.path
import pytmx
from pytmx.util_pygame import load_pygame
import pygame
#import pyscroll
import pyscroll.data
from pyscroll.util import PyscrollGroup
from pygame.locals import *

RESOURCES_DIR = 'res'
FPS = 60
HERO_MOVE_SPEED = 200

MAP_FILENAME = 'PlatformerDebugMap.tmx'

#used for 2x scaling
temp_surface = None

def init_screen(width, height):
    global temp_surface
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    temp_surface = pygame.Surface((width, height)).convert()#Causes the image to be scaled 2x
    return screen

def get_map(filename):
    return os.path.join(RESOURCES_DIR, filename)

def load_image(filename):
    return pygame.image.load(os.path.join(RESOURCES_DIR, filename))

class Hero(pygame.sprite.Sprite):
    """ Our Hero

    The Hero has three collision rects, one for the whole sprite "rect" and
    "old_rect", and another to check collisions with walls, called "feet".

    The position list is used because pygame rects are inaccurate for
    positioning sprites; because the values they get are 'rounded down' to
    as integers, the sprite would move faster moving left or up.

    Feet is 1/2 as wide as the normal rect, and 8 pixels tall.  This size size
    allows the top of the sprite to overlap walls.

    There is also an old_rect that is used to reposition the sprite if it
    collides with level walls.
    """
    def __init__(self, image_filename = "ball.png"):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(image_filename).convert_alpha()
        self.velocity = [0, 0]
        self._position = [0, 0]
        self._old_position = self._position
        self.rect = self.image.get_rect() #TODO: Set this as an input parameter when you start doing multi-sprite images
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, self.rect.height * 0.25)
    
    @property
    def position(self):
        return list(self._position)
    
    @position.setter
    def position(self, value):
        self._position = list(value) 
    
    def update(self, dt):
        self._old_position = self._position
        self._position[0] += self.velocity[0] * dt
        self._position[1] += self.velocity[1] * dt
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom
        self.velocity[1] = min(self.velocity[1] + 25, 500)
        
    def move_back(self, dt):
        self.velocity = [0, 0]
        self._position = self._old_position
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom

class ScrollGame(object):
    """ This class is a basic game.

    This class will load data, create a pyscroll group, a hero object.
    It also reads input and moves the Hero around the map.
    Finally, it uses a pyscroll group to render the map and Hero.
    """
    filename = get_map(MAP_FILENAME)
    def __init__(self):
        self.running = False
        
        tmx_data = load_pygame(self.filename)
        
        #Wall collision prep code
        self.collisions = list()
        for object in tmx_data.get_layer_by_name("Collision"):
            self.collisions.append(pygame.Rect(
                                               object.x, object.y,
                                               object.width, object.height))
        
        map_data = pyscroll.data.TiledMapData(tmx_data)
        
        w, h = screen.get_size()
        
        # create new renderer (camera)
        # clamp_camera is used to prevent the map from scrolling past the edge
        self.map_layer = pyscroll.BufferedRenderer(map_data,
                                                   (w, h),
                                                   clamp_camera = True)
        
        # pyscroll supports layered rendering.  our map has 3 'under' layers'''My map has three so somewhat ignore this'''
        # layers begin with 0, so the layers are 0, 1, and 2.
        # since we want the sprite to be on top of layer 1, we set the default
        # layer for sprites as 1
        self.group = PyscrollGroup(map_layer = self.map_layer,
                                   default_layer = 3)
        
        self.hero = Hero("wizard.png")
        
        self.hero.position = self.map_layer.rect.center #TODO: Add spawn object in map
        
        self.group.add(self.hero) 
   
    def draw(self, surface):
        self.group.center(self.hero.rect.center)
        self.group.draw(surface)
    
    def _handle_input(self):
        event = pygame.event.poll()
        while event:
            if event.type == QUIT:
                self.running = False
            event = pygame.event.poll()
        pass
    
    def update(self, dt):
        self.group.update(dt)
        
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.collisions) > -1:
                sprite.move_back(dt)
        pass
    
    def run(self):
        clock = pygame.time.Clock()
        scale = pygame.transform.scale
        self.running = True
        try:
            while self.running:
                dt = clock.tick(FPS) / 1000.0
                self._handle_input()
                self.update(dt)
                self.draw(temp_surface)
                scale(temp_surface, screen.get_size(), screen)
                pygame.display.flip()
        except KeyboardInterrupt:
            self.running = False
        
if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    screen = init_screen(800, 600)
    pygame.display.set_caption("Side Scroller")
    try:
        game = ScrollGame()
        game.run()
    except:
        pygame.quit()
        raise