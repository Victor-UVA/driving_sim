from moog_class import MOOG
import time
import numpy as np
import matplotlib.pyplot as plt

neutral_heave = 29000

def calibrate(acc_desired): # calibrate pos_differential to acc_desired in Gs
    pos_differential = 0
    return pos_differential


def main():
    moog = MOOG()
    moog.initialize_platform()
    amplitude = 11136/8
    sleep_time = 1/60
    samples= np.linspace(0, 14400, 60*14400)
    wave = 16383 + amplitude*np.sin(2*np.pi*4*samples)

    # fig = plt.figure()
    # plt.plot(samples,wave , 'b')
    # plt.show()

    for point in wave:
        moog.command_dof(heave= int(point))
        time.sleep(sleep_time)

# def rough_loop():
#     while True:{
#         for pos in np.arange(32767, 0, -step_size):
#             moog.command_dof(heave=pos)
#             time.sleep(1/60)
#         for pos in np.arange(0, 32767, step_size):
#             moog.command_dof(heave=pos)
#             time.sleep(1/60)


if __name__ == "__main__":

    main()