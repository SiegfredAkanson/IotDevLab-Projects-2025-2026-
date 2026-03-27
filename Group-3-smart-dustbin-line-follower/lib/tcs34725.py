"""Minimal TCS34725 driver and calibrated line sensing helper."""

import time
from machine import I2C

from lib.utils import lerp, normalize


class TCS34725:
    ADDRESS = 0x29
    COMMAND_BIT = 0x80

    REG_ENABLE = 0x00
    REG_ATIME = 0x01
    REG_CONTROL = 0x0F
    REG_CDATAL = 0x14

    ENABLE_PON = 0x01
    ENABLE_AEN = 0x02

    def __init__(self, i2c):
        self.i2c = i2c

        devices = self.i2c.scan()
        if self.ADDRESS not in devices:
            raise OSError("TCS34725 not found on I2C bus")

        # Integration time and gain tuned for indoor line follower use.
        self._write8(self.REG_ATIME, 0xD5)  # ~101 ms
        self._write8(self.REG_CONTROL, 0x01)  # 4x gain
        self._write8(self.REG_ENABLE, self.ENABLE_PON)
        time.sleep_ms(3)
        self._write8(self.REG_ENABLE, self.ENABLE_PON | self.ENABLE_AEN)
        time.sleep_ms(10)

    def _write8(self, reg, value):
        self.i2c.writeto_mem(self.ADDRESS, self.COMMAND_BIT | reg, bytes([value]))

    def _read16(self, reg):
        data = self.i2c.readfrom_mem(self.ADDRESS, self.COMMAND_BIT | reg, 2)
        return data[0] | (data[1] << 8)

    def read_raw(self):
        clear = self._read16(self.REG_CDATAL)
        red = self._read16(self.REG_CDATAL + 2)
        green = self._read16(self.REG_CDATAL + 4)
        blue = self._read16(self.REG_CDATAL + 6)
        return {
            "clear": clear,
            "red": red,
            "green": green,
            "blue": blue,
        }


class TCS34725Sensor:
    """Wraps TCS34725 + filtering + black line confidence estimation."""

    def __init__(self, name, i2c_cfg, calibration, filter_alpha=0.35):
        self.name = name
        self.filter_alpha = filter_alpha
        self.calibration = calibration

        self.i2c = I2C(
            i2c_cfg["bus_id"],
            sda=i2c_cfg["sda"],
            scl=i2c_cfg["scl"],
            freq=i2c_cfg.get("freq", 100000),
        )

        self.sensor = TCS34725(self.i2c)
        self._filtered_ratio = calibration.get("ratio_floor", 0.6)

    def _ratio_from_raw(self, raw):
        rgb_sum = raw["red"] + raw["green"] + raw["blue"] + 1
        return raw["clear"] / float(rgb_sum)

    def read(self):
        raw = self.sensor.read_raw()
        ratio = self._ratio_from_raw(raw)
        self._filtered_ratio = lerp(self._filtered_ratio, ratio, self.filter_alpha)

        line_confidence = 1.0 - normalize(
            self._filtered_ratio,
            self.calibration["ratio_black"],
            self.calibration["ratio_floor"],
        )

        return {
            "name": self.name,
            "raw": raw,
            "ratio": ratio,
            "ratio_filtered": self._filtered_ratio,
            "line_confidence": line_confidence,
        }
