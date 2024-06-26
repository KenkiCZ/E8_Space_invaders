import pygame, sys, random
from pygame.locals import *
from assets import *
from pygame.sprite import Sprite, Group

pygame.mixer.pre_init()
pygame.mixer.init()

FPS = 60
pygame.display.set_caption("Space Invaders")
FPS_CLOCK = None
DISPLAY_SURFACE = None
BASIC_FONT = None
BASIC_FONT_SIZE = 30

HP_WIDTH = 30
HP_HEIGHT = 10
HP_BORDER_SIZE = 2
SCORE_FONT_SIZE = 15

#load sounds
shoot_sound = pygame.mixer.Sound(INVADER_SHOOT)
explosion_sound = pygame.mixer.Sound(EXPLOSION)
minus_hp_sound = pygame.mixer.Sound(HEALTH_DOWN)
you_win = pygame.mixer.Sound(YOU_WIN)
game_over = pygame.mixer.Sound(GAME_OVER)
bg_music = pygame.mixer.music.load(BACKGROUND_MUSIC)
title_music = pygame.mixer.Sound(INTRO_MUSIC)

# Class for Game
class Game:
    def __init__(self, Invader_group, SpaceShip, Projectile_group_inv, Projectile_group_spa, key_pressed):
        # Create a game class with all the groups
        self.invader_group = Invader_group
        self.projectile_group_invaders = Projectile_group_inv
        self.projectile_group_spaceship = Projectile_group_spa
        self.spaceship = SpaceShip
        self.key_pressed = key_pressed
        self.game_active = False
        self.score = 0

    def update(self, DISPLAY_SURFACE):
        self.move_sprites()
        self.projectile_invader_collision()
        self.spaceship_collision()

    def move_sprites(self):
        for invader in self.invader_group:
            invader.update(self)
        self.projectile_movement()
        
    def projectile_invader_collision(self):
        collisions = pygame.sprite.groupcollide(self.projectile_group_spaceship, self.invader_group, True, True)
        for invader_list in collisions.values():
            for invader in invader_list:
                invader.kill()
                self.invader_group.remove(invader)
                self.score += 100
                explosion_sound.play()

        num_invaders = len(self.invader_group)
        if num_invaders == 0:
            win(self)

    def spaceship_collision(self):
        value = pygame.sprite.spritecollide(self.spaceship, self.projectile_group_invaders, True)
        if value:
            minus_hp_sound.play()
            self.spaceship.health -= 1
            self.score -= 50
            if self.score < 0:
                self.score = 0

            if self.spaceship.health == 0:
                lose(self)      
        
    def projectile_movement(self):
        if self.game_active:
            self.projectile_group_invaders.update()
            self.projectile_group_invaders.draw(DISPLAY_SURFACE)

            self.projectile_group_spaceship.update()
            self.projectile_group_spaceship.draw(DISPLAY_SURFACE)


# Class for SpaceShip
class SpaceShip(pygame.sprite.Sprite):  # Here we are inheriting from the pygame.sprite.Sprite class
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(SPACESHIP_IMG).convert_alpha(), (
        int(WINDOW_WIDTH * 0.15), int(WINDOW_WIDTH * 0.15)))
        # The order of self.rect: get rect from image -> set rect position
        self.rect = self.image.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 75))
        self.health = 3


# Class for Invader 
class Invader(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(INVADER_IMG).convert_alpha(),
                                            (int(WINDOW_WIDTH * 0.10), int(WINDOW_WIDTH * 0.10)))
        self.rect = self.image.get_rect(midbottom=(x_pos, y_pos))

        self.change_in_y = 0
        self.go_down = False
        self.direction = -1
        self.speed = 1

    def update(self, game: Game):
        if random.randint(0, 35*int(len(game.invader_group))) == 1 and 5 > len(game.projectile_group_invaders) and game.game_active:
            # Create a projectile
            shoot_projectile(game=game, position=(self.rect.midbottom[0], self.rect.midbottom[1]), direction=1, speed=4)
            shoot_sound.play()
        if game.game_active:
            self.movement(game)

    def movement(self, game: Game):
        if not self.go_down:
            self.rect.x += self.direction * self.speed
            if self.rect.right > WINDOW_WIDTH or self.rect.left < 0:
                for invader in game.invader_group:
                    invader.go_down = True
        else:
            self.rect.y += 1
            self.change_in_y += 1
            if self.change_in_y == 10:
                self.direction *= -1
                self.go_down = False
                self.change_in_y = 0
            if self.rect.bottom+30 > WINDOW_HEIGHT:
                lose(game=game)

