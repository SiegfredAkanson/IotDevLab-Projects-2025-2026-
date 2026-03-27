"""Central project configuration.

Edit this file first when tuning behavior or changing wiring.
"""

# -----------------------------------------------------------------------------
# Motor driver pins (L298N-style dual H-bridge)
# -----------------------------------------------------------------------------
MOTOR_PINS = {
    "ENA": 25,  # Left motor PWM
    "IN1": 13,  # Left motor direction 1
    "IN2": 27,  # Left motor direction 2
    "ENB": 26,  # Right motor PWM
    "IN3": 14,  # Right motor direction 1
    "IN4": 12,  # Right motor direction 2
}

# -----------------------------------------------------------------------------
# TCS34725 sensor buses (same I2C address, so two separate buses)
# -----------------------------------------------------------------------------
I2C_SENSOR_LEFT = {
    "bus_id": 0,
    "sda": 21,
    "scl": 22,
    "freq": 100000,
}

# ESP32 commonly supports I2C(1) for a second software-configurable bus.
I2C_SENSOR_RIGHT = {
    "bus_id": 1,
    "sda": 18,
    "scl": 19,
    "freq": 100000,
}

# -----------------------------------------------------------------------------
# Line follower tuning
# -----------------------------------------------------------------------------
LINE_TUNING = {
    "base_speed": 42000,
    "gentle_turn": 9000,
    "medium_turn": 17000,
    "sharp_turn": 26000,
    "search_sway": 18000,
    "loop_delay_ms": 45,
    "black_detect_threshold": 0.42,
    "diff_small": 0.06,
    "diff_medium": 0.14,
    "diff_sharp": 0.26,
    "sensor_filter_alpha": 0.35,
    "line_lost_timeout_ms": 700,
}

# -----------------------------------------------------------------------------
# Per-sensor calibration ranges for wood + black tape scenes
# ratio = clear_value / (r + g + b + 1)
# lower ratio tends toward darker/black tape.
# -----------------------------------------------------------------------------
SENSOR_CALIBRATION = {
    "left": {
        "ratio_black": 0.22,
        "ratio_floor": 0.63,
    },
    "right": {
        "ratio_black": 0.22,
        "ratio_floor": 0.63,
    },
}

# -----------------------------------------------------------------------------
# Wi-Fi hotspot + web control
# -----------------------------------------------------------------------------
WIFI = {
    "ssid": "DustbinBot-ESP32",
    "password": "dustbin123",
    "channel": 6,
    "authmode": 3,  # WPA2-PSK
    "port": 80,
}
