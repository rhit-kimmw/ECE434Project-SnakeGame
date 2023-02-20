#!/usr/bin/env python3

import Adafruit_BBIO.GPIO as GPIO
import time

button1 = "P9_21"
GPIO.setup(button1, GPIO.IN)
while(True):
    print(GPIO.input(button1), end='\r')
    time.sleep(0.1)