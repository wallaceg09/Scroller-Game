'''
Created on Feb 28, 2015

@author: Glen
'''
import pytmx
import pygame
import pyscroll
import os.path
from pytmx import util_pygame
from pygame.sprite import DirtySprite
from SpriteSheet import spritesheet

RESOURCES_DIR = 'res'
FPS = 60
HERO_MOVE_SPEED = 200
FPS = 60

MAP_FILENAME = 'PlatformerDebugMap.tmx'
PLAYER_FILENAME = 'wizard_green.png'

SPRITESHEET_MAP = {}

def get_map(filename):
    
    return os.path.join(RESOURCES_DIR, filename)

def load_image(filename):
    
    return pygame.image.load(os.path.join(RESOURCES_DIR, filename))

def get_full_img_path(filename):
    
    return os.path.join(RESOURCES_DIR, filename)

#FIXME: Issue #1: Player spritesheet isn't maintaining transparency when being drawn
#Workaround: use color_key. 
class Player(DirtySprite):
    
    def __init__(self, image_filename, source_rect, colorkey = None):
        DirtySprite.__init__(self)
        image_filename = get_full_img_path(image_filename)
        
        if image_filename not in SPRITESHEET_MAP:
            sprite_sheet = spritesheet(image_filename)
            SPRITESHEET_MAP[image_filename] = sprite_sheet
        else:
            sprite_sheet = SPRITESHEET_MAP[image_filename]
        if colorkey is not None:
            self.image = sprite_sheet.image_at(source_rect, colorkey)#FIXME: Issue #2: Sprite outlined in color_key color (with green color_key value)
        else:
            self.image = sprite_sheet.image_at(source_rect).convert_alpha()
            
        self.source_rect = source_rect
        self._position = [0, 0]
        self._old_position = [0, 0]
        self.rect = pygame.Rect(self.position[0], self.position[1], self.source_rect.width, self.source_rect.height)
        
    @property
    def position(self):
        return list(self._position)
    
    @position.setter
    def position(self, value):
        self._position = list(value)
        
    def update(self, delta):
        pass
    
class ScrollGame(object):
    
    def __init__(self):
        
        #Initialize pygame
        pygame.init()
        self.screen_size = (400, 400)
        self.screen = pygame.display.set_mode(self.screen_size)
        #Load map        #TODO: make this dynamic (i.e. process can load any map)
        self.tmx_data = util_pygame.load_pygame(get_map(MAP_FILENAME))
        self.map_data = pyscroll.TiledMapData(self.tmx_data)
        #Initialize renderer
        self.map_layer = pyscroll.BufferedRenderer(self.map_data, self.screen_size, clamp_camera = True)
        #Setup rendering group
        self.group = pyscroll.PyscrollGroup(map_layer = self.map_layer,
                                            default_layer = 0)
        print(self.tmx_data.get_layer_by_name("Player"))
        #Add Player
        player_rect = pygame.Rect(0, 400, 100, 100)
        self.player = Player(PLAYER_FILENAME, player_rect, (0, 255, 0))  
        self.group.add(self.player)
        pass
        
    def run(self):
        
        clock = pygame.time.Clock()
        self.quit = False
        while not self.quit:
            #Limit FPS
            delta = clock.tick(FPS)/1000.0
            #Handle input
            self._handle_input()
            #Update everything
            self._update(delta)
            #Draw everything
            self._draw()
            pygame.display.flip()
            
    def _handle_input(self):
        
        event = pygame.event.poll()
        while event:
            if event.type == pygame.QUIT:
                self.quit = True
            event = pygame.event.poll()
        pass
    
    def _update(self, delta):
        
        self.group.update(delta)
        #TODO: Check for collisions
        pass
    
    def _draw(self):
        
        self.group.center(self.player.rect.center)
        self.group.draw(self.screen)

if __name__ == '__main__':
    ScrollGame().run()