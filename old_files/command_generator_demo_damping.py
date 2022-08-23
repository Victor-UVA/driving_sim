
# Command Generator Script - Generates new commands for the platform, and calculates checksum
# Status:        
# Written by:    Cameron Miksh, Jihong Cai, Robert Krammer
# Last Update:   2/10/17

#===============================================================================
#--------------------------    Import Libraries     ----------------------------
import time
import binascii
from select import select
import sys
import zmq
from decimal import *
import math
import matplotlib.pyplot as plt


sleepy_time = float(1/60)
sleepy_time = sleepy_time/100

#===============================================================================
#-----   Subscribe to ZMQ telemetry socket (publisher = TCP.py)    -------------

context = zmq.Context()
socket_telemetry = context.socket(zmq.SUB)

socket_telemetry.connect("tcp://localhost:7979")

farts=b''
# socket_telemetry.setsockopt(zmq.SUBSCRIBE,farts)
socket_telemetry.setsockopt_string(zmq.SUBSCRIBE,farts)

#===============================================================================
#--   Subscribe to ZMQ platform status socket (publisher = communication.py)  --

context = zmq.Context()
socket_platform_status = context.socket(zmq.SUB)

socket_platform_status.connect("tcp://localhost:8989")

farts=b''
# socket_platform_status.setsockopt(zmq.SUBSCRIBE,farts)
socket_platform_status.setsockopt_string(zmq.SUBSCRIBE,farts)


#===============================================================================
#------------------     Define Timer Functions     -----------------------------
   #tic() function: records current Unix time (very accurate)
def tic():
    global startTime_for_tictoc
    startTime_for_tictoc = time.time()
    
   #toc() function: records current Unix time and subtracts the difference. 
   #Returns elapsed time to variable 'calctime'
def toc():
	if 'startTime_for_tictoc':
		global calctime
		calctime = time.time() - startTime_for_tictoc

writetime = 60**-1

#===============================================================================
#-------------     Define call_telemery() function        ----------------------

def call_telemetry():
	string = socket_telemetry.recv()

#	The part below was added in order to not have whole number rounding,
#	so it splits both sides of the decimal into integers so that they stay intact
#	then they can be put back together, not losing data and accuracy
	
	speed_before_dec, speed_after_dec, RPM, orientation_before_dec, orientation_after_dec, altitude_before_dec, altitude_after_dec, longitude_before_dec, longitude_after_dec, latitude_before_dec, latitude_after_dec, steerAngle_before_dec, steerAngle_after_dec, brakePedal_before_dec, brakePedal_after_dec, gasPedal_before_dec, gasPedal_after_dec, acceleration_before_dec, acceleration_after_dec = string.split()
	
	global speed
	speed = speed_before_dec + '.' + speed_after_dec
	RPM = RPM
	orientation = orientation_before_dec + '.' + orientation_after_dec
	altitude = altitude_before_dec + '.' + altitude_after_dec
	longitude = longitude_before_dec + '.' + longitude_after_dec
	latitude = latitude_before_dec + '.' + latitude_after_dec
	steerAngle =steerAngle_before_dec + '.' + steerAngle_after_dec
	brakePedal = brakePedal_before_dec + '.' + brakePedal_after_dec
	gasPedal = gasPedal_before_dec + '.' + gasPedal_after_dec
	global Acceleration1
	flipped_accel_after_dec = acceleration_after_dec[::-1]
	Acceleration1 = float(acceleration_before_dec + '.' + flipped_accel_after_dec)
	
	"""
	print ('Speed = ') + speed + '\n'
	print ('RPM = ') + RPM  + '\n'
	print ('Orientation = ') + orientation + '\n'
	print ('Altitude = ') + altitude + '\n'
	print ('Longitude = ') + longitude + '\n'
	print ('Latitude = ') + latitude + '\n'
	print ('Steering Wheel Angle = ') + steerAngle + '\n'
	print ('Brake Pedal = ') + brakePedal + '\n'
	print ('Gas Pedal = ') + gasPedal + '\n'
	print('***********         command_generator data				******')
	"""
	"""
	global steering_angle 
	steering_angle = steerAngle_before_dec + '.' + steerAngle_after_dec
	return steering_angle
	"""
	global steering_angle
	steering_angle = steerAngle
	return steering_angle, Acceleration1, speed
