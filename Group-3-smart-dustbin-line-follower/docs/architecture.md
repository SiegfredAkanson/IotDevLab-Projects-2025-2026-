# Architecture

## Modules
- `main.py`: App entrypoint and main loop.
- `config.py`: All wiring and tuning in one place.
- `lib/tcs34725.py`: TCS34725 driver + filtered line confidence output.
- `lib/motor_driver.py`: Motor direction and speed via `duty_u16` PWM.
- `lib/line_follower.py`: Autonomous control logic.
- `lib/wifi_remote.py`: AP mode + tiny HTTP server + command router.

## Runtime flow
1. `main.py` builds motor, sensors, line follower, and Wi-Fi remote.
2. Wi-Fi AP and HTTP server start.
3. Main loop calls `remote.tick()` every cycle.
4. If mode is `auto`, `line_follower.step()` drives the robot.
5. If mode is `manual`, browser commands drive motors directly.

## Safety behavior
- Manual drive commands are accepted only in `manual` mode.
- Switching modes triggers motor stop to prevent mode conflict.
