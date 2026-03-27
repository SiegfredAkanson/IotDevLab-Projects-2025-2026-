"""Read both sensors continuously for calibration."""

import time
from config import I2C_SENSOR_LEFT, I2C_SENSOR_RIGHT, SENSOR_CALIBRATION, LINE_TUNING
from lib.tcs34725 import TCS34725Sensor

left = TCS34725Sensor("left", I2C_SENSOR_LEFT, SENSOR_CALIBRATION["left"], LINE_TUNING["sensor_filter_alpha"])
right = TCS34725Sensor("right", I2C_SENSOR_RIGHT, SENSOR_CALIBRATION["right"], LINE_TUNING["sensor_filter_alpha"])

while True:
    l = left.read()
    r = right.read()
    print(
        "L conf={:.3f} ratio={:.3f} | R conf={:.3f} ratio={:.3f}".format(
            l["line_confidence"], l["ratio_filtered"], r["line_confidence"], r["ratio_filtered"]
        )
    )
    time.sleep_ms(200)
