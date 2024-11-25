from PyAccSharedMemory import accSharedMemory
from moog_class import MOOG
import time
import numpy as np

# Tunable Parameters
roll_window_size = 40  # proposed 50 / old 16
pitch_window_size = 40  # proposed 50 / old 18
yaw_window_size = 15  # proposed 30 / old 4

yaw_vel_threshold = 0.5
# 4 and 10 completely got rid of it. Maybe we still want some?
gear_dampening_scale_factor = 7 
gear_dampening_window_size = 20

# These shoud
roll_scale_factor = 0.4 
pitch_scale_factor = 0.4
yaw_scale_factor = 1.0

roll_degree_excursion = 25 
pitch_degree_excursion = 28
yaw_degree_excursion = 29

roll_actuator_max = 32767
pitch_actuator_max = 32767
yaw_actuator_max = 32767

roll_actuator_min = 0
pitch_actuator_min = 0
yaw_actuator_min = 0

x_accel_limit = 1  # Gs (corresponds to roll)
z_accel_limit = 1  # Gs (corresponds to pitch)

shift_rpm_threshold = 800

def main():
    moog = MOOG()
    time.sleep(2)
    while moog.state != 'IDLE':
        print('Resetting...')
        moog.reset()
        time.sleep(1/60)
    moog.initialize_platform()
    asm = accSharedMemory()

    roll_avg = np.zeros(roll_window_size)
    pitch_avg = np.zeros(pitch_window_size)
    yaw_avg = np.zeros(yaw_window_size)

    index = 0
    gear_dampening_index = 0
    initialized = False
    frequency = 960  # Hz
    previous_gear = 0
    while True:
        start_time = time.time()
        sm = asm.read_shared_memory()

        if sm is None: continue

        if not moog.is_engaged(): 
            print("MOOG not engaged. Exiting Assetto program")
            break

        roll = sm.Physics.roll
        pitch = sm.Physics.pitch
        heading = sm.Physics.heading
        vel_x = sm.Physics.velocity.x
        vel_z = sm.Physics.velocity.z

        if abs(vel_x) < yaw_vel_threshold and abs(vel_z) < yaw_vel_threshold:
            vel_angle = heading
        else:
            vel_angle = -np.arctan2([vel_x], [vel_z])[0]

        # https://stackoverflow.com/questions/1878907/how-can-i-find-the-difference-between-two-angles#comment1927356_2007355

        a = (heading - vel_angle) % (np.pi)
        b = (vel_angle - heading) % (np.pi)
        yaw = -a if a < b else b

        x_accel = sm.Physics.g_force.x
        z_accel = sm.Physics.g_force.z
        
        # Gear shift dampening
        gear = sm.Physics.gear
        if gear != previous_gear:
            gear_dampening_index = gear_dampening_window_size
        # TODO: Test this
        if gear_dampening_index > 0:
            z_accel /= gear_dampening_scale_factor
            gear_dampening_index -= 1
        previous_gear = gear

        # Calculate angle from acceleration
        x_angle = np.arcsin(
            max(min(x_accel/9.81, x_accel_limit), -x_accel_limit))
        z_angle = np.arcsin(
            max(min(z_accel/9.81, z_accel_limit), -z_accel_limit))

        roll = roll + -x_angle

        pitch = -pitch + -z_angle

        # Convert to degrees and scale
        roll = roll_scale_factor * roll * 180 / np.pi
        pitch = pitch_scale_factor * pitch * 180 / np.pi
        yaw = yaw_scale_factor * yaw * 180 / np.pi

        # Limit degrees to max/min values from manual
        roll = max(min(roll, roll_degree_excursion), -roll_degree_excursion)
        pitch = max(min(pitch, pitch_degree_excursion), -pitch_degree_excursion)
        yaw = max(min(yaw, yaw_degree_excursion), -yaw_degree_excursion)


        # Map degrees to 0-32767 range for MOOG
        roll = max(min(int(32767/58 * (roll + 29)), roll_actuator_max), roll_actuator_min)
        pitch = max(min(int(32767/66 * (pitch + 33)), pitch_actuator_max), pitch_actuator_min)
        yaw = max(min(int(32767/58 * (yaw + 29)), yaw_actuator_max), yaw_actuator_min)

        # Moving average filter
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

        # Send frame
        try:
            moog.command_dof(
                roll=final_roll, pitch=final_pitch, yaw=final_yaw)

        except Exception as e:
            print(e)

        # Calculate elapsed time and sleep for the remaining time
        elapsed_time = time.time() - start_time
        sleep_time = 1/frequency - elapsed_time
        # TESTING IF SLEEP IS NECESSARY -- I don't think it is?
        if sleep_time > 0:
            time.sleep(sleep_time)

    asm.close()


if __name__ == "__main__":
    main()