# Class for Projectile
class Projectile(pygame.sprite.Sprite):
    def __init__(self, position, direction, speed):
        super().__init__()
        # create a surface with the size of 5x10
        self.image = pygame.Surface((5, 10))
        # fill the surface with red color
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(midbottom=position)
        self.speed = direction * speed

    def update(self):
        """"Move projectile by given distance of speed"""
        self.rect.y += self.speed
        # If projectile goes off the screen, remove it
        if self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT:
            self.kill()  # Remove the projectile if it goes off the screen

class KeyPressed:
    def __init__(self):
        self.type = None
        self.key = None
        self.is_held = False


def lose(game: Game):
    game.game_active = False
    draw_game(game)
    explosion_sound.play()
    display_lose_screen()
    game_over.play()
    end_game_timer()  


def win(game: Game):
    game.game_active = False
    draw_game(game)
    display_win_screen()
    end_game_timer()


def load_highscore():
    with open(file="Max_score.txt", mode="r", encoding="UTF-8") as f:
        return f.read()


def handle_keypress(event, game: Game):
    if event.key == pygame.K_SPACE:
        if not game.projectile_group_spaceship.sprites():
            shoot_projectile(game, position=game.spaceship.rect.midtop, direction=-1)
            shoot_sound.play()
        return

    if event.key == pygame.K_RIGHT or pygame.K_LEFT == event.key:
        game.key_pressed.type = event.type
        game.key_pressed.key = event.key
        game.key_pressed.is_held = True
        move_spaceship(game=game, change_distance=5)


def move_spaceship(game: Game, change_distance):
    if game.key_pressed.key == pygame.K_RIGHT:
        game.spaceship.rect.x += change_distance
    elif game.key_pressed.key == pygame.K_LEFT:
        game.spaceship.rect.x -= change_distance
    
    if game.spaceship.rect.x < 0:
        game.spaceship.rect.x = 0
    if game.spaceship.rect.x > WINDOW_WIDTH - game.spaceship.rect.width:
       game.spaceship.rect.x = WINDOW_WIDTH - game.spaceship.rect.width


def shoot_projectile(game: Game, position, direction, speed=10):
    # Create a projectile and add it to the projectile group
    projectile = Projectile(position, direction, speed)
    if direction == 1:
        game.projectile_group_invaders.add(projectile)
    elif direction == -1:
        game.projectile_group_spaceship.add(projectile)


def terminate():
    # End pygame and programme
    pygame.mixer.quit()
    pygame.quit()
    sys.exit()


def load_background(DISPLAY_SURFACE):
    # Load the background image and scale it to the size of the window
    DISPLAY_SURFACE.blit(source=pygame.transform.scale(pygame.image.load(BACKGROUND_IMG).convert_alpha(),
                                                       size=(WINDOW_HEIGHT, WINDOW_HEIGHT)),
                         dest=(0, 0, WINDOW_HEIGHT, WINDOW_WIDTH))


def draw_health_bar(game: Game):
    for hp in range(-1, game.spaceship.health-1):
        hp_rect = ((WINDOW_WIDTH/2 +hp*(HP_WIDTH+15) - HP_WIDTH/2), WINDOW_HEIGHT-20, HP_WIDTH, HP_HEIGHT)
        border_rect = ((WINDOW_WIDTH/2 +hp*(HP_WIDTH+15) - HP_WIDTH/2) - HP_BORDER_SIZE, WINDOW_HEIGHT-20 - HP_BORDER_SIZE, HP_WIDTH+HP_BORDER_SIZE*2, HP_HEIGHT+2*HP_BORDER_SIZE)
        pygame.draw.rect(DISPLAY_SURFACE, (0, 0, 0), border_rect)
        pygame.draw.rect(DISPLAY_SURFACE, (0, 255, 0), hp_rect)


def draw_score(score, text="Score: "):
    font = pygame.font.Font(FONT_PATH, SCORE_FONT_SIZE)
    score_text = font.render(text + str(score), True, (0, 0, 0))
    DISPLAY_SURFACE.blit(score_text, (WINDOW_WIDTH - score_text.get_width() - 10, WINDOW_HEIGHT-score_text.get_height()))


