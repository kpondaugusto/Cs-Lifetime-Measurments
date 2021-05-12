#! /usr/bin/env python 3.9.1

######################################
#Written by Wolfgang Klassen, 2020
#Review and migration to Python 3.0 by Kiera Pond Augusto, 2021
#Developed for the TUCAN physics collaboration
#retrieves data from scope
######################################

import numpy as np
import pyvisa as visa
from datetime import datetime
import time



class UnsupportedChannelError(Exception):
	"""Raised when the oscilloscope channel does not support the attempted operation"""


scope_channels = {      1: "CH1",       2: "CH2",       3:  "CH3",     4: "CH4",
                    "CH1": "CH1",   "CH2": "CH2",   "CH3":  "CH3", "CH4": "CH4",
                    "ch1": "CH1",   "ch2": "CH2",   "ch3":  "CH3", "ch4": "CH4",
                      "1": "CH1",     "2": "CH2",     "3":  "CH3",   "4": "CH4",
                   "REF1": "REF1", "REF2": "REF2", "MATH": "MATH",
                 }


def get_data( scope, channel ):
	"""Transfers the captured waveform for a single channel on a Tektronix oscilloscope.

	Parameters:
	      scope  a visa resource
	    channel  the channel from which you want the data (can be 1, 2, or "CH1", "CH2", etc.)

	Returns:
	    a 2 row numpy array containing the waveform data
	        row 0: time in seconds
	        row 1: voltage in volts
    """
	# Page numbers refer to the DPO2000 and MSO2000 Series Manual, Revision A, released 2011-09-22, part number 077-0097-01
	# This file is currently for use with DPO4000 and MSO4000 series scopes, some SCPI commands did not carry over from the 2000 series

	# The instructions for transferring data from the oscilloscope are on page 2-51 in the manual
	try:
		# Set the data source (channel) from which we want the waveform data (page 2-127)
		scope.write( "DAT:SOU " + scope_channels[channel] )
	except KeyError:
		raise UnsupportedChannelError(channel)

	# Set the data encoding, which is how the samples are represented as binary data (page 2-125)
	# Using DAT:ENC is equivalent to setting: WFMO:ENC, WFMO:BN_F, WFMO:FILTERF (page 2-125)
	scope.write( "DAT:ENC SRI" )  # SRI: samples are signed integers stored in little endian (least significant byte first)

	# Set the data width, which is the number of bytes per sample (page 2-131)
	# Equivalent to setting WFMO:BYT_N (page 2-363)
#FIXME: Is the above true? I know WFMO:BYT_N -> DAT:WID but not sure if DAT:WID -> WFMO:BYT_N (DAT:WID could also be for incoming data)
	scope.write( "DAT:WID 2" )

	# Get the waveform record length (page 2-168)
	# When HOR:RECO is used as a command, you give it the nominal record length (either 100000 or 1000000)
	record_length = scope.query( "HOR:RECO?" )
	#print(record_length)
#FIXME: does HOR:RECO ever give 125000 or do I need to rely on the header from the CURVE? response?
#FIXME: or do I query WFMO:NR_P?
	# Set how much of the waveform you want to transfer
	scope.write( "DAT:STAR 1" )  # start transfer from the first data point (page 2-130)
	scope.write( "DAT:STOP " + record_length ) # end at the last data point (page 2-130)
	time.sleep(0.1)
	# Transfer full resolution data (what was actually acquired rather than what was displayed)
	#scope.write( "DAT:RESO FULL" ) 
#FIXME: Do I need to check WFMPRE:XUNIT and WFMPRE:YUNIT? A: only if you are expecting something other than Volts regularily
	# Get waveform preamble, which contains information about the timebase and
	# how to compute the voltage measurement from the raw ADC codes transferred from the scope
	y_scale   = float( scope.query( "WFMPRE:YMULT?" ) )  # vertical scale factor
	y_zero    = float( scope.query( "WFMPRE:YZERO?" ) )  # vertical offset
	y_offset  = float( scope.query( "WFMPRE:YOFF?" ) )   # vertical position
	time_step = float( scope.query( "WFMPRE:XINCR?" ) )  # horizontal interval between waveform points (time step)
	# Transfer the waveform data
	scope.write( "CURVE?" )
	raw_data = scope.read_raw()
	time.sleep(0.5)
#TODO:
# check "*ESR?" for error bits (see note on page 2-123)
# *ESR? returns the Standard Event Status Register (SESR)
# bit 7: PON, power on
# bit 6: URQ, user request
# bit 5: CME, command error
# bit 4: EXE, execution error
# bit 3: DDE, device error
# bit 2: QYE, query error
# bit 1: RQC, request control
# bit 0: OPC, operation complete


	# Waveform header format (page 2-122 in the manual):
	#     #<x><yyy><data><newline>
	#           #    a literal '#'
	#         <x>    the size of <yyy> in bytes (as a string)
	#       <yyy>    the number of bytes of data (as a string)
	# Can possibly turn this off by setting HEAD to 0 (page 2-164)
	header_length = 1 + int(raw_data[1]) # the +1 is for the literal '#'

	# Generate a numpy array for the vertical data
	# The dtype is chosen to match our settings above: '<' means little endian, 'h' means short signed integer (2 bytes)
	y_data = np.frombuffer( raw_data[header_length+1:-1], dtype="<h" ) # the +1 is for the <x> byte
	y_data = (y_data - y_offset) * y_scale + y_zero
	#print(len(y_data))

	# Generate the timestamps for waveform
	time_data = time_step * np.arange( 0, len(y_data), 1 )

	return np.stack( (time_data, y_data) )


def read_isf_file( filename ):
	"""Extracts the waveform data from an ISF file.

	An ISF file contains a waveform captured by a Tektronix oscilloscope. The
	format is the same as what the scope would respond to a "WAVFrm?" command.

	Parameters:
	    filename  the name of the ISF file to process

	Returns:
	    a 2 row numpy array containing the waveform data
	        row 0: time in seconds
	        row 1: voltage in volts
	"""
	with open( filename, 'rb' ) as f:
		# slurp and lex the file
		file_contents = f.read()
		file_contents = { x.split(b" ", 1)[0].lstrip(b":"): x.split(b" ", 1)[1] for x in file_contents.split(b";") }

		# get scale factors and offsets from header
		y_scale   = float( file_contents[b"YMU"] )
		y_zero    = float( file_contents[b"YZE"] )
		y_offset  = float( file_contents[b"YOF"] )
		time_step = float( file_contents[b"XIN"] )

		# determine the format of the data
		dtype = ""

		# determine endianness of samples
		if file_contents[b"BYT_O"] == b"MSB":
			dtype += "<"
		elif file_contents[b"BYT_O"] == b"LSB":
			dtype += ">"

		# determine size of samples
		if file_contents[b"WFMP:BYT_N"] == b"1":
			dtype += "b"  # char
		elif file_contents[b"WFMP:BYT_N"] == b"2":
			dtype += "h"  # short

		# check if samples are unsigned
		if file_contents[b"BN_F"] == b"RP":
			dtype = dtype.upper()

		header_length = 1 + int( file_contents[b"CURV"][1] )
		y_data = np.frombuffer( file_contents[b"CURV"][header_length:-1], dtype=dtype )
		y_data = (y_data - y_offset) * y_scale + y_zero

		# Generate the timestamps for waveform
		time_data = time_step * np.arange( 0, len(y_data), 1 )

		return np.stack( ( time_data, y_data ) )
