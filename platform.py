import pygame

BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
BLUE     = (   0,   255, 255)
RED      = ( 255,   0,   0)
GREEN    = (   0, 255,   0)
 

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
 
class Player(pygame.sprite.Sprite):

    def __init__(self, max_health, attack, defence):

        super().__init__()
 

        width = 40
        height = 60
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)
 

        self.rect = self.image.get_rect()
 

        self.vel_x = 0
        self.vel_y = 0

        self.attack = attack
        self.health = max_health
        self.max_health = max_health
        self.defence = defence
 

        self.level = None
        self.num_jumps = 2
        self.jump_counter = 0

        self.facing_right = True

    def jump_reset(self):
        self.jump_counter = self.num_jumps

    def on_right_collision(self, rect):
        self.rect.right = rect.left

    def on_left_collision(self, rect):
        self.rect.left = rect.right
        
    def on_bottom_collision(self, rect):
        self.rect.bottom = rect.top
        self.vel_y = 0
        self.jump_reset()
        
    def on_top_collision(self, rect):
        self.vel_y = 0
        self.rect.top = rect.bottom
 
 
    def update(self):
        """ Move the player. """

        self.calc_grav()

        self.rect.x += self.vel_x
 
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:

            if self.vel_x > 0:
                
                self.on_right_collision(block.rect)
            elif self.vel_x < 0:

                self.on_left_collision(block.rect)
                
 

        self.rect.y += self.vel_y
 

        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
 

            if self.vel_y > 0 and block.rect.top <= self.rect.bottom:
                self.on_bottom_collision(block.rect)
            elif self.vel_y < 0:
                self.on_top_collision(block.rect)


        if self.health <= 0:
            self.kill()
 
  
            
 
    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.vel_y == 0:
            self.jump_counter -= 1
            self.vel_y = 1
        else:
            self.vel_y += .35
 
  
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.vel_y >= 0:
            self.vel_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height
            self.jump_reset()
 
    def jump(self):
        """ Called when user hits 'jump' button. """

        self.jump_counter -= 1

        if self.jump_counter>=0:
            self.vel_y = -10

    def on_damange(self, amount):
        self.health = self.health - (amount - self.defence)
 
    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.vel_x = -6
        self.facing_right = False
 
    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.vel_x = 6
        self.facing_right = True
 
    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.vel_x = 0



class Bullet(pygame.sprite.Sprite):
    def __init__(self,pos_x, pos_y, vel_x, vel_y, damange = 1):
        super().__init__()
        width = 15
        height = 10
        self.image = pygame.Surface([width, height])
        self.image.fill((255,255,0))

        self.damange = damange
 
        # Set a referance to the image rect.
        self.rect = self.image.get_rect()

        self.rect.x=pos_x
        self.rect.y=pos_y
 
        # Set speed vector of player
        self.vel_x = vel_x
        self.vel_y = vel_y

    def update(self):

        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.kill()
 
        # If the player gets near the left side, shift the world right (+x)
        if self.rect.left < 0:
            self.rect.left = 0
            self.kill()
        
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

    def on_enemy_collision(self, enemy_list):
        if enemy_list:
            enemy_list[0].on_damange(self.damange)
            self.kill()
        
        

class Shooter(Player):
    def __init__(self, max_health, attack, defence):
        super().__init__(max_health, attack, defence)
    def create_bullet(self):
        if self.facing_right:
            bullet = Bullet(0,0,12,0, self.attack)
            bullet.rect.topleft = self.rect.topright
        else:
            bullet = Bullet(0,0,-12,0, self.attack)
            bullet.rect.topright = self.rect.topleft

        return bullet
    def shoot_player(self):
        self.level.spawn_player_bullet(self.create_bullet())
        
    def shoot_enemy(self):
        self.level.spawn_enemy_bullet(self.create_bullet())
        
        
        

class Enemy(Player):
    def __init__(self, max_health, attack, defence):
        super().__init__(max_health, attack, defence)
class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """
 
    def __init__(self, width, height):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this
            code. """
        super().__init__()
 
        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)
 
        self.rect = self.image.get_rect()
 
class Level(object):
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """
 

    platform_list = None
    enemy_list = None
 

    background = None
 
    def __init__(self, player):
        """ Constructor. Pass in a handle to player. Needed for when moving platforms
            collide with the player. """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.player = player
        self.players.add(player)
 

    def update(self):
        """ Update everything in this level."""

        collissions = pygame.sprite.groupcollide(self.player_bullets, self.enemy_list,False,False)

        for bullet in self.player_bullets:
            bullet.on_enemy_collision(collissions.get(bullet,[]))
        self.players.update()

        if self.player.rect.right > SCREEN_WIDTH:
            self.player.rect.right = SCREEN_WIDTH
 

        if self.player.rect.left < 0:
            self.player.rect.left = 0
        self.platform_list.update()
        self.enemy_list.update()
        self.player_bullets.update()
        self.enemy_bullets.update()

        

        

        
 
    def draw(self, screen):
        """ Draw everything on this level. """
 

        screen.fill(BLUE)
 

        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        self.players.draw(screen)
        self.player_bullets.draw(screen)
        self.enemy_bullets.draw(screen)

    def spawn_player_bullet(self, bullet):
        self.player_bullets.add(bullet)

    def spawn_enemy_bullet(self, bullet):
        self.enemy_bullets.add(bullet)
 
 

class Level_01(Level):
    """ Definition for level 1. """
 
    def __init__(self, player):
        """ Create level 1. """
 

        Level.__init__(self, player)

        player.rect.x = 340
        player.rect.y = SCREEN_HEIGHT/2 - player.rect.height
        player.level = self
 

        level = [[210, 70, 500, 500],
                 [210, 70, 200, 400],
                 [210, 70, 600, 300],
                 ]

        enemy = Enemy(5,1,0)
        enemy.level=self
        enemy.rect.x = 640
        enemy.rect.y = SCREEN_HEIGHT/2 - player.rect.height

        self.enemy_list.add(enemy)

 
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)
 
def main():
    """ Main Program """
    pygame.init()

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
 
    pygame.display.set_caption("Platform")
 

    player = Shooter(10,1,0)
 

    level_list = []
    level_list.append( Level_01(player) )
 

    current_level_no = 0
    current_level = level_list[current_level_no]
 
    
 
    
 

    done = False
 

    clock = pygame.time.Clock()

    while not done:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                done = True
 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()
                if event.key == pygame.K_SPACE:
                    player.shoot_player()
 
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.vel_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.vel_x > 0:
                    player.stop()
            
 

        current_level.update()
 

        current_level.draw(screen)

        clock.tick(60)

        pygame.display.flip()
 

    pygame.quit()
 
if __name__ == "__main__":
    main()
