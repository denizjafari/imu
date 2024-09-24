#This calibration sequence attempts to use the BNO055 built-in calibration and then save
# it to a JSON file for future use so that the board does not need to be recalibrated.
#The way it is saved can be adjusted accordingly to the microcontroller/raspberry pi
# since some microcontrollers have an EEPROM that data can be saved to instead.

#You could run this for each IMU

import time
import json
import board
import busio
from adafruit_bno055 import BNO055_I2C

# Set up I2C and sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = BNO055_I2C(i2c)

# Function to save calibration data
def save_calibration(sensor):
    calibration_data = {
        "accel_offsets": sensor.offsets_accelerometer,
        "gyro_offsets": sensor.offsets_gyroscope,
        "mag_offsets": sensor.offsets_magnetometer,
        "accel_radius": sensor.radius_accelerometer,
        "mag_radius": sensor.radius_magnetometer
    }

    with open("calibration_data.json", "w") as file:
        json.dump(calibration_data, file)
    print("Calibration data saved!")

# Function to load calibration data
def load_calibration(sensor):
    try:
        with open("calibration_data.json", "r") as file:
            calibration_data = json.load(file)

        sensor.offsets_accelerometer = calibration_data["accel_offsets"]
        sensor.offsets_gyroscope = calibration_data["gyro_offsets"]
        sensor.offsets_magnetometer = calibration_data["mag_offsets"]
        sensor.radius_accelerometer = calibration_data["accel_radius"]
        sensor.radius_magnetometer = calibration_data["mag_radius"]

        print("Calibration data restored!")
    except FileNotFoundError:
        print("No calibration data found. Please calibrate the sensor.")

# Main loop to monitor and save calibration, exit when calibration is saved
while True:
    if all(cal == 3 for cal in sensor.calibration_status):
        print("Sensor fully calibrated!")
        save_calibration(sensor)
        break
    else:
        print(f"Calibration status - System: {cal_status[0]}, Gyro: {cal_status[1]}, Accel: {cal_status[2]}, Mag: {cal_status[3]}")
    time.sleep(0.5)