def display_win_screen():
    pygame.mixer.music.stop()
    you_win.play()
    font = pygame.font.Font(FONT_PATH, BASIC_FONT_SIZE)
    win_text=font.render("YOU WIN !",True,(255,255,255))
    DISPLAY_SURFACE.blit(win_text,(WINDOW_WIDTH // 2 - win_text.get_width() // 2, 200))
    pygame.display.flip()


def display_lose_screen():
    pygame.mixer.music.stop()
    font = pygame.font.Font(FONT_PATH, BASIC_FONT_SIZE)
    lose_text=font.render("GAME OVER",True,(255,255,255))
    DISPLAY_SURFACE.blit(lose_text,(WINDOW_WIDTH // 2 - lose_text.get_width() // 2, 200))
    invader_sprite_group = pygame.sprite.Group()
    for _ in range(30):
        invader = Invader(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT))
        invader_sprite_group.add(invader)

    for invader in invader_sprite_group:
        invader.rect.x += random.randint(-1, 1)
        invader.rect.y += random.randint(-1, 1)
        invader.rect.x = max(0, min(invader.rect.x, WINDOW_WIDTH - invader.rect.width))
        invader.rect.y = max(0, min(invader.rect.y, WINDOW_HEIGHT - invader.rect.height))
    pygame.display.flip()

  
def title_screen_animation(game: Game):
    invader_sprite_group = pygame.sprite.Group()
    for _ in range(10):
        invader = Invader(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT))
        invader_sprite_group.add(invader)

    font = pygame.font.Font(FONT_PATH, BASIC_FONT_SIZE)
    game_title=font.render("Space Invaders",True,(255,255,255))
    start_text=font.render("Press SPACE to Start",True,(255,255,255))

    highlighted_surface_title = pygame.Surface((game_title.get_width(), game_title.get_height()))
    highlighted_surface_title.fill((0, 0, 0))
    highlighted_surface_start = pygame.Surface((start_text.get_width(), start_text.get_height()))
    highlighted_surface_start.fill((0, 0, 0))

    title_music.play()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game.game_active = True
                title_music.stop()
                return
            if event.type == pygame.QUIT:
                terminate()
        pygame.mixer.music.play()
        load_background(DISPLAY_SURFACE=DISPLAY_SURFACE)
        draw_score(score=load_highscore(), text="HIGHSCORE: ")
        invader_sprite_group.update(game)
        invader_sprite_group.draw(DISPLAY_SURFACE)

        for invader in invader_sprite_group:
            invader.rect.x += 1
            if invader.rect.left > WINDOW_WIDTH:
                invader.rect.right = 0

        DISPLAY_SURFACE.blit(highlighted_surface_title, (WINDOW_WIDTH // 2 - game_title.get_width() // 2, 200))
        DISPLAY_SURFACE.blit(game_title, (WINDOW_WIDTH // 2 - game_title.get_width() // 2, 200))
        
        DISPLAY_SURFACE.blit(highlighted_surface_start, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, 300))
        DISPLAY_SURFACE.blit(start_text, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, 300))

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def end_game_timer():
    for cycle in range(180):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                terminate()
        FPS_CLOCK.tick(FPS)
        

def draw_game(main_game: Game):
    load_background(DISPLAY_SURFACE=DISPLAY_SURFACE)
    DISPLAY_SURFACE.blit(main_game.spaceship.image, main_game.spaceship.rect)
    main_game.invader_group.draw(DISPLAY_SURFACE)
    draw_health_bar(main_game)
    draw_score(score=main_game.score)


def load_game():
    invaders_list = [Invader(x_pos=x * 85, y_pos=y * 60) for x in range(1, 7) for y in range(1, 4)]
    invader_sprite_group = Group()
    for invader in invaders_list:
        invader_sprite_group.add(invader)
    return Game(Invader_group=invader_sprite_group, SpaceShip=SpaceShip(), Projectile_group_inv=Group(),
                     Projectile_group_spa=Group(), key_pressed= KeyPressed())

def main():
    global FPS_CLOCK, DISPLAY_SURFACE, BASIC_FONT
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', BASIC_FONT_SIZE)
    main_game = load_game()
    title_screen_animation(game=main_game)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                terminate()

            if event.type == pygame.KEYDOWN:
                handle_keypress(event=event,game=main_game)

            if event.type == pygame.KEYUP and event.key == main_game.key_pressed.key:
                main_game.key_pressed.is_held = False


        if main_game.game_active: 
            if main_game.key_pressed.is_held == True:
                move_spaceship(game=main_game, change_distance=2)
            draw_game(main_game=main_game)
            main_game.update(DISPLAY_SURFACE=DISPLAY_SURFACE)  # Update projectile positions

        else:
            if int(load_highscore()) < main_game.score:
                with open(file="Max_score.txt", mode="w", encoding="UTF-8") as f:
                    f.write(str(main_game.score))
            main_game = load_game()
            title_screen_animation(game=main_game)
            
  
        pygame.display.update()
        FPS_CLOCK.tick(60)


if __name__ == "__main__":
    main()
