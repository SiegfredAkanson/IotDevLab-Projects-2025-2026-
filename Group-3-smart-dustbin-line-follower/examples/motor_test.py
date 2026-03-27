"""Basic motor direction and speed test."""

import time
from config import MOTOR_PINS, LINE_TUNING
from lib.motor_driver import MotorDriver

motor = MotorDriver(MOTOR_PINS)
speed = LINE_TUNING["base_speed"]

print("Forward")
motor.forward(speed)
time.sleep(2)

print("Backward")
motor.backward(speed)
time.sleep(2)

print("Turn left")
motor.turn_left(speed, pivot=True)
time.sleep(2)

print("Turn right")
motor.turn_right(speed, pivot=True)
time.sleep(2)

print("Stop")
motor.stop()
