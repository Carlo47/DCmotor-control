"""
Module      main.py
Author      2023-02-26 Charles Geiser (https://www.dodeka.ch)

Purpose     The program shows how 2 motors, controlled by an ESP8266, 
            can perform different motion tasks simultaneously.
            In addition, the built-in led flashes every second. 

Board       ESP8266
Firmware    micropython from https://micropython.org
                                                                                 .---.
                                                                                 |   |
Wiring                                                                          .-.  |
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
"""


import time
from machine import Pin
from dcMotor import DCmotor


ledBuiltin = const(2)
led = Pin(ledBuiltin, Pin.OUT)
ledPeriod = 1000    # blink builtin led every second
ledPulsewidth = 50  # for 50ms


motorA = DCmotor('A',  0,  4,  5, 220)
motorB = DCmotor('B', 13, 12, 14, 110)

stateA = 0
stateB = 0

"""
Task for motor A
    - Run motor for msRun milliseconds at speed
    - Stop motor for msStop milliseconds, reverse
        direction of rotation an repeat cycle
"""
def taskA(motor, speed, msRun, msStop):
    global stateA
    if (stateA == 0):
        if (motor.runFor(speed, msRun)):
            stateA = 1
    if (stateA == 1):
        if (motor.waitFor(msStop)):
            motor.reverseRotation()
            stateA = 0
            


"""
Task for motor B
    - Accelerate motor from 0 to 100% in 6 secs (100 steps each of 60 ms duration)
    - Run motor for 2000 ms at speed 50%
    - Slow down the motor from 50% to 0 in 5 secs (50 steps each of 100 ms duration)
        brake the motor and reverse direction of rotation
    - Wait 5000 ms then repeat the cycle
"""
def taskB(motor):
    global stateB
    if stateB == 0:
        if motor.accelerate(0, 100, 60):
            stateB = 1
    if stateB == 1:
        if motor.runFor(50, 2000):
            stateB = 2
    if stateB == 2:
        if motor.accelerate(50, 0, 100):
            motor.brake()
            motor.reverseRotation()
            stateB = 3
    if stateB == 3:
        if motor.waitFor(5000):
            stateB = 0


while True:
    led.value(0 if (time.ticks_ms() % ledPeriod < ledPulsewidth) else 1)
    taskA(motorA, 30, 1000, 500)
    taskB(motorB)
