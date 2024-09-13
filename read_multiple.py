import csv
import logging
import numpy as np
import sys
import time

from Adafruit_BNO055 import BNO055

prev_millis = 0
sampling = 20  # Magnetometer sampling at 20Hz, everything else, 100Hz.

# Create and configure two BNO sensor connections. You can modify these with different I2C addresses or buses.
bno1 = BNO055.BNO055(serial_port='/dev/serial0', rst=18)  # Sensor 1
bno2 = BNO055.BNO055(serial_port='/dev/serial1', rst=19)  # Sensor 2 (change as needed)

# Enable verbose debug logging if -v is passed as a parameter.
if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
    logging.basicConfig(level=logging.DEBUG)

# Initialize both BNO055 sensors and stop if something goes wrong.
if not bno1.begin():
    raise RuntimeError('Failed to initialize BNO055 sensor 1! Is the sensor connected?')

if not bno2.begin():
    raise RuntimeError('Failed to initialize BNO055 sensor 2! Is the sensor connected?')

# Function to print sensor diagnostic data (same for both sensors)
def print_sensor_info(sensor, sensor_name):
    status, self_test, error = sensor.get_system_status()
    print(f'System status of {sensor_name}: {status}')
    print(f'Self test result of {sensor_name} (0x0F is normal): 0x{self_test:02X}')
    if status == 0x01:
        print(f'System error on {sensor_name}: {error}')
    sw, bl, accel, mag, gyro = sensor.get_revision()
    print(f'Software version:   {sw}')
    print(f'Bootloader version: {bl}')
    print(f'Accelerometer ID:   0x{accel:02X}')
    print(f'Magnetometer ID:    0x{mag:02X}')
    print(f'Gyroscope ID:       0x{gyro:02X}\n')

# Print sensor info for both sensors
print_sensor_info(bno1, "Sensor 1")
print_sensor_info(bno2, "Sensor 2")

print('Reading BNO055 data from both sensors, press Ctrl-C to quit...')

def check_time():
    global prev_millis
    time_millis = 1000 * (time.time() - start)
    if time_millis >= (1000 / sampling) + prev_millis:
        prev_millis = time_millis
        write_to_csv()

def get_data(sensor):
    data = np.zeros(12)
    data[10], data[11], data[12], data[9] = sensor.read_quaterion()
    data[6], data[7], data[8] = sensor.read_magnetometer()
    data[0], data[1], data[2] = sensor.read_gyroscope()
    data[3], data[4], data[5] = sensor.read_accelerometer()
    return data

def name_csv():
    names = ["Time_Stamp", "ACCEL_LN_X", "ACCEL_LN_Y", "ACCEL_LN_Z", "GYRO_X", "GYRO_Y", "GYRO_Z", "MAG_X",
             "MAG_Y", "MAG_Z", "EMG_1", "EMG_2", "q0", "q1", "q2", "q3", "d0", "d1", "d2", "d'0", "d'1", "d'2"]
    units = ["s", "m/s^2", "m/s^2", "m/s^2", "deg/s", "deg/s", "deg/s", "localFlux", "localFlux", "localFlux", 'mV',
             'mV', 'scalar', 'i', 'j', 'k', 'deg', 'deg', 'deg', 'deg', 'deg', 'deg']
    with open('data/multi_sensor_data.csv', 'w') as csv_file:  # Write headers into the CSV file
        csv_writer_names = csv.DictWriter(csv_file, fieldnames=names)
        csv_writer_names.writeheader()
        csv_writer_units = csv.DictWriter(csv_file, fieldnames=units)
        csv_writer_units.writeheader()

def write_to_csv():
    with open('data/multi_sensor_data.csv', 'a') as csv_file:
        names = ["Time_Stamp", "ACCEL_LN_X", "ACCEL_LN_Y", "ACCEL_LN_Z", "GYRO_X", "GYRO_Y", "GYRO_Z", "MAG_X",
                 "MAG_Y", "MAG_Z", "EMG_1", "EMG_2", "q0", "q1", "q2", "q3", "d0", "d1", "d2", "d'0", "d'1", "d'2"]
        csv_writer = csv.DictWriter(csv_file, fieldnames=names)
        
        # Reading from sensor 1
        readings_1 = get_data(bno1)
        info_1 = {
            "Time_Stamp": time.time() - start,
            "ACCEL_LN_X": readings_1[3],
            "ACCEL_LN_Y": readings_1[4],
            "ACCEL_LN_Z": readings_1[5],
            "GYRO_X": readings_1[0],
            "GYRO_Y": readings_1[1],
            "GYRO_Z": readings_1[2],
            "MAG_X": readings_1[6],
            "MAG_Y": readings_1[7],
            "MAG_Z": readings_1[8],
            "EMG_1": 0,
            "EMG_2": 0,
            "q0": readings_1[9],
            "q1": readings_1[10],
            "q2": readings_1[11],
            "q3": readings_1[12],
            "d0": 0, "d1": 0, "d2": 0, "d'0": 0, "d'1": 0, "d'2": 0,
        }
        csv_writer.writerow(info_1)

        # Reading from sensor 2
        readings_2 = get_data(bno2)
        info_2 = {
            "Time_Stamp": time.time() - start,
            "ACCEL_LN_X": readings_2[3],
            "ACCEL_LN_Y": readings_2[4],
            "ACCEL_LN_Z": readings_2[5],
            "GYRO_X": readings_2[0],
            "GYRO_Y": readings_2[1],
            "GYRO_Z": readings_2[2],
            "MAG_X": readings_2[6],
            "MAG_Y": readings_2[7],
            "MAG_Z": readings_2[8],
            "EMG_1": 0,
            "EMG_2": 0,
            "q0": readings_2[9],
            "q1": readings_2[10],
            "q2": readings_2[11],
            "q3": readings_2[12],
            "d0": 0, "d1": 0, "d2": 0, "d'0": 0, "d'1": 0, "d'2": 0,
        }
        csv_writer.writerow(info_2)

# Create CSV file with headers
name_csv()
start = time.time()

# Main loop
while True:
    check_time()
    # Read Euler angles from both sensors and print calibration status
    heading1, roll1, pitch1 = bno1.read_euler()
    heading2, roll2, pitch2 = bno2.read_euler()

    sys1, gyro1, accel1, mag1 = bno1.get_calibration_status()
    sys2, gyro2, accel2, mag2 = bno2.get_calibration_status()

    print(f'Sensor 1: Heading={heading1:0.2F} Roll={roll1:0.2F} Pitch={pitch1:0.2F}\t')
