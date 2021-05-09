import pygame, sys, random, math, csv, time
from pygame.locals import *
from abc import ABC, abstractmethod
from enum import IntEnum

pygame.init()

NUM_OF_ROW = 18
NUM_OF_COLUMN = 20

infoObject = pygame.display.Info()
WINDOW_WIDTH = infoObject.current_h # window's width
WINDOW_HEIGHT = int(WINDOW_WIDTH / NUM_OF_COLUMN * NUM_OF_ROW) # window's height
DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Tank')

FPS = 30    # frames per second
FPS_CLOCK = pygame.time.Clock()
FPI = 3 # number of frames per image
FPA = 30 # number of frames per action

# image size
TILE_SIZE = (WINDOW_WIDTH // NUM_OF_COLUMN, WINDOW_HEIGHT // NUM_OF_ROW)
CHARACTER_IMAGE_SIZE = (int(TILE_SIZE[0] * 2 / 3), int(TILE_SIZE[1] * 2 / 3))
PROJECTILE_SIZE = (int(TILE_SIZE[0] * 2 / 9), int(TILE_SIZE[1] * 1 / 3))
PLASMA_SIZE = (int(TILE_SIZE[0] * 2 / 9), int(TILE_SIZE[1] * 4 / 9))
ICON_SIZE = (int(TILE_SIZE[0] * 5 / 9), int(TILE_SIZE[1] * 5 / 9))

# load images
BACKGOUND_IMAGE = pygame.transform.scale(pygame.image.load('Images/background.png'), (WINDOW_WIDTH, WINDOW_HEIGHT))    # background image
TANK_IMAGE = pygame.transform.scale(pygame.image.load('Images/tank.png'), CHARACTER_IMAGE_SIZE)
PROJECTILE_IMAGE = pygame.transform.scale(pygame.image.load('Images/Light_Shell.png'), PROJECTILE_SIZE)
PLASMA_IMAGE = pygame.transform.scale(pygame.image.load('Images/plasma.png'), PLASMA_SIZE)

PROJECTILE = pygame.transform.scale(pygame.image.load('Images/Light_Shell.png'), ICON_SIZE)
HEART = pygame.transform.scale(pygame.image.load('Images/heart.png'), ICON_SIZE)
SKULL = pygame.transform.scale(pygame.image.load('Images/skull.jpg'), ICON_SIZE)
LIGHTNING = pygame.transform.scale(pygame.image.load('Images/lightning.png'), ICON_SIZE)
PLASMA = pygame.transform.scale(pygame.image.load('Images/plasma.png'), ICON_SIZE)

BRICK_TOPLEFT       = pygame.transform.scale(pygame.image.load('Images/brick_tl.png'), TILE_SIZE)
BRICK_TOP           = pygame.transform.scale(pygame.image.load('Images/brick_t.png'), TILE_SIZE)
BRICK_TOPRIGHT      = pygame.transform.scale(pygame.image.load('Images/brick_tr.png'), TILE_SIZE)
BRICK_LEFT          = pygame.transform.scale(pygame.image.load('Images/brick_l.png'), TILE_SIZE)
BRICK_CENTER        = pygame.transform.scale(pygame.image.load('Images/brick_c.png'), TILE_SIZE)
BRICK_RIGHT         = pygame.transform.scale(pygame.image.load('Images/brick_r.png'), TILE_SIZE)
BRICK_BOTTOMLEFT    = pygame.transform.scale(pygame.image.load('Images/brick_bl.png'), TILE_SIZE)
BRICK_BOTTOM        = pygame.transform.scale(pygame.image.load('Images/brick_b.png'), TILE_SIZE)
BRICK_BOTTOMRIGHT   = pygame.transform.scale(pygame.image.load('Images/brick_br.png'), TILE_SIZE)

ROCK_TOPLEFT        = pygame.transform.scale(pygame.image.load('Images/rock_tl.png'), TILE_SIZE)
ROCK_TOP            = pygame.transform.scale(pygame.image.load('Images/rock_t.png'), TILE_SIZE)
ROCK_TOPRIGHT       = pygame.transform.scale(pygame.image.load('Images/rock_tr.png'), TILE_SIZE)
ROCK_LEFT           = pygame.transform.scale(pygame.image.load('Images/rock_l.png'), TILE_SIZE)
ROCK_CENTER         = pygame.transform.scale(pygame.image.load('Images/rock_c.png'), TILE_SIZE)
ROCK_RIGHT          = pygame.transform.scale(pygame.image.load('Images/rock_r.png'), TILE_SIZE)
ROCK_BOTTOMLEFT     = pygame.transform.scale(pygame.image.load('Images/rock_bl.png'), TILE_SIZE)
ROCK_BOTTOM         = pygame.transform.scale(pygame.image.load('Images/rock_b.png'), TILE_SIZE)
ROCK_BOTTOMRIGHT    = pygame.transform.scale(pygame.image.load('Images/rock_br.png'), TILE_SIZE)

# types of icons
ICONS = {
   'PROJECTILE' : PROJECTILE,
   'HEART' : HEART,
   'SKULL' : SKULL,
   'LIGHTNING' : LIGHTNING,
   'PLASMA' : PLASMA 
}

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Direction
class RotateDirection(IntEnum):
    LEFT = 1
    RIGHT = -1

class GoDirection(IntEnum):
    AHEAD = 1
    BACK = -1


class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, speed = 4, numOfProjectiles = 1):
        super().__init__()
        self.x = x
        self.y = y
        self.speed = speed
        self.original_image = TANK_IMAGE
        self.image = self.original_image
        self.angle = 0
        self.rect = self.image.get_rect() 
        self.rect.center = (self.x, self.y)
        self.projectiles = pygame.sprite.Group()
        self.numOfProjectiles = numOfProjectiles
        self.plasmas = pygame.sprite.Group()
        self.numOfPlasmas = 0
        self.lastState = (self.x, self.y, self.angle, self.rect)
        self.blood = 1
       
    def rotate(self, direction, angle = 5):
        self.lastState = (self.x, self.y, self.angle, self.rect)
        self.angle = (self.angle + angle * direction) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def go(self, direction):
        self.lastState = (self.x, self.y, self.angle, self.rect)
        self.x = self.x - self.speed * math.sin(math.radians(self.angle)) * direction
        self.y = self.y - self.speed * math.cos(math.radians(self.angle)) * direction
        self.rect.center = (self.x, self.y)

    def shoot(self):
        if len(self.projectiles.sprites()) < self.numOfProjectiles:
            x = self.x - self.speed * math.sin(math.radians(self.angle))
            y = self.y - self.speed * math.cos(math.radians(self.angle))
            projectile = Projectile(x, y)
            direction = RotateDirection.LEFT
            if self.angle < 0:
                direction = RotateDirection.RIGHT 
            projectile.rotate(direction, self.angle)
            self.projectiles.add(projectile)

    def shoot_plasma(self):
        if len(self.plasmas.sprites()) < self.numOfPlasmas:
            x = self.x - self.speed * math.sin(math.radians(self.angle))
            y = self.y - self.speed * math.cos(math.radians(self.angle))
            plasma = Projectile(x, y, image = PLASMA_IMAGE, isPlasma = True)
            direction = RotateDirection.LEFT
            if self.angle < 0:
                direction = RotateDirection.RIGHT 
            plasma.rotate(direction, self.angle)
            self.plasmas.add(plasma)
    
    def update(self):
        DISPLAYSURF.blit(self.image, self.rect)
        #pygame.draw.rect(DISPLAYSURF, RED, self.rect, 1)
        self.projectiles.update()
        self.plasmas.update()


