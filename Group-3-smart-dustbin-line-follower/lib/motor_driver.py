"""Dual motor driver abstraction for ESP32 + MicroPython."""

from machine import PWM, Pin

from lib.utils import clamp


class MotorDriver:
    """Controls left and right motors with direction + PWM speed."""

    PWM_FREQ = 1000
    MAX_DUTY = 65535

    def __init__(self, pin_cfg):
        self.ena = PWM(Pin(pin_cfg["ENA"]), freq=self.PWM_FREQ, duty_u16=0)
        self.enb = PWM(Pin(pin_cfg["ENB"]), freq=self.PWM_FREQ, duty_u16=0)

        self.in1 = Pin(pin_cfg["IN1"], Pin.OUT)
        self.in2 = Pin(pin_cfg["IN2"], Pin.OUT)
        self.in3 = Pin(pin_cfg["IN3"], Pin.OUT)
        self.in4 = Pin(pin_cfg["IN4"], Pin.OUT)

        self.stop()

    def _set_left_direction(self, forward=True):
        if forward:
            self.in1.value(1)
            self.in2.value(0)
        else:
            self.in1.value(0)
            self.in2.value(1)

    def _set_right_direction(self, forward=True):
        if forward:
            self.in3.value(1)
            self.in4.value(0)
        else:
            self.in3.value(0)
            self.in4.value(1)

    def drive(self, left_speed, right_speed):
        """Drive each side with signed speed (-65535..65535)."""
        left_speed = int(clamp(left_speed, -self.MAX_DUTY, self.MAX_DUTY))
        right_speed = int(clamp(right_speed, -self.MAX_DUTY, self.MAX_DUTY))

        self._set_left_direction(left_speed >= 0)
        self._set_right_direction(right_speed >= 0)

        self.ena.duty_u16(abs(left_speed))
        self.enb.duty_u16(abs(right_speed))

    def forward(self, speed):
        self.drive(speed, speed)

    def backward(self, speed):
        self.drive(-speed, -speed)

    def turn_left(self, speed, pivot=False):
        if pivot:
            self.drive(-speed, speed)
        else:
            self.drive(speed // 3, speed)

    def turn_right(self, speed, pivot=False):
        if pivot:
            self.drive(speed, -speed)
        else:
            self.drive(speed, speed // 3)

    def stop(self):
        self.in1.value(0)
        self.in2.value(0)
        self.in3.value(0)
        self.in4.value(0)
        self.ena.duty_u16(0)
        self.enb.duty_u16(0)
