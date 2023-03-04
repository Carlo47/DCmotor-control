"""
Class       DCmotor
Author      2023-02-23 Charles Geiser (www.dodeka.ch)

Purpose     Implements a DCmotor class that controls the speed of a
            brushed DC motor using a PWM signal. With the used 
            dual H-Bridge motor driver L298N, 2 brushed DC motors
            can be operated simultaneously independently of each 
            other in both directions of rotation.

Features    - rotation(CW | CCW)        Set direction of rotation clockwise or counterclockwise
            - reverseRotation()         Reverse the direction of rotation
            - brake()                   Brake the motor quickly by short-circuiting the terminals
            - run(speed)                Run the motor at a speed 0 .. 100%
            - runFor(speed, msToRun)    Run the motor at given speed for msToRun milliseconds
            - waitFor(msWait)           Do nothing for msWait milliseconds (non blocking)
            - accelerate(speedFrom, speedTo, msWait = 10)   Accelerate the motor in steps of 1%.
                                                            Each step lasts msWait milliseconds

Board       ESP8266 with MicroPython firmware
"""
from machine import Pin, PWM
from time import ticks_ms
from math import trunc

CCW = const(0) # counterclockwise
CW  = const(1) # clockwise
PWMRESOLUTIONBITS = const(10) # 10 bit 

# Map x in the range inMin .. inMax to the range outMin .. outMax
# e.g. map speed x from 0 .. 100% to pwm 0 .. 1023
def map(x, inMin, inMax, outMin, outMax):
    m = (outMax - outMin)/(inMax - inMin)
    q = outMax - m * inMax 
    return trunc(m * x + q + 0.5)


class DCmotor:
    def __init__(self, motorID, pinPwmEnab, pin1, pin2, pwmFrequency):
        self._id = motorID
        self._pinPwm = PWM(Pin(pinPwmEnab), freq = pwmFrequency, duty = 0) 
        self._pin1 = Pin(pin1, Pin.OUT)
        self._pin2 = Pin(pin2, Pin.OUT)
        self._pin1.value(1)   # rotate CW
        self._pin2.value(0)
        self._rotation = CW
        self._dutyMax = (1 << PWMRESOLUTIONBITS) - 1
        self._dutyMin = 0
        self._firstRun = True
        self._msPrevious = 0
        self._accelMode = 0
        self._sp = 0


#   Run the motor at the given speed
    def run(self, speed):
        duty = map(speed, 0, 100, self._dutyMin, self._dutyMax)
        self._pinPwm.duty(duty)
        self.rotate(self._rotation)


#   Run the motor with the given speed for msToRun milliseconds
    def runFor(self, speed, msToRun):
        if self._firstRun:
            self._msPrevious = ticks_ms()
            self._firstRun = False
        if speed >= 0:
            self.run(speed)     # no need to drive motor at speed 0
        if (ticks_ms() - self._msPrevious) > msToRun:   # time is over, stop motor
            self.brake()
            self._firstRun = True   # rearm for next runFor
        return self._firstRun


#   Wait for the given msToWait milliseconds
    def waitFor(self, msToWait):
        if self._firstRun:
            self.brake()
            self._msPrevious = ticks_ms()
            self._firstRun = False
        if (ticks_ms() - self._msPrevious) > msToWait:
            self._firstRun = True
        return self._firstRun


#   Accelerate the speed from speedFrom to speedTo by incrementing
#   the speed by 1.
#   If speedFrom is greater than speedTo, the motor is slowed down
#   by decrementing the speed by 1.
#   Each step takes msWait milliseconds.
    def accelerate(self, speedFrom, speedTo, msWait = 10): 
        ms = 0
        if self._firstRun:
            self._sp = speedFrom
            self._msPrevious = ticks_ms()
            if (speedFrom < speedTo):
                self._accelMode = 0  # accelerating
            if (speedFrom > speedTo):
                self._accelMode = 1  # decelerating
            if (speedFrom == speedTo):
                self._accelMode = 2  # constant speed
            self._firstRun = False
        self.run(self._sp)
        if self._accelMode == 0:  # speed up
            if (self._sp <= speedTo):
                ms = ticks_ms()
                if (ms - self._msPrevious) >  msWait:
                    self._msPrevious = ms
                    self._sp += 1
            else:
                self._firstRun = True
                return True
        if self._accelMode == 1:  # slow down
            if (self._sp >= speedTo):
                ms = ticks_ms()
                if (ms - self._msPrevious) > msWait:
                    self._msPrevious = ms
                    self._sp -= 1
            else:
                self._firstRun = True
                return True
        if self._accelMode == 2:  # constant speed
            self._firstRun = False
            return True
        return False


#   Set the direction of rotation as CW (clockwise)
#   or CCW (counterclockwise) and start the motor
#   with the speed set by method run
    def rotate(self, direction):
        if (direction == CW):
            self._pin1.value(1)
            self._pin2.value(0)
            self._rotation = CW
        else:
            self._pin1.value(0)
            self._pin2.value(1)
            self._rotation = CCW            


#   Reverse the direction of rotation
    def reverseRotation(self):
        self._rotation = CW if self._rotation == CCW else CCW
        

#   Brake the motor quickly by short-circuiting the terminals.
#   At the same time the period is set to 0 
    def brake(self):
        self._pin1.value(0)
        self._pin2.value(0)
        self._pinPwm.duty(0)
        

#   Query the motors ID
    def id(self):
        return self._id