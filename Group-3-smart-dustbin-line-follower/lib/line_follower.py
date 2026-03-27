"""Autonomous black-line following logic."""

import time

from lib.utils import clamp


class LineFollower:
    """Two-sensor line follower tuned for black tape on wooden surfaces."""

    def __init__(self, motor_driver, left_sensor, right_sensor, tuning):
        self.motor = motor_driver
        self.left_sensor = left_sensor
        self.right_sensor = right_sensor
        self.tuning = tuning

        self.last_seen_ms = time.ticks_ms()
        self.search_direction = 1

    def _compute_turn_offset(self, error_abs):
        if error_abs >= self.tuning["diff_sharp"]:
            return self.tuning["sharp_turn"]
        if error_abs >= self.tuning["diff_medium"]:
            return self.tuning["medium_turn"]
        return self.tuning["gentle_turn"]

    def _search_motion(self):
        sway = self.tuning["search_sway"]
        if self.search_direction > 0:
            self.motor.drive(sway, clamp(sway - 7000, 0, 65535))
        else:
            self.motor.drive(clamp(sway - 7000, 0, 65535), sway)

    def step(self):
        left = self.left_sensor.read()
        right = self.right_sensor.read()

        l_conf = left["line_confidence"]
        r_conf = right["line_confidence"]
        now = time.ticks_ms()

        on_line_left = l_conf >= self.tuning["black_detect_threshold"]
        on_line_right = r_conf >= self.tuning["black_detect_threshold"]

        if on_line_left or on_line_right:
            self.last_seen_ms = now

        if on_line_left and on_line_right:
            error = l_conf - r_conf
            if abs(error) < self.tuning["diff_small"]:
                self.motor.forward(self.tuning["base_speed"])
            else:
                turn = self._compute_turn_offset(abs(error))
                if error > 0:
                    self.motor.drive(self.tuning["base_speed"] - turn, self.tuning["base_speed"] + turn)
                else:
                    self.motor.drive(self.tuning["base_speed"] + turn, self.tuning["base_speed"] - turn)
        elif on_line_left:
            # Left sensor sees black more strongly, steer left.
            self.search_direction = -1
            self.motor.drive(
                self.tuning["base_speed"] - self.tuning["medium_turn"],
                self.tuning["base_speed"] + self.tuning["medium_turn"],
            )
        elif on_line_right:
            # Right sensor sees black more strongly, steer right.
            self.search_direction = 1
            self.motor.drive(
                self.tuning["base_speed"] + self.tuning["medium_turn"],
                self.tuning["base_speed"] - self.tuning["medium_turn"],
            )
        else:
            if time.ticks_diff(now, self.last_seen_ms) > self.tuning["line_lost_timeout_ms"]:
                # Lost line for a while: sway to recover trail.
                self.search_direction *= -1
            self._search_motion()

        time.sleep_ms(self.tuning["loop_delay_ms"])
