import matplotlib.pyplot as pyplot
import numpy as np
from scipy.spatial.transform import Rotation as R
from matplotlib import animation
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D



def transformation_matrix(x=0, y=0, z=0, roll=0, pitch=0, yaw=0, quaternion=None):
        if quaternion is not None:
            qw = quaternion[0]
            qx = quaternion[1]
            qy = quaternion[2]
            qz = quaternion[3]

            return np.matrix([[2 * (qw * qw - 0.5 + qx * qx), 2 * (qx * qy - qw * qz), 2 * (qx * qz + qw * qy), x],
                                 [2 * (qx * qy + qw * qz), 2 * (qw * qw - 0.5 + qy * qy), 2 * (qy * qz - qw * qx), y],
                                 [2 * (qx * qz - qw * qy), 2 * (qy * qz + qw * qx), 2 * (qw * qw - 0.5 + qz * qz), z],
                                 [0, 0, 0, 1]])
        else:
            sr = np.sin(np.radians(roll))
            cr = np.cos(np.radians(roll))

            sp = np.sin(np.radians(pitch))
            cp = np.cos(np.radians(pitch))

            sy = np.sin(np.radians(yaw))
            cy = np.cos(np.radians(yaw))

            return np.matrix([[cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr, x],
                                [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr, y],
                                [-sp, cp * sr, cp * cr, z],
                                [0, 0, 0, 1]])
            

def normalize_quternion(quternion):
    # input of the formal [w, x, y, z]
    return quternion / np.linalg.norm(quternion)

def calculate_angle_wrt_z(quternion1, quternion2):
    # implementing wrt to z
    # in practice, we need to compare wrt the straight line
    # calculated when the user holds an upright position 
    # Quaternions from IMUs
    
    # Create Rotation objects
    r1 = R.from_quat(quternion1)  # Note the order: [x, y, z, w]
    r2 = R.from_quat(quternion2)

    # Convert to rotation matrices
    R1 = r1.as_matrix()
    R2 = r2.as_matrix()
    
    # Extract z-axis unit vectors
    z1 = R1[:, 2]
    z2 = R2[:, 2]

    # Normalize the vectors
    z1_unit = z1 / np.linalg.norm(z1)
    z2_unit = z2 / np.linalg.norm(z2)

    # Calculate the dot product
    dot_product = np.dot(z1_unit, z2_unit)

    # Clamp the dot product to avoid numerical errors
    dot_product = np.clip(dot_product, -1.0, 1.0)

    # Calculate the angle in radians and degrees
    angle_rad = np.arccos(dot_product)
    angle_deg = np.degrees(angle_rad)
    
    return angle_deg

def shoulder_elevation(quternion1):
    # calculate how much the shoulder is moved up wrt to the x axis at the initial position
    
    return elevation_angle

def upper_arm_ab_ad_angle():
    # calculate the upper arm ab_ad angle wrt to z-axis
    # ideally from the patient specific initial up right position in the future
    
def upper_arm_flex_angle():
    
def lower_arm_felx_angle():
    
def elbow_sway_angle():
    
def shoulder_rotation_angle():
    
def initial_user_data():
    # take readings from initial user worn sensors to calculate the neutral position of the sensors
    # from which the angles during the dynamic movement will be calculated from 