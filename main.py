import pygame
import random
import os
import pyperclip
import sys
import subprocess

from io import StringIO

#初始畫面參數
GAME_NAME = 'Codebot Adventures'
# 畫面參數
FPS = 60
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750
# 顏色
WHITE = (255, 255, 255)
BLACK = (0,0,0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GOLD = (255,215,0)
# 動作參數
JUMP_SPEED = -10.5
GRAVITY = 0.2
# 平台參數
PLATFORM_WIDTH = 300
PLATFORM_HEIGHT = 20
PLATFORM_COLOR = GREEN
PLATFORM_COUNT = 3
PLATFORM_RECT = [[200,650],[700,650],[500,450],[20,300],[500,175],[900,400]]
#動畫頻率
WALK_FREQUENCY =3
#碰撞參數 (以幀數計算)
INVINCIBILITY_DURATION = 120  # 2秒無敵時間

#遊戲初始設定
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("期末project")
clock = pygame.time.Clock()

#載入圖片
#角色圖片
L_walk_img = []
for i in range(8):
    L_walk_img.append(pygame.image.load(os.path.join("image","player",f"walk{i}.png")).convert_alpha())
#背景圖片
background = pygame.image.load(os.path.join("image","background","laboratory2.png")).convert_alpha()
ini_background = pygame.image.load(os.path.join("image","background","laboratory1.png")).convert_alpha()
#零件
component_img = []
for i in range(3):
    component_img.append(pygame.image.load(os.path.join("image","component",f"component{i}.png")).convert_alpha())
#平台
platform_img = pygame.image.load(os.path.join("image","background","platform.png")).convert_alpha()
#寶箱
chest_img = []
for i in range(3):
    chest_img.append(pygame.image.load(os.path.join("image","chest",f"chest{i}.png")).convert_alpha())
#子彈
bullet_img = pygame.image.load(os.path.join("image","player","bullet.png")).convert_alpha()
#生命值
lives_img = pygame.image.load(os.path.join("image","player","lives.png")).convert_alpha()
lives_img = pygame.transform.scale(lives_img,(50,50))


#敵人圖片
foe2_walk_img = []
for i in range(9):
    foe2_walk_img.append(pygame.image.load(os.path.join("image","foe",f"robot2_{i}.png")).convert_alpha())
foe1_walk_img = []
for i in range(11):
    foe1_walk_img.append(pygame.image.load(os.path.join("image","foe","foe1",f"robot1_{i}.png")).convert_alpha())


#生成字串函式
font_name = os.path.join("font","GenJyuuGothic-Bold.ttf")

#設定顯示字串的函式
def draw_text(surf,text,size,x,y,text_color, outline_color = WHITE, outline_width=2):
    font = pygame.font.Font(font_name,size)

    text_surface = font.render(text,True,text_color)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y

    outline_surface = font.render(text, True, outline_color)
    outline_rect = outline_surface.get_rect()
    outline_rect.centerx = x
    outline_rect.top = y

    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                surf.blit(outline_surface, outline_rect.move(dx, dy))

    surf.blit(text_surface,text_rect)

#顯示當前角色生命值
def draw_lives(surf,lives,img,x,y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 50*i
        img_rect.y = y
        surf.blit(img,img_rect)

#顯示敵人血條
def draw_foe_health(surf,hp,x,y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 50
    BAR_HEIGHT = 10
    fill = (hp/100) * BAR_LENGTH
    outline_rect = pygame.Rect(x,y,BAR_LENGTH,BAR_HEIGHT)
    fill_rect = pygame.Rect(x,y,fill,BAR_HEIGHT)
    pygame.draw.rect(surf,RED,fill_rect)
    pygame.draw.rect(surf,WHITE,outline_rect,2)

#顯示能量條
def draw_player_energy(surf,energy,x,y):
    if energy > 100:
        energy = 100
    BAR_LENGTH = 200
    BAR_HEIGHT = 30
    outline_rect = pygame.Rect(x,y,BAR_LENGTH,BAR_HEIGHT)
    fill = BAR_LENGTH
    fill_rect = pygame.Rect(x,y,fill,BAR_HEIGHT)
    pygame.draw.rect(surf,WHITE,fill_rect)
    fill = (energy/100) * BAR_LENGTH
    fill_rect = pygame.Rect(x,y,fill,BAR_HEIGHT)
    pygame.draw.rect(surf,GOLD,fill_rect)
    pygame.draw.rect(surf,BLACK,outline_rect,2)

#設定初始畫面
def draw_init():
    draw_text(screen, GAME_NAME,64,SCREEN_WIDTH/2,200,BLACK)
    draw_text(screen, '上下左右鍵移動 Z:射擊',32,SCREEN_WIDTH/2,400,BLACK)
    draw_text(screen, "輸入任意鍵以開始...",32,SCREEN_WIDTH/2,500,BLACK)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYUP:
                waiting = False

#設定結算畫面
def draw_gameover():
    draw_text(screen, "GAME OVER",64,SCREEN_WIDTH/2,200,BLACK)
    draw_text(screen, "按下任意鍵以結束...",32,SCREEN_WIDTH/2,500,BLACK)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYUP:
                waiting = False
    pygame.quit()

# 角色設定
class Player(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # 物體參數
        self.image = pygame.transform.scale(L_walk_img[0], (50,90))
        self.face_right = True
        self.lives = 3
        self.energy = 0
        # 物體初始位置
        self.rect = self.image.get_rect()
        self.rect.centerx = 100
        self.rect.bottom = 700
        self.on_ground = False
        # 物體初始速度
        self.vel_x = 0
        self.vel_y = 0
        #走路動畫參數
        self.walk_count = 0
        self.walk_degree = 0
        #碰撞參數
        self.invincible = False
        self.invincibility_timer = 0

    def update(self, platforms):
        self.vel_x = 0

        # 碰撞偵測
        self.on_ground = False
        for platform in platforms:
            if self.rect.right > platform.rect.left and self.rect.left < platform.rect.right:
                if self.rect.bottom >= platform.rect.top-4 and self.rect.bottom < platform.rect.bottom:
                    self.rect.bottom = platform.rect.top-4
                    self.on_ground = True
                    self.vel_y = 0
                if self.rect.top > platform.rect.top and self.rect.top < platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
            if self.rect.bottom > platform.rect.top and self.rect.top < platform.rect.bottom and self.rect.right < platform.rect.right and self.rect.right > platform.rect.left:
                self.rect.right = platform.rect.left
                self.vel_x = 0
            if self.rect.bottom > platform.rect.top and self.rect.top < platform.rect.bottom and self.rect.left < platform.rect.right  and self.rect.left > platform.rect.left:
                self.rect.left = platform.rect.right
                self.vel_x = 0
      
        # 碰到地面Y方向速度為0
        if self.rect.bottom >= SCREEN_HEIGHT-10:
            self.rect.bottom = SCREEN_HEIGHT-10
            self.on_ground = True
            self.vel_y = 0

        # 在空中時Y方向速度為預設重力給的速度
        if self.on_ground:
            self.vel_y = 0
        else:
            self.vel_y += GRAVITY
        # 鍵盤操作左右跳
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.vel_x = -2
            self.face_right = False
        if keys[pygame.K_RIGHT]:
            self.vel_x = 2
            self.face_right = True
        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = JUMP_SPEED

        # 依照當前X.Y速度運動
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # 控制人物左右移動範圍
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH

        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False

    def hit(self):
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincibility_timer = INVINCIBILITY_DURATION

    def walking(self):
        if self.vel_x != 0:
            self.walk_count += 1
            if self.walk_count >= 10:  # 控制動畫播放速度
                self.walk_count = 0
                self.walk_degree = (self.walk_degree + 1) % 8
            self.image = pygame.transform.scale(L_walk_img[self.walk_degree], (60, 100))
            if self.face_right:
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.walk_degree = 0
            self.image = pygame.transform.scale(L_walk_img[0], (60, 100))
            if self.face_right:
                self.image = pygame.transform.flip(self.image, True, False)
        return self.walk_degree  
    
    def shoot(self):
        if self.face_right:
            bullet = Bullet(self.rect.right, self.rect.centery, 10)
        else:
            bullet = Bullet(self.rect.left, self.rect.centery, -10) 
        all_sprites.add(bullet)
        bullets.add(bullet)

class Foe(pygame.sprite.Sprite):
    def __init__(self,platform):
        pygame.sprite.Sprite.__init__(self)
        # 物體參數
        self.image = pygame.Surface((50, 90))
        self.image = pygame.transform.scale(foe2_walk_img[0], (60,100))
        self.face_right = False
        self.health = 100
        # 物體初始位置
        self.rect = self.image.get_rect()
        self.rect.centerx = platform.rect.centerx
        self.rect.bottom = platform.rect.top - 10
        self.on_ground = False
        # 物體初始速度
        self.vel_x = random.randint(1, 3)
        self.vel_y = 0
        #走路動畫參數
        self.walk_count = 0
        self.walk_degree = 0

    def update(self, platform):
        # 在空中時Y方向速度為預設重力給的速度
        self.vel_y += GRAVITY

        # 依照當前X.Y速度運動
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # 碰到地面Y方向速度為0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.on_ground = True
            self.vel_y = 0
        
        if self.vel_x < 0 :
            self.face_right == False
        elif self.vel_x > 0:
            self.face_right == True
        # 控制人物左右移動範圍
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH

        # 碰撞偵測
        for platform in platforms:
            if pygame.sprite.collide_rect(self, platform):
                collision = self.rect.colliderect(platform.rect)
                if collision:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        self.on_ground = True
                        self.vel_y = 0
                    elif self.vel_y < 0:
                        self.rect.top = platform.rect.bottom
                        self.vel_y = 0
                    if self.vel_x > 0:
                        if self.rect.bottomright >= platform.rect.topright:
                            self.vel_x = -random.randint(1, 2)
                            self.vel_y = 0
                            self.face_right = False
                    elif self.vel_x < 0:
                        if self.rect.bottomleft <= platform.rect.topleft:
                            self.vel_x = random.randint(1, 2)
                            self.face_right = True
                            self.vel_y = 0
    def walking(self):
        if self.vel_x != 0:
            self.walk_count += 1
            if self.walk_count >= 30:  # 控制動畫播放速度
                self.walk_count = 0
                self.walk_degree = (self.walk_degree + 1) % 9
            self.image = pygame.transform.scale(foe2_walk_img[self.walk_degree], (60, 100))
            if self.face_right:
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.walk_degree = 0
            self.image = pygame.transform.scale(foe2_walk_img[0], (60, 100))
            if self.face_right:
                self.image = pygame.transform.flip(self.image, True, False)
        return self.walk_degree  
# 平台設定
class Platform(pygame.sprite.Sprite):

    def __init__(self, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        # 平台樣式
        self.image = pygame.Surface((width, height))
        self.image = pygame.transform.scale(platform_img, (width, height))
        # 平台位置
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

#輸入框設定
class InputBox(pygame.sprite.Sprite,):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.box_width = SCREEN_WIDTH-100   #輸入框大小
        self.box_height = SCREEN_HEIGHT-100
        self.cursor_x = 20            #游標座標
        self.cursor_y = 20
        self.image = pygame.Surface((self.box_width, self.box_height))
        self.image.fill((20, 20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH/2
        self.rect.top = 50
        self.problem={
            "problem" : "add two numbers",
            "input": ["1\n2", "3\n4"],
            "expected_output": ["3\n", "7\n"]
        }

        self.active = False #是否選中輸入框
        self.input_set = set() #現在選中的鍵值
        self.input_interval = {} #選中的鍵值冷卻時間
        self.text = f"\"\"\"\r\n{self.problem['problem']}\r\n\r\n\"\"\"" #文本

        self.font = pygame.font.SysFont("Yozai-Medium.ttf", 30)
    
    def update(self):
        self.image.fill((20, 20, 20))
        
        if self.active:
            current_time = pygame.time.get_ticks()
            self.text_x = 20
            self.text_y = 20
            for i in self.text.split("\r\n"):
                self.text_surface = self.font.render(i, True,(200, 200, 200), (20, 20, 20))
                self.image.blit(self.text_surface, (self.text_x, self.text_y))
                self.text_y += 20

            self.cursor_x = self.text_surface.get_width()+23
            self.cursor_y = self.text_y - 20

            pygame.draw.rect(self.image, (200, 200, 200), [10, 10, self.box_width-20, self.box_height-20], 2) #灰色邊框
            if(current_time%1000 > 500):   #游標閃爍
                pygame.draw.line(self.image, (200, 200, 200), (self.cursor_x, self.cursor_y), (self.cursor_x, self.cursor_y+15), 2)
            
            for i in self.input_set:
                if(current_time-self.input_interval[i] > 155):
                    self.input_interval[i] = current_time
                    if i == '\b':
                        self.text = self.text[:-1]
                    else:
                        self.text += i

        else:
            pygame.draw.rect(self.image, (140, 140, 140), [10, 10, self.box_width-20, self.box_height-20], 2) #灰色邊框
            pygame.draw.line(self.image, (20, 20, 20), (self.cursor_x, self.cursor_y), (self.cursor_x, self.cursor_y+10), 2)


    def execute_code(self, user_code, problem):
        results = []
        ap = True
        for i in range(len(problem["input"])):
            sys.stdin = StringIO(problem["input"][i])
            output = StringIO()
            sys.stdout = output
            exec(user_code, {}, {})
            if output.getvalue() == problem["expected_output"][i]:
                results.append(f"Test case {i+1}: Passed")
            else:
                results.append(f"Test case {i+1}: Failed\nExpected {problem['expected_output'][i].split()}\nbut got {output.getvalue().split()}")
                ap = False
            sys.stdout = sys.__stdout__
        return (results, ap)

    def event_process(self, event): #處理事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
        if event.type == pygame.MOUSEBUTTONUP:
            pass            
        if event.type == pygame.KEYDOWN:
            ctrl_pressed = pygame.key.get_mods() & pygame.KMOD_CTRL
            if ctrl_pressed and event.key == pygame.K_v:
                # 检测到 Ctrl+V 组合键
                self.text += pyperclip.paste()
                
            elif event.key == pygame.K_BACKSPACE:
                self.input_set.add('\b')
                self.input_interval['\b'] = -100
            elif event.key == pygame.K_RETURN:
                self.input_set.add('\r\n')
                self.input_interval['\r\n'] = -100
            elif event.key == pygame.K_TAB:
                self.input_set.add('    ')
                self.input_interval['    '] = -100
            elif event.key == pygame.K_KP_ENTER:
                results, ap = self.execute_code(self.text, self.problem)
                self.text += '\r\n'
                for i in results:
                    self.text += '\r\n'
                    self.text += i
                return ap
            elif event.key == pygame.K_ESCAPE:
                self.kill()
            else:
                self.input_set.add(event.unicode)
                self.input_interval[event.unicode] = -100
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                self.input_set.remove('\b')
            elif event.key == pygame.K_RETURN:
                self.input_set.remove('\r\n')
            elif event.key == pygame.K_TAB:
                self.input_set.remove('    ')
            else:
                self.input_set.discard(event.unicode)

    
    def inputbox_print(self, s):
        self.text += s

#解題環節
def problem_challenge():
    subprocess.run(['python', 'C:\\Users\\hongc\\OneDrive\\桌面\\PYGAME\\input_box.py'])
   

# 寶箱設定
class Chest(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        #寶箱樣式
        self.image = pygame.Surface((60, 60))
        self.image = pygame.transform.scale(chest_img[0], (60, 60))
        #寶箱位置
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# 零件設定
class Component(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        #零件樣式
        self.image = pygame.Surface((60, 100))
        self.image = pygame.transform.scale(component_img[random.randint(0,2)], (50, 60))
        #零件位置
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# 子彈設定
class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, vel_x):
        pygame.sprite.Sprite.__init__(self)
        # 子彈參數
        self.image = pygame.Surface((30, 20))
        self.image = pygame.transform.scale(bullet_img,(30,20))
        if vel_x < 0:
            self.image = pygame.transform.flip(self.image, True, False)
        # 子彈初始位置
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        # 物體初始速度
        self.vel_x = vel_x

    def update(self,*args):
        self.rect.centerx += self.vel_x
        if self.rect.centerx < 0 or self.rect.centerx > SCREEN_WIDTH:
            self.kill()

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
platforms = pygame.sprite.Group()
foes = pygame.sprite.Group()
components = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# 生成平台/敵人/門
for i in range(len(PLATFORM_RECT)):
    platform_width = PLATFORM_WIDTH  
    platform_height = PLATFORM_HEIGHT
    platform = Platform(PLATFORM_RECT[i][0], PLATFORM_RECT[i][1], platform_width, platform_height)

    all_sprites.add(platform)
    platforms.add(platform)

    if i == 5:
        continue

    foe = Foe(platform)
    all_sprites.add(foe)
    foes.add(foe)

#生成寶箱
chest = Chest(PLATFORM_RECT[5][0] + 125, PLATFORM_RECT[5][1] - 57)
all_sprites.add(chest)

# 遊戲迴圈
                
with open('result.txt', 'w') as f:
    f.write("RESULT:")
show_init = True
running = True
game_over = False
while running:
    if show_init:
        ini_background = pygame.transform.scale(ini_background,(1600,1000))
        screen.blit(ini_background,(-175,-160))
        draw_init()
        show_init = False
    
    if game_over:
        draw_gameover()


    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                player.shoot()

    all_sprites.update(platforms)
    all_sprites.update(foes)

    player.walking()
    for foe in foes:
        foe.walking()

    #當玩家與敵人碰撞時會扣一點生命值
    if  not player.invincible:
        player_hits = pygame.sprite.spritecollide(player, foes, False, pygame.sprite.collide_rect)
        for hit in player_hits:
            player.hit()
            if player.lives <= 0:
                screen.fill(BLACK)
                ini_background = pygame.transform.scale(ini_background,(1600,1000))
                screen.blit(ini_background,(-175,-160))
                draw_gameover()

    #當玩家與零件碰撞時會增加充能
    player_hits_component = pygame.sprite.spritecollide(player, components, True, pygame.sprite.collide_rect)
    for hit in player_hits_component:
        problem_challenge()
        player.energy += 20
    if player.energy == 100:
        chest.image = pygame.transform.scale(chest_img[2], (60, 60))


    player_hits_chest = pygame.sprite.collide_rect(player,chest)
    if player_hits_chest:
        if player.energy == 100:
            screen.fill(BLACK)
            ini_background = pygame.transform.scale(ini_background,(1600,1000))
            screen.blit(ini_background,(-175,-160))
            game_over = True
        else:
            draw_text(screen, "零件尚未集齊!",20,chest.rect.centerx,chest.rect.top,BLACK)
            pygame.display.update()
            if player.vel_x > 0 and player.rect.right > chest.rect.left:
                    player.rect.right = chest.rect.left
                    player.vel_x = 0
            if player.vel_y > 0 and player.rect.bottom > chest.rect.top:
                    player.rect.bottom = chest.rect.top
                    player.on_ground = True
                    player.vel_y = 0
            
    # 無敵閃爍效果
    if player.invincible:
        if player.invincibility_timer % 20 < 10:
            all_sprites.draw(screen)
        else:
            all_sprites.draw(screen)
            player.image.set_alpha(128)  # 透明度設置為50%
    else:
        all_sprites.draw(screen)
        player.image.set_alpha(255)  # 恢復到100%透明度

    foe_hits = pygame.sprite.groupcollide(foes,bullets,False,True)
    for foe in foe_hits:
        foe.health -= 40
        if foe.health <= 0:
            component = Component(foe.rect.centerx,foe.rect.centery-10)
            all_sprites.add(component)
            components.add(component)
            foe.kill()

    screen.fill(BLACK)
    background = pygame.transform.scale(background,(1600,1000))
    screen.blit(background,(-175,-160))
    all_sprites.draw(screen)
    draw_lives(screen , player.lives , lives_img , SCREEN_WIDTH - 170 , 15)
    draw_player_energy(screen , player.energy , 10 , 15)
    for foe in foes:
        draw_foe_health(screen,foe.health,foe.rect.left,foe.rect.top)
    pygame.display.update()

pygame.quit()