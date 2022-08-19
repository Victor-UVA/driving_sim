import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PyAccSharedMemory import accSharedMemory
import pygetwindow as gw
import numpy as np

import time

fig = plt.figure()
ax1 = plt.subplot(121)
ax2 = plt.subplot(122)
asm = accSharedMemory()

timestamps = []
g_force_x = []
g_force_y = []
g_force_z = []
gear = []
brake = []
vel_heading = []
heading = []
yaw = []
datapoints = 100


def stage_screen():
    windows = gw.getAllWindows()
    for window in windows:
        if window.title == 'Assetto Corsa':
            assetto_window : gw.Win32Window = window
            break
    assetto_window.moveTo(2314, 0)
    assetto_window.resizeTo(4900, 1047)

def animate(i, timestamps, g_force_x, g_force_y, g_force_z, gear, brake, vel_heading, heading):
    sm = asm.read_shared_memory()
    if sm is not None:
        x_accel = sm.Physics.g_force.x
        y_accel = sm.Physics.g_force.y
        z_accel = sm.Physics.g_force.z
        current_gear = sm.Physics.gear
        applied_brake = sm.Physics.brake
        vel_x = sm.Physics.velocity.x
        vel_z = sm.Physics.velocity.z

        # threshold = 0.1
        # if abs(vel_x) < threshold and abs(vel_z) < threshold:
        #     vel_angle = heading
        # else:
        #     vel_angle = -np.arctan2([vel_x], [vel_z])[0]
        # if vel_angle*heading >= 0:
        #     yaw = vel_angle - heading
        # # these signs may need tso flip
        # elif vel_angle > 0:
        #     yaw = -(2*np.pi - vel_angle + heading)
        # else:
        #     yaw = 2*np.pi - vel_angle + heading

        threshold = 0.01
        if sm.Physics.velocity.x < threshold and sm.Physics.velocity.z < threshold:
            vel_angle = sm.Physics.heading
        else:
            vel_angle = -np.arctan2([sm.Physics.velocity.x], [sm.Physics.velocity.z])[0]
        # vel_angle = -np.arctan(sm.Physics.velocity.x/sm.Physics.velocity.z)
        vel_heading.append(vel_angle)
        heading.append(sm.Physics.heading)
        
        # yaw = vel_heading - sm.Physics.heading


        timestamps.append(time.time())
        g_force_x.append(x_accel)
        g_force_y.append(y_accel)
        g_force_z.append(z_accel)
        gear.append(current_gear)
        brake.append(applied_brake)

        timestamps = timestamps[-datapoints:]
        g_force_x = g_force_x[-datapoints:]
        g_force_y = g_force_y[-datapoints:]
        g_force_z = g_force_z[-datapoints:]
        gear = gear[-datapoints:]
        brake = brake[-datapoints:]
        vel_heading = vel_heading[-datapoints:]
        heading = heading[-datapoints:]

        
    ax1.clear()
    ax1.plot(timestamps, g_force_x, label="G Force X")
    ax1.plot(timestamps, g_force_y, label="G Force Y")
    ax1.plot(timestamps, g_force_z, label="G Force Z")

    # ax2.clear()
    # # ax2.plot(timestamps, gear, label="Gear")
    # ax2.plot(timestamps, vel_heading, label="Vel Heading")
    # ax2.plot(timestamps, heading, label="Heading")

    
    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    ax1.set_title('G-Force vs. Time')
    ax1.set_ylabel('Gs')
    ax1.set_xlabel('Time')
    ax1.legend()
    
    # ax2.set_title("Headings")
    # ax2.set_ylabel('Radians')
    # ax2.set_xlabel('Time')
    # ax2.legend()


stage_screen()
ani = animation.FuncAnimation(fig, animate, fargs=(timestamps, g_force_x, g_force_y, g_force_z, gear, brake, vel_heading, heading), interval = 1)
plt.show()

