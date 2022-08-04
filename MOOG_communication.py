#!/usr/bin/env python

import time
import serial 

ser = serial.Serial(
	port = 'COM3', 
	baudrate = 57600,
	parity = serial.PARITY_NONE,
	stopbits = serial.STOPBITS_ONE,
	bytesize = serial.EIGHTBITS,
	timeout = None,
)
# ser.flushInput()
# ser.reset_input_buffer()
# ser.flushOutput()
# ser.reset_output_buffer()
# time.sleep(3)

command = 0
cmd = b"\xff\x82\x43\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x29\x00" # this is the command to enter idle state
# cmd = "ff82430004000400040004000400042900" # this is the command to enter idle state

# structure of this command is listed in the document online
# no inputs for now, so I will have it automatically try to raise up. 
now = time.time()
check1 = now + 5 # so it will switch to engage after 45 seconds
check2 = now + 6 # switch back to initial command right after
check3 = now + 20 # switch to extend
# check3 = now + 22 # andrew testing
check4 = now + 30 # switch back to initial position
# check4 = now + 27 # andrew testing
check5 = now + 45 # switch to park
check6 = now + 46 # switch to send new postion command
check7 = now + 51 

startTime_for_tictoc = 0 
elapsed_time = 0
def tic():
	global startTime_for_tictoc
	startTime_for_tictoc = time.time()
	
def toc():
	global elapsed_time
	global startTime_for_tictoc

	elapsed_time = time.time() - startTime_for_tictoc


while 1:
	print(cmd)
	tic()
	ser.write(cmd)
	
	if (time.time() < check1):
		cmd = b"\xff\x82\x43\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x29\x00" # this is the command to enter idle state
	elif (time.time() > check1 and time.time() < check2):
		cmd = b"\xff\xB4\x75\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x29\x00" # this is the command to enter engage state
	elif (time.time() > check2 and time.time() < check3):
		cmd = b"\xff\x82\x43\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x29\x00" # this is the command to enter extend state
	elif (time.time() > check3 and time.time() < check4):
		cmd = b"\xff\x82\x1A\x10\x27\x10\x27\x10\x27\x20\x4e\x20\x4e\x20\x4e\x29\x00" # this is the command to enter extend state
	elif (time.time() > check4 and time.time() < check5):
		cmd = b"\xff\x82\x1A\x20\x4e\x20\x4e\x20\x4e\x10\x27\x10\x27\x10\x27\x29\x00" # this is the command to enter idle state
	elif (time.time() > check5 and time.time() < check6):
		cmd = b"\xff\xD2\x6A\x20\x4e\x20\x4e\x20\x4e\x10\x27\x10\x27\x10\x27\x29\x00" # this is the command to enter idle state
	elif (time.time() > check6 and time.time() < check7):
		cmd = b"\xff\x82\x43\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x29\x00" # this is the command to enter idle state
	else:
		cmd = b"\xff\x82\x43\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x29\x00" # this is the command to enter idle state
	toc()
	time.sleep(1/60 - elapsed_time)
#	n = 1
#	while n<2:
#		if input == 'engage'
#		command = "\xff\xB4\x75\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x29\x00"
#		ser.write(command)
#		n=n+1
#	if input == 'extend'
#		cmd = "\xff\x82\x1f\xff\x3f\xff\x3f\xff\x3f\xff\x3f\xff\x3f\xff\x3f\x29\x00" #extend command
#	else
#		cmd = "\xff\x82\x43\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x29\x00" #zero command 
#
# below is test code that will calculate the zero MSB 
# first is converting the hex to the decimal value:
# 2n = second byte, the command byte
# 4n = fourth byte, the first actuator byte
# 5n = fifth byte, the second actuator byte
# and so on
# 2h = int("2n",16) this is how you convert to decimal value
# 4h = int("4n",16)
# and so on
# summation = 2h + 4h + ... + 17n
# binsum = bin(summation) converts the sum to binary
# how to make the leading bit a zero is going to be a challenge
# 
