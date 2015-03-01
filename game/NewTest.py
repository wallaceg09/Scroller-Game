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
from pygame.constants import *

RESOURCES_DIR = 'res'
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
    MOVE_SPEED = 400
    FALL_SPEED = 1000
    DELTA_V = 50
    GRAVITY = 50
    
    #State enum hack
    IDLE, MOVING_LEFT, MOVING_RIGHT, JUMPING, FALLING = range(5)
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
        self.velocity = [0, 0]
        self._position = [0, 0]
        self._old_position = [0, 0]
        self.rect = pygame.Rect(self._position[0], self._position[1], self.source_rect.width, self.source_rect.height)
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, self.rect.height * 0.2)
        self.feet.midbottom = self.rect.midbottom
        self.state = Player.IDLE
        self.gravity = True
        
    @property
    def position(self):
        return list(self._position)
    
    @position.setter
    def position(self, value):
        self._position = list(value)
        
    def update(self, delta):
        self.update_velocity()
        self.update_gravity()
        self._old_position = self._position[:]
        self._position[0] += self.velocity[0] * delta
        self._position[1] += self.velocity[1] * delta
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom
        pass
    
    def update_gravity(self):
        if self.gravity:
            self.velocity[1] += Player.GRAVITY
            self.velocity[1] = min(self.velocity[1] + Player.GRAVITY, Player.FALL_SPEED)
        else:
            self.velocity[1] = 0
        pass
    
    def update_velocity(self):
        if self.state == Player.IDLE:
            if self.velocity[0] < 0:
                self.velocity[0] = min(self.velocity[0] + Player.MOVE_SPEED, 0)
            elif self.velocity[0] > 0:
                self.velocity[0] = max(self.velocity[0] - Player.MOVE_SPEED, 0)
        elif self.state == Player.MOVING_LEFT:
            self.velocity[0] = max(self.velocity[0] - Player.DELTA_V, -Player.MOVE_SPEED)
        elif self.state == Player.MOVING_RIGHT:
            self.velocity[0] = min(self.velocity[0] + Player.DELTA_V, Player.MOVE_SPEED)
            
    def move_left(self):
        self.state = Player.MOVING_LEFT
    
    def move_right(self):
        self.state = Player.MOVING_RIGHT
        
    def set_idle(self):
        self.state = Player.IDLE
        
    #TODO: Remove
    def move_back(self, delta):
        self.velocity[1] = 0
        self._position = self._old_position[:]
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom
    
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
                                            default_layer = 4)
        print(self.tmx_data.get_layer_by_name("Player"))
        
        #Add Player
        player_rect = pygame.Rect(0, 400, 100, 100)
        self.player = Player(PLAYER_FILENAME, player_rect, (0, 255, 0))  
        self.group.add(self.player)
        
        #Initialize collision map
        self.collisions = list()
        for collidable in self.tmx_data.get_layer_by_name("Collision"):
            self.collisions.append(pygame.Rect(
                                               collidable.x, collidable.y,
                                               collidable.width, collidable.height))
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
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    self.quit = True
                elif event.key == K_RIGHT:
                    self.player.move_right()
                elif event.key == K_LEFT:
                    self.player.move_left()
            elif event.type == pygame.KEYUP:
                if event.key == K_RIGHT or event.key == K_LEFT:
                    self.player.set_idle()
            event = pygame.event.poll()
        pass
    
    def _update(self, delta):
        
        self.group.update(delta)
        #TODO: Check for collisions
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.collisions) > -1:
                sprite.gravity = False
                #sprite.move_back(delta)
            else:
                sprite.gravity = True
        pass
    
    def _draw(self):
        
        self.group.center(self.player.rect.center)
        self.group.draw(self.screen)

if __name__ == '__main__':
    ScrollGame().run()