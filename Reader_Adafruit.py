# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Original code from: https://github.com/adafruit/Adafruit_CircuitPython_BNO055/tree/main simpletest.py
# Modified to write data to a CSV file

import csv
import numpy as np
import time
import gpiod
import board
import adafruit_bno055

prev_millis = [0., 0.]  # Initialise variable for counting time
sampling = 20  # Desired sampling frequency (for recording to CSV)


i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
sensor = adafruit_bno055.BNO055_I2C(i2c)
# If you are going to use UART uncomment these lines
# uart = board.UART()
# sensor = adafruit_bno055.BNO055_UART(uart)
last_val = 0xFFFF


def temperature():
    global last_val  # pylint: disable=global-statement
    result = sensor.temperature
    if abs(result - last_val) == 128:
        result = sensor.temperature
        if abs(result - last_val) == 128:
            return 0b00111111 & result
    last_val = result
    return result

def get_data():       # Collect  data from BNO055 module
    data[10], data[11], data[12], data[9] = sensor.quaternion
    data[6], data[7], data[8] = sensor.magnetic
    data[0], data[1], data[2] = sensor.gyro
    data[3], data[4], data[5] = sensor.acceleration
    data[13], data[14], data[15] = sensor.euler
    return data
def printdata(time_between_prints):
    global prev_millis
    time_millis = 1000 * (time.time() - start)
    if time_millis >= time_between_prints + prev_millis[1]:
        print("Sensor Temperature: {} degrees C".format(sensor.temperature))
        print("Raspberry Pi Temperature: {} degrees C".format(temperature()))
        print("Accelerometer (m/s^2): {}".format(sensor.acceleration))
        print("Magnetometer (microteslas): {}".format(sensor.magnetic))
        print("Gyroscope (rad/sec): {}".format(sensor.gyro))
        print("Euler angle: {}".format(sensor.euler))
        print("Quaternion: {}".format(sensor.quaternion))
        print("Linear acceleration (m/s^2): {}".format(sensor.linear_acceleration))
        print("Gravity (m/s^2): {}".format(sensor.gravity))
        print()
        prev_millis[1] = time_millis

def check_time():    # Check the time since last write to CSV and write new data if desired time has passed
    global prev_millis
    time_millis = 1000 * (time.time() - start)
    if time_millis >= (1000 / sampling) + prev_millis[0]:
        prev_millis[0] = time_millis
        write_to_csv()





def name_csv():  # Initialise CSV file (note, some columns may not be used)
    names = ["Time_Stamp", "ACCEL_LN_X", "ACCEL_LN_Y", "ACCEL_LN_Z", "GYRO_X", "GYRO_Y", "GYRO_Z", "MAG_X",
             "MAG_Y", "MAG_Z", "EMG_1", "EMG_2", "q0", "q1", "q2", "q3", "d0", "d1", "d2", "d'0", "d'1", "d'2"]
    units = ["s", "m/s^2", "m/s^2", "m/s^2", "deg/s", "deg/s", "deg/s", "localFlux", "localFlux", "localFlux", 'mV',
             'mV',
             'scalar',
             'i', 'j', 'k', 'deg', 'deg', 'deg', 'deg', 'deg', 'deg']

    # today = date.today()    # Change this and the line below to save CSV with a date/string
    # filename = "data/" + str(today) + "_" + time_filename + name + ".csv"
    filename = 'data/data.csv' # Comment out if the above filename is used

    with open(filename, 'w') as csv_file:  # THis part writes headers into the CSV file
        csv_writer_names = csv.DictWriter(csv_file, fieldnames=names)
        csv_writer_names.writeheader()
        csv_writer_units = csv.DictWriter(csv_file, fieldnames=units)
        csv_writer_units.writeheader()


def write_to_csv():   # Write data to CSV
    with (open('data/data.csv', 'a') as csv_file):   # Open CSV file
        names = ["Time_Stamp", "ACCEL_LN_X", "ACCEL_LN_Y", "ACCEL_LN_Z", "GYRO_X", "GYRO_Y", "GYRO_Z", "MAG_X",
                 "MAG_Y", "MAG_Z", "EMG_1", "EMG_2", "q0", "q1", "q2", "q3", "d0", "d1", "d2", "d'0", "d'1", "d'2"]
        csv_writer = csv.DictWriter(csv_file, fieldnames=names)
        readings = get_data()   # Get data from sensor

        info = {
            "Time_Stamp": time.time() - start,
            "ACCEL_LN_X": readings[3],
            "ACCEL_LN_Y": readings[4],
            "ACCEL_LN_Z": readings[5],
            "GYRO_X": readings[0],
            "GYRO_Y": readings[1],
            "GYRO_Z": readings[2],
            "MAG_X": readings[6],
            "MAG_Y": readings[7],
            "MAG_Z": readings[8],
            "EMG_1": 0,
            "EMG_2": 0,
            "q0": readings[9],
            "q1": readings[10],
            "q2": readings[11],
            "q3": readings[12],
            "d0": readings[13],
            "d1": readings[14],
            "d2": readings[15],
            "d'0": 0,
            "d'1": 0,
            "d'2": 0,

        }
        csv_writer.writerow(info)


data = np.zeros(18)  # Initialise empty list for current data
name_csv()     # Initialise CSV and fill with data labels and unit labels
start = time.time()     # Save start time of signal reading


while True:
    check_time()
    printdata(2000) # Print data at an interval of the given integer (milliseconds)


