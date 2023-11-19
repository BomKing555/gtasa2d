from pygame import *
from random import randint
'''Необходимые классы'''


#класс-родитель для спрайтов
class GameSprite(sprite.Sprite):
   #конструктор класса
   def __init__(self, player_image, player_x, player_y, player_speed, w = 65, h = 65):
       super().__init__()
       # каждый спрайт должен хранить свойство image - изображение
       self.image = transform.scale(image.load(player_image), (w, h))
       self.speed = player_speed
       # каждый спрайт должен хранить свойство rect - прямоугольник, в который он вписан
       self.rect = self.image.get_rect()
       self.rect.x = player_x
       self.rect.y = player_y

   def reset(self):
       window.blit(self.image, (self.rect.x, self.rect.y))


#класс-наследник для спрайта-игрока (управляется стрелками)
class Player(GameSprite):
    reload = 0 
    def update(self):
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
        if keys[K_w] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[K_s] and self.rect.y < win_height - 80:
            self.rect.y += self.speed
        if keys[K_SPACE]:
            if self.reload >= 30:
                self.fire()
                self.reload = 0
        if keys[K_ESCAPE]:
            if e.key == K.ESCAPE:
                game = quit()

        self.reload += 1
    
    def fire(self):
        bullet = Bullet('bullet.png', self.rect.x + self.rect.width - 15, self.rect.y - 30, 3, 30,50)
        bullets.add(bullet)


class Star(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.kill()

class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < -self.rect.height:
            self.kill()

class Ufo(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            ufos.remove(self)
            global ufo_miss
            ufo_miss += 1

class Boom(sprite.Sprite):
    def __init__(self, ufo_center, boom_sprites, booms) -> None:
        super().__init__() 
        #global booms, boom_sprites              
        self.frames = boom_sprites        
        self.frame_rate = 1   
        self.frame_num = 0
        self.image = boom_sprites[0]
        self.rect = self.image.get_rect()
        self.rect.center = ufo_center
        self.add(booms)
    
    def next_frame(self):
        self.image = self.frames[self.frame_num]
        self.frame_num += 1
        
    
    def update(self):
        self.next_frame()
        if self.frame_num == len(self.frames)-1:
            self.kill()

def sprites_load(folder:str, file_name:str, size:tuple, colorkey:tuple = None):    
    sprites = []
    load = True
    num = 1
    while load:
        try:
            spr = transform.scale(image.load(f'{folder}\\{file_name}{num}.png'),size)
            if colorkey: spr.set_colorkey((0,0,0))
            sprites.append(spr)
            num += 1
        except:
            load = False
    return sprites

def create_star():
    star = Star('star.png', randint(0, win_width), -30, 10, 20,20)
    stars.add(star)

def create_ufo():
    ufo = Ufo('bigsmoke.png', randint(0, win_width-60), -100, 2, 60, 110)
    ufos.add(ufo)

font.init()
font1 = font.Font(None, 36)

#Игровая сцена:
win_width = 1200
win_height = 800
window = display.set_mode((win_width, win_height), FULLSCREEN)
display.set_caption("GALAXY")
background = transform.scale(image.load("groove.jpg"), (win_width, win_height))


#Персонажи игры:
ship = Player('cj.png', win_width/2 - 30, win_height - 80, 10, 60, 130)

boom_sprites = sprites_load('boom', 'boom', (100,100), (0,0,0))

stars = sprite.Group()
ufos = sprite.Group()
bullets = sprite.Group()
booms = sprite.Group()

game = True
clock = time.Clock()
FPS = 60
finish = False
win = False
ticks = 0
ufo_miss = 0
goals = 0
ufo_spawn = 120


#музыка
mixer.init()
fon_sound = mixer.Sound('maintheme.ogg')
fire_sound = mixer.Sound('fire1.ogg')
boom_sound = mixer.Sound('boom1.ogg')   
fon_sound.set_volume(0.6)
fon_sound.play(-1)


while game:
   for e in event.get():
       if e.type == QUIT:
           game = False
    
   if not finish:

        if ticks % 20 == 0:
           create_star()

        if ticks % ufo_spawn == 0:
           create_ufo()
  

        window.blit(background,(0, 0))

        window.blit(
            font1.render('Пропущено: ' + str(ufo_miss), 1,
            (255, 255, 255)), (10,10)
        )

        stars.update()
        ufos.update()
        bullets.update()
        booms.update()

        collisions = sprite.groupcollide(ufos, bullets, True, True)
        for ufo, bullet in collisions.items():
            Boom(ufo.rect.center, boom_sprites, booms)
            goals += 1
            ufo_spawn -= 5

        stars.draw(window)
        ufos.draw(window)
        bullets.draw(window)
        booms.draw(window)

        for star in stars:
            star.update()
            star.reset()
        
        for ufo in ufos:
            ufo.update()
            ufo.reset()

        for bullet in bullets:
            bullet.update()
            bullet.reset()

        ship.update()
        ship.reset()

        if ufo_miss >= 3:
            finish = True
            win = False
        if goals == 15:
            finish = True
            win = True
        

   else:
        if win: 
            go = GameSprite('win.jpg', 0,0, 0, win_width, win_height)
            go.reset()
        else:
            go = GameSprite('gameover.jpg', 0,0, 0, win_width, win_height)
            go.reset()

   ticks += 1
   display.update()
   clock.tick(FPS)