#===============================================================================
#-------------      Define call_status_platform() function      ----------------

def call_status_platform():	
	#print('Calling Platform Status......')
	status_platform = socket_platform_status.recv()
	time.sleep(.0079)
	# slice up platform_status and make it into a list
	fault = False
	fault_name = 'Fault Status: '
	status_platform = status_platform[2:36]
	n = 2
	list_status_platform = [status_platform[i:i+n] for i in range(0, len(status_platform), n)]
		
	global fault_data_1	
	fault_data_1 = list_status_platform[0]
	global fault_data_2
	fault_data_2 = list_status_platform[1]
	global discrete_io_info
	discrete_io_info = list_status_platform[2]
	global act_a_low_feedback
	act_a_low_feedback = list_status_platform[4]     # skip number here (#3 = checksum whcih we dont 	need)
	global act_a_high_feedback
	act_a_high_feedback = list_status_platform[5]
	global act_b_low_feedback
	act_b_low_feedback = list_status_platform[6]
	global act_b_high_feedback
	act_b_high_feedback = list_status_platform[7]
	global act_c_low_feedback
	act_c_low_feedback = list_status_platform[8]
	global act_c_high_feedback
	act_c_high_feedback = list_status_platform[9]
	global act_d_low_feedback
	act_d_low_feedback = list_status_platform[10]
	global act_d_high_feedback
	act_d_high_feedback = list_status_platform[11]
	global act_e_low_feedback
	act_e_low_feedback = list_status_platform[12]
	global act_e_high_feedback
	act_e_high_feedback = list_status_platform[13]
	global act_f_low_feedback
	act_f_low_feedback = list_status_platform[14]	
	global act_f_high_feedback
	act_f_high_feedback = list_status_platform[15]
	global machine_state_info
	machine_state_info = list_status_platform[16]
	
	return fault_data_1, fault_data_2, discrete_io_info, act_a_low_feedback, act_a_high_feedback, act_b_low_feedback, act_b_high_feedback, act_c_low_feedback, act_c_high_feedback, act_d_low_feedback, act_d_high_feedback, act_e_low_feedback, act_e_high_feedback, act_f_low_feedback, act_f_high_feedback, machine_state_info

#===============================================================================
#------------         Define hex_cmd_type() function         -------------------

def hex_cmd_type(command):
	# Hex Commands - Command Byte
	global cmd_type_dictionary
	cmd_type_dictionary = {'estop':'E6', 'disable':'DC', 'park':'D2', 'low_limit_eneable':'C8', 'low_limit_disable':'BE', 'engage':'B4', 'start':'AF', 'length_mode':'AC', 'dof_mode':'AA', 'reset':'A0', 'inhibit':'96', 'reserved':'8C', 'new_position':'82'}
	cmd = cmd_type_dictionary[command]
	return cmd

	
#===============================================================================	
#-----------         Define command_checksum() function         ----------------
	
