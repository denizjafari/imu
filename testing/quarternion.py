import time
import board
import busio
import numpy as np
import math
import matplotlib.pyplot as plt
from adafruit_bno055 import BNO055_I2C
from scipy.signal import butter, lfilter
from filters import high_pass_filter, low_pass_filter, clip_data 
from calib_seq_v2 import load_calibration_0x28

# Set up filtering parameters
fs = 10.0
cutoff = 0.0001
highpass_cutoff = 1

# Function to convert radians to degrees
def rad_to_degrees(rad):
    return rad * 180 / math.pi

# Set up I2C and sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = BNO055_I2C(i2c, address=0x28)
print(f"Current mode: {sensor.mode}")

load_calibration_0x28(sensor)

# Function to read and filter angles
def read_angles(sensor, cutoff, highpass_cutoff, fs):
    quaternion = sensor.quaternion
    
    if any(q is None for q in quaternion):
        return np.zeros(3)

    qw = clip_data(low_pass_filter([quaternion[0]], cutoff, fs)[-1])
    qx = clip_data(low_pass_filter([quaternion[1]], cutoff, fs)[-1])
    qy = clip_data(low_pass_filter([quaternion[2]], cutoff, fs)[-1])
    qz = clip_data(low_pass_filter([quaternion[3]], cutoff, fs)[-1])

    '''qw = quaternion[0]
    qx = quaternion[1]
    qy = quaternion[2]
    qz = quaternion[3]'''

    norm = math.sqrt(qw**2 + qx**2 + qy**2 + qz**2)
    qw /= norm
    qx /= norm
    qy /= norm
    qz /= norm
    
    # Calculate angles (roll, pitch, yaw)
    angles = np.zeros(3)
    angles[0] = rad_to_degrees(math.atan2(2.0 * (qx * qy + qz * qw), (qx**2 - qy**2 - qz**2 + qw**2)))  # Roll
    angles[1] = rad_to_degrees(math.asin(-2.0 * (qx * qz - qy * qw) / (qx**2 + qy**2 + qz**2 + qw**2)))  # Pitch
    angles[2] = rad_to_degrees(math.atan2(2.0 * (qy * qz + qx * qw), (-qx**2 - qy**2 + qz**2 + qw**2)))  # Yaw

    print(f"Roll: {angles[0]:.2f}, Pitch: {angles[1]:.2f}, Yaw: {angles[2]:.2f}")

    return angles

# Create empty lists for plotting data
time_data, roll, pitch, yaw = [], [], [], []

# Set up real-time plotting
plt.ion()
fig, ax = plt.subplots()
line_roll, = ax.plot([], [], label="Roll", color='r')
line_pitch, = ax.plot([], [], label="Pitch", color='g')
line_yaw, = ax.plot([], [], label="Yaw", color='b')

ax.set_xlim(0, 10)
ax.set_ylim(-180, 180)
plt.legend()
plt.title("Real-Time IMU Angles (Roll, Pitch, Yaw)")
plt.xlabel("Time (s)")
plt.ylabel("Angle (degrees)")

# Time tracking
start_time = time.time()

def update_plot():
    line_roll.set_data(time_data, roll)
    line_pitch.set_data(time_data, pitch)
    line_yaw.set_data(time_data, yaw)
    
    ax.set_xlim(max(0, time_data[-1] - 10), time_data[-1])
    plt.draw()
    plt.pause(0.01)

# Main loop
while True:
    current_time = time.time() - start_time
    time_data.append(current_time)
    
    angles = read_angles(sensor, cutoff, highpass_cutoff, fs)
    
    roll.append(angles[0])
    pitch.append(angles[1])
    yaw.append(angles[2])
    
    update_plot()
    
    # Limit stored data
    if len(time_data) > 1000:
        time_data.pop(0)
        roll.pop(0)
        pitch.pop(0)
        yaw.pop(0)
   
    time.sleep(0.1)
