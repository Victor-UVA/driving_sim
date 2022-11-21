from moog_class import MOOG
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

amplitude = 110
sleep_time = 0.2 # 0.2 = borderline acceptable
duration = 30 # s 
resolution = 600 # Hz
period = 1/resolution # s

samples= np.linspace(0, duration, resolution*duration) #s
wave = amplitude*np.sin(2*np.pi*4*samples) + 16383 


fig = plt.figure()
ax1 = plt.subplot()

moog = MOOG()


def main():
    moog.override_frequency(60)
    moog.initialize_platform()


    while True:
        moog.command_dof(heave = 16383 + amplitude)
        time.sleep(sleep_time)
        moog.command_dof(heave = 16383 - amplitude)
        time.sleep(sleep_time)
    moog.park()

        
    # for point in wave:
    #     print("Sent:" + str(int(point)))
    #     moog.command_dof(heave= int(point), buffer=True)
      
    # while moog.is_engaged():
    #     pass



if __name__ == "__main__":

    main()


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


        
    # ani = animation.FuncAnimation(fig, animate, fargs=(timestamps, points, wave), interval = period*1000)
    # ax1.plot(samples, wave)
    # plt.show()