def command_checksum(new_hex_cmd_type,cmd):
	roll = cmd[0]
	pitch = cmd[1]
	heave = cmd[2]
	surge = cmd[3]
	yaw = cmd[4]
	lateral = cmd[5]
	
	#-------------------------------------------------------------
	# Set hex commands for the first, second, and last bytes  (byte 0,1,15,16)
	# [0=Frame sync, 1=Command byte, 15=ID low, 16=ID high]

	command_prefix_hex = 'ff'								# first byte (byte 0)
	command_prefix_dec =  int(command_prefix_hex,16)
	command_byte_hex = new_hex_cmd_type # second byte (byte 1) sent to platform, hex command for new position
	command_byte_dec =	 int(command_byte_hex,16)			# other commands listed in manual page 2-2
	command_machine_id_hex_1 = '29'							# machine ID part1 in hex
	command_machine_id_hex_2 = '00'							# machine ID part2 in hex
	command_machine_id_dec_1 = int(command_machine_id_hex_1,16)
	command_machine_id_dec_2 = int(command_machine_id_hex_2,16)
	command_machine_id_dec = command_machine_id_dec_1 + command_machine_id_dec_2

	#----------------------------------------------------
	# Initialize lists

	command_decimal=[1,1,1,1,1,1]
	command_hex = [1,1,1,1,1,1]
	firsthalf = [1,1,1,1,1,1]
	secondhalf = [1,1,1,1,1,1]
	command_hex_split = [1,1,1,1,1,1,1,1,1,1,1,1]
	command_dec_split = [1,1,1,1,1,1,1,1,1,1,1,1]
		
	#------------------------------------------------------------------------
	# Create hex string from decimal Motion commands	
	i=0
	while i<6:
		command_hex[i]=long(command_hex[i])						# convert hex command to long format
		command_decimal[i]=long(cmd[i])							# convert dec command to long format
		command_hex[i]=command_decimal[i]						# copy dec command list to hex command list
		command_hex[i]=hex(command_hex[i])						# convert hex list variable into hex 																	characters
		ggg=len(command_hex[i])-1								# used to drop 'L' from long variables
		command_hex[i]=command_hex[i][2:ggg]					# read the (hex) command dropping the '0x'
		firsthalf[i], secondhalf[i] = command_hex[i][:len(command_hex[i])/2], command_hex[i][len(command_hex[i])/2:] 													 # split each command in half 	
		secondhalf[i] = str(secondhalf[i])
		firsthalf[i] = str(firsthalf[i])
		SH_length = len(secondhalf[i])
		FH_length = len(firsthalf[i])
		if firsthalf[i] == '':									# This allows for a byte to be less than two digits
			firsthalf[i] = '00' + firsthalf[i]					# and even zero, fills in blanks to keep it two digits
		if secondhalf[i] == '':									# so that the platform pc receives 20 byte messages
			secondhalf[i] = '00' + secondhalf[i]
		if FH_length == 1:
			firsthalf[i] = '0' + firsthalf[i]
		if SH_length == 1:
			secondhalf[i] = '0' + secondhalf[i]
		i=i+1	
	#--------------------------------------------------------------------------
	# Make sure all lists contain zeros instead of blank spaces
	i=0
	g=0
	while g<6:													#Does this duplicate the above?? RK
		if firsthalf[i] == "":
			firsthalf[i]=str(0)
			i=i+1	
		else:
			farts = 0
			i=i+1
		if secondhalf[g] == "":
			secondhalf[g]=str(0)
			g=g+1
		else:
			farts = 0
			g=g+1	
	#---------------------------------------------------------------------------
	# Split hex commands into 2bit strings, and translate to decimal		
	
	i=0
	gg=0
	hh=0
	
	while i<12:
		command_hex_split[i] = str(command_hex_split[i])
		command_hex_split[i] = secondhalf[gg]
		ii=i+1
		command_hex_split[ii] =firsthalf[gg]
		command_dec_split[hh] = int(command_hex_split[hh],16)
		hh=hh+1
		command_dec_split[hh] = int(command_hex_split[hh],16)
		hh=hh+1
		gg=gg+1
		i=i+2

	#---------------------------------------------------------------------------
	# Compute checksum
	
	checksum = int(0)
	checksum = sum(command_dec_split)					         		 # add all motion commands together
	checksum = checksum + command_byte_dec + command_machine_id_dec   	 # add remaining commands
	
	checksum_hex = hex(checksum)										 # convert to hex
	checksum_hex_spliced = checksum_hex[-2:]							 # get rid of everything but lowest 2 																					bits	
	checksum_binary = bin(int(checksum_hex_spliced, 16))[2:]			 # convert to binary			

	#---------------------------------------------------------------------------
	# Make MSB = 0 if it is 8 bits or longer
	
	zeroed_checksum_binary_final=str('')
	length = len(checksum_binary)										#check length of binary checksum
	if length==8:	
																		# if length is 8, zero MSB
		checksum_binary= list(checksum_binary)							# convert to list
		checksum_binary[0] = '0'										# reassign first byte to 0
		rrr=0															# counter
		zeroed_checksum_binary=[0,0,0,0,0,0,0,0]						# initialize list
		while rrr<length:	
																		# reassemble binary string
			zeroed_checksum_binary[rrr]=checksum_binary[rrr]
			zeroed_checksum_binary_final= zeroed_checksum_binary_final + zeroed_checksum_binary[rrr] 
			rrr=rrr+1
	else:
		zeroed_checksum_binary_final = checksum_binary
	
	final_hex_checksum = hex(int(zeroed_checksum_binary_final, 2))[2:]			# value of the hex checksumto send to 																					  platform  must reassemble full command 																					and format before sending
	length_checksum = len(str(final_hex_checksum))
	if length_checksum == 0:											# used to make checksum into a full byte 
		final_hex_checksum = 00											# message with two digits
	elif length_checksum ==1:											# makes it two digits if not already
		final_hex_checksum = '0' + final_hex_checksum

	#---------------------------------------------------------------------------
	# Assemble final command
	
	assembled_command = command_prefix_hex + command_byte_hex + final_hex_checksum 
	i=0
	while i<12:
		assembled_command = assembled_command + command_hex_split[i]
		i=i+1
	global final_command
	final_command = assembled_command + command_machine_id_hex_1 + command_machine_id_hex_2
	#print final_command
	final_command = final_command.decode("hex")         #transfer to hex
	return final_command


