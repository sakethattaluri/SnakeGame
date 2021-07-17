from collections import deque
from model import get_normal_classifier, get_threshold_classifier
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
COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (255, 255, 102)

class SnakePart:
    """
        Class for each block of the snake
    """
    def __init__(self, xpos = None, ypos = None, direction = None):
        self.xpos = xpos
        self.ypos = ypos 
        self.dir = direction

    def update(self, xpos = None, ypos = None, direction = None):
        self.xpos = xpos
        self.ypos = ypos
        self.dir = direction

class Snake:
    """
        Class for the whole snake body
    """
    def __init__(self):
        self.body = [SnakePart(xpos = int(SC_X/2), ypos = int(SC_Y/2), direction = DR)]
        self.body.append(SnakePart(xpos = int(SC_X/2)+10, ypos = int(SC_Y/2), direction = DR))
        self.speed = 12
    
    def on_consume_egg(self):
        """
            Function to increase the size of body
        """
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
        """
            Function to update the body after every frame (or) direction change
        """
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
    
    def on_change_direction(self, new_dir):
        """
            Function to check if the new direction is valid or not and update accordingly
        """
        if (new_dir != self.body[-1].dir) and (new_dir+self.body[-1].dir != 0):
            #New direction is valid. Update the snake accordingly
            self.update_snake(direction = new_dir)
            return True
        return False
    
    def is_pos_available(self, posx, posy):
        """
            Function to check if the given position on screen is occupied by the body or not
        """
        for part in self.body:
            if part.xpos == posx and part.ypos == posy:
                return False
        return True

class Game:
    """
        Class for the Game.
    """
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.dis = pg.display.set_mode((SC_X, SC_Y))
        self.egg_pos = [random.randint(0, int(SC_X/10))*10, random.randint(0, int(SC_Y/10))*10]
        self.score = 1
        self.is_game_over = False
        self.snake = Snake()
        self.threshold_classifier = get_threshold_classifier()
        self.normal_classifier = get_normal_classifier()
        pg.display.update()
        pg.display.set_caption('Snake Game')
    
    def handle_snake_catch_egg(self):
        """
            Function to handle the snake catches egg scenario. Creates a new egg and random position and update the snake body
        """
        if self.egg_pos[0] == self.snake.body[-1].xpos and self.egg_pos[1] == self.snake.body[-1].ypos:
            self.snake.on_consume_egg()
            self.score += 1
            self.egg_pos = [random.randint(5, int(SC_X/10)-1)*10, random.randint(5, int(SC_Y/10)-1)*10]
            while not self.snake.is_pos_available(self.egg_pos[0], self.egg_pos[1]):
                self.egg_pos = [random.randint(5, int(SC_X/10))*10, random.randint(5, int(SC_Y/10))*10]
    
    def handle_boundaries(self):
        """
            Function to check if the snake encounters the boundaries or its own body
        """
        head = self.snake.body[-1]
        if not (0<=head.xpos<=SC_X and 0<=head.ypos<=SC_Y):
            self.is_game_over = True
        for part in self.snake.body[:-2]:
            if (part.xpos == self.snake.body[-1].xpos) and (part.ypos == self.snake.body[-1].ypos):
                print("Collision at ({}, {})".format(str(part.xpos), str(part.ypos)))
                print("Game over")
                self.is_game_over = True
    
    def update_direction(self):
        """
            Function to update the snake body based on the direction predicted
        """
        #Calculate the required parameters for the prediction of new direction
        head = self.snake.body[-1]
        bot_obs, top_obs, right_obs, left_obs = SC_Y-head.ypos, head.ypos, SC_X-head.xpos, head.xpos
        for part in self.snake.body[:-2]:
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
        slope = math.atan2(self.egg_pos[1]-head.ypos, self.egg_pos[0]-head.xpos)
        bot_obs = 0 if head.dir == DU else bot_obs
        top_obs = 0 if head.dir == DD else top_obs
        right_obs = 0 if head.dir == DL else right_obs
        left_obs = 0 if head.dir == DR else left_obs
        X_test = [[head.dir, slope, right_obs/SC_X, bot_obs/SC_Y, left_obs/SC_X, top_obs/SC_Y]]
        #Check for the threshold condition
        if 0<X_test[0][2]<0.05 or 0<X_test[0][3]<0.05 or 0<X_test[0][4]<0.05 or 0<X_test[0][5]<0.05:
            #Use threshold classifier
            df = pd.DataFrame(X_test, columns=['CurDir', 'Slope', 'Right', 'Bottom', 'Left', 'Top'])
            new_dir = self.threshold_classifier.predict(df)
            # print('Cur: {}, NewDir: {}'.format(str(X_test), str(new_dir)))
        else:
            #Use normal classifier
            df = pd.DataFrame([[head.dir, slope]], columns=['CurDir', 'Slope'])
            new_dir = self.normal_classifier.predict(df)
            # print('Cur-> {}, NewDir-> {}'.format(str(X_test), str(new_dir)))
        if self.snake.on_change_direction(new_dir):
            self.update_snake = False
    
    def run_game(self):
        """
            Function to run the game
        """
        while not self.is_game_over:
            self.update_snake = True
            self.dis.fill(COLOR_WHITE)
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
            self.update_direction()
            if self.update_snake:
                self.snake.update_snake()
            self.clock.tick(self.snake.speed)
        print('Score: {}'.format(str(self.score)))
        pg.quit()

if __name__ == '__main__':
    game = Game()
    game.run_game()