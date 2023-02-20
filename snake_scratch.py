#!/usr/bin/env python3
import sys
import getpass
if getpass.getuser() != 'root':
    sys.exit("Must be run as root.")
import os
import pygame
import time
import threading

import random
from datetime import datetime
from datetime import timedelta

import Adafruit_BBIO.GPIO as GPIO

class Game:
    screen = None
    WHITE = (255,255,255)
    RED = (255,0,0)
    GREEN = (0,255,0)
    done = False
    clock = pygame.time.Clock()
    last_moved_time = datetime.now()
    
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
        
        while not self.done:
            self.clock.tick(10)
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
                    
            if timedelta(seconds=0.1) <= datetime.now() - self.last_moved_time:
                snake.move()
                self.last_moved_time = datetime.now()
                
            if snake.positions[0] == apple.position:
                snake.grow()
                apple.position = (random.randint(0,12), random.randint(0,16))
                
            if snake.positions[0] in snake.positions[1:]:
                self.done = True
            if snake.positions[0][0] > 12 or snake.positions[0][0] < 0 or snake.positions[0][1] > 16 or snake.positions[0][1] < 0:
                print(snake.positions[0])
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

button1 = "P9_21"
GPIO.setup(button1, GPIO.IN)
while True:
    restart = GPIO.input(button1)
    if restart:
        game = Game()
        game.runGame()