#===============================================================================
#------------------      Define   check_state()  function    -------------------
def check_state():
	call_status_platform()
	time.sleep(sleepy_time)
	bin_machine_state_info = bin(int(machine_state_info, 16)).zfill(8)
	bin_machine_state_info = str(bin_machine_state_info)
	bin_machine_state_info = bin_machine_state_info.replace("b", "")
	global mode
	mode =  bin_machine_state_info[2]
	bin_machine_state_info = bin_machine_state_info[3:7]
	#print bin_machine_state_info
	msi = bin_machine_state_info
	#print('%%%%%%%%%')
	if msi == '0000':
		Platform_State = 'Power-Up'
	elif msi == '0001':
		Platform_State = 'Idle'
	elif msi == '0010':
		Platform_State = 'Standby'
	elif msi == '0011':
		Platform_State = 'Engaged'
	elif msi == '1000':
		Platform_State = 'Parking'
	elif msi == '1001':
		Platform_State = 'Fault 2'
	elif msi == '1010':
		Platform_State = 'Fault 3'
	elif msi == '1011':
		Platform_State = 'Dasabled'
	elif msi == '1100':
		Platform_State = 'Inhibited'
	else:
		Platform_State = 'State Read Error'
	global state
	state = Platform_State
	return state, mode
	
	
#===============================================================================	
#===============================================================================		
#===============================================================================
#==============        Define Platform Commands       ==========================


