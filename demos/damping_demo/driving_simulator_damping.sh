#!/bin/bash
#set -x
echo 'Platform booting up, make sure area is clear.... '
sleep 1
killall screen

echo  Welcome
echo  Driving simulator starting....
# cd /home/tomonari/opends4.0
sleep 1
# python /home/tomonari/Desktop/driving_simulator/communication.py &
python /home/drivesim/demos/damping_demo/communication.py &
sleep 1
# python /home/tomonari/Desktop/driving_simulator/command_generator_demo_damping.py
python /home/drivesim/demos/damping_demo/command_generator_demo_damping.py
