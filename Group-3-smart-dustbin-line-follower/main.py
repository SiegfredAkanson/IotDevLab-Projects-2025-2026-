"""Main entrypoint for smart dustbin line follower robot."""

import time

from config import I2C_SENSOR_LEFT, I2C_SENSOR_RIGHT, LINE_TUNING, MOTOR_PINS, SENSOR_CALIBRATION, WIFI
from lib.line_follower import LineFollower
from lib.motor_driver import MotorDriver
from lib.tcs34725 import TCS34725Sensor
from lib.wifi_remote import WifiRemoteController


def build_robot_system():
    """Create and wire all core components."""
    motor = MotorDriver(MOTOR_PINS)

    left_sensor = TCS34725Sensor(
        name="left",
        i2c_cfg=I2C_SENSOR_LEFT,
        calibration=SENSOR_CALIBRATION["left"],
        filter_alpha=LINE_TUNING["sensor_filter_alpha"],
    )
    right_sensor = TCS34725Sensor(
        name="right",
        i2c_cfg=I2C_SENSOR_RIGHT,
        calibration=SENSOR_CALIBRATION["right"],
        filter_alpha=LINE_TUNING["sensor_filter_alpha"],
    )

    follower = LineFollower(
        motor_driver=motor,
        left_sensor=left_sensor,
        right_sensor=right_sensor,
        tuning=LINE_TUNING,
    )

    remote = WifiRemoteController(
        motor_driver=motor,
        line_follower=follower,
        wifi_cfg=WIFI,
    )
    return follower, remote


def main():
    """Start Wi-Fi controller and run loop forever."""
    follower, remote = build_robot_system()
    remote.start()

    print("[MAIN] Robot ready. Use browser for manual/auto mode.")
    while True:
        remote.tick()
        if remote.mode == "auto":
            follower.step()
        else:
            # Keep loop responsive while in manual mode.
            time.sleep_ms(25)


if __name__ == "__main__":
    main()
