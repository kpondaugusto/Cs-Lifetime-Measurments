#! /usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def fitfun(x,a,b,c,d,f):
	return a*np.exp(-b*(x))*np.sin(c*(x)+d)+f

def show(metadata,savefig):
	data = pd.read_csv(metadata['directory']+"/"+metadata['fileName']+".csv")
	T2times = [el[1] for el in metadata['params']]
	displaydata = data['Probe'][metadata['starts'][0]:metadata['ends'][0]]
	displaytime = data['Time'][metadata['starts'][0]:metadata['ends'][0]]
	displaytime = displaytime - min(displaytime)
	fig, ax = plt.subplots(4,1,figsize=(15, 15))
	ax[0].plot(data['Time'],data['Probe'],'b',label = 'Probe')
	ax[0].plot(data['Time'],data['Pump'],'r',label = 'Pump')
	ax[1].plot(T2times,label = 'T2 times')
	#ax[2].plot(metadata['Field'])
	ax[3].plot(displaytime,displaydata)
	ax[3].plot(displaytime,fitfun(displaytime,*metadata['params'][0][:]),
		'r',label = 'fit')
	plt.legend()
	if savefig:
		plt.savefig(metadata['fileName']+".png")
	plt.show()
