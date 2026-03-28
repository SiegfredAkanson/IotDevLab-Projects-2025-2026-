# Complete Setup Guide: Smart Multi-Face Recognition Attendance System

This document outlines the comprehensive step-by-step process required to build, flash, and run the attendance tracking system. 

---

## 1. Prerequisites

Before beginning, ensure your environment meets the following requirements:
- **Python 3.9+** installed on the central PC.
- **Thonny IDE** installed for flashing MicroPython to the ESP32 boards.
- Required USB-to-Serial drivers installed (e.g., CP210x or CH340) for ESP32 and ESP32-CAM communication.
- A 2.4 GHz Wi-Fi hotspot (or standard router network).

---

## 2. PC Software Installation

All central facial recognition processing is handled by the PC. 

1. Clone or download this project repository.
2. Open a terminal or command prompt inside the project folder.
3. Install the specific python dependencies required by the server:
   ```bash
   pip install opencv-contrib-python requests pyserial flask openpyxl
   ```
4. Verify that the repository root contains the `dataset` folder. Any initial un-enrolled face images can be cleared.

---

## 3. Hardware Wiring (ESP32-S3 Main Board)

To replicate the physical feedback and interaction system, wire your components to the primary ESP32-S3 microcontroller exactly as mapped in `esp32_main_board.py`:

| Component | Pin Type | ESP32-S3 GPIO Pin | Notes |
| :--- | :--- | :--- | :--- |
| **PIR Sensor** | Signal (OUT) | `GPIO 13` | Requires 5V/3.3V power & GND. |
| **Push Button** | Signal | `GPIO 27` | Uses internal Pull-Up. Wire other leg to GND. |
| **Buzzer** | Signal (PWM) | `GPIO 14` | |
| **RGB LED** | Red | `GPIO 25` | Use appropriate current-limiting resistors. |
| | Green | `GPIO 26` | |
| | Blue | `GPIO 33` | |
| **RTC (DS3231)** | SDA (I2C) | `GPIO 21` | Connect VCC to 3.3V or 5V. |
| | SCL (I2C) | `GPIO 22` | |
| **TFT (ST7735)** | SCK (SPI) | `GPIO 18` | Hardware SPI Clock. |
| | MOSI (SPI) | `GPIO 23` | Hardware SPI Data. |
| | CS | `GPIO 5` | Chip Select. |
| | DC / A0 | `GPIO 2` | Data/Command. |
| | RESET / RST | `GPIO 4` | Reset line. |

---

## 4. Flashing the Microcontrollers

You must flash MicroPython scripts to two separate boards.

### A. Flashing the ESP32-S3 Main Board
1. Open **Thonny IDE**.
2. Connect the ESP32-S3 Main Board to your PC via USB.
3. Select the correct MicroPython (ESP32) interpreter in Thonny's bottom-right corner.
4. Open the `esp32_main_board.py` file from your PC within Thonny.
5. Save the file directly to the MicroPython device and name it **`main.py`** (so it runs automatically on boot).
6. **Critical Requirement**: You must also save the `st7735.py` driver file directly onto the ESP32-S3 filesystem. Without it, the TFT screen will fail to initialize.

### B. Flashing the ESP32-CAM

Because the ESP32-CAM module lacks a built-in USB port, you must wire it to a programmer. If you are using a standard **ESP32 Dev Kit** as a USB-to-Serial converter instead of an FTDI board, wire them together as follows:

| ESP32 Dev Kit | ESP32-CAM | Notes |
| :--- | :--- | :--- |
| **GND** | **EN** | Disables the Dev Kit processor to allow pass-through. |
| **5V or 3.3V** | **5V or 3.3V** | Provide power. |
| **GND** | **GND** | Common ground. |
| **TX (GPIO 1)** | **U0R** | Transmit to Receive. |
| **RX (GPIO 3)** | **U0T** | Receive to Transmit. |
| *(Self/Camera)* | **IO0 to GND** | **CRITICAL:** Jumper IO0 to GND on the ESP32-CAM to force Flash Mode. |

*Note: You must remove the IO0-to-GND jumper and press the reset button on the ESP32-CAM after flashing is complete so it boots normally.*

There are two methods to flash the camera module: using the custom MicroPython script or the standard Arduino CameraWebServer sketch.

#### Method 1: Using the Custom MicroPython Script (Recommended)
1. Connect the wired ESP32-CAM (with IO0 grounded) to your PC via USB.
2. Open the `esp32_cam_server.py` file in Thonny.
3. Scroll to the Configuration block (around lines 23-25).
4. Update the Wi-Fi credentials to match the network you want the camera to stream on. (See the *Testing Network* section below).
5. Save the script to the ESP32-CAM device as **`main.py`**.
6. Reboot the ESP32-CAM and watch the shell printout in Thonny to note the **IP Address** it is assigned.

#### Method 2: Using the Arduino CameraWebServer (Alternative)
1. Open the **Arduino IDE**.
2. Go to **File > Examples > ESP32 > Camera > CameraWebServer**.
3. In the sketch, uncomment your specific camera model (typically `#define CAMERA_MODEL_AI_THINKER`).
4. Enter your network or hotspot credentials in the `ssid` and `password` variables.
5. Select the **AI Thinker ESP32-CAM** board in the Tools menu and hit **Upload**.
6. Once uploaded, open the Serial Monitor (115200 baud) and press the reset button on the camera module to obtain its **IP Address**.

---

## 5. Setting up the Testing Network (Optional)

If you are away from your permanent Wi-Fi network (or demonstrating the project), use the predefined mobile testing hotspot:
1. Turn on your smartphone or Windows PC **Mobile Hotspot** (Lock it to the **2.4 GHz** band; ESP32s cannot use 5 GHz).
2. Set the SSID (Network Name) to: `Project_Testing`
3. Set the Password to: `12345678`
4. Providing you flashed the ESP32-CAM with these credentials, it will automatically connect upon powering up.

---

## 6. Configuring and Running the PC Server

With the hardware flashed and powered up, you must point the PC script to the camera.

1. Open `pc_server.py` in your code editor.
2. Locate the variable `ESP32_CAM_IP` (around line 53).
3. Change the string to match the IP address generated by your ESP32-CAM during boot (e.g., `"192.168.1.5"`).
4. Plug the ESP32-S3 main board into your PC via USB so `pc_server.py` can capture the serial triggers from the PIR sensor.
5. Run the PC application:
   ```bash
   python pc_server.py
   ```
6. The system is active! You can view the live face recognition processing in the OpenCV window, and the remote dashboard by opening a web browser to: `http://localhost:5000`

---

## 7. Operational Modes

- **Manual Enrollment:** If your model has no trained faces, hold the physical ESP32-S3 push button for 3 seconds. The PC will prompt you for a name, the camera will automatically capture 50 samples under bright LED lighting, and it will dynamically retrain the model and generate `trainer.yml`.
- **System Logs:** Keep an eye on `attendance_log.csv` and `attendance_log.xlsx` which automatically populate with identified faces, alongside the RTC timestamp fetched via the dashboard.