# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 11:49:11 2021

@author: saket
"""
from collections import deque
import pygame as pg
import random
import pandas as pd
import math

SC_X = 900  # Screen size X
SC_Y = 600  # Screen size Y
DR = 1      # Right
DL = -1     # Left
DU = 2      # Up
DD = -2     # Down
COLOR_BLUE = (0, 0, 255)
COLOR_RED = (255, 0, 0)
COLOR_BLACK = (0, 0, 0)
COLOR_YELLOW = (255, 255, 102)

class SnakePart:
    def __init__(self, xpos = None, ypos = None, direction = None):
        self.xpos = xpos
        self.ypos = ypos 
        self.dir = direction

    def update(self, xpos = None, ypos = None, direction = None):
        self.xpos = xpos
        self.ypos = ypos
        self.dir = direction

class Snake:
    def __init__(self):
        self.body = [SnakePart(xpos = int(SC_X/2), ypos = int(SC_Y/2), direction = DR)]
        self.body.append(SnakePart(xpos = int(SC_X/2)+10, ypos = int(SC_Y/2), direction = DR))
        self.speed = 15
        self.history = []
    
    def on_consume_egg(self):
        tail = self.body[0]
        if tail.dir == DR:
            self.body.insert(0, SnakePart(xpos = tail.xpos-10, ypos = tail.ypos, direction = DR))
        elif tail.dir == DL:
            self.body.insert(0, SnakePart(xpos = tail.xpos+10, ypos = tail.ypos, direction = DL))
        elif tail.dir == DU:
            self.body.insert(0, SnakePart(xpos = tail.xpos, ypos = tail.ypos+10, direction = DU))
        else:
            self.body.insert(0, SnakePart(xpos = tail.xpos, ypos = tail.ypos-10, direction = DD))
    
    def update_snake(self, direction = None):
        tmp_queue = deque(self.body)
        tmp_queue.rotate(-1)
        self.body = list(tmp_queue)
        tmp = self.body[-2]
        head = self.body[-1]
        #Update the direction if new direction is provided as argument else update the snake normally
        new_dir = tmp.dir if direction == None else direction
        if new_dir == DR:
            head.update(xpos = tmp.xpos+10, ypos = tmp.ypos, direction = DR)
        elif new_dir == DL:
            head.update(xpos = tmp.xpos-10, ypos = tmp.ypos, direction = DL)
        elif new_dir == DU:
            head.update(xpos = tmp.xpos, ypos = tmp.ypos-10, direction = DU)
        else:
            head.update(xpos = tmp.xpos, ypos = tmp.ypos+10, direction = DD)
    
    def on_change_direction(self, new_dir, egg_pos):
        if (new_dir != self.body[-1].dir) and (new_dir+self.body[-1].dir != 0):
            #Direction changed. Update the snake accordingly
            head = self.body[-1]
            bot_obs, top_obs, right_obs, left_obs = SC_Y-head.ypos, head.ypos, SC_X-head.xpos, head.xpos
            for part in self.body[:-2]:
                if part.xpos == head.xpos:
                    if part.ypos > head.ypos:
                        bot_obs = min(bot_obs, part.ypos-head.ypos)
                    else:
                        top_obs = min(top_obs, head.ypos-part.ypos)
                elif part.ypos == head.ypos:
                    if part.xpos > head.xpos:
                        right_obs = min(right_obs, part.xpos-head.xpos)
                    else:
                        left_obs = min(left_obs, head.ypos-part.ypos)
            bot_obs = 0 if head.dir == DU else bot_obs
            top_obs = 0 if head.dir == DD else top_obs
            right_obs = 0 if head.dir == DL else right_obs
            left_obs = 0 if head.dir == DR else left_obs
            slope = math.atan2(egg_pos[1]-head.ypos,egg_pos[0]-head.xpos)
            self.history.append([head.dir, slope, top_obs/SC_Y, right_obs/SC_X, bot_obs/SC_Y, left_obs/SC_X, new_dir])
            self.update_snake(direction = new_dir)
    
    def is_pos_available(self, posx, posy):
        for part in self.body:
            if part.xpos == posx and part.ypos == posy:
                return False
        return True

class Game:
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.dis = pg.display.set_mode((SC_X, SC_Y))
        self.egg_pos = [random.randint(0, int(SC_X/10))*10, random.randint(0, int(SC_Y/10))*10]
        self.score = 1
        self.is_game_over = False
        self.snake = Snake()
        pg.display.update()
        pg.display.set_caption('Snake Game')
    
    def handle_snake_catch_egg(self):
        if self.egg_pos[0] == self.snake.body[-1].xpos and self.egg_pos[1] == self.snake.body[-1].ypos:
            self.snake.on_consume_egg()
            self.score += 1
            self.egg_pos = [random.randint(2, int(SC_X/10)-1)*10, random.randint(2, int(SC_Y/10)-1)*10]
            while not self.snake.is_pos_available(self.egg_pos[0], self.egg_pos[1]):
                self.egg_pos = [random.randint(2, int(SC_X/10))*10, random.randint(2, int(SC_Y/10))*10]
    
    def handle_boundaries(self):
        head = self.snake.body[-1]
        if not (0<=head.xpos<=SC_X and 0<=head.ypos<=SC_Y):
            self.is_game_over = True
        for part in self.snake.body[:-2]:
            if (part.xpos == self.snake.body[-1].xpos) and (part.ypos == self.snake.body[-1].ypos):
                print("{}, {}".format(str(part.xpos), str(part.ypos)))
                print("Game over")
                self.is_game_over = True
    
    def update_direction(self, new_dir):
        self.snake.on_change_direction(new_dir, self.egg_pos)
        self.update_snake = False
    
    def run_game(self):
        while not self.is_game_over:
            self.update_snake = True
            self.dis.fill(COLOR_BLACK)
            for part in self.snake.body:
                pg.draw.rect(self.dis, COLOR_BLUE, [part.xpos, part.ypos, 10, 10])
            pg.draw.rect(self.dis, COLOR_RED, [self.egg_pos[0], self.egg_pos[1], 10, 10])
            pg.display.update()
            self.handle_snake_catch_egg()
            self.handle_boundaries()
            #Keyboard event
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.is_game_over = True
                    pass
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        self.update_direction(DL)
                    elif event.key == pg.K_RIGHT:
                        self.update_direction(DR)
                    elif event.key == pg.K_UP:
                        self.update_direction(DU)
                    elif event.key == pg.K_DOWN:
                        self.update_direction(DD)
            if self.update_snake:
                self.snake.update_snake()
            self.clock.tick(self.snake.speed)
        print(self.score)
        df = pd.DataFrame(self.snake.history, columns=['CurDir', 'Slope', 'Right', 'Bottom', 'Left', 'CurDir', 'NewDir'])
        df.to_excel('Data.xlsx')
        pg.quit()

if __name__ == '__main__':
    game = Game()
    game.run_game()