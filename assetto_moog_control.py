from PyAccSharedMemory import accSharedMemory
from moog_class import MOOG
import time
import pygetwindow as gw
import serial
import numpy as np

# Tunable Parameters
roll_window_size = 24  # proposed 50 / old 16
pitch_window_size = 27  # proposed 50 / old 18
yaw_window_size = 15  # proposed 30 / old 4

yaw_vel_threshold = 0.5

gear_dampening_scale_factor = 4 # 4 and 10 completelt got rid of it. Maybe we still want some?
gear_dampening_window_size = 8

dof_scale = 1.0
roll_scale_factor = 1.0*dof_scale
pitch_scale_factor = 1.0*dof_scale
yaw_scale_factor = 1.0*dof_scale

x_accel_limit = 1  # Gs
z_accel_limit = 1  # Gs

shift_rpm_threshold = 800


def stage_screen():
    windows = gw.getAllWindows()
    for window in windows:
        if window.title == 'Assetto Corsa':
            assetto_window: gw.Win32Window = window
            break
    assetto_window.moveTo(2314, 0)
    assetto_window.resizeTo(4900, 1047)


def main():
    try:
        tachometer_serial = serial.Serial(
            port='COM4',
            baudrate=115200,
            timeout=0,
            rtscts=True
        )
    except:
        print(
            "Cannot detect tachometer Arduino. Please ensure it is plugged in and try again")
        return -1
    time.sleep(1)
    stage_screen()
    asm = accSharedMemory()
    moog = MOOG()
    moog.initialize_platform()

    roll_avg = np.zeros(roll_window_size)
    pitch_avg = np.zeros(pitch_window_size)
    yaw_avg = np.zeros(yaw_window_size)

    index = 0
    gear_dampening_index = 0
    initialized = False
    frequency = 960  # Hz
    previous_gear = 0
    cycle = 0
    while True:
        start_time = time.time()
        sm = asm.read_shared_memory()

        if sm is not None:

            # Tachometer Interface -- TODO: Put in own process
            max_rpm = sm.Static.max_rpm
            rpm = round(sm.Physics.rpm/100)*100  # TODO: why?

            kmh = sm.Physics.speed_kmh
            mph = int(kmh/1.60934)

            shift = (max_rpm - rpm) <= shift_rpm_threshold

            fuel = int(100 - (sm.Physics.fuel / sm.Static.max_fuel) * 100)

            gear = sm.Physics.gear

            # Charles Code----------------------------------------------------------------------------------
            engine_status = 0
            front = sm.Physics.car_damage.front
            rear = sm.Physics.car_damage.rear
            left = sm.Physics.car_damage.left
            right = sm.Physics.car_damage.right
            center = sm.Physics.car_damage.center

            FL = sm.Physics.wheel_slip.front_left
            FR = sm.Physics.wheel_slip.front_right
            RL = sm.Physics.wheel_slip.rear_left
            RR = sm.Physics.wheel_slip.rear_right

            ab = sm.Physics.abs

            FLP = sm.Physics.wheel_pressure.front_left
            FRP = sm.Physics.wheel_pressure.front_right
            RLP = sm.Physics.wheel_pressure.rear_left
            RRP = sm.Physics.wheel_pressure.rear_right

            if FL > 1 or FR > 1 or RL > 1 or RR > 1:
                slip = 1
            else:
                slip = 0

            if FLP > 17 or FRP > 17 or RLP > 17 or RRP > 17:
                pressure = 1
            else:
                pressure = 0

            if front > 50 or rear > 40 or left > 20 or right > 20 or center > 50:
                engine_status = 0
            else:
                engine_status = 1

            # TODO: what does this do?
            if cycle == 0:
                packet = "<C{}R{}M{}S{}F{}G{}E{}L{}>".format(int(cycle), rpm, mph, int(
                    shift), fuel, int(gear), int(engine_status), int(slip))
                cycle = 1
            elif cycle == 1:
                packet = "<C{}R{}A{}P{}>".format(
                    int(cycle), rpm, int(ab), int(pressure))
                cycle = 0

            # tachometer_serial.write(packet.encode('utf-8'))

            if moog.is_engaged():

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

                if gear != previous_gear:
                    gear_dampening_index = gear_dampening_window_size
                # TODO: Test this
                if gear_dampening_index > 0:
                    z_accel /= gear_dampening_scale_factor
                    gear_dampening_index -= 1
                previous_gear = gear

                x_angle = np.arcsin(
                    max(min(x_accel/9.81, x_accel_limit), -x_accel_limit))
                z_angle = np.arcsin(
                    max(min(z_accel/9.81, z_accel_limit), -z_accel_limit))

                roll = roll + -x_angle

                pitch = -pitch + -z_angle

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
                # send frame
                try:
                    moog.command_dof(
                        roll=final_roll, pitch=final_pitch, yaw=final_yaw)

                except Exception as e:
                    print(e)
            elapsed_time = time.time() - start_time
            sleep_time = 1/frequency - elapsed_time
            # TESTING IF SLEEP IS NECESSARY -- I don't think it is?
            # if sleep_time > 0:
            #     time.sleep(sleep_time)

    asm.close()


if __name__ == "__main__":

    main()