#===============================================================================
#------------          Define Initialize_Platform()         --------------------
# DANGER: THIS WILL BEGIN PLATFORM ACTUATION, PERFORM SAFETY CHECKS PRIOR TO EXECUTING
def Initialize_Platform():	
	#  Initial command (length mode) [NEVER CHANGES]
	cmd = [1024, 1024, 1024, 1024, 1024, 1024]				# Length Mode: Roll, Pitch, Heave, Surge, Yaw, Lateral

	while True:
		print('\n\n		Connecting to communication.py:')
		check_state()
		print('')
		# send DOF command
		new_hex_cmd_type = hex_cmd_type('new_position')				# command type = new position (82 in hex)
		final_command1 = command_checksum(new_hex_cmd_type,cmd)		# calculate checksum
		socket_new_command.send("%s" % (final_command1))			# send command
		check_state()
		if state =='Idle':
			print('		Idle State Reached.\n')
			break
			
	#-------------------------------------------------------------------------------
	# Change mode to DOF [NEVER CHANGES]
	cmd = [16383, 16383, 29000, 16383, 16383, 16383]				# DOF: Roll, Pitch, Heave, Surge, Yaw, Lateral
	while True:
		check_state()
		time.sleep(sleepy_time*2)	
		new_hex_cmd_type = hex_cmd_type('dof_mode')					# command type = DOF command
		print('		DOF mode requested...\n')
		final_command1 = command_checksum(new_hex_cmd_type,cmd)		# calculate checksum
		time.sleep(sleepy_time*3)	
		socket_new_command.send("%s" % (final_command1))			# send command
		time.sleep(sleepy_time*2)	
		if mode == '1':
			print('		DOF mode entered.\n')
			break

	#-------------------------------------------------------------------------------
	#  Continue sending new position (DOF mode) [NEVER CHANGES]
	cmd = [16383, 16383, 29000, 16383, 16383, 16383]				# DOF: Roll, Pitch, Heave, Surge, Yaw, Lateral
	pp=0
	while pp<8:
		check_state()
		time.sleep(sleepy_time)
		new_hex_cmd_type = hex_cmd_type('new_position')				# command type = new position (82 in hex)
		final_command1 = command_checksum(new_hex_cmd_type,cmd)		# calculate checksum
		try:
			socket_new_command.send("%s" % (final_command1)) 		# send command
		except:
			yyyyyyyyyyyy=0
		time.sleep(.005)
		pp=pp+1
	#-------------------------------------------------------------------------------
	# Engage command [NEVER CHANGES]
	cmd = [16383, 16383, 29000, 16383, 16383, 16383]				# DOF: Roll, Pitch, Heave, Surge, Yaw, Lateral
	check_state()
	time.sleep(sleepy_time)
	new_hex_cmd_type = hex_cmd_type('engage')						# command type = Engage command
	final_command1 = command_checksum(new_hex_cmd_type,cmd)			# calculate checksum
	try:
		socket_new_command.send("%s" % (final_command1))			# send command
	except:
		yyyyyyyyyyyyyy=0
	print('		Platform Engaging........\n')
	#-------------------------------------------------------------------------------
	# New Position [NEVER CHANGES]
	cmd = [16383, 16383, 29000, 16383, 16383, 16383]				# DOF: Roll, Pitch, Heave, Surge, Yaw, Lateral
	while True:
		check_state()
		time.sleep(sleepy_time)
		time.sleep(sleepy_time)	
		new_hex_cmd_type = hex_cmd_type('new_position')				# command type = new position (82 in hex)
		final_command1 = command_checksum(new_hex_cmd_type,cmd)		# calculate checksum
		try:
			socket_new_command.send("%s" % (final_command1))		# send command
		except:
			yyyyyyyyyyy=0
		check_state()
		if state =='Engaged':
			print('		State = Engaged\n')
			break

#===============================================================================	
#--------       Define  New_Position_Command(cmd)  function   ----------
def New_Position_Command(cmd):
	yy=0
	while yy<1:								# number of iterations to send at 60hz yy = 1 is equivalent 													to 0.016666667 seconds
		check_state()
		time.sleep(sleepy_time)
		new_hex_cmd_type = hex_cmd_type('new_position')				# command type = new position (82 in hex)
		final_command1 = command_checksum(new_hex_cmd_type,cmd)		# calculate checksum
		try:
			socket_new_command.send("%s" % (final_command1))		# send command
		except:
			yyyyyyyyyyyyyyyyyyyy=0
		yy=yy+1	
	
	
#===============================================================================	
#-------------------       Define  Park() command    ---------------------------	
# Must be called at the end, otherwise base will fault
	
def Park():
	# Park [NEVER CHANGES]
	cmd =  [16383, 16383, 29000, 16383, 16383, 16383]				# DOF: Roll, Pitch, Heave, Surge, Yaw, Lateral
	while True:
		check_state()
		time.sleep(sleepy_time)
		time.sleep(sleepy_time)	
		new_hex_cmd_type = hex_cmd_type('park')						# command type = PARK command
		final_command1 = command_checksum(new_hex_cmd_type,cmd)		# calculate checksum
		try:
			socket_new_command.send("%s" % (final_command1))		# send command
			print('		Parking........\n		Please remain seated.')
			time.sleep(sleepy_time/2)
		except:
			yyyyyyyyyyyyyyyyy=0
		if state =='Idle':
			print('		State = Idle\n')
			break
	print('\n\n\n\n		#######################################\n		#######################################\n		#######################################\n		#                                     #\n		#                                     #\n		#                Parked.              #\n		#                                     #\n		#              Ride over.             #\n		#                                     #\n		#       It is safe to unbuckle!       #\n		#                                     #\n		#                                     #\n		#######################################\n		#######################################\n		#######################################')
	

#===============================================================================
#===============================================================================
#-------------------         Define Reaction         --------------------------

