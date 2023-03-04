# Control 2 brushed DC motors with L298N
Implements a DCmotor class in Python that controls the 
speed of a brushed DC motor using a PWM signal. With the 
used dual H-Bridge motor driver L298N, 2 brushed DC motors 
can be operated simultaneously independently of each 
other in both directions of rotation. 

## Board
- ESP8266 with [MicroPhyton](https://micropython.org/download/) firmware

## Features
- rotation(CW | CCW)        
Set the direction of rotation clockwise or counterclockwise

- reverseRotation()         
Reverse the direction of rotation

- brake()                   
Brake the motor quickly by short-circuiting the terminals

- run(speed)                
Run the motor at a speed 0 .. 100%

- runFor(speed, msToRun) 
Run the motor at given speed for msToRun milliseconds

- waitFor(msWait)   
Do nothing during msWait milliseconds (non blocking).

- accelerate(speedFrom, speedTo, msWait = 10)   
Accelerate the motor in steps of 1%. The motor is slowed
down when the initial speed is greater than the final speed. 

## Wiring
```
                                                                                 .---.
                                                                                 |   |
                                                                                .-.  |
                                USB                                   Motor A  ( M ) |
                    .-----------I...I-----------.                               `-´  |
                    | ( )   [o] |   | [o]   ( ) |                                |   |
                    |     Flash '---' Reset     |                          .-----o---o--------.    
                    o 3V3                   Vin o                          |                  |
                    o GND                   GND o                          |                  |
            ~GPIO1  o TX                    RST o               5..12V <-- o Vcc              |
            ~GPIO3  o RX                     EN o                  GND <-- o GND              |
            ~GPIO15 o D8                    3V3 o                          o 5V               |
            ~GPIO13 o D7                    GND o                          |       L298N      |
            ~GPIO12 o D6                    CLK o GPIO6  SCLK              |   Dual H-Bridge  |   
            ~GPIO14 o D5                    SD0 o GPIO7  MISO    GPIO0 <-- o EN_A             | 
                    o GND    ...........    CMD o GPIO11 CS      GPIO4 <-- o IN1_A            | 
                    o 3V3   I           I   SD1 o GPIO8  MOSI    GPIO5 <-- o IN2_A            |
BUILTIN LED ~GPIO2  o D4    I  ESP8266  I   SD2 o ~GPIO9        GPIO12 <-- o IN1_B            |
            ~GPIO0  o D3    I           I   SD3 o ~GPIO10       GPIO14 <-- o IN2_B            |
            ~GPIO4  o D2    I           I   RSV o               GPIO13 <-- o EN_B             | 
            ~GPIO5  o D1    I           I   RSV o                          |                  |
             GPIO16 o D0    I...........I   AD0 o ADC0                     |  MB_1   MB_2     | 
                    |       |  _   _  | |       |                          '-----o---o--------'
                    | ( )   |_| |_| |_|_|   ( ) |                                |   |
                    '---------------------------'                               .-.  | 
                                                                      Motor B  ( M ) |
                                                                                `-´  | 
                                                                                 |   |
                                                                                 '---'

```
## Usage
The implemented methods are most usefull when called as part of a state machine, for example:
```
from dcMotor import DCmotor

motorA = DCmotor('A',  0,  4,  5, 220)
stateA = 0

def taskA(motor, speed, msRun, msStop):
    global stateA
    if (stateA == 0):
        if (motor.runFor(speed, msRun)):
            stateA = 1
    if (stateA == 1):
        if (motor.waitFor(msStop)):
            motor.reverseRotation()
            stateA = 0

            
while True:
    taskA(motorA, 30, 1000, 500)
```