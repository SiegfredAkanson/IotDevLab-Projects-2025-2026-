"""Boot script for ESP32 MicroPython.

Keep boot.py minimal and robust. Main application logic is in main.py.
"""

import gc

# Keep memory cleaner before app startup.
gc.collect()
