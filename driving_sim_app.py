from concurrent.futures import thread
from moog_class import MOOG
import time
import pygetwindow as gw
import tkinter as tk
import numpy as np
from assetto_moog_control import accSharedMemory
import csv
import threading
import serial

class DrivingSim():
    def __init__(self):
        self.moog = MOOG()
        self.app = tk.Tk()
        self.app.title('Driving Simulator')
        
        self.assetto_thread = threading.Thread(target=self.assetto_loop)
        self.assetto_thread.start()
        # Assetto Section
        stage_button = tk.Button(self.app, text='Stage Screen', command=self.stage_screen)
        # telemetry_button = tk.Button(self.app, text = 'Record Telemetry', )
        stage_button.pack()
        
        # MOOG Section
        init_button = tk.Button(self.app, text = 'Initialize MOOG', command=self.moog.initialize_platform) #TODO: Require reset before
        estop_button = tk.Button(self.app, text = 'ESTOP', command=self.moog.e_stop)
        disable_button = tk.Button(self.app, text = 'Disable', command=self.moog.disable)
        park_button = tk.Button(self.app, text = 'Park', command=self.moog.park)
        # TODO: Add other commands
        reset_button = tk.Button(self.app, text = 'Reset', command=self.moog.reset)
        inhibit_button = tk.Button(self.app, text = 'Inhibit', command=self.moog.inhibit)
        # begin_button = tk.Button(self.app, text = 'Begin', command=moog_thread.start)
        #TODO: Add text output from moog_class
        # feedback = tk.StringVar(self.app, self.moog.text_output)
        # moog_output = tk.Label(self.app, feedback)

        init_button.pack()
        estop_button.pack() 
        disable_button.pack()
        park_button.pack()
        reset_button.pack()
        inhibit_button.pack()
        # begin_button.pack()
        
        self.app.mainloop()
        self.asm.close()

    def stage_screen(self):
        windows = gw.getAllWindows()
        for window in windows:
            if window.title == 'Assetto Corsa':
                assetto_window : gw.Win32Window = window
                break
        assetto_window.moveTo(2314, 0)
        assetto_window.resizeTo(4900, 1047)

    def telemetry(self, filename):
        fields = ['Time', 'Roll', 'Pitch', 'Yaw/Heading', 'G-Force (X)', 'G-Force (Y)', 'G-Force (Z)']
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(fields)
        # with open(filename, 'a') as f:
            #     writer = csv.writer(f)
            #     writer.writerow([sm.Graphics.current_time, sm.Physics.roll, sm.Physics.pitch, sm.Physics.heading, sm.Physics.g_force.x, sm.Physics.g_force.y, sm.Physics.g_force.z])

    def assetto_loop(self):
        asm = accSharedMemory()

        roll_window_size = 15
        pitch_window_size = 18
        roll_avg = np.zeros(roll_window_size)
        pitch_avg = np.zeros(pitch_window_size)
        index = 0
        initialized = False
        p_t = 0    
        frequency = 960 # Hz

        tachometer_serial = serial.Serial(
            port = 'COM4',
            baudrate = 115200,
            timeout=0,
            rtscts=True
        )
        time.sleep(1)
        while threading.main_thread().is_alive():# listen for lock or something
            start_time = time.time()
            sm = asm.read_shared_memory()

            if sm is not None:
                max_rpm = sm.Static.max_rpm
                rpm = round(sm.Physics.rpm/100)*100

                kmh = sm.Physics.speed_kmh
                mph = int(kmh/1.60934)

                shift = (max_rpm - rpm) <= 800   

                fuel = int(100 - (sm.Physics.fuel / sm.Static.max_fuel) * 100)

                gear = sm.Physics.gear

                packet = "<RPM{}MPH{}SHIFT{}FUEL{}GEAR{}>".format(rpm, mph, int(shift), fuel, gear)
                tachometer_serial.write(packet.encode('utf-8'))
                if self.moog.is_engaged():
                    # save rpy and derivatives
                    roll = sm.Physics.roll
                    pitch = sm.Physics.pitch
                    yaw = sm.Physics.heading

                    t = sm.Graphics.current_time
                    dt= (t-p_t)/1000 # s
                    if dt == 0 :
                        dt = 0.001
                    
                    p_t = t
                    
                    x_accel = sm.Physics.g_force.x
                    z_accel = sm.Physics.g_force.z
                
                    x_angle = np.arcsin(max(min(x_accel/9.81, 1), -1))
                    z_angle = np.arcsin(max(min(z_accel/9.81, 1), -1))

                    roll = roll + -x_angle

                    pitch = -pitch + -z_angle

                    roll = roll * 180 / np.pi 
                    pitch = pitch * 180 / np.pi

                    roll = max(min(roll, 29), -29)
                    pitch = max(min(pitch, 33), -33)

                    roll = max(int(32767/58 * (roll + 29)), 0)
                    pitch = max(int(32767/66 * (pitch + 33)), 0)
                    
                    if not initialized:
                        roll_avg = np.full(roll_window_size, roll)
                        pitch_avg = np.full(pitch_window_size, pitch)
                        initialized = True
                    roll_avg[index % roll_window_size] = roll
                    pitch_avg[index % pitch_window_size] = pitch
                    index += 1
                    roll_scale_factor = 1.0
                    pitch_scale_factor = 1.0

                    final_roll = int(roll_scale_factor*sum(roll_avg)/roll_window_size)
                    final_pitch = int(pitch_scale_factor*sum(pitch_avg)/pitch_window_size)

                    try:
                        self.moog.command_dof(roll=final_roll, pitch=final_pitch) # TODO: Try a callback
                    except Exception as e: 
                        print(e)
                    elapsed_time = time.time() - start_time

                    sleep_time = 1/frequency - elapsed_time
                    if sleep_time > 0:
                        time.sleep(sleep_time)


if __name__ == "__main__":
    ds = DrivingSim()