class Player(Tank):
    def __init__(self, x, y, speed = 4, numOfProjectiles = 1):
        super().__init__(x, y, speed, numOfProjectiles)
        self.key_ahead = None
        self.key_back = None
        self.key_left = None
        self.key_right = None
        self.key_shoot = None
        self.key_skill = None

    def set_key(self, key_ahead, key_back, key_left, key_right, key_shoot, key_skill):
        self.key_ahead = key_ahead
        self.key_back = key_back
        self.key_left = key_left
        self.key_right = key_right
        self.key_shoot = key_shoot
        self.key_skill = key_skill

    def move(self):
        keys = pygame.key.get_pressed() # keys is a dictionary. value is 1 if the key is being pressed, 0 otherwise
        if keys[self.key_left]:
            self.rotate(RotateDirection.LEFT)

        if keys[self.key_right]:
            self.rotate(RotateDirection.RIGHT)

        if keys[self.key_ahead]:
            self.go(GoDirection.AHEAD)

        if keys[self.key_back]:
            self.go(GoDirection.BACK)

class Enemy(Tank):
    def __init__(self, x, y, speed = TILE_SIZE[0], numOfProjectiles = 1):
        super().__init__(x, y, speed, numOfProjectiles)
        self.blood = 10
        self.moveCount = 0
        self.shootCount = 0

    def rotate(self, direction):
        super().rotate(direction, angle = 90)

    def go(self):
        super().go(direction = GoDirection.AHEAD)

    def move(self):
        if self.moveCount == 25:
            if random.randint(0,5) == 0:
                direction = random.choice([RotateDirection.LEFT, RotateDirection.RIGHT])
                self.rotate(direction)
            else:
                self.go()
            self.moveCount = 0
        else:
            self.moveCount += 1

    def shoot(self):
        if self.shootCount == 20:
            super().shoot()
            self.shootCount = 0
        else:
            self.shootCount += 1

    def action(self):
        self.move()
        self.shoot()

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, speed = 15, image = PROJECTILE_IMAGE, isPlasma = False):
        super().__init__()
        self.speed = speed
        self.original_image = image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.angle = 0
        self.lastState = (self.angle, self.rect)
        self.isPlasma = isPlasma

    def rotate(self, direction, angle = 5):
        self.angle = (self.angle + angle * direction) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        x, y = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def fly(self):
        x = self.rect.center[0] - self.speed * math.sin(math.radians(self.angle))
        y = self.rect.center[1] - self.speed * math.cos(math.radians(self.angle))
        self.rect.center = (x, y)

    def update(self):
        DISPLAYSURF.blit(self.image, self.rect)
        #pygame.draw.rect(DISPLAYSURF, RED, self.rect, 1)        


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.lastState = self.rect.topleft
        self.moveCount = 0
        self.blood = 2

    def update(self):
        DISPLAYSURF.blit(self.image, self.rect)

    def move(self):
        if self.moveCount == 20:
            self.moveCount = 0
            self.lastState = self.rect.topleft
            directions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
            direction = random.choice(directions)
            if direction == 'UP':
                self.rect.top -= TILE_SIZE[0]
            elif direction == 'DOWN':
                self.rect.top += TILE_SIZE[0]
            elif direction == 'LEFT':
                self.rect.left -= TILE_SIZE[0]
            elif direction == 'RIGHT':
                self.rect.left += TILE_SIZE[0]
        else:
            self.moveCount += 1



