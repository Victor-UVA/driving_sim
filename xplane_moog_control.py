from moog_class import MOOG
import pygetwindow as gw
import time
import numpy as np
from XPlaneUdp import *

# Tunable Parameters
roll_window_size = 25  # proposed 50 / old 16
pitch_window_size = 25  # proposed 50 / old 18
yaw_window_size = 15  # proposed 30 / old 4

yaw_vel_threshold = 0.5

dof_scale = 1.0
roll_scale_factor = 1.0*dof_scale
pitch_scale_factor = 1.0*dof_scale
yaw_scale_factor = 1.0*dof_scale

x_accel_limit = 1  # Gs
z_accel_limit = 1  # Gs
def main():
    moog = MOOG()
    moog.initialize_platform()
    xp = XPlaneUdp()
    try:
        beacon = xp.FindIp()
        frequency = 60  # Hz
        
        # xp.AddDataRef("sim/flightmodel2/controls/roll_ratio", frequency)
        # xp.AddDataRef("sim/flightmodel2/controls/pitch_ratio", frequency)


        # xp.AddDataRef("sim/cockpit2/gauges/indicators/roll_AHARS_deg_pilot", frequency)
        # xp.AddDataRef("sim/cockpit2/gauges/indicators/pitch_AHARS_deg_pilot", frequency)
        xp.AddDataRef("sim/flightmodel/position/theta", frequency) # pitch
        xp.AddDataRef("sim/flightmodel/position/phi", frequency) # roll
        xp.AddDataRef("sim/flightmodel/position/local_ax", frequency) # x_accel ; m/s^2
        xp.AddDataRef("sim/flightmodel/position/local_az", frequency) # z_accel ; m/s^2


        
        roll_avg = np.zeros(roll_window_size)
        pitch_avg = np.zeros(pitch_window_size)
        yaw_avg = np.zeros(yaw_window_size)
        index = 0
        initialized = False

        while True:
            start_time = time.time()

            try:
                values = xp.GetValues()
                # print(values)
            except XPlaneTimeout:
                print("XPlane Timeout")
                # exit(0)
            if moog.is_engaged():
                # roll = values["sim/flightmodel2/controls/roll_ratio"]
                # pitch = values["sim/flightmodel2/controls/pitch_ratio"]
                
                # roll = values["sim/cockpit2/gauges/indicators/roll_AHARS_deg_pilot"]
                # pitch = values["sim/cockpit2/gauges/indicators/pitch_AHARS_deg_pilot"]

                roll = values["sim/flightmodel/position/phi"]
                pitch = values["sim/flightmodel/position/theta"]
                yaw = 0

                x_accel = values["sim/flightmodel/position/local_ax"]
                z_accel = values["sim/flightmodel/position/local_az"]
                x_angle = np.arcsin(
                    max(min(x_accel/9.81, x_accel_limit), -x_accel_limit))
                z_angle = np.arcsin(
                    max(min(z_accel/9.81, z_accel_limit), -z_accel_limit))

                roll = roll + x_angle

                pitch = pitch + z_angle
                
                roll = roll_scale_factor * -roll 
                pitch = pitch_scale_factor * -pitch 
                yaw = yaw_scale_factor * yaw 

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
                        pitch=final_pitch)

                except Exception as e:
                    print(e)
            elapsed_time = time.time() - start_time
            sleep_time = 1/frequency - elapsed_time
            # TESTING IF SLEEP IS NECESSARY -- I don't think it is?
            if sleep_time > 0:
                time.sleep(sleep_time)

    except XPlaneVersionNotSupported:
        print("XPlane Version not supported.")
        exit(0)

    except XPlaneIpNotFound:
        print("XPlane IP not found. Probably there is no XPlane running in your local network.")
        exit(0)

if __name__ == "__main__":
    main()