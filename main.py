import pygame
from pygame.locals import *
import sys
import random
from assets import *
from pygame.sprite import Sprite, Group

FPS = 60
BLANK = None

# constants
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

# global variable to be used in multiple functions, default value is None
FPS_CLOCK = None
DISPLAY_SURFACE = None
BASIC_FONT = None
BASIC_FONT_SIZE = 30
BUTTONS = None


# Class for SpaceShip 
class SpaceShip(pygame.sprite.Sprite): # Here we are inheriting from the pygame.sprite.Sprite class
    def __init__(self):
        super().__init__()
        # The order of self.image: load image -> resize image -> rotate image
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(SPACESHIP_IMG).convert_alpha(), (int(WINDOW_WIDTH * 0.2), int(WINDOW_WIDTH * 0.2))), 180.0)
        # The order of self.rect: get rect from image -> set rect position
        self.rect = self.image.get_rect(midbottom=(WINDOW_WIDTH/2, WINDOW_HEIGHT-75))
    
# Class for Invader 
class Invader(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.x = x_pos
        self.y = y_pos
        # Same order as SpaceShip
        self.image = pygame.transform.scale(pygame.image.load(INVADER_IMG).convert_alpha(), (int(WINDOW_WIDTH * 0.10), int(WINDOW_WIDTH * 0.10)))
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

# Class for Projectile
class Projectile(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        # create a surface with the size of 5x10
        self.image = pygame.Surface((5, 10))
        # fill the surface with red color
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(midbottom=position)
        self.speed = 10 

    def update(self):
        """"Move projectile by given distance of speed"""
        self.rect.y -= self.speed
        # If projectile goes off the screen, remove it
        if self.rect.bottom < 0:
            self.kill()  # Remove the projectile if it goes off the screen

# Class for Game
class Game:
    def __init__(self, Invader_group, SpaceShip: SpaceShip, Projectile_group):
        # Create a game class with all the groups
        self.invader_group = Invader_group
        self.projectile_group = Projectile_group
        self.spaceship = SpaceShip


def handle_keypress(event, game: Game):
    # check if the key pressed is left or right
    if event == pygame.K_LEFT:
        game.spaceship.rect.x -= 10
    elif event == pygame.K_RIGHT:
        game.spaceship.rect.x += 10
    elif event == pygame.K_SPACE:
        shoot_projectile(game)


def shoot_projectile(game: Game):
    # Create a projectile and add it to the projectile group
    projectile = Projectile(game.spaceship.rect.midtop)
    game.projectile_group.add(projectile) 
    

def terminate():
    # End pygame and programme
    pygame.quit()
    sys.exit()    


def load_background(DISPLAY_SURFACE):
    # Load the background image and scale it to the size of the window
    DISPLAY_SURFACE.blit(source=pygame.transform.scale(pygame.image.load(BACKGROUND_IMG).convert_alpha(), size=(WINDOW_HEIGHT, WINDOW_HEIGHT)), dest=(0,0,WINDOW_HEIGHT,WINDOW_WIDTH))



def main():
    global FPS_CLOCK, DISPLAY_SURFACE, BASIC_FONT, BUTTONS, BLANK
    
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
    load_background(DISPLAY_SURFACE=DISPLAY_SURFACE)

    BASIC_FONT = pygame.font.Font('freesansbold.ttf', BASIC_FONT_SIZE)

    spaceship = SpaceShip()
    invaders_list = [Invader(x_pos=x*85, y_pos= y*60) for x in range(1,7) for y in range(1,4)]
    invader_sprite_group = Group()
    for invader in invaders_list:
        invader_sprite_group.add(invader)

    projectile_sprite_group = Group()  # Create a sprite group for projectiles

    main_game = Game(Invader_group=invader_sprite_group, SpaceShip=spaceship, Projectile_group=projectile_sprite_group)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                terminate()
            if event.type == pygame.KEYDOWN:
                handle_keypress(event=event.key, game=main_game)

        load_background(DISPLAY_SURFACE=DISPLAY_SURFACE)
        DISPLAY_SURFACE.blit(spaceship.image, spaceship.rect)
        invader_sprite_group.draw(DISPLAY_SURFACE)

        # Update and draw projectiles
        main_game.projectile_group.update()  # Update projectile positions
        main_game.projectile_group.draw(DISPLAY_SURFACE)  # Draw projectiles

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
