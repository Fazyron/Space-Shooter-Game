import pygame as pg, asyncio
from sys import exit
from random import randint, uniform
import cv2
from pygame.sprite import LayeredUpdates

class Ship(pg.sprite.Sprite):
    def __init__(self,groups):
        super().__init__(groups)
        self.ship = pg.image.load('../SpaceShooter/sprites/ship.png').convert_alpha()
        self.ship_damaged = pg.image.load('../SpaceShooter/sprites/damaged ship.png').convert_alpha()
        self.ship_boost =  pg.image.load('../SpaceShooter/sprites/ship boost.png').convert_alpha()
        self.image = self.ship
        self.rect = self.image.get_rect(center = (width/2,height -50))

        self.can_shoot = True
        self.shoot_time = None

        self.angle = 0

        self.mask = pg.mask.from_surface(self.image)

        self.max_health = 5

        self.damaged_start = 0
        self.damaged = False

        self.laser_sfx = pg.mixer.Sound('../SpaceShooter/Sfx/laser.wav')
        self.laser_sfx.set_volume(0.2)
    
    def movement(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.rect.y -= 500*dt
            self.image = self.ship_boost
        else:
            self.image = self.ship
        if keys[pg.K_s]:
            self.rect.y += 400*dt
            self.image = self.ship
        if keys[pg.K_d]:
            self.rect.x += 400*dt
            self.image = self.ship
        if keys[pg.K_a]:
            self.rect.x -= 400*dt
            self.image = self.ship


        if self.rect.bottom >= height:
            self.rect.bottom = height
        if self.rect.right >= width:
            self.rect.right = width
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.left <= 0:
            self.rect.left = 0  
        
    def laser_shoot(self):
        if pg.mouse.get_pressed()[0] and self.can_shoot:
            self.can_shoot = False
            self.shoot_time = pg.time.get_ticks()
            Laser(laser_group,self.rect.midtop)
            all_sprites.add(Laser(laser_group,self.rect.midtop), layer=1)
            self.laser_sfx.play()

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pg.time.get_ticks()
            if current_time - self.shoot_time > 400:
                self.can_shoot = True
        

    def health(self):
        for health in range(self.max_health):
            screen.blit(fuel, (health*60,0))

    def handle_ship_collision(self):
        self.image = self.ship_damaged
        self.damaged_start = pg.time.get_ticks()
        self.damaged = True

    def ship_damaged_then_recover(self):
        if self.damaged:
            current_time = pg.time.get_ticks()
            if current_time - self.damaged_start > 200:
                self.image = self.ship
                self.damaged = False

    def update(self):
        self.health()
        self.movement()
        self.laser_shoot()
        self.laser_timer()
        self.ship_damaged_then_recover()



class Laser(pg.sprite.Sprite):
    def __init__(self,groups,pos):
        super().__init__(groups)
        self.image = pg.image.load('../SpaceShooter/sprites/laser.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom = pos)
        self.pos = pg.math.Vector2(self.rect.midbottom)

        self.speed = 500
        self.direction = pg.math.Vector2(0,-1)
 
        self.mask = pg.mask.from_surface(self.image)

    def laser_movement(self):
        self.pos += self.direction * self.speed * dt
        self.rect.midbottom = (round(self.pos.x),round(self.pos.y))

    def update(self):
        self.laser_movement()
        
        if self.rect.midbottom[1] < 0:
            self.kill()

class Meteor(pg.sprite.Sprite):
    def __init__(self,groups,pos,speed):
        super().__init__(groups)
        meteor_surface = pg.image.load('../SpaceShooter/sprites/meteorite.png').convert_alpha()
        self.meteor_size = pg.math.Vector2(meteor_surface.get_size()) * uniform(0.5,1.5)
        self.meteor_scaled_surface = pg.transform.scale(meteor_surface,self.meteor_size)
        self.image = self.meteor_scaled_surface
        self.rect = self.image.get_rect(center = pos)

        self.pos = pg.math.Vector2(self.rect.center)
        self.direction = pg.math.Vector2(uniform(-0.5,0.5),1)
        self.speed = speed

        self.rotation = 0
        self.rotation_speed = randint(80,100)

        self.mask = pg.mask.from_surface(self.image)

        self.shattered_meteorite_image = pg.image.load('../SpaceShooter/sprites/meteorite shatter.png')
        self.shattered_meteorite_scaled_surface = pg.transform.scale(self.shattered_meteorite_image,self.meteor_size)
        self.shattered = False
        self.shattered_start = None
        self.shattered_cooldown = 300

        self.explosion_sfx = pg.mixer.Sound('../SpaceShooter/Sfx/explosion.wav')
        self.explosion_sfx.set_volume(0.4)
        self.meteor_collision_sfx = pg.mixer.Sound('../SpaceShooter/sfx/meteor_collision.wav')
        self.meteor_collision_sfx.set_volume(0.4)


    def rotate(self):
        self.rotation += self.rotation_speed * dt
        rotated_surf = pg.transform.rotozoom(self.meteor_scaled_surface,self.rotation,1 )
        self.image = rotated_surf
        self.rect = self.image.get_rect(center = self.rect.center)
    
    def collide_with_laser(self):
        if pg.sprite.spritecollide(self,laser_group,True,pg.sprite.collide_mask):
            global score_game
            score_game += 1
            self.explosion_sfx.play()
            if self.shattered_start is None:
                self.shattered = True
                self.shattered_start = pg.time.get_ticks()
            
            
    
    def shattered_meteorite(self):
        if self.shattered == True:
            self.meteor_scaled_surface = self.shattered_meteorite_scaled_surface
    
    def shattered_meteorite_vanish(self):
        if self.shattered_start is not None:
            current_time = pg.time.get_ticks()
            if current_time - self.shattered_start >= self.shattered_cooldown:
                self.shattered = False
                self.kill()

    def collide_with_meteor(self):
        global screen_shake
        if pg.sprite.spritecollide(self,ship_group,False,pg.sprite.collide_mask):
            self.meteor_collision_sfx.play()
            ship_group.sprite.max_health -= 1
            screen_shake = 30
            ship_group.sprite.handle_ship_collision()
            self.kill()

    def update(self):
        self.pos += self.direction * self.speed * dt
        self.rect.center = (round(self.pos.x),round(self.pos.y))
        self.rotate()
        self.collide_with_laser()
        self.shattered_meteorite()
        self.shattered_meteorite_vanish()
        self.collide_with_meteor()
        if self.rect.top > height:
            self.kill()

class Score(pg.sprite.Sprite):
    def __init__(self):
        global font

    def display_score(self):
        score_text = f'Score : {score_game}'
        score_surf = font.render(score_text,True,'white')
        score_rect = score_surf.get_rect(topright = (width-30,10))
        screen.blit(score_surf,score_rect)

class Start_menu(pg.sprite.Sprite):
    def __init__(self):
        global font
        self.select = 'Select Difficulty'
        self.select_surf = font.render(self.select, True, 'white')
        self.select_rect = self.select_surf.get_rect(center = (width/2,200))

        self.text_list = ['EASY','MEDIUM','HARD']
        self.text_surfaces = [font.render(text,True,(255,255,255)) for text in self.text_list]
        self.text_rect = [surface.get_rect(center = (170 + i*280,height-200)) for i,surface in enumerate(self.text_surfaces)]

        self.click_sfx = pg.mixer.Sound('../SpaceShooter/Sfx/click.wav')
        self.click_sfx.set_volume(0.7)

    def render_text(self):
        mouse_pos = pg.mouse.get_pos()
        for i,rect in enumerate(self.text_rect):
            if rect.collidepoint(mouse_pos):
                self.text_surfaces[i] = font.render(self.text_list[i],True,(255,0,0))
            else:
                self.text_surfaces[i] = font.render(self.text_list[i],True,(255,255,255))
    def select_difficulty(self):
        global Game, Game_Menu, speed_meteor,score_game
        mouse_pos = pg.mouse.get_pos()
        for rect in self.text_rect:
            if pg.mouse.get_pressed()[0] and rect.collidepoint(mouse_pos):
                self.click_sfx.play()
                if rect == self.text_rect[0]:
                    speed_meteor = randint(150,250)
                elif rect == self.text_rect[1]:
                    speed_meteor = randint(250,350)
                elif rect == self.text_rect[2]:
                    speed_meteor = randint(350,450)

                Game_Menu = False
                Game = True

    def update(self):
        self.render_text()
        screen.blit(self.select_surf,self.select_rect)
        for text_surfaces,text_rect in zip(self.text_surfaces,self.text_rect):
            screen.blit(text_surfaces,text_rect)
        self.select_difficulty()





class End(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        global font
        self.retry_surf = None 
        self.retry_rect = None 

    def display(self):
        retry_text = 'RETRY'
        self.retry_surf = font.render(retry_text,True,'white')
        self.retry_rect = self.retry_surf.get_rect(center = (width/2,height/2))
        screen.blit(self.retry_surf,self.retry_rect)
    
    def remove(self):
        self.kill()

#SETUP
pg.init()
pg.mixer.init()
width , height = 900,700
org_screen = pg.display.set_mode((width,height))
screen = pg.display.set_mode((width,height))
pg.display.set_caption('AmbatuShoot')

#VIDEO
video_path = '../SpaceShooter/Video/SpaceBackground.mp4' 
cap = cv2.VideoCapture(video_path)
def restart_video(cap, video_path):
    cap.release()
    cap.open(video_path)


#IMAGES
background_image = pg.image.load('../SpaceShooter/sprites/galaxybackground.jpg').convert()
fuel = pg.image.load('../SpaceShooter/sprites/fuel.png').convert_alpha()
fuel = pg.transform.rotozoom( fuel,0,1.3)

#FONT
font = pg.font.Font('../SpaceShooter/orbitron.ttf',50)

#VARIABLES
score_game = 0
screen_shake = 0
speed_meteor = 0
clock = pg.time.Clock()

Game_Menu = True
Game = False
Game_End = False
mouse_pos = pg.mouse.get_pos()

#INSTANCES

all_sprites = LayeredUpdates()

ship_group = pg.sprite.GroupSingle()
ship = Ship(ship_group)
all_sprites.add(ship, layer=2)

laser_group = pg.sprite.Group()
meteor_group = pg.sprite.Group()

score = Score()
start_menu = Start_menu()
end = End()


#CUSTOM EVENT
meteor_timer = pg.event.custom_type()
pg.time.set_timer(meteor_timer,200)


#Music
spacebackgroundmusic ='../SpaceShooter/Sfx/spacebackgroundmusic.mp3'
pg.mixer.music.load(spacebackgroundmusic)
pg.mixer.music.play(-1)

ship_boost_sfx =pg.mixer.Sound('../SpaceShooter/Sfx/ship_boost.wav')
ship_boost_sfx.set_volume(0.3)
is_ship_boost_playing = False

#Refresh rate
dt = clock.tick(144)/1000


while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
                pg.quit()
                exit()

        if event.type == meteor_timer:
                    meteor_y = randint(-100,-50)
                    meteor_x = randint(-100,width+100)
                    Meteor(meteor_group,(meteor_x,meteor_y),speed_meteor)
                    all_sprites.add(Meteor(meteor_group,(meteor_x,meteor_y),speed_meteor), layer=1)

        if event.type == pg.KEYDOWN:
                if event.key == pg.K_w and not is_ship_boost_playing:
                    ship_boost_sfx.play()
                    is_ship_boost_playing = True
        if event.type == pg.KEYUP:
                if event.key == pg.K_w:
                    is_ship_boost_playing = False


    ret, frame = cap.read() 
    if not ret:
            restart_video(cap,video_path)
            continue

    frame = cv2.resize(frame, (width, height))
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    frame_surface = pg.surfarray.make_surface(frame.swapaxes(0, 1))


    if Game_Menu and not Game and not Game_End:
            screen.blit(frame_surface, (0, 0))
            start_menu.update()
            for laser in laser_group:
                laser.kill()
            laser_group.empty()
            for meteor in meteor_group:
                meteor.kill()
            meteor_group.empty()

            ship_group.sprite.rect.centerx = width/2
            ship_group.sprite.rect.centery = height-50
            score_game = 0
            ship_group.sprite.max_health = 5

    if Game and not Game_End and not Game_Menu:
            screen.blit(frame_surface, (0, 0))
            retry_sfx = pg.mixer.Sound('../SpaceShooter/sfx/retry.wav')
            retry_sfx.set_volume(0.7)


            all_sprites.update()
            all_sprites.draw(screen)

            score.display_score()

            if ship_group.sprite.max_health <= 0:
                Game = False
                Game_End = True
                retry_sfx.play()

    if Game_End and not Game_Menu and not Game:
            screen.blit(frame_surface, (0, 0))
            
            end.display()
            mouse_pos = pg.mouse.get_pos()
            if pg.mouse.get_pressed()[0] and end.retry_rect.collidepoint(mouse_pos):
                start_menu.click_sfx.play()
                Game_Menu = True
                Game_End = False
                end.remove()


    if screen_shake > 0:
            screen_shake -= 1
        
    render_offset = [0,0]
    if screen_shake:
            render_offset[0] = randint(0,8) - 4
            render_offset[1] = randint(0,8) - 4

    org_screen.blit(screen, render_offset)
    pg.display.update()
    clock.tick(144)

