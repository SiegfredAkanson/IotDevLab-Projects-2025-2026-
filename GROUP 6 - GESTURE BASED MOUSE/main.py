from machine import Pin, SoftI2C, ADC
import time
import math
from Kalman import KalmanAngle
from MPU6050 import MPU6050
from hid_services import Mouse

# --- Configuration ---
SENSITIVITY_X = 1.2
SENSITIVITY_Y = 1.2
DEAD_ZONE = 6

LDR_PIN = 34
# Adjust this based on your lighting conditions (use Serial Monitor if needed)
CLICK_THRESHOLD = 400

TOGGLE_BTN_PIN = 14

# --- Classes ---

class AirMouse:
    def __init__(self):
        print("Initializing Hardware...")
        
        # Power Toggle Button
        self.toggle_btn = Pin(TOGGLE_BTN_PIN, Pin.IN, Pin.PULL_UP)
        self.is_active = True 
        self.last_btn_state = 1 
        
        # LDR
        self.ldr = ADC(Pin(LDR_PIN))
        self.ldr.atten(ADC.ATTN_11DB) 
        self.ldr.width(ADC.WIDTH_12BIT)
        self.ldr_state = "LIGHT"
        
        # I2C & MPU
        i2c = SoftI2C(sda=Pin(21), scl=Pin(22), freq=400000)
        self.mpu = MPU6050(i2c)
        
        # Kalman Filters
        self.kf_x = KalmanAngle()
        self.kf_y = KalmanAngle()
        
        # Bluetooth Mouse
        self.mouse = Mouse(name="ESP32 Air Mouse")
        
        # State variables
        self.center_x = 0.0
        self.center_y = 0.0
        self.prev_time = time.ticks_ms()
        
        # Gyro Offsets
        self.gyro_offset_x = 0.0
        self.gyro_offset_y = 0.0
        
        time.sleep_ms(1000)

    def calibrate(self):
        print("Calibrating... Keep hand perfectly flat and STILL.")
        
        # 1. Warm up the filter
        for _ in range(50):
            self.update_kalman_raw()
            time.sleep_ms(10)

        # 2. Calculate GYRO OFFSETS
        print("Calculating Gyro Offsets (Do not move!)...")
        sum_gx = 0
        sum_gy = 0
        samples = 200
        
        for _ in range(samples):
            gyro = self.mpu.read_gyro_data()
            sum_gx += gyro['x']
            sum_gy += gyro['y']
            time.sleep_ms(5)
            
        self.gyro_offset_x = sum_gx / samples
        self.gyro_offset_y = sum_gy / samples
        print(f"Gyro Offsets - X: {self.gyro_offset_x:.4f}, Y: {self.gyro_offset_y:.4f}")

        # 3. Recalculate center angles
        print("Finalizing Center Position...")
        for _ in range(50):
            self.update_kalman()
            time.sleep_ms(10)
            
        self.center_x = self.kf_x.angle
        self.center_y = self.kf_y.angle
        print(f"Calibration Complete. Center: X={self.center_x:.1f}, Y={self.center_y:.1f}")

    def update_kalman_raw(self):
        current_time = time.ticks_ms()
        dt = time.ticks_diff(current_time, self.prev_time) / 1000.0
        self.prev_time = current_time
        if dt == 0: dt = 0.01
        accel = self.mpu.read_accel_data()
        gyro = self.mpu.read_gyro_data()
        return accel, gyro, dt

    def update_kalman(self):
        current_time = time.ticks_ms()
        dt = time.ticks_diff(current_time, self.prev_time) / 1000.0
        self.prev_time = current_time
        
        if dt == 0: dt = 0.01

        accel = self.mpu.read_accel_data()
        gyro = self.mpu.read_gyro_data()
        
        # ACCELEROMETER MATH
        acc_roll = math.degrees(math.atan2(-accel['y'], -accel['z']))
        acc_pitch = math.degrees(math.atan2(-accel['x'], -accel['z']))
        
        # GYRO MATH
        gyro_rate_x = (gyro['x'] - self.gyro_offset_x)
        gyro_rate_y = (gyro['y'] - self.gyro_offset_y)
        
        # Apply Kalman Filter
        roll = self.kf_x.getAngle(acc_roll, gyro_rate_x, dt)
        pitch = self.kf_y.getAngle(acc_pitch, gyro_rate_y, dt)
        
        return roll, pitch

    def perform_single_click(self):
        """Executes a single Left Click"""
        print(">>> CLICK TRIGGERED <<<")
        # 1. Press Down
        self.mouse.set_buttons(b1=1, b2=0)
        self.mouse.notify_hid_report()
        time.sleep_ms(50) # Hold for 50ms
        
        # 2. Release
        self.mouse.set_buttons(b1=0, b2=0)
        self.mouse.notify_hid_report()

    def check_click_gesture(self):
        # Read average
        val = 0
        for _ in range(5):
            val += self.ldr.read()
        val = val // 5
        
        # --- DEBUG PRINT (Optional) ---
        # print(f"LDR Raw: {val} | State: {self.ldr_state} | Thresh: {CLICK_THRESHOLD}")
        
        is_covered = val < CLICK_THRESHOLD
        
        if is_covered and self.ldr_state == "LIGHT":
            self.ldr_state = "DARK"
            self.perform_single_click()
            
        elif not is_covered and self.ldr_state == "DARK":
            self.ldr_state = "LIGHT"

    def check_toggle_button(self):
        current_state = self.toggle_btn.value()
        if current_state == 0 and self.last_btn_state == 1:
            self.is_active = not self.is_active
            if self.is_active:
                print("System Activated")
                self.calibrate() 
            else:
                print("System Deactivated")
                self.mouse.set_axes(0, 0)
                self.mouse.set_buttons(b1=0, b2=0)
                self.mouse.notify_hid_report()
        self.last_btn_state = current_state

    def run(self):
        print("Starting Bluetooth Mouse...")
        self.mouse.start()
        self.mouse.start_advertising()
        print("Waiting for connection...")
        
        while True:
            if not self.mouse.is_connected():
                time.sleep_ms(100)
                continue

            self.check_toggle_button()

            if not self.is_active:
                time.sleep_ms(50)
                continue

            current_roll, current_pitch = self.update_kalman()
            
            dx_angle = current_roll - self.center_x
            dy_angle = current_pitch - self.center_y
            
            move_x = 0
            move_y = 0
            
            if abs(dx_angle) > DEAD_ZONE:
                move_x = int(dx_angle * SENSITIVITY_X)
            
            if abs(dy_angle) > DEAD_ZONE:
                move_y = int(dy_angle * SENSITIVITY_Y)
            
            move_x = max(-127, min(127, move_x))
            move_y = max(-127, min(127, move_y))
            
            self.mouse.set_axes(move_x, move_y)
            self.mouse.notify_hid_report()
            
            self.check_click_gesture()
            
            time.sleep_ms(20)

if __name__ == "__main__":
    try:
        airmouse = AirMouse()
        airmouse.calibrate()
        airmouse.run()
    except KeyboardInterrupt:
        print("Stopping...")