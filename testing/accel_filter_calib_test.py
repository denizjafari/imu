import time
import board
import busio
import matplotlib.pyplot as plt
from adafruit_bno055 import BNO055_I2C
from scipy.signal import butter, lfilter

fs = 10.0
cutoff = 2.0
highpass_cutoff = 0.1

def butter_lpf(data, cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, data)

def high_pass_filter(data, cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return lfilter(b, a, data)

# Set up I2C and sensors
i2c = busio.I2C(board.SCL, board.SDA)
sensors = {
    "sensor_1": BNO055_I2C(i2c, address=0x28),
    "sensor_2": BNO055_I2C(i2c, address=0x29)
}

offsets = {
    "sensor_1": [0.0, 0.0, 0.0],
    "sensor_2": [0.0, 0.0, 0.0]
}

# Static calibration: I am using this to obtain calib offsets
def calibrate_sensor(sensor, num_samples=100):
    offset_x, offset_y, offset_z = 0, 0, 0
    for _ in range(num_samples):
        accel = sensor.acceleration
        offset_x += accel[0]
        offset_y += accel[1]
        offset_z += accel[2]
        time.sleep(0.01)
    return [offset_x / num_samples, offset_y / num_samples, offset_z / num_samples]

# Calibrate sensor offsets
offsets["sensor_1"] = calibrate_sensor(sensors["sensor_1"])
offsets["sensor_2"] = calibrate_sensor(sensors["sensor_2"])

# Create empty lists for plotting data
time_data, accel_1_x, accel_1_y, accel_1_z = [], [], [], []
accel_2_x, accel_2_y, accel_2_z = [], [], []

# Set up a real-time plot to see the changes and noise
plt.ion()
fig, ax = plt.subplots()
lines = {
    "X1": ax.plot([], [], label="IMU1 X", color='r')[0],
    "Y1": ax.plot([], [], label="IMU1 Y", color='g')[0],
    "Z1": ax.plot([], [], label="IMU1 Z", color='b')[0],
    "X2": ax.plot([], [], label="IMU2 X", color='orange')[0],
    "Y2": ax.plot([], [], label="IMU2 Y", color='purple')[0],
    "Z2": ax.plot([], [], label="IMU2 Z", color='cyan')[0]
}
ax.set_xlim(0, 10)
ax.set_ylim(-10, 10)
plt.legend()
plt.title("Real-Time Accelerometer Data from Two IMUs")
plt.xlabel("Time (s)")
plt.ylabel("Acceleration (m/s^2)")

start_time = time.time()

def update_plot():
    for key, line in lines.items():
        line.set_data(time_data, globals()[f'accel_{key[1].lower()}_{key[0].lower()}'])
    ax.set_xlim(max(0, time_data[-1] - 10), time_data[-1])
    plt.draw()
    plt.pause(0.01)

# Buffers to accumulate data
buffer_length = 50
buffer_accel_1_x = []
buffer_accel_1_y = []
buffer_accel_1_z = []
buffer_accel_2_x = []
buffer_accel_2_y = []
buffer_accel_2_z = []

while True:
    accel_1 = sensors["sensor_1"].acceleration
    accel_2 = sensors["sensor_2"].acceleration
    
    if accel_1 and accel_2 and all(a is not None for a in accel_1) and all(a is not None for a in accel_2):
        current_time = time.time() - start_time
        time_data.append(current_time)
        
        buffer_accel_1_x.append(accel_1[0] - offsets["sensor_1"][0])
        buffer_accel_1_y.append(accel_1[1] - offsets["sensor_1"][1])
        buffer_accel_1_z.append(accel_1[2] - offsets["sensor_1"][2])
        buffer_accel_2_x.append(accel_2[0] - offsets["sensor_2"][0])
        buffer_accel_2_y.append(accel_2[1] - offsets["sensor_2"][1])
        buffer_accel_2_z.append(accel_2[2] - offsets["sensor_2"][2])
        
        # Keep buffer lengths within limit
        if len(buffer_accel_1_x) > buffer_length:
            buffer_accel_1_x.pop(0)
            buffer_accel_1_y.pop(0)
            buffer_accel_1_z.pop(0)
            buffer_accel_2_x.pop(0)
            buffer_accel_2_y.pop(0)
            buffer_accel_2_z.pop(0)
        
        filtered_accel_1_x = high_pass_filter(butter_lpf(buffer_accel_1_x, cutoff, fs), highpass_cutoff, fs)
        filtered_accel_1_y = high_pass_filter(butter_lpf(buffer_accel_1_y, cutoff, fs), highpass_cutoff, fs)
        filtered_accel_1_z = high_pass_filter(butter_lpf(buffer_accel_1_z, cutoff, fs), highpass_cutoff, fs)
        filtered_accel_2_x = high_pass_filter(butter_lpf(buffer_accel_2_x, cutoff, fs), highpass_cutoff, fs)
        filtered_accel_2_y = high_pass_filter(butter_lpf(buffer_accel_2_y, cutoff, fs), highpass_cutoff, fs)
        filtered_accel_2_z = high_pass_filter(butter_lpf(buffer_accel_2_z, cutoff, fs), highpass_cutoff, fs)

        accel_1_x.append(filtered_accel_1_x[-1])
        accel_1_y.append(filtered_accel_1_y[-1])
        accel_1_z.append(filtered_accel_1_z[-1])
        accel_2_x.append(filtered_accel_2_x[-1])
        accel_2_y.append(filtered_accel_2_y[-1])
        accel_2_z.append(filtered_accel_2_z[-1])
        
        update_plot()
        
        # Limit stored data to avoid memory overflow
        for data_list in [time_data, accel_1_x, accel_1_y, accel_1_z, accel_2_x, accel_2_y, accel_2_z]:
            if len(data_list) > 1000:
                data_list.pop(0)
    
    time.sleep(0.1)
