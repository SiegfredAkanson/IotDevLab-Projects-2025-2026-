"""Start Wi-Fi remote server and keep robot in manual mode for testing."""

import time
from config import I2C_SENSOR_LEFT, I2C_SENSOR_RIGHT, LINE_TUNING, MOTOR_PINS, SENSOR_CALIBRATION, WIFI
from lib.line_follower import LineFollower
from lib.motor_driver import MotorDriver
from lib.tcs34725 import TCS34725Sensor
from lib.wifi_remote import WifiRemoteController

motor = MotorDriver(MOTOR_PINS)
left = TCS34725Sensor("left", I2C_SENSOR_LEFT, SENSOR_CALIBRATION["left"], LINE_TUNING["sensor_filter_alpha"])
right = TCS34725Sensor("right", I2C_SENSOR_RIGHT, SENSOR_CALIBRATION["right"], LINE_TUNING["sensor_filter_alpha"])
follower = LineFollower(motor, left, right, LINE_TUNING)

remote = WifiRemoteController(motor, follower, WIFI)
remote.start()
remote.mode = "manual"

while True:
    remote.tick()
    time.sleep_ms(20)
