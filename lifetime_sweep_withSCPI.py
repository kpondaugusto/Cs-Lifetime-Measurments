#! /usr/bin/env python

import pyvisa    # imports pyvisa
import tekscope as tk
import time
import numpy as np
import pandas as pd
from timeit import default_timer as timer
from datetime import datetime
import os
import find_indices as find
import fit_data as fit
import show_data as show
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox

## prompt user for filename right away##########################
#fileName = raw_input('Enter a file name for this data set (excluding extension):\n')
directory = datetime.today().strftime('%y_%m_%d')
currenttime = datetime.today().strftime('%H:%M')
fileName = directory+'_'+currenttime
print("Using filename " + fileName)
## serial communication ########################################
rm = pyvisa.ResourceManager( "@py" )
scope = rm.open_resource( "USB0::1689::1025::C011321::0::INSTR" )
print("Scope: " + scope.query( "*IDN?" ))
keithleyPS = rm.open_resource( "USB0::1510::8752::9030775::0::INSTR" )
print("Power Supply: " + keithleyPS.query( "*IDN?" ))
time.sleep(0.1)

## scope setup #################################################
scope.write( "HOR:RECO 1000000" )#record 1M data points
scope.write( "HOR:SCA 20" )#2 second major time base
scope.write( "HORizontal:DELay:TIME 100" )#center waveform on screen
scope.write( "ACQUIRE:MODE HIRES" )#oversamples and averages out hf noise
scope.write( "ACQuire:STOPAfter SEQuence" )#only take one screens worth of data
scope.write( "ACQuire:STATE OFF" )#don't take any data yet
scope.write( "CH1:COUPling DC" )#setup CH1 & CH2
scope.write( "CH2:COUPling DC" )
scope.write( "CH1:TERmination MEG" )
scope.write( "CH2:TERmination MEG" )
scope.write( "CH1:BANdwidth TWEnty" )
scope.write( "CH2:BANdwidth TWEnty" )
scope.write( "CH1:SCAle 0.2" )
scope.write( "CH2:SCAle 5" )
scope.write( "CH1:OFFset 0" )
scope.write( "CH2:OFFset 0" )
scope.write( "CH1:POSition 0" )
scope.write( "CH2:POSition 0" )
scope.write( "TRIGger:A:EDGE:COUPling DC" )#setup trigger
scope.write( "TRIGger:A:EDGE:SLOpe FALL" )
scope.write( "TRIGger:A:EDGE:SOUrce CH2" )
scope.write( "TRIGger:A:LEVel 2.5" )

###############################################################
#values to send to Mod In via the keithley PS
laserTune = np.linspace(0.35,0.45,num = 82)
#laserTune = np.flip(laserTune)
###############################################################

## power supply setup #########################################
keithleyPS.write( "SYST:REM" )#puts Keithley into remote operation IMPORTANT
#                  INST <CH> selects channel to apply settings to
keithleyPS.write( "INST CH1; VOLT 5; CURR 0.3; CHAN:OUTP ON" )                    #Bcoil values
keithleyPS.write( "INST CH2; VOLT 5; CURR 0.1; CHAN:OUTP ON" )                    #Shutter
keithleyPS.write( "INST CH3; VOLT "+str(laserTune[0])+"; CURR 0.1; CHAN:OUTP ON" )#Laser Mod
time.sleep(3)

## take data ##################################################
scope.write( "ACQuire:STATE ON" )#start aqcuisition on scope
time.sleep(1)#let scope start recording before starting
start = timer()
for i in range(0,len(laserTune)):#loop to turn shutter on/off and adjust laser tune
	keithleyPS.write( "INST CH2; CHAN:OUTP OFF" )
	time.sleep(1.5)
	keithleyPS.write("INST CH2; CHAN:OUTP ON")
	time.sleep(0.2)#delay for shutter closing
	keithleyPS.write( "INST CH3; VOLT " + str(laserTune[i]) )
	time.sleep(0.7)
end = timer()
print("Finished taking data at t = " + str(end-start) + "\nWaiting for t = 200 to continue")
while end-start-201<0:#wait until 201 seconds has elapsed before triggering retrieval
	end = timer()

## retrieve data ##############################################
CH1 = tk.get_data( scope, 1 )# probe signal is on CH1
CH2 = tk.get_data( scope, 2 )# pump monitor is on CH2
probedata = CH1[1,:]
pumpdata = CH2[1,:]
timedata = CH1[0,:]

#the Pandas dataFrame structure is a nice way to store data in named arrays, easy to save to CSV
data = pd.DataFrame({"Probe" : probedata, "Pump" : pumpdata, "Time" : timedata})

## save to file before trying to do anything else #############
data.to_csv(fileName +".csv", index=False)

## analyze and show data#######################################
trim = 50 #choose an amount tp trim off the start and end of sections before fit
show.show_data(fileName,trim)

#close serial when done
scope.close
keithleyPS.close









































