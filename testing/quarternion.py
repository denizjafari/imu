import time
import board
import busio
import matplotlib.pyplot as plt
from adafruit_bno055 import BNO055_I2C
from calib_seq_v2 import load_calibration

fs = 10.0
cutoff = 1
highpass_cutoff = 0

# Set up I2C and sensors
i2c = busio.I2C(board.SCL, board.SDA)
sensors = {
    "sensor_1": BNO055_I2C(i2c, address=0x28),
    "sensor_2": BNO055_I2C(i2c, address=0x29)
}
def read_angles(sensor):
  quaternion = sensor.quaternion
  
  qw = high_pass_filter(low_pass_filter(quaternion[0], cutoff, fs), highpass_cutoff, fs)
  qx = high_pass_filter(low_pass_filter(quaternion[1], cutoff, fs), highpass_cutoff, fs)
  qy = high_pass_filter(low_pass_filter(quaternion[2], cutoff, fs), highpass_cutoff, fs)
  qz = high_pass_filter(low_pass_filter(quaternion[3], cutoff, fs), highpass_cutoff, fs)
  
  Vector<3> angles;

  angles.x() = atan2(2.0 * (qx * qy + qz * qw), (pow(qx,2) - pow(qy,2) - pow(qz,2) + pow(qw,2)));
  angles.y() = asin(-2.0 * (qx * qz - qy * qw) / (pow(qx,2) + pow(qy,2) + pow(qz,2) + pow(qw,2)));
  angles.z() = atan2(2.0 * (qy * qz + qx * qw), (-pow(qx,2) - pow(qy,2) + pow(qz,2) + pow(qw,2)));

  return angles;
  

load_calibration(sensor["sensor_1"])
load_calibration(sensor["sensor_2"])

