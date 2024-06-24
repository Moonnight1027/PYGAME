import pygame
import pyperclip
import sys
import os
from io import StringIO

FPS = 60
WIDTH = 800
HIGH = 600
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HIGH))
clock  = pygame.time.Clock()
running  = True

font = os.path.join("Yozai-Medium.ttf")


class InputBox(pygame.sprite.Sprite,):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.box_width = WIDTH-100   #輸入框大小
        self.box_height = HIGH-100
        self.cursor_x = 20            #游標座標
        self.cursor_y = 20
        self.image = pygame.Surface((self.box_width, self.box_height))
        self.image.fill((20, 20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH/2
        self.rect.top = 50
        self.problem={
            "problem" : "Add two numbers",
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
                results.append(f"Test case {i+1}: Failed - Expected {problem['expected_output'][i].split()}, but got {output.getvalue().split()}")
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
                
                with open('result.txt', 'a') as f:
                    f.write(self.text)
                    f.write(str(ap))
                    for line in results:
                        f.write(line)
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



all_sprites = pygame.sprite.Group()
input_box = InputBox()
all_sprites.add(input_box)

#遊戲迴圈
while running:
    clock.tick(FPS)
    #取得輸入
    for event in pygame.event.get(): #event 會是個列表
        if event.type == pygame.QUIT:
            running = False
        if input_box.active:
            input_box.event_process(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            input_box.active = True if input_box.rect.collidepoint(event.pos) else False
                
    
            
    #更新遊戲
    all_sprites.update()

    #畫面顯示
    pygame.display.update() #更新畫面
    screen.fill(WHITE)
    all_sprites.draw(screen)


pygame.quit()


"""

a = int(input())
b = int(input())

print(a+b)
"""