# Define Brake reaction
def brake_reaction():
	if Acceleration1> pos_accel:			
		cmd[1] = 16383 + (Acceleration1)*(-500)					# Pitch back for positive acceleration	
		return cmd[1]
	elif Acceleration1< neg_accel:	
		cmd[1] = 16383 + (Acceleration1)*(-700)					# Pitch forward for decceleration
		return cmd[1]
	elif Acceleration1> neg_accel and Acceleration1<pos_accel:
		cmd[1] = 16383
		return cmd[1]
	else:
		cmd[1] = 16383
		return cmd[1]

# Define Steering Reaction
def steering_reaction():
	if steering_angle > gentle_left:				
		cmd[0] = 16383 - float(steering_angle)*(-130)*(float(speed) /60) 			# gently pitch right
		return cmd[0]
	elif steering_angle < gentle_right:	
		cmd[0] = 16383 + float(steering_angle)*(-130)*(float(speed) /60)			# gently pitch left
		return cmd[0]
	elif steering_angle > gentle_right and steering_angle < gentle_left:
		cmd[0] = 16383
		return cmd[0]
	else:
		cmd[0] = 16383
		return cmd[0]
#=================================================================================
#-   Initialize Zero MQ messenger service (publishes commands to communication.py)

context= zmq.Context()
socket_new_command = context.socket(zmq.PUB)
socket_new_command.bind("tcp://*:9999")



#===============================================================================
#===============================================================================
#===============================================================================
#------------------             Main Loops            --------------------------
#-------------------------------------------------------------------------------
print('------------          Command Generator Script        ----------------\n-----------------------------------------------------------------')

#------------------------------------------------------------------------------
#-   Initialize Zero MQ messenger service (publishes commands to communication.py)

context= zmq.Context()
socket_new_command = context.socket(zmq.PUB)
socket_new_command.bind("tcp://*:9999")

#===============================================================================
#Read CSV suspension reaction data


import csv
from collections import defaultdict

columns = defaultdict(list) # each value in each column is appended to a list

# with open('/home/tomonari/Desktop/Cameron/csv_60hz.csv') as f:
# with open('/home/drivesim/demos/damping_demo/csv_60hz.csv') as f:
# with open('/home/drivesim/demos/damping_demo/reaction_csv.csv') as f:
#     reader = csv.DictReader(f) # read rows into a dictionary format
#     for row in reader: # read a row as {column1: value1, column2: value2,...}
#         for (k,v) in row.items(): # go over each column name and value 
#             columns[k].append(v) # append the value into the appropriate list # based on column name k





#-------------------------------------------------------------------------------
# Start sending commands

Initialize_Platform()
time.sleep(2)
print('		Damping demonstration beginning.....')
time.sleep(2)

roll = 16383		#  cmd[0]
pitch = 16383		#  cmd[1]
# heave = 16383		#  cmd[2]
heave = 20000	    #  cmd[2]
surge = 16383		#  cmd[3]
yaw = 16383			#  cmd[4]
lateral = 16383		#  cmd[5]

cmd = [roll, pitch, heave, surge, yaw, lateral] 
New_Position_Command(cmd)

time.sleep(3)

"""
now = time.time()
plt.axis([0, 600, -3, 0])
plt.ion()
array_x=[]
array_z=[]
plt.plot(array_x, array_z)
plt.show()
short_sleep = 10**-36
"""

# i=4 # For damping
i=3 # For reaction

# gain = 8000
gain = 5000

# while i<600:
# 	tic()										# referencing values from damping demo .csv file
# 	cmd[2] = heave + gain*float(columns[k][i])
# 	New_Position_Command(cmd)
# 	i = i+1
# 	"""											# uses value, then skips 3 for smoother motion
# 	array_x.append(i)
# 	array_z.append(columns[k][i])
# 	plt.plot(array_x, array_z)
# 	plt.pause(short_sleep)
# 	"""
# 	toc()
# 	if calctime < writetime:
# 		sleeptime = writetime - calctime
# 		time.sleep(sleeptime)

while i < 153:
	cmd[2] = heave + gain * float(columns[k][i])
	New_Position_Command(cmd)
	i = i + 1
	print('Command:\n', cmd)

time.sleep(4)
Park()





