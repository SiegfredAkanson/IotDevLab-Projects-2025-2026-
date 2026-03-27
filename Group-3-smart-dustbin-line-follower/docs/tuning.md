# Tuning Guide

Start by editing `config.py`.

## Main parameters
- `base_speed`: normal forward speed.
- `gentle_turn`, `medium_turn`, `sharp_turn`: turn strength bands.
- `search_sway`: sweep speed when line is lost.
- `loop_delay_ms`: control loop pace.
- `black_detect_threshold`: confidence threshold for black tape.

## Calibration strategy for wood + black tape
1. Run `examples/sensor_test.py`.
2. Place sensors over wooden floor and note filtered `ratio` values.
3. Place sensors over black tape and note filtered `ratio` values.
4. Update `SENSOR_CALIBRATION` in `config.py`:
   - `ratio_black`: close to black tape reading.
   - `ratio_floor`: close to floor reading.
5. Increase `black_detect_threshold` if false positives happen.
6. Reduce turn strengths if robot oscillates too aggressively.

## Practical advice
- Keep both sensors at equal height from floor.
- Prevent direct sunlight during calibration.
- Use matte black tape for best contrast.
