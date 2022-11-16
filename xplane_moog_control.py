from moog_class import MOOG
import pygetwindow as gw
import time
import numpy as np
from XPlaneUdp import *

# Tunable Parameters
roll_window_size = 25  # proposed 50 / old 16
pitch_window_size = 30  # proposed 50 / old 18
yaw_window_size = 15  # proposed 30 / old 4

yaw_vel_threshold = 0.5

dof_scale = 1.0
roll_scale_factor = 1.0*dof_scale
pitch_scale_factor = 1.0*dof_scale
yaw_scale_factor = 1.0*dof_scale

def stage_screen():
    windows = gw.getAllWindows()
    for window in windows:
        if window.title == 'Assetto Corsa':
            assetto_window: gw.Win32Window = window
            break
    assetto_window.moveTo(2314, 0)
    assetto_window.resizeTo(4900, 1047)

  


def main():
    stage_screen()
    moog = MOOG()
    moog.initialize_platform()
    xp = XPlaneUdp()
    try:
        beacon = xp.FindIp()
        print(beacon)
        # "sim/cockpit2/controls/total_pitch_ratio"
        # "sim/cockpit2/controls/total_roll_ratio"
        #  sim/cockpit2/gauges/indicators/

        
        xp.AddDataRef("sim/flightmodel/position/indicated_airspeed", freq=1)
        xp.AddDataRef("sim/flightmodel/position/latitude")
        
        while True:
            try:
                values = xp.GetValues()
                print(values)
            except XPlaneTimeout:
                print("XPlane Timeout")
                exit(0)

    except XPlaneVersionNotSupported:
        print("XPlane Version not supported.")
        exit(0)

    except XPlaneIpNotFound:
        print("XPlane IP not found. Probably there is no XPlane running in your local network.")
        exit(0)

    roll_avg = np.zeros(roll_window_size)
    pitch_avg = np.zeros(pitch_window_size)
    yaw_avg = np.zeros(yaw_window_size)
    index = 0
    initialized = False
    while True:
        start_time = time.time()

        roll = 0
        pitch = 0
        yaw = 0
        
        roll = roll_scale_factor * roll * 180 / np.pi
        pitch = pitch_scale_factor * pitch * 180 / np.pi
        yaw = yaw_scale_factor * yaw * 180 / np.pi

        roll = max(min(roll, 29), -29)
        pitch = max(min(pitch, 33), -33)
        yaw = max(min(yaw, 29), -29)

        roll = max(int(32767/58 * (roll + 29)), 0)
        pitch = max(int(32767/66 * (pitch + 33)), 0)
        yaw = max(int(32767/58 * (yaw + 29)), 0)

        if not initialized:
            roll_avg = np.full(roll_window_size, roll)
            pitch_avg = np.full(pitch_window_size, pitch)
            yaw_avg = np.full(yaw_window_size, yaw)
            initialized = True
        roll_avg[index % roll_window_size] = roll
        pitch_avg[index % pitch_window_size] = pitch
        yaw_avg[index % yaw_window_size] = yaw

        index += 1

        final_roll = int(sum(roll_avg)/roll_window_size)
        final_pitch = int(sum(pitch_avg)/pitch_window_size)
        final_yaw = int(sum(yaw_avg)/yaw_window_size)

        try:
            moog.command_dof(
                roll=final_roll, pitch=final_pitch, yaw=final_yaw)

        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()