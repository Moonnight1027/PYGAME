import pygame
import pyperclip
import sys
import os
from io import StringIO
import random


FPS = 60
WIDTH = 1000
HEIGHT = 750
WHITE = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

font_path = os.path.join("font/Yozai-Medium.ttf")


class InputBox(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.box_width = WIDTH - 100
        self.box_height = HEIGHT - 100
        self.cursor_x = 20
        self.cursor_y = 20
        self.image = pygame.Surface((self.box_width, self.box_height))
        self.image.fill((20, 20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.top = 50

        self.active = False
        self.input_set = set()
        self.input_interval = {}
        self.font = pygame.font.Font(font_path, 28)

        # 定義題庫
        self.problems = [
            {
                "problem": "Add two numbers",
                "input": ["1\n2", "3\n4"],
                "expected_output": ["3\n", "7\n"]
            },
            {
                "problem": "Multiply two numbers",
                "input": ["2\n3", "4\n5"],
                "expected_output": ["6\n", "20\n"]
            },
            {
                "problem": "Subtract two numbers",
                "input": ["5\n3", "10\n4"],
                "expected_output": ["2\n", "6\n"]
            },
            {
                "problem": "Calculate factorial of a number",
                "input": ["5", "0"],
                "expected_output": ["120\n", "1\n"]
            },
            {
                "problem": "Count the number of words in a sentence",
                "input": ["Hello world", "Python is awesome"],
                "expected_output": ["2\n", "3\n"]
            },
            {
                "problem": "Calculate the sum of a list of numbers",
                "input": ["1 2 3 4 5", "10 20 30"],
                "expected_output": ["15\n", "60\n"]
            },
            {
                "problem": "Check if a number is prime",
                "input": ["7", "12"],
                "expected_output": ["True\n", "False\n"]
            },
            {
                "problem": "Convert Celsius to Fahrenheit",
                "input": ["25", "100"],
                "expected_output": ["77\n", "212\n"]
            },
            {
                "problem": "Calculate Area and Circumference of a Circle to Two Decimal Places",
                "input": ["5", "10"],
                "expected_output": ["78.54\n31.42\n", "314.16\n62.83\n"]
            }
        ]

        self.set_random_problem()

    def set_random_problem(self):
        self.problem = random.choice(self.problems)
        self.text = f"{self.problem['problem']}\r\n-------------------------\r\nType the code below ( Press Enter to submit ):\r\n"

    def update(self):
        self.image.fill((20, 20, 20))

        if self.active:
            current_time = pygame.time.get_ticks()
            self.text_x = 20
            self.text_y = 20
            for i in self.text.split("\r\n"):
                self.text_surface = self.font.render(i, True, (200, 200, 200), (20, 20, 20))
                self.image.blit(self.text_surface, (self.text_x, self.text_y))
                self.text_y += 32

            self.cursor_x = self.text_surface.get_width() + 23
            self.cursor_y = self.text_y - 30

            pygame.draw.rect(self.image, (200, 200, 200), [10, 10, self.box_width - 20, self.box_height - 20], 2)  # 灰色边框
            if (current_time % 1000 > 500):  # 光標閃爍
                pygame.draw.line(self.image, (200, 200, 200), (self.cursor_x, self.cursor_y),
                                 (self.cursor_x, self.cursor_y + 30), 2)

            for i in self.input_set:
                if current_time - self.input_interval[i] > 155:
                    self.input_interval[i] = current_time
                    if i == '\b':
                        self.text = self.text[:-1]
                    else:
                        self.text += i

        else:
            pygame.draw.rect(self.image, (140, 140, 140), [10, 10, self.box_width - 20, self.box_height - 20], 2)  # 灰色边框
            pygame.draw.line(self.image, (20, 20, 20), (self.cursor_x, self.cursor_y),
                             (self.cursor_x, self.cursor_y + 30), 2)

    def execute_code(self, user_code, problem):
        user_code = user_code.split("Type the code below ( Press Enter to submit ):\r\n")[-1]
        results = []
        ap = True
        for i in range(len(problem["input"])):
            sys.stdin = StringIO(problem["input"][i])
            output = StringIO()
            sys.stdout = output
            try:
                exec(user_code, {}, {})
            except Exception as e:
                results.append(f"Test case {i + 1}: Failed，Error {e}")
                ap = False
                break
            finally:
                sys.stdin = sys.__stdin__
                sys.stdout = sys.__stdout__

            if output.getvalue() == problem["expected_output"][i]:
                results.append(f"Test case {i + 1}: Passed")
            else:
                results.append(
                    f"Test case {i + 1}: Failed - Expected {problem['expected_output'][i].strip()}，but got {output.getvalue().strip()}")
                ap = False

        return results, ap

    def event_process(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
        if event.type == pygame.MOUSEBUTTONUP:
            pass
        if event.type == pygame.KEYDOWN:
            ctrl_pressed = pygame.key.get_mods() & pygame.KMOD_CTRL
            if ctrl_pressed and event.key == pygame.K_v:
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

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if input_box.active:
            input_box.event_process(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            input_box.active = True if input_box.rect.collidepoint(event.pos) else False

    all_sprites.update()
    screen.fill(WHITE)
    all_sprites.draw(screen)
    pygame.display.update()

pygame.quit()

