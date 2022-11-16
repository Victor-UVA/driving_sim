from moog_class import MOOG
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

neutral_heave = 29000

amplitude = 11136/16
duration = 30 # s 
frequency = 60 # Hz
period = 1/frequency # s

samples= np.linspace(0, duration, frequency*duration) #s
wave = amplitude*np.sin(2*np.pi*4*samples) + 16383 


fig = plt.figure()
ax1 = plt.subplot()

moog = MOOG()

# timestamps = []
# points = []
# datapoints = 60

# def animate(i, timestamps, points, wave):
#     timestamps.append(time.time())
#     points.append(wave[i])

#     timestamps = timestamps[-datapoints:]
#     points = points[-datapoints:]

#     moog.command_dof(heave= int(wave[i]))

#     ax1.clear()
#     ax1.plot(timestamps, points, label="Heave")
#     plt.xticks(rotation=45, ha='right')
#     plt.subplots_adjust(bottom=0.30)

#     ax1.set_ylabel('Heave')
#     ax1.set_xlabel('Time')



def main():
    moog.initialize_platform()

    # ani = animation.FuncAnimation(fig, animate, fargs=(timestamps, points, wave), interval = period*1000)
    # ax1.plot(samples, wave)
    # plt.show()

    for point in wave:
        # start_time = time.time()
        # print(point)
        moog.command_dof(heave= int(point), buffer=True)
        # elapsed_time = time.time() - start_time
        # sleep_time = period - elapsed_time
        # if sleep_time > 0:
        #     time.sleep(sleep_time)
    while moog.is_engaged():
        pass



if __name__ == "__main__":

    main()