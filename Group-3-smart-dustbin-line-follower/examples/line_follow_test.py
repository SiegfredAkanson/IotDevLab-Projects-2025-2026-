"""Run autonomous line follow without Wi-Fi remote."""

from config import I2C_SENSOR_LEFT, I2C_SENSOR_RIGHT, LINE_TUNING, MOTOR_PINS, SENSOR_CALIBRATION
from lib.line_follower import LineFollower
from lib.motor_driver import MotorDriver
from lib.tcs34725 import TCS34725Sensor

motor = MotorDriver(MOTOR_PINS)
left = TCS34725Sensor("left", I2C_SENSOR_LEFT, SENSOR_CALIBRATION["left"], LINE_TUNING["sensor_filter_alpha"])
right = TCS34725Sensor("right", I2C_SENSOR_RIGHT, SENSOR_CALIBRATION["right"], LINE_TUNING["sensor_filter_alpha"])

follower = LineFollower(motor, left, right, LINE_TUNING)

while True:
    follower.step()
