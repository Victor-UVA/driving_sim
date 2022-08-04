# MOOG Control Class
# Author: Hudson Burke
import codecs
import serial
import time
import threading

class MOOG():
    #===============================================================================
    #------------       Set up serial connections   --------------------------------
    # This is the main connection to the platform.  Commands are delivered at 60 hz using this script.
    def __init__(self):
        self.ser = serial.Serial(
            port = 'COM3',
            baudrate = 57600,							# Serial port transfer rate (bits/s)
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = 0.002 
        )

        self.command_types_hex = { # this is the hex format to send to serial
            'ESTOP':                0xe6, 
            'DISABLE':              0xdc, 
            'PARK':                 0xd2, 
            'LOW LIMIT ENABLE':     0xc8, 
            'LOW LIMIT DISABLE':    0xbe, 
            'ENGAGE':               0xB4, 
            'START':                0xaf, 
            'LENGTH MODE':          0xac, 
            'DOF MODE':             0xaa, 
            'RESET':                0xa0, 
            'INHIBIT':              0x96, 
            'RESERVED':             0x8c, 
            'NEW POSITION':         0x82
        }
        # self.command_types_hex = { # this is the hex format to send to serial
        #     'ESTOP':                'e6', 
        #     'DISABLE':              'dc', 
        #     'PARK':                 'd2', 
        #     'LOW LIMIT ENABLE':     'c8', 
        #     'LOW LIMIT DISABLE':    'be', 
        #     'ENGAGE':               'B4', 
        #     'START':                'af', 
        #     'LENGTH MODE':          'ac', 
        #     'DOF MODE':             'aa', 
        #     'RESET':                'a0', 
        #     'INHIBIT':              '96', 
        #     'RESERVED':             '8c', 
        #     'NEW POSITION':         '82'
        # }

        # self.command_types_hex = { # this is the hex format to send to serial
        #     'ESTOP':                '\xe6', 
        #     'DISABLE':              '\xdc', 
        #     'PARK':                 '\xd2', 
        #     'LOW LIMIT ENABLE':     '\xc8', 
        #     'LOW LIMIT DISABLE':    '\xbe', 
        #     'ENGAGE':               '\xB4', 
        #     'START':                '\xaf', 
        #     'LENGTH MODE':          '\xac', 
        #     'DOF MODE':             '\xaa', 
        #     'RESET':                '\xa0', 
        #     'INHIBIT':              '\x96', 
        #     'RESERVED':             '\x8c', 
        #     'NEW POSITION':         '\x82'
        # }

        self.command_types_dec = {
            'ESTOP':                230, 
            'DISABLE':              220, 
            'PARK':                 210, 
            'LOW LIMIT ENABLE':     200, 
            'LOW LIMIT DISABLE':    190, 
            'ENGAGE':               180, 
            'START':                175, 
            'LENGTH MODE':          172, 
            'DOF MODE':             170, 
            'RESET':                160, 
            'INHIBIT':              150, 
            'RESERVED':             140, 
            'NEW POSITION':         130
        }
        # Initial command to begin communication with the platform
        self.command = "\xff\x82\x43\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x00\x04\x29\x00"
        self.prev_command = self.command
        
        self.state = 'POWER-UP'
        self.states = {
            0b0000 : 'POWER-UP',
            0b0001 : 'IDLE',
            0b0010 : 'STANDBY',
            0b0011 : 'ENGAGED',
            0b0100 : '(NOT USED)',
            0b1000 : 'PARKING',
            0b1001 : 'FAULT 2',
            0b1010 : 'FAULT 3',
            0b1011 : 'DISABLED',
            0b1100 : 'INHIBITED',       
        }
        self.startTime_for_tictoc = 0
        self.elapsed_time = 0
        command_loop = threading.Thread(target=self.communication_loop)
        command_loop.start()
        self.initialize_platform()

    def communication_loop(self): # publish current command at 60 Hz
        while True:
            self.tic() # Start timer
            self.communicate()
            # TODO: Handle states
            self.toc() # Stop timer
            # wait to publish at 60 Hz
            print(self.elapsed_time)
            try:
                time.sleep(1/60 - self.elapsed_time)
            except:
                print("bad sleep")
    def tic(self):
        self.startTime_for_tictoc = time.time()
        
    def toc(self):
        self.elapsed_time = time.time() - self.startTime_for_tictoc
    
   
    def communicate(self):
        self.ser.write(self.command.encode())					            # Write current command to platform base
        bytesToRead = 20                                            # Response data is 20 bytes
        response_bytes : bytes = self.ser.read(bytesToRead)         # Read full platform status message
        response_hex_string : str = response_bytes.hex(':')     
        self.response = response_hex_string.split(':')              #TODO: Automatically convert hex strings to int
        try:
        # parse through 20 bytes read from serial port
            self.frame_sync =            self.response[0]
            self.fault_data_1 =          self.response[1]
            self.fault_data_2 =          self.response[2]
            self.discrete_io_info =      self.response[3]
            self.checksum =              self.response[4]     
            self.act_a_low_feedback =    self.response[5] 
            self.act_a_high_feedback =   self.response[6]
            self.act_b_low_feedback =    self.response[7]
            self.act_b_high_feedback =   self.response[8]
            self.act_c_low_feedback =    self.response[9]
            self.act_c_high_feedback =   self.response[10]
            self.act_d_low_feedback =    self.response[11]
            self.act_d_high_feedback =   self.response[12]
            self.act_e_low_feedback =    self.response[13]
            self.act_e_high_feedback =   self.response[14]
            self.act_f_low_feedback =    self.response[15]	
            self.act_f_high_feedback =   self.response[16]
            self.machine_state_info =    self.response[17]
            self.motion_base_id_low =    self.response[18]
            self.motion_base_id_high =   self.response[19]
        except:
            print("Response Error")

        try:
            machine_state_int = int(self.machine_state_info, 16)
            self.state = self.states[machine_state_int & 0b1111] # use last 4 bits to look up state 
            self.mode = (machine_state_int >> 4) & 1
        except: 
            print("State Read Error")


    # command_type string corresponding to hex in dict ; commands list of ints
    def build_frame(self, command_type : str, commands=[0,0,0,0,0,0]):
        command_prefix_hex = 0xff #'ff' #'\xff' # frame sync
        command_machine_id_hex_1 = 0x92 #'92' #'\x92' # IDK where these came from
        command_machine_id_hex_2 = 0x00 #'00'     #'\x00'
        command_machine_id_dec_1 = 41
        command_machine_id_dec_2 = 0

        command_type_hex = self.command_types_hex[command_type]
        command_type_dec = self.command_types_dec[command_type]

        # Add bytes 1 and 3-16, limit to 8 bits, then zero MSB
        checksum = command_type_dec + sum(commands) + command_machine_id_dec_1 + command_machine_id_dec_2
        checksum &= 0b01111111
        # checksum_hex = bytes(bytearray.fromhex(hex(checksum).lstrip('0x').rstrip('L').zfill(2)[-2:]))
        checksum_hex = hex(checksum).lstrip('0x').rstrip('L').zfill(2)[-2:]

        # Split commands into low and high bytes in hex (high bytes must have msb of 0)
        commands_hex = []
        for command in commands:
            command &= 0x7FFF
            commands_hex.append(
                    hex(command).lstrip('0x').rstrip('L').zfill(2)[-2:]

            #     bytes(bytearray.fromhex(
            #         hex(command).lstrip('0x').rstrip('L').zfill(2)[-2:]
            #     )
            # )
            ) # I'm sorry this is so gross

        # Final command to send in hex (should be in format '\x1a\x....')
        frame = bytearray([])
        final_command = command_prefix_hex + command_type_hex + checksum_hex + ''.join(commands_hex) + command_machine_id_hex_1 + command_machine_id_hex_2
        # final_command = bytearray.fromhex(final_command)
        return final_command


    def initialize_platform(self):
        # Initial command
        while self.state != 'IDLE':
            self.set_command(self.build_frame('NEW POSITION', [1024, 1024, 1024, 1024, 1024, 1024]))
            # TODO: add timer

        # Change to DOF mode
        while not self.mode: 
            self.set_command(self.build_frame('DOF MODE', [16383, 16383, 29000, 16383, 16383, 16383]))
        
        self.set_command(self.build_frame('NEW POSITION', [16383, 16383, 29000, 16383, 16383, 16383]))
        
        # Engage
        self.set_command(self.build_frame('ENGAGE', [16383, 16383, 29000, 16383, 16383, 16383]))
        time.sleep(10)
        
        # Ready to accept new positions
        self.set_command(self.build_frame('NEW POSITION', [16383, 16383, 29000, 16383, 16383, 16383]))
        

    def park(self):
        # Park
        while self.state != "IDLE":
            self.set_command(self.build_frame('PARK', [16383, 16383, 29000, 16383, 16383, 16383]))
        # while self.state != "DISABLED":
        #     self.set_command(self.build_frame('DISABLE', [16383, 16383, 29000, 16383, 16383, 16383]))
        

    def set_command(self, new_command):
        self.prev_command = self.command
        self.command = new_command

    def command_dof(self, roll, pitch, heave, surge, yaw, lateral):
        self.set_command(self.build_frame('NEW_POSITION', [roll, pitch, heave, surge, yaw, lateral]))

    
            