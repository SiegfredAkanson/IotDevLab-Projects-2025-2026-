# Wiring Guide

## Motor Driver (L298N-style)
- ENA -> GPIO 25
- IN1 -> GPIO 13
- IN2 -> GPIO 27
- ENB -> GPIO 26
- IN3 -> GPIO 14
- IN4 -> GPIO 12
- GND of driver and ESP32 must be common

## TCS34725 Sensor 1 (Left)
- SDA -> GPIO 21
- SCL -> GPIO 22
- VCC -> 3.3V
- GND -> GND

## TCS34725 Sensor 2 (Right)
- SDA -> GPIO 18 (configurable)
- SCL -> GPIO 19 (configurable)
- VCC -> 3.3V
- GND -> GND

## Power Notes
- Use a separate battery rail for motors when possible.
- Keep ESP32 and sensor supply stable at 3.3V logic.
- Always connect all grounds together.
