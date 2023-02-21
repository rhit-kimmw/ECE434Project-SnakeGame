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

#Setup the Matrix
import smbus
bus = smbus.SMBus(2)
matrix = 0x70
indexHold = [0x80, 0x00, 0x00, 0x00,
	 0x00, 0x00, 0x00, 0x00,
	 0x00, 0x00, 0x00, 0x00,
	 0x00, 0x00, 0x00, 0x00]

bus.write_byte_data(matrix, 0x21, 0)
bus.write_byte_data(matrix, 0x81, 0)
bus.write_byte_data(matrix, 0xe7, 0)

#Setup GPIO Buttons
button1 = "P9_21"
button2 = "P9_23"
GPIO.setup(button1, GPIO.IN)
GPIO.setup(button2, GPIO.IN)
   
one =  [0x02,0x00,0x02,0x00,0x02,0x00,0x02,0x00,
         0x02,0x00,0x02,0x00,0x02,0x00,0x00,0x00]
two = [0x0e,0x00,0x08,0x00,0x08,0x00,0x0e,0x00,
       0x02,0x00,0x02,0x00,0x0e,0x00,0x00,0x00]
three = [0x0e,0x00,0x02,0x00,0x02,0x00,0x0e,0x00,
         0x02,0x00,0x02,0x00,0x0e,0x00,0x00,0x00]
four = [0x02,0x00,0x02,0x00,0x02,0x00,0x0e,0x00,
        0x0a,0x00,0x0a,0x00,0x0a,0x00,0x00,0x00]
five = [0x0e,0x00,0x02,0x00,0x02,0x00,0x0e,0x00,
       0x08,0x00,0x08,0x00,0x0e,0x00,0x00,0x00]
six = [0x0e,0x00,0x0a,0x00,0x0a,0x00,0x0e,0x00,
       0x08,0x00,0x08,0x00,0x0e,0x00,0x00,0x00]
seven = [0x02,0x00,0x02,0x00,0x02,0x00,0x02,0x00,
       0x0a,0x00,0x0a,0x00,0x0e,0x00,0x00,0x00]
eight = [0x0e,0x00,0x0a,0x00,0x0a,0x00,0x0e,0x00,
       0x0a,0x00,0x0a,0x00,0x0e,0x00,0x00,0x00]
nine = [0x0e,0x00,0x02,0x00,0x02,0x00,0x0e,0x00,
       0x0a,0x00,0x0a,0x00,0x0e,0x00,0x00,0x00]
zero = [0x0e,0x00,0x0a,0x00,0x0a,0x00,0x0a,0x00,
       0x0a,0x00,0x0a,0x00,0x0e,0x00,0x00,0x00]
numbers = [zero,one,two,three,four,five,six,seven,eight,nine]

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
    
    def increasescore(self):
        self.displayNumber(self.score)
    
    def shift_to_tens_digit(self,ones_digit_matrix):
        tens_digit_matrix = [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
            0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
        for i in range(len(ones_digit_matrix)):
            if ones_digit_matrix[i] != 0:
                tens_digit_matrix[i] = ones_digit_matrix[i] << 4
        return tens_digit_matrix

    def getGameMatrix(self,tens_digit, ones_digit):
        game = [tens_digit[i] | ones_digit[i] for i in range(len(tens_digit))]
        return game

    def displayNumber(self, num):
        tens_digit = self.shift_to_tens_digit(numbers[num // 10])
        ones_digit = numbers[num%10]
        game = self.getGameMatrix(tens_digit, ones_digit)
        bus.write_i2c_block_data(matrix, 0, game)
        
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
                self.increasescore()
                apple.position = (random.randint(0,12), random.randint(0,16))
                
            if snake.positions[0] in snake.positions[1:]:
                self.done = True
            
            if snake.positions[0][0] > 12 or snake.positions[0][0] < 0 or snake.positions[0][1] > 16 or snake.positions[0][1] < 0:
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
     
 
button3 = "P9_26"
GPIO.setup(button3, GPIO.IN)
button4 = "P9_22"
GPIO.setup(button4, GPIO.IN)
start = GPIO.input(button3)
done = GPIO.input(button4)
while done == False:
    start = GPIO.input(button3)
    done = GPIO.input(button4)
    if start:
        print("Game Start")
        bus.write_i2c_block_data(matrix, 0, zero)
        game = Game()
        game.runGame()
    if done: 
        print("Game Ended")
        Game.done = True
