#! /usr/bin/env python

import pyvisa    # imports pyvisa
import tekscope as tk
import time
import os
from datetime import datetime
import numpy as np
import pandas as pd
import json

def setup():
	## serial communication ########################################
	rm = pyvisa.ResourceManager( "@py" )
	scope = rm.open_resource( "USB0::1689::1025::C011321::0::INSTR" )
	ScopeName = scope.query( "*IDN?" )
	print("Scope: " + ScopeName)
	keithleyPS = rm.open_resource( "USB0::1510::8752::9030775::0::INSTR" )
	VmodPSName = keithleyPS.query( "*IDN?" )
	print("Vmod Power Supply: " + VmodPSName)
	time.sleep(0.2)
	GPIB = rm.open_resource( "ASRL/dev/ttyUSB0::INSTR" )
	time.sleep(0.2)
	if GPIB.query("++mode")!=1: GPIB.write( "++mode 1" )
	GPIB.write("++auto 1")
	time.sleep(0.2)
	GBIPName = GPIB.query( "++ver" )
	print("GPIB controller: " + GBIPName)
	time.sleep(0.2)
	GPIB.write( "++addr 3" )
	AWGName = GPIB.query( "*IDN?" )
	print("AWG: " + AWGName)
	time.sleep(0.2)
	GPIB.write( "++addr 4" )
	time.sleep(0.2)
	BCoilPSName = GPIB.query( "*IDN?" )
	print("Bcoil Power Supply: " + BCoilPSName)
	time.sleep(0.2)
	GPIB.write( "++addr 1" )
	time.sleep(0.2)
	DMMName = GPIB.query( "*IDN?" )
	print("Multi-Meter: " + DMMName)
	GPIB.write( "++auto 0" )
	bcoilCurrent = float(raw_input('Bcoil Current (mA):\n'))
	centerFrequency = float(raw_input('Modulation Frequency (Hz):\n'))
	modAmplitude = float(raw_input('Modulation Amplitude (Vpp):\n'))
	dCycle = float(raw_input('Modulation Duty Cycle (%):\n'))
	fidRate = float(raw_input('Rate of FIDs (Hz):\n'))
	nCycles = float(raw_input('Number of Cycles in burst:\n'))
	preampGain = float(raw_input('SRS preamp gain:\n'))
	bcoilsetup = int(raw_input('Reset Bcoil? (0/1):\n'))
	degauss = int(raw_input('Degauss? (0/1):\n'))

	metadata = {'ScopeName':ScopeName,'VmodPSName':VmodPSName,'GBIPName':GBIPName,
			'AWGName':AWGName,'BCoilPSName':BCoilPSName, 'DMMName':DMMName,
			'bcoilCurrent':bcoilCurrent,'centerFrequency':centerFrequency,
			'modAmplitude':modAmplitude,'dCycle':dCycle,'fidRate':fidRate,
			'nCycles':nCycles,'degauss':degauss,'preampGain':preampGain}
	

	## scope setup #################################################
	print("setting up "+metadata['ScopeName'])
	scope.write( "HOR:RECO 100000" )#record 100,000 data points
	scope.write( "HOR:SCA 0.4" )#2 second major time base
	scope.write( "HORizontal:DELay:TIME 2" )#center waveform on screen
	scope.write( "ACQUIRE:MODE HIRES" )#oversamples and averages out hf noise
	scope.write( "ACQuire:STOPAfter SEQuence" )#only take one screens worth of data
	scope.write( "ACQuire:STATE OFF" )#don't take any data yet
	scope.write( "CH1:COUPling DC" )#setup CH1 & CH2
	scope.write( "CH3:COUPling DC" )
	scope.write( "CH1:TERmination MEG" )
	scope.write( "CH3:TERmination MEG" )
	scope.write( "CH1:BANdwidth TWEnty" )
	scope.write( "CH3:BANdwidth TWEnty" )
	scope.write( "CH1:SCAle 1" )
	scope.write( "CH3:SCAle 2" )
	scope.write( "TRIGger:A:EDGE:COUPling DC" )#setup trigger
	scope.write( "TRIGger:A:EDGE:SLOpe RISE" )
	scope.write( "TRIGger:A:EDGE:SOUrce CH4" )
	scope.write( "TRIGger:A:LEVel 1.5" )

	## DMM setup ###################################################
	print("setting up "+metadata['DMMName'])
	GPIB.write( "++addr 1" )
	time.sleep(0.2)
	GPIB.write("*CLS")
	time.sleep(0.2)
	GPIB.write("*RST")
	time.sleep(0.2)	
	GPIB.write("SENSE1:VOLT:DC:RANGE:UPPER 2")
	time.sleep(0.2)	
	GPIB.write("SENSE1:VOLT:DC:NPLC 10")
	time.sleep(0.2)	
	GPIB.write("SENSE1:VOLT:DC:DIGITS 8.5")
	time.sleep(0.2)

	## Bcoil PS setup ##############################################
	if bcoilsetup:
		print("setting up "+metadata['BCoilPSName'])
		GPIB.write("++addr 4")
		GPIB.write(":SOUR1:FUNC:MODE CURR")
		time.sleep(0.1)
		GPIB.write(":SENSE1:VOLT:Dc:PROT:POS 3")
		time.sleep(0.1)
		GPIB.write(":SOUR1:CURR "+str(bcoilCurrent)+"E-3")##Bcoil
		time.sleep(0.1)
		GPIB.write(":OUTP1 ON")
		time.sleep(0.1)
		GPIB.write("SOUR2:FUNC:MODE CURR")
		time.sleep(0.1)
		GPIB.write("SOUR2:CURR 0")
		time.sleep(0.1)
		GPIB.write(":SENS2:VOLT:DC:PROT:POS 6")
		time.sleep(0.1)
		GPIB.write(":OUTP2 ON")

	## AWG setup ###################################################
	print("setting up "+metadata['AWGName'])
	GPIB.write("++addr 3")
	GPIB.write( "++auto 0" )
	time.sleep(0.1)
	GPIB.write("*CLS")
	time.sleep(0.5)
	GPIB.write("*RST")
	time.sleep(3)
	GPIB.write("SYSTEM:BEEP:STATE OFF")
	time.sleep(0.2)
	GPIB.write("SOURCE2:FUNC SQUARE")
	time.sleep(0.2)
	GPIB.write("SOURCE2:FREQ " + str(centerFrequency))##center freq
	time.sleep(0.2)
	GPIB.write("SOURCE2:VOLT:UNIT VPP")
	time.sleep(0.2)
	GPIB.write("SOURCE2:VOLT " + str(modAmplitude))##RFmod amplitude
	time.sleep(0.2)
	GPIB.write("SOURCE2:VOLT:OFFSET " + str(modAmplitude/2))##RFmodAmp/2
	time.sleep(0.2)
	GPIB.write("SOURCE2:FUNC:SQUARE:DCYClE " + str(dCycle))##DCYCLE(%)
	time.sleep(0.2)
	GPIB.write("SOURCE2:FUNC:PHASE 0")
	time.sleep(1)
	GPIB.write("OUTPUT2:LOAD 50")
	time.sleep(0.2)
	GPIB.write("OUTPUT2 ON")
	time.sleep(0.2)
	GPIB.write("OUTPUT:SYNC:SOURCE CH2")
	time.sleep(0.2)
	GPIB.write("OUTOUT:SYNC ON")
	time.sleep(0.2)
	GPIB.write("SOURCE2:BURST:MODE TRIG")
	time.sleep(0.2)
	GPIB.write("TRIG2:SOUR TIM")
	time.sleep(0.2)
	GPIB.write("TRIG2:TIM " + str(1/fidRate))##time between Fids: 1/FIDrate
	time.sleep(0.2)
	GPIB.write("SOURCE2:BURST:NCYCLES " + str(nCycles))##NCYCLES
	time.sleep(0.2)
	GPIB.write("SOURCE2:BURST:STATE ON")
	time.sleep(0.2)

	## degaussing setup ############################################
	if degauss:
		print("setting up degaussing")
		GPIB.write('MMEM:LOAD:DATA1 "INT:\DG2.ARB"')
		time.sleep(0.1)
		GPIB.write('FUNC:ARB "INT:\DG2.ARB"')
		time.sleep(0.1)
		GPIB.write("FUNC:ARB:SRATE 4000")
		time.sleep(0.1)
		GPIB.write("SOURCE1:FUNC SIN")
		time.sleep(0.1)
		GPIB.write("SOURCE1:VOLT:UNIT VPP")
		time.sleep(0.1)
		GPIB.write("SOURCE1:VOLT 7")
		time.sleep(0.1)
		GPIB.write("SOURCE1:FREQ 10")
		time.sleep(0.1)
		GPIB.write("SOURCE1:AM:DSSC ON")
		time.sleep(0.1)
		GPIB.write("SOURCE1:AM:SOURCE INT")
		time.sleep(0.1)
		GPIB.write("SOURCE1:AM:INT:FUNC ARB")
		time.sleep(0.1)
		GPIB.write("SOURCE1:AM:STATE ON")
		time.sleep(0.1)
		GPIB.write("OUTPUT1 ON")
		time.sleep(0.1)
		raw_input("Degaussing, press enter to continue")
		GPIB.write("OUTPUT1 OFF")

	## make directory and return metadata ##########################
	currenttime = datetime.today().strftime('%H:%M')
	directory = datetime.today().strftime('%y_%m_%d')
	if not os.path.exists(directory):
	    os.makedirs(directory)
	fileName = directory+'_'+currenttime
	metadata['fileName'] = fileName
	metadata['directory'] = directory
	print('Using filename: ' + fileName)
	scope.close
	keithleyPS.close
	GPIB.close
	return metadata
