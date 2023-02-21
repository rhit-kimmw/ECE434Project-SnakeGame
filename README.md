# ECE434Project-SnakeGame

## Setup instructions

1. download the repository
2. install the packages by sudo ./install.sh
3. wire the hardware:
> The first thing you do to run the code is first to do 'chmod +x setup.sh' and then run './setup.sh' this will setup all your ports to be gpio or eqep for the necessary pins to run the program. After that is complete do 'chmod +x snake.py' and to run the file do 'sudo ./snake.py' this will run the snake game on the LCD and you can play the game as instructed.

> To turn right turn the encoder counter-clockwise.

> To turn left turn the encoder clockwise.

> To slow the game down press the push button connected to pin P9_23 or to speed the game up press the push button connected to P9_21.

> To start and restart the game press the push button connected to P9_26.

> To end the Game once in play press the push button connected to P9_22.

> To get the LED matrix to work connected the SCL to P9_19 and the SDA to P9_20 and connected the positive pin to voltage and the negative pin to ground.

4. Run the game by 'sudo ./snake.py'
