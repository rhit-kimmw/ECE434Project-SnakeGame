#!/usr/bin/env python3
import sys
import getpass
if getpass.getuser() != 'root':
    sys.exit("Must be run as root.")
import os
import pygame
import time
import threading
import Adafruit_BBIO.GPIO as GPIO
import random
from datetime import datetime
from datetime import timedelta

#Setup Flask
from flask import Flask, render_template, request
app = Flask(__name__)

#Setup GPIO Buttons
button1 = "P9_21"
button2 = "P9_23"
button3 = "P9_26"
GPIO.setup(button1, GPIO.IN)
GPIO.setup(button2, GPIO.IN)
GPIO.setup(button3, GPIO.IN)
   
class Game:
    screen = None
    WHITE = (255,255,255)
    RED = (255,0,0)
    GREEN = (0,255,0)
    done = False
    clock = pygame.time.Clock()
    last_moved_time = datetime.now()
    tick = 10
    time = 0.1
    score = 0
    reset = 0
    
    def __init__(self): 
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        # os.putenv('SDL_FBDEV',   '/dev/fb0')
        # os.putenv('SDL_VIDEODRIVER', driver)
        os.putenv('SDL_NOMOUSE', '1')
        pygame.display.init()
        
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        print("Framebuffer size: ", size[0], "x", size[1])
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))   
        # Turn off cursor
        pygame.mouse.set_visible(False)
        # Initialise font support
        pygame.font.init()
        
    def timeincrease(self):
        print("Time increase works")
        Game.tick = Game.tick + 1
        # self.Game.time = self.Game.time + 0.01
   
    def timedecrease(self):
        print("Time decrease works")
        Game.tick = Game.tick - 1
    
    def resetGame(self):
        print("Reseting game")
        reset = 1
        Snake.positions = [(0,2),(0,1),(0,0)] 
        Snake.direction = ''
        game = Game()
        game.runGame()

    def draw_block(self, screen, color, position):
        block = pygame.Rect((position[1] * 20, position[0] * 20),
                            (20, 20))
        pygame.draw.rect(screen, color, block)
        
    def runGame(self):
        snake = Snake(self)
        apple = Apple(self)
        
        # Encoder - input(direction for snake)
        EncPath1 = '/sys/bus/counter/devices/counter2/count0'
        f = open(EncPath1+'/ceiling', 'w')
        f.write('1000000')
        f.close()
        f = open(EncPath1+'/count', 'w')
        f.write('500000')
        f.close()
        f = open(EncPath1+'/enable', 'w')
        f.write('1')
        f.close()
        f = open(EncPath1+'/count','r')
        
        oldDir = int(f.read())
        #event for encoder
        encoderEvent = pygame.USEREVENT + 1
        pygame.time.set_timer(encoderEvent, 250)
        
        repeat = 0
        while not self.done:
            self.clock.tick(self.tick)
            self.screen.fill(self.WHITE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True 
                if event.type == encoderEvent:
                    f.seek(0)
                    newDir = int(f.read())
                    
                    right = (oldDir > newDir)
                    left = (oldDir < newDir)
                    
                    oldDir = newDir
                    snake.turn(right, left)
                    
            if timedelta(seconds=self.time) <= datetime.now() - self.last_moved_time:
                snake.move()
                self.last_moved_time = datetime.now()
                
            if snake.positions[0] == apple.position:
                snake.grow()
                apple.position = (random.randint(0,19), random.randint(0,19))
                
            if snake.positions[0] in snake.positions[1:]:
                self.done = True
            
            if snake.positions[0][0] > 16 or snake.positions[0][0] < 0 or snake.positions[0][1] > 12 or snake.positions[0][1] < 0:
                self.done = True
                
            snake.draw()
            apple.draw()
            pygame.display.update()
    
class Snake:
    def __init__(self, Game):
        self.positions = [(0,2),(0,1),(0,0)] 
        self.direction = ''
        self.Game = Game
        self.directions = ['N','E','S','W']
        self.direction_offset = 1

    def draw(self):
        for position in self.positions: 
            self.Game.draw_block(self.Game.screen, self.Game.GREEN, position)
    
    def turn(self, right, left):
        if right:
            self.direction_offset = (self.direction_offset + 1) % 4
            self.direction = self.directions[self.direction_offset]
            print('right', self.direction)
        if left:
            self.direction_offset = (self.direction_offset - 1) % 4
            self.direction = self.directions[self.direction_offset]
            print('left', self.direction)
            
    def move(self):
        head_position = self.positions[0]
        y, x = head_position
        if self.direction == 'N':
            self.positions = [(y - 1, x)] + self.positions[:-1]
        elif self.direction == 'S':
            self.positions = [(y + 1, x)] + self.positions[:-1]
        elif self.direction == 'W':
            self.positions = [(y, x - 1)] + self.positions[:-1]
        elif self.direction == 'E':
            self.positions = [(y, x + 1)] + self.positions[:-1]

    def grow(self):
        self.Game.score = self.Game.score + 1
        tail_position = self.positions[-1]
        y, x = tail_position
        if self.direction == 'N':
            self.positions.append((y - 1, x))
        elif self.direction == 'S':
            self.positions.append((y + 1, x))
        elif self.direction == 'W':
            self.positions.append((y, x - 1))
        elif self.direction == 'C':
            self.positions.append((y, x + 1))    

class Apple:
    def __init__(self, Game, position=(5, 5)):
        self.position = position
        self.Game = Game

    def draw(self):
        self.Game.draw_block(self.Game.screen, self.Game.RED, self.position)
  
GPIO.add_event_detect(button1, GPIO.BOTH, callback=Game.timeincrease)
GPIO.add_event_detect(button2, GPIO.BOTH, callback=Game.timedecrease)
GPIO.add_event_detect(button3, GPIO.BOTH, callback=Game.resetGame) 
      
# # #Basic case of the route for Flask
# @app.route("/")
# def index():
#     scoreboard = Game.score
#     template_data = {
#         'title' : "Snake Game Scoreboard",
#         'Scoreboard' : scoreboard
#     }
#     return render_template("SnakeGame.html", **template_data)
# # Route for flask based on the button press
# @app.route("/<action>")
# def action(action):
# 	#Select the action
# 	if action == 'right':
# 		Snake.turn(100,0)
# 	elif action == 'left':
# 		Snake.turn(0,100)
# 	elif action == 'reset':
# 		Game.resetGame(Game)

# 	template_data = {
# 		'title' : "Snake Game Controls",
# 	}

# 	return render_template("SnakeGame.html", **template_data)
# if __name__=="__main__":
#     app.run(host='0.0.0.0', port=8082, debug=True)  
    
if Game.reset == 0:    
    game = Game()
    game.runGame()

