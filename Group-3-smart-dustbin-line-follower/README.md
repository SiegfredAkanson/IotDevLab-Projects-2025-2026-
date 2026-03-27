# Smart Dustbin Line Follower (ESP32 + MicroPython)

A clean, modular, demo-ready ESP32 MicroPython project for a smart dustbin robot that follows black tape on a wooden brown surface using **two TCS34725 RGB sensors**, and also supports **browser-based Wi-Fi manual control**.

## Elevator pitch
This project turns a 4-wheel ESP32 robot into a reliable smart dustbin base that can autonomously follow floor tape with smooth corrective steering, recover when the line is lost, and switch to manual remote driving from any phone connected to its hotspot.

## Project overview
The robot uses two front-facing TCS34725 sensors (left and right) on separate I2C buses, continuously estimates line confidence, and adjusts motor speeds gradually to handle straight paths, curves, divergence, and sharp turns.

A built-in Wi-Fi AP mode hosts a tiny web controller with movement and mode buttons, allowing quick demos without external routers.

## Features
- Autonomous black-tape line following with gradual steering.
- Recovery behavior when trail is lost (left-right sway search).
- Smooth handling of gentle and sharp turns.
- Two TCS34725 sensors on separate I2C buses (same address workaround).
- Tunable thresholds and speed bands from `config.py`.
- Wi-Fi hotspot + browser control page for manual driving.
- Auto/manual mode switching with conflict-safe motor control.
- Modular codebase with subsystem test scripts.

## How it works
1. Each TCS34725 sensor reads RGB+clear values.
2. A filtered reflectance-like ratio estimates black-line confidence.
3. The line follower computes left-vs-right confidence error.
4. Motor speed offsets are applied as gentle/medium/sharp turns.
5. If line is lost, the bot sways to reacquire it.
6. Wi-Fi controller can switch between autonomous and manual behavior.

## Why two RGB sensors?
- Better directional correction than one sensor.
- Early detection of left/right drift before severe deviation.
- More stable line reacquisition at branch-like divergence.
- Improved curve tracking due to differential confidence comparison.

## Design considerations
- Originally planned to use dedicated reflectance/line-tracking arrays (e.g., QTR/TCRT) for higher sampling rates and simpler thresholding.
- Due to part availability and schedule constraints, we repurposed TCS34725 color sensors. We compensated with dual I2C buses, a calibrated reflectance ratio, and tunable thresholds/steering bands.
- Trade-offs include slightly lower effective sampling rate and higher sensitivity to ambient light; mitigations include filtering, conservative steering bands, and a recovery search behavior.
- Decision rationale: deliver a reliable, demo-ready system with available components while preserving a clean abstraction boundary for later sensor upgrades.
- Migration path: the architecture isolates sensor reading/conversion logic; swapping to dedicated line sensors would primarily affect `lib/tcs34725.py` and tuning in `config.py`, leaving motor control and higher-level behaviors unchanged.

## Hardware components
- ESP32 development board (MicroPython firmware)
- 2 x TCS34725 RGB color sensors
- Dual-channel motor driver (L298N-style or equivalent)
- 4-wheel robot chassis with 2 motor channels (left/right drive groups)
- Battery pack for motors + stable power for ESP32/sensors
- Black tape track on wooden brown floor/surface

## Wiring summary
### Motor pins (configured in `config.py`)
- ENA = GPIO 25
- IN1 = GPIO 13
- IN2 = GPIO 27
- ENB = GPIO 26
- IN3 = GPIO 14
- IN4 = GPIO 12

### Sensor bus 1 (left)
- SDA = GPIO 21
- SCL = GPIO 22

### Sensor bus 2 (right, configurable)
- Default: SDA = GPIO 18, SCL = GPIO 19

See detailed instructions: `docs/wiring.md`

## Folder structure
```text
smart-dustbin-line-follower/
├── README.md
├── LICENSE
├── .gitignore
├── main.py
├── boot.py
├── config.py
├── lib/
│   ├── tcs34725.py
│   ├── motor_driver.py
│   ├── line_follower.py
│   ├── wifi_remote.py
│   └── utils.py
├── web/
│   └── index.html
├── docs/
│   ├── wiring.md
│   ├── architecture.md
│   └── tuning.md
└── examples/
    ├── sensor_test.py
    ├── motor_test.py
    ├── line_follow_test.py
    └── wifi_remote_test.py
```

## Setup instructions
1. Assemble wiring as in `docs/wiring.md`.
2. Flash MicroPython firmware to ESP32.
3. Upload repository files to ESP32 filesystem.
4. Edit `config.py` for your wiring/tuning.
5. Run `main.py`.

## Flash MicroPython to ESP32
1. Install [esptool](https://github.com/espressif/esptool).
2. Erase flash (replace serial port):
   ```bash
   esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
   ```
3. Write MicroPython firmware:
   ```bash
   esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-xxxx.bin
   ```

## Upload files to ESP32
Use [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) or ampy.

Example with `mpremote`:
```bash
mpremote connect /dev/ttyUSB0 fs cp -r smart-dustbin-line-follower/* :
mpremote connect /dev/ttyUSB0 reset
```

## Calibrate sensors (important)
1. Run `examples/sensor_test.py`.
2. Observe `ratio_filtered` over wooden floor and black tape.
3. Update `SENSOR_CALIBRATION` values in `config.py`.
4. Adjust `black_detect_threshold` in `LINE_TUNING`.
5. Tune turn strengths to reduce overshoot.

Detailed notes: `docs/tuning.md`

## Run autonomous mode
- Ensure `main.py` is present and board is rebooted.
- Default mode starts as `auto`.
- Robot follows black trail using `lib/line_follower.py`.

## Connect to ESP32 hotspot
1. Power the robot.
2. Connect phone/laptop to SSID in `config.py` (default: `DustbinBot-ESP32`).
3. Open browser to printed IP (usually `192.168.4.1`).

## Browser remote control
The hosted page provides buttons for:
- Forward
- Backward
- Left
- Right
- Stop
- Auto mode
- Manual mode

### Auto vs Manual mode
- **Auto mode**: browser movement buttons are ignored; line follower controls motors.
- **Manual mode**: movement buttons directly control motor driver.
- Mode switch issues `stop` for safe handover.

## Troubleshooting
- Sensor not detected:
  - Check I2C wiring and 3.3V/GND.
  - Confirm each sensor is on different I2C bus pins.
- Robot oscillates heavily:
  - Reduce `medium_turn`/`sharp_turn`.
  - Increase `loop_delay_ms` slightly.
- Misses black tape:
  - Recalibrate `ratio_black` and `ratio_floor`.
  - Lower `black_detect_threshold` slightly.
- Wi-Fi page not loading:
  - Confirm AP credentials in `config.py`.
  - Ensure phone stays connected to ESP32 hotspot.

## Known limitations
- Basic HTTP server supports low request volume (sufficient for control UI).
- No authentication on command endpoints beyond AP password.
- Sensor calibration may shift under strong ambient light changes.

## Future improvements
- Add PID-style steering control.
- Add sensor auto-calibration routine.
- Add telemetry endpoint (sensor confidence, mode, speed).
- Add OTA update support.
- Add obstacle detection and smart-bin behaviors.

## License
This project uses the MIT License (`LICENSE`).

## Group Members
- Nkrumah Caleb Joel
- Henry Boateng
- Samuel Arko-Mensah
