import pygame , sys , random , time



class Player(pygame.sprite.Sprite):
    def __init__(self, x, y , speed):
        super().__init__()  
        self.original_image = pygame.image.load('./images/player.png').convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect()  
        self.rect.midbottom = (x, y) 
        self.speed = speed
        self.shadow_effect = []  # each item is [rect, age]
        self.angle = 0 # to rotate when move
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        self.image = rotated_image
        self.rect = rotated_rect
        self.fz = False # when game over it freeze player

    def handle_input(self , screen_width):
        '''This Method handles player movement and screen limit'''
        keys = pygame.key.get_pressed()
        moving = False   # this for handle the shadow effect
        self.angle = 0 # noremal state 
        if keys[pygame.K_LEFT] and self.rect.left > 0:
                        moving = True
                        self.angle = 15
                        if keys[pygame.K_LSHIFT]: # when click left shift player sprints
                            self.rect.x -= self.speed * 2
                        else: 
                            self.rect.x -= self.speed

        # the following code is the same as above but for right movement 
        if keys[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.angle = -15
            moving = True
            if keys[pygame.K_LSHIFT]:
                self.rect.x += self.speed * 2

            else: 
                self.rect.x += self.speed

        if keys[pygame.K_LSHIFT] and moving:
            self.shadow_effect.append([self.rect.copy() , 15]) # get last player pos and its lifespan
        
        if len(self.shadow_effect) > 8: # limit it to 8 
            self.shadow_effect.pop(0)
              

    def draw_shadow(self  , surface):

        for shadow in self.shadow_effect:
            temp_image = self.image.copy()
            temp_image.set_alpha(80)
            surface.blit(temp_image, shadow[0])
        
        # decreases lifespan for shadow
        for shadow in self.shadow_effect:
            shadow[1] -= 1
        
        # if its lifespan ended delete it
        self.shadow_effect = [s for s in self.shadow_effect if s[1] > 0]



    def rotate_player(self):
        # Rotate the original image based on the current angle
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)

        # Set the new rect centered at the old center
        rotated_rect = rotated_image.get_rect(center=self.rect.center)

        # Update the current image and rect
        self.image = rotated_image
        self.rect = rotated_rect
    def update(self , screen_width , surface):
        self.handle_input(screen_width)
        self.draw_shadow(surface)
        self.rotate_player()
class Projectile(pygame.sprite.Sprite):
    def __init__(self, img, pos):
        super().__init__()
        self.image = pygame.image.load(img).convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()  # remove from group



class Game:
    def __init__(self):
        # Game Settings
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("Comic Sans MS", 30)
        pygame.mixer.init()
        pygame.display.set_caption("Space Invaders")
        self.WIDTH , self.HEIGHT = 1000 , 500
        self.display_surface = pygame.display.set_mode((self.WIDTH,self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.bg_img = pygame.transform.scale( pygame.image.load('./images/bg.jpg')  , (1000, 500)) 

        # Groups 
        self.player = Player(self.WIDTH/2 , self.HEIGHT , 4 )  # Centered in the bottom of screen
        self.player_sprite = pygame.sprite.GroupSingle()
        self.player_sprite.add(self.player)

        self.pro_sprite = pygame.sprite.Group()
        self.projectile_img = "./images/laser.png"
        # init values for other classes
        self.hit = False

        # score
        self.init_time =  time.time()
        self.final_score = 0

        # enemy spawn
        self.enemy_add_increament = 2000  # add an enemy every 2 seconds
        self.e_surface = pygame.image.load('./images/meteor.png')
        self.star_count = 0  # handle the enemy_add_increament
        self.enemies = []

        # game over text
        self.gm = self.font.render("GAME OVER", True, "white")
        self.st = self.font.render("Press SPACE to restart", True, "white")

        # sounds
        self.hit_sound = pygame.mixer.Sound("./audio/explosion.wav")
        self.laser_sound = pygame.mixer.Sound("./audio/laser.wav")
        self.gm_music = pygame.mixer.Sound("./audio/game_music.wav")
    def music(self):
         self.gm_music.play(-1)

    def draw(self):
        self.display_surface.blit(self.bg_img , (0,0))
          # Draw projectiles 
        self.pro_sprite.update()
        self.pro_sprite.draw(self.display_surface)

        self.player_sprite.draw(self.display_surface)
        if not self.hit:
            self.player_sprite.update(self.WIDTH, self.display_surface)

        # Check collision between projectiles and enemies
        for projectile in self.pro_sprite:
            for enemy in self.enemies[:]:
                if projectile.rect.colliderect(enemy):
                    self.enemies.remove(enemy)
                    projectile.kill()
                    break

    def shoot(self ):
        pos = self.player.rect.midtop
        projectile = Projectile(self.projectile_img, pos)
        self.pro_sprite.add(projectile)
        self.laser_sound.play()




    def enemy_spawn(self):
        # Add enemies every 2 seconds
        if self.star_count > self.enemy_add_increament and self.hit == False:
            for _ in range(3):
                enemy_x = random.randint(0, self.WIDTH - 101)
                e_rect = self.e_surface.get_rect()
                e_rect.x = enemy_x
                e_rect.y = 0
                self.enemies.append(e_rect)

            self.enemy_add_increament = max(200, self.enemy_add_increament - 50)
            self.star_count = 0

        # enemy movement and collision
        for enemy in self.enemies[:]: 
            enemy.y += 4
            if enemy.y > self.HEIGHT:
                self.enemies.remove(enemy)
            elif enemy.y + 84 >= self.player.rect.y and enemy.colliderect(self.player.rect):
                self.enemies.remove(enemy)
                self.hit = True
                self.final_score = round(time.time() - self.init_time)
                self.hit_sound.play()
                break

        # draw enemies
        for enemy in self.enemies:
            self.display_surface.blit(self.e_surface, enemy)

    def game_over(self):
            self.display_surface.blit(self.gm, (350, 150))
            self.display_surface.blit(self.st, (350, 250))
            self.player.image = pygame.Surface((0,0))
    


    def reset(self):
        self.hit = False
        self.player.rect.midbottom = (self.WIDTH/2 , self.HEIGHT)
        self.player.image = self.player.original_image
        self.init_time = time.time()  # RESET TIMER
        self.final_score = 0
        self.enemies.clear()
        self.pro_sprite.empty()
        self.enemy_add_increament = 2000 
        self.star_count = 0  
    

    def timer(self):
        if not self.hit:
            sec = round(time.time() - self.init_time)
            self.timing = self.font.render(f"Score : {sec}", True, "white")
        else:
            self.timing = self.font.render(f"Score : {self.final_score}", True, "white")

        self.display_surface.blit(self.timing, (80, 50))

    def run(self):
        self.music()
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and not self.hit:
                        self.shoot()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and  self.hit:
                        self.reset()


            self.star_count += self.clock.tick(self.fps) #returns the number of ms since game started 
            self.draw()
            self.enemy_spawn()
            if self.hit:
                self.game_over()
            self.time2 = time.time()
            self.sec = self.timer()
            pygame.display.update()

game = Game()
if __name__ == "__main__":
    game.run()

