import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math
from scipy.ndimage import uniform_filter1d

data = pd.read_csv('telemetry.csv')

roll_list = data['Roll']
pitch_list = data['Pitch']
yaw_heading_list = data['Yaw/Heading']

x_accel_list = data["G-Force(X)"]
y_accel_list = data["G-Force(Y)"]
z_accel_list = data["G-Force(Z)"]

final_roll = []
final_pitch = []
for i in range(len(roll_list)):
    roll = roll_list[i]
    pitch = pitch_list[i]
    yaw = yaw_heading_list[i]

    x_accel = x_accel_list[i]
    y_accel = y_accel_list[i]
    z_accel = z_accel_list[i]

    z_angle = np.arcsin(z_accel/9.81)
    x_angle = np.arcsin(x_accel/9.81)

    roll = roll + -x_angle

    pitch = -pitch + -z_angle

    roll = roll * 180 / math.pi 
    pitch = pitch * 180 / math.pi

    roll = max(min(roll, 29), -29)
    pitch = max(min(pitch, 33), -33)

    roll = max(int(32767/58 * (roll + 29)), 0)
    pitch = max(int(32767/66 * (pitch + 33)), 0)
    final_roll.append(roll)
    final_pitch.append(pitch)


plt.figure()
t = data['Time']
plt.xlabel('Time')
plt.plot(t, final_roll, 'r')
for i in range(3, 100, 10):
    final_roll_filtered = uniform_filter1d(final_roll, size=i)
    plt.plot(t, final_roll_filtered, '--', label=f"{i}")
# final_roll_filtered = uniform_filter1d(final_roll, size=18)
# plt.plot(t, final_roll_filtered, '--', label=f"{18}")
plt.legend()
plt.show()