def drawGame(cars, enemies):
    DISPLAYSURF.blit(BACKGOUND_IMAGE, (0, 0))

    cars.update()
    enemies.update()
    rocks.update()
    bricks.update()
    projectiles.update()
    hearts.update()
    skulls.update()
    lightnings.update()
    plasmas.update()

    pygame.display.update()
    FPS_CLOCK.tick(FPS)


rocks = pygame.sprite.Group()
bricks = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
hearts = pygame.sprite.Group()
skulls = pygame.sprite.Group()
lightnings = pygame.sprite.Group()
plasmas = pygame.sprite.Group()
def game_init():
    draw_map('map.csv')   


def draw_map(url):
    mapFile = open(url, mode = 'r')
    tiles = csv.reader(mapFile, delimiter = ',')
    images = {
        'ROCK_TOPLEFT'      : ROCK_TOPLEFT,
        'ROCK_TOP'          : ROCK_TOP,
        'ROCK_TOPRIGHT'     : ROCK_TOPRIGHT,
        'ROCK_LEFT'         : ROCK_LEFT,
        'ROCK_CENTER'       : ROCK_CENTER,
        'ROCK_RIGHT'        : ROCK_RIGHT,
        'ROCK_BOTTOMLEFT'   : ROCK_BOTTOMLEFT,
        'ROCK_BOTTOM'       : ROCK_BOTTOM,
        'ROCK_BOTTOMRIGHT'  : ROCK_BOTTOMRIGHT,
        'BRICK_TOPLEFT'     : BRICK_TOPLEFT,
        'BRICK_TOP'         : BRICK_TOP,
        'BRICK_TOPRIGHT'    : BRICK_TOPRIGHT,
        'BRICK_LEFT'        : BRICK_LEFT,
        'BRICK_CENTER'      : BRICK_CENTER,
        'BRICK_RIGHT'       : BRICK_RIGHT,
        'BRICK_BOTTOMLEFT'  : BRICK_BOTTOMLEFT,
        'BRICK_BOTTOM'      : BRICK_BOTTOM,
        'BRICK_BOTTOMRIGHT' : BRICK_BOTTOMRIGHT        
    }

    firstLine = True
    for tile in tiles:
        if firstLine:
            firstLine = False
            continue
        row = int(tile[0])
        column = int(tile[1])
        image = tile[2]
        if image == '':
            continue
        elif image[0] == 'R':
            add_rock(row, column, images[image])
        elif image[0] == 'B':
            add_brick(row, column, images[image])

        
def add_rock(row, column, image):
    assert row >=0 and row < NUM_OF_ROW
    assert column >= 0 and column < NUM_OF_COLUMN
    rocks.add(Tile(column * TILE_SIZE[0], row * TILE_SIZE[0], image))

def add_brick(row, column, image):
    assert row >=0 and row < NUM_OF_ROW
    assert column >= 0 and column < NUM_OF_COLUMN
    bricks.add(Tile(column * TILE_SIZE[0], row * TILE_SIZE[0], image))

def add_icon(brick, icon):
    if icon == 'PROJECTILE':
        projectiles.add(Tile(brick.rect.left + (TILE_SIZE[0] - ICON_SIZE[0]) // 2, brick.rect.top + (TILE_SIZE[0] - ICON_SIZE[0]) // 2, ICONS[icon]))
    elif icon == 'HEART':
        hearts.add(Tile(brick.rect.left + (TILE_SIZE[0] - ICON_SIZE[0]) // 2 , brick.rect.top + (TILE_SIZE[0] - ICON_SIZE[0]) // 2, ICONS[icon]))
    elif icon == 'SKULL':
        skulls.add(Tile(brick.rect.left + (TILE_SIZE[0] - ICON_SIZE[0]) // 2, brick.rect.top + (TILE_SIZE[0] - ICON_SIZE[0]) // 2, ICONS[icon]))
    elif icon == 'LIGHTNING':
        lightnings.add(Tile(brick.rect.left + (TILE_SIZE[0] - ICON_SIZE[0]) // 2, brick.rect.top + (TILE_SIZE[0] - ICON_SIZE[0]) // 2, ICONS[icon]))
    elif icon == 'PLASMA':
        plasmas.add(Tile(brick.rect.left + (TILE_SIZE[0] - ICON_SIZE[0]) // 2, brick.rect.top + (TILE_SIZE[0] - ICON_SIZE[0]) // 2, ICONS[icon]))

def icon_selection_sound():
    iconSelectionSound = pygame.mixer.Sound('Sounds/noisecreations_SFX-NCFREE02_Flabby-Burd.wav')
    iconSelectionSound.play()

def brick_explosion_sound():
    tileProjectileCollisionSound = pygame.mixer.Sound('Sounds/pm_ag_20_3_abstract_guns_265.wav')
    tileProjectileCollisionSound.set_volume(0.1)
    tileProjectileCollisionSound.play()

def tank_projectile_collision_sound():
    tankProjectileCollisionSound = pygame.mixer.Sound('Sounds/PM_FSSF2_WEAPONS_D1_SHOT_323.wav')
    tankProjectileCollisionSound.set_volume(0.5)
    tankProjectileCollisionSound.play() 

def tank_explosion_sound():
    tankExplosionSound = pygame.mixer.Sound('Sounds/zapsplat_explosion_large_boom_slight_distance_25207.wav')
    #tankProjectileCollisionSound.set_volume(0.2)
    tankExplosionSound.play()  

def plasma_sound():
    plasmaSound = pygame.mixer.Sound('Sounds/zapsplat_science_fiction_retro_laser_beam_002_44337.wav')
    plasmaSound.set_volume(0.4)
    plasmaSound.play()          

def collision_handling(cars, enemies):
    # ensure window's boundary
    for car in cars.sprites() + enemies.sprites():
        if car.rect.left < 0 or car.rect.right > WINDOW_WIDTH or car.rect.top < 0 or car.rect.bottom > WINDOW_HEIGHT:
            car.x, car.y, car.angle, car.rect = car.lastState
        for projectile in car.projectiles.sprites():
            if projectile.rect.left < 0 or projectile.rect.right > WINDOW_WIDTH or projectile.rect.top < 0 or projectile.rect.bottom > WINDOW_HEIGHT:
                car.projectiles.remove(projectile)           
        for plasma in car.plasmas.sprites():
            if plasma.rect.left < 0 or plasma.rect.right > WINDOW_WIDTH or plasma.rect.top < 0 or plasma.rect.bottom > WINDOW_HEIGHT:
                car.plasmas.remove(plasma)

    for skull in skulls.sprites():
        if skull.rect.left < 0 or skull.rect.right > WINDOW_WIDTH or skull.rect.top < 0 or skull.rect.bottom > WINDOW_HEIGHT:
            skull.rect.topleft = car.lastState            

    # collision between cars and projectiles
    for car1 in cars.sprites() + enemies.sprites():
        for car2 in cars.sprites() + enemies.sprites():
            if car1 == car2:
                continue
            if pygame.sprite.spritecollide(car1, car2.projectiles, True):
                car1.blood -= 1
                if car1.blood == 0:
                    if type(car1) is Player:
                        cars.remove(car1)
                    elif type(car1) is Enemy:
                        enemies.remove(car1)
                    tank_explosion_sound()
                else:
                    tank_projectile_collision_sound()

    # collision between players and enemies
    pygame.sprite.groupcollide(cars, enemies, True, False)

    # collision between bricks/rocks and plasmas
    for car in cars.sprites() + enemies.sprites():
        for brick in pygame.sprite.groupcollide(bricks, car.plasmas, True, True):
            rocks.add(Tile(brick.rect.left, brick.rect.top, ROCK_CENTER))
            plasma_sound()
        for rock in pygame.sprite.groupcollide(rocks, car.plasmas, True, True):
            bricks.add(Tile(rock.rect.left, rock.rect.top, BRICK_CENTER))
            plasma_sound()

    # collision between rocks and players
    for car in pygame.sprite.groupcollide(cars, rocks, False, False).keys():
        car.x, car.y, car.angle, car.rect = car.lastState

    # collision between bricks and players
    for car in pygame.sprite.groupcollide(cars, bricks, False, False).keys():
        car.x, car.y, car.angle, car.rect = car.lastState

    # collision between rocks and enemies
    for car in pygame.sprite.groupcollide(enemies, rocks, False, False).keys():
        car.x, car.y, car.angle, car.rect = car.lastState
        direction = random.choice([RotateDirection.LEFT, RotateDirection.RIGHT])
        car.rotate(direction)


    # collision between bricks and enemies
    for car in pygame.sprite.groupcollide(enemies, bricks, False, False).keys():
        car.x, car.y, car.angle, car.rect = car.lastState
        direction = random.choice([RotateDirection.LEFT, RotateDirection.RIGHT])
        car.rotate(direction)

    # collision between rocks and projectiles
    for car in cars.sprites() + enemies.sprites():
        pygame.sprite.groupcollide(rocks, car.projectiles, False, True)

    # collision between bricks and projectiles
    for car in cars.sprites() + enemies.sprites():
        for brick in pygame.sprite.groupcollide(bricks, car.projectiles, False, True).keys():
            brick.blood -= 1
            if brick.blood == 0:
                if random.randint(0, 5) == 0:
                    icon = random.choice(list(ICONS))
                    add_icon(brick, icon)
                bricks.remove(brick)
                brick_explosion_sound()

    # collision between rocks and skulls   
    for skull in pygame.sprite.groupcollide(skulls, rocks, False, False).keys():
        skull.rect.topleft = skull.lastState

    # collision between bricks and skulls
    for skull in pygame.sprite.groupcollide(skulls, bricks, False, False).keys():
        skull.rect.topleft = skull.lastState

    # players get icons
    for car in pygame.sprite.groupcollide(cars, projectiles, False, True).keys():
        car.numOfProjectiles += 1
        icon_selection_sound()

    for car in pygame.sprite.groupcollide(cars, hearts, False, True).keys():
        car.blood += 1
        icon_selection_sound()

    for car in pygame.sprite.groupcollide(cars, skulls, False, True).keys():
        effects = ['SLOW SPEED', 'LOST PROJECTILE', 'LOST SKILL', 'SWAP DIRECTION']
        effect = random.choice(effects)
        if effect == 'SLOW SPEED':
            car.speed = 1
        elif effect == 'LOST PROJECTILE':
            car.numOfProjectiles = 1
        elif effect == 'LOST SKILL':
            car.numOfPlasmas = 0
        elif effect == 'SWAP DIRECTION':
            car.key_ahead, car.key_back = car.key_back, car.key_ahead
            car.key_left, car.key_right = car.key_right, car.key_left
        icon_selection_sound()

    for car in pygame.sprite.groupcollide(cars, lightnings, False, True).keys():
        car.speed += 1
        icon_selection_sound()

    for car in pygame.sprite.groupcollide(cars, plasmas, False, True).keys():
        car.numOfPlasmas += 1
        icon_selection_sound()



# This function sets up the game and implement the game's logic
def main():
    game_init()
    cars = pygame.sprite.Group()
    player = Player(765, 675)
    player2 = Player(120, 120)
    cars.add(player)
    cars.add(player2)

    player.set_key(key_ahead= K_UP, key_back= K_DOWN, key_left= K_LEFT, key_right= K_RIGHT, key_shoot= K_RETURN, key_skill = K_QUOTE)
    player2.set_key(key_ahead= K_w, key_back= K_s, key_left= K_a, key_right= K_d, key_shoot= K_SPACE, key_skill = K_LALT)    

    enemy1 = Enemy(787.5, 112.5)
    enemy2 = Enemy(112.5, 697.5)
    enemies = pygame.sprite.Group()
    enemies.add(enemy1)
    enemies.add(enemy2)

    running = True    
    while running: # main game loop
        for event in pygame.event.get():    # event game loop
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

                for car in cars.sprites():
                    if event.key == car.key_shoot:
                        car.shoot()
                    if event.key == car.key_skill:
                        if car.numOfPlasmas > 0:
                            car.shoot_plasma()

        for tank in cars.sprites():
            tank.move()

        for tank in cars.sprites():
            for projectile in tank.projectiles.sprites():
                projectile.fly()
            for plasma in tank.plasmas.sprites():
                plasma.fly()

        for tank in enemies.sprites():
            for projectile in tank.projectiles.sprites():
                projectile.fly()

        for enemy in enemies.sprites():
            enemy.action()

        for skull in skulls.sprites():
            skull.move()

        collision_handling(cars, enemies)

        drawGame(cars, enemies)
    
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()