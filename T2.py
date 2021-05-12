#! /usr/bin/env python

import pyvisa    # imports pyvisa
import numpy as np
import tekscope as tk
import time
import pandas as pd
from timeit import default_timer as timer
import os
import json
import matplotlib.pyplot as plt
import T2_setup as setup
import find_indices as find
import fit_FIDs as fit
import show_FIDs as show

## setup instruments############################################
metadata = setup.setup()
################################################################


## re-establish serial communication############################
rm = pyvisa.ResourceManager( "@py" )
scope = rm.open_resource( "USB0::1689::1025::C011321::0::INSTR" )
keithleyPS = rm.open_resource( "USB0::1510::8752::9030775::0::INSTR" )
GPIB = rm.open_resource( "ASRL/dev/ttyUSB0::INSTR" )
time.sleep(0.5)#works best if you wait a bit after connecting to the GPIB controller
if GPIB.query("++mode")!=1: GPIB.write( "++mode 1" )
GPIB.write( "++addr 1" )
GPIB.write( "*IDN?" )
GPIB.write( "++auto 1" )
GPIB.read()
#the above 3 lines switches the Keithley2002 to auto reply without throwing a -420 error
time.sleep(2)
################################################################


## take data####################################################
coilVolt = []
print('Taking data...')
scope.write( "ACQuire:STATE RUN" )#start aqcuisition on scope
time.sleep(0.5)#let scope start recording before starting
start = timer()
end = start
while end-start-4<0:#wait until scope is done before triggering retrieval
	coilVolt.append(GPIB.query(":MEAS?"))
	time.sleep(0.05)
	end = timer()
################################################################


## retrieve data################################################
CH1 = tk.get_data( scope, 1 )# probe signal is on CH1
CH3 = tk.get_data( scope, 3 )# pump monitor is on CH3
CH4 = tk.get_data( scope, 4 )# trig is on CH4
probedata = CH1[1,:]
pumpdata = CH3[1,:]
trigdata = CH4[1,:]
timedata = CH1[0,:]
################################################################


## save data####################################################
data = pd.DataFrame({"Probe" : probedata,"Trig" : trigdata, "Pump" : pumpdata, "Time" : timedata})
data.to_csv(metadata['directory'] + '/' +metadata['fileName']+".csv", index=False)
metadata['Field'] = coilVolt
################################################################


## fit data#####################################################
inds = find.find_ind(data['Trig'])
starts = inds[0,:]
ends = inds[1,:]
ends = np.delete(ends,0)
ends = np.append(ends, len(data['Trig']))
metadata['starts'] = starts.tolist()
metadata['ends'] = ends.tolist()
params, perr = fit.fit_FIDs(metadata)
print("Average T2: "+str(np.mean(params[:,1])))
if 'preampGain' in metadata:
	ORconversion = 1/(metadata['preampGain']*2*1.611)
	print("Average Amp: "+str(ORconversion*np.mean(np.abs(params[:,0]))))
metadata['params'] = params.tolist()
metadata['perr'] = perr.tolist()
################################################################


## show data####################################################
show.show(metadata,1)
################################################################


## save metadata##########################################################################
with open(metadata['directory'] + '/' + metadata['fileName'] + '_metadata', 'w') as fp:
	json.dump(metadata, fp,sort_keys=True,indent=4, separators=(',', ': '))
################################################################

GPIB.close
scope.close
keithleyPS.close
