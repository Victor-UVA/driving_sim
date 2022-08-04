######### Communication script - Listens to platform and issues commands at 60hz
# Status: Functioning
# Written by: Cameron Miksh, Jihong Cai
# Last Update: 3/28/17

#===============================================================================
#----------------------      Import Libraries     ------------------------------

import time
import serial
import sys
from select import select
import zmq

#===============================================================================
#------------------     Define Timer Functions     -----------------------------
#   tic() function: records current Unix time (very accurate)

def tic():
    global startTime_for_tictoc
    startTime_for_tictoc = time.time()
    
#   toc() function: records current Unix time and subtracts the difference. 
#   Returns elapsed time to variable 'calctime'
def toc():
	if 'startTime_for_tictoc':
		global calctime
		calctime = time.time() - startTime_for_tictoc

writetime = 60**-1

#===============================================================================
#------------       Set up serial connections   --------------------------------
# This is the main connection to the platform.  Commands are delivered at 60 hz using this script.
ser2 = serial.Serial(
    port = 'COM3',
    baudrate = 57600,							# Serial port transfer rate (bits/s)
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 0.002
)


#===============================================================================
#------------        Initialize Zero MQ publishers           --------------------
# These publishers deliver the platform status message to the safety light script and the command generator script

# The first publisher named 'socket' publishes to port 8989 which the command generator script listens to
context= zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:8989")

# The second publisher named 'socket2' publishes to port 8008 which is listened to by the safety light script
context= zmq.Context()
socket2 = context.socket(zmq.PUB)
socket2.bind("tcp://*:8008")

#===============================================================================
#-----------         Initialize Zero MQ subscriber          --------------------
# This subscriber listens to the command generator script which is delivering new platform position commands

context = zmq.Context()
socket_new_command = context.socket(zmq.SUB)
socket_new_command.connect("tcp://localhost:9999")
blank=b''
socket_new_command.setsockopt(zmq.SUBSCRIBE,blank)
socket_new_command.RCVTIMEO =1  # in milliseconds

#===============================================================================
#---------      Define   communicate(new_command)  Function      ---------------
# This function writes commands to the motion platform.  This must happen continuously at 60 hz.  Every time the 17 byte command is written to the platform a 20 byte status message is returned.   The formatting of these messages is detailed in the Moog manual.

def communicate(new_command):
	tic()
	# ser2.write(new_command)					        # Write initial command to platform base
	bytesToRead = 20
	global status_platform1
	status_platform1 = ser2.read(bytesToRead).hex()        # Read full platform status message
	toc()
	return status_platform1

#==============================================================================
#-----------      Define send_status(status_platform) Command       -----------
# This function forwards the 20 byte platform status message to the Command Generator script and the Safety Light script.
 
def send_status(status_platform1):
	socket.send_string("%s" % (status_platform1))
	socket2.send_string("%s" % (status_platform1))

#==============================================================================
#------------     Define   get_new_command(last_command)  function   ----------
# This function tries to get a new platform position command from the command generator script.  If it is no new command available it will use the most recent command.

def get_new_command(last_command):
	while True:
		try:
			data = socket_new_command.recv()
			new_command = data
			return new_command
			break
		except:
			new_command = last_command
			return new_command
			break



#==============================================================================
#==============================================================================
#==============================================================================
#-------------------              Main Loop             -----------------------

# Prints to the terminal window
print('\n\n\n------------------------------------------------------------------\n------------          Communication Script        ----------------\n------------------------------------------------------------------\n')

# Initial command to begin communication with the platform
first_command = "\xff\x82\x43\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x29\x00"		

# Loop variables 
check = 0
checkcheck = 0

# Initial communication loop
while check < 1:
	while checkcheck < 1:
		# try:
		status_platform = communicate(first_command)		# introduces the first command to the platform
		checkcheck = checkcheck +1
		# except:
			# print('Communication failed.')
	time.sleep(writetime/4)
	last_command = first_command								# sets the first command to the previous
	try:
		send_status(status_platform)
		check = check + 1
	except:
		print('Platform status not received.')
	time.sleep(writetime/4)
	user_message = ' Communicating...'
	print(user_message + '\n\n')
	
#-----------------------------------------------------------------------------
#
print_counter = 0

while True:	
	tic()											# Start timer
	print_counter = print_counter + 1
	
	# This section creates a loading bar type output to the terminal 
	if print_counter == 60:							
		sys.stdout.write("\033[F") 					# back to previous line
		sys.stdout.write("\033[K") 					# clear line
		sys.stdout.write("\033[F") 					# back to previous line
		sys.stdout.write("\033[K") 					# clear line
		sys.stdout.write("\033[F") 					# back to previous line
		sys.stdout.write("\033[K") 					# clear line
		user_message = user_message + '.'			# add another period to the 'Communicating...' message
		if len(str(user_message)) == 66:			# Reset when it gets to the edge of the window
			user_message = ' Communicating...'
		print(user_message + '\n\n')
		print_counter = 0
		
	new_command = get_new_command(last_command)		# Ask command generator for new platform command
	status_platform = communicate(new_command)		# Send the new command to the platform and return the platform's status
	time.sleep(writetime/10)						# Time to think
	last_command = new_command						# Reassign the last command variable
	send_status(status_platform)					# Forward platform's status to Command Gen Script and Safety Light script
	toc()											# Stop timer
	time_to_wait = writetime - calctime				# Check difference between desired write time and time returned from tictoc
	# print(time_to_wait)
	if time_to_wait>0:								# If the difference is positive, wait that long, otherwise print error
		time.sleep(time_to_wait)
	else:
		print('   ***************    COMMUNICATION TOO SLOW!!!!    *************')

