#! /usr/bin/env python 3.9.1

######################################
#Written by Wolfgang Klassen, 2020
#Review and migration to Python 3.0 by Kiera Pond Augusto, 2021
#Developed for the TUCAN physics collaboration
#turn 2 arrays of start and end points into 1 array
######################################

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def find_ind(pumpdata):
	
	diffs = np.diff(pumpdata)#take first order differential
	


	thresh = np.abs(0.1*(max(diffs)-min(diffs)))

	#print(thresh)
	#plt.plot(diffs)
	#plt.show()

	starts = np.where(diffs < -1*thresh)[0]#find negative spikes
	ends = np.where(diffs > thresh)[0]#find positive spikes
	startDiff = np.diff(starts)
	endDiff = np.diff(ends)

	startDel = np.where(startDiff < 100)[0]#find doubly sampled peaks
	endDel = np.where(endDiff < 100)[0]

	newstarts = np.delete(starts, startDel)#delete doubly sampled peaks
	newends = np.delete(ends, endDel)

	#print(newstarts)
	#print(newends)

	#Quality control
	#assert (len(newstarts)==len(newends)),"Something wrong with Pump signal"
	#assert (newstarts[0]<newends[0]),"Something wrong with Pump signal"
	#assert (newstarts[-1]<newends[-1]),"Something wrong with Pump signal"

	return np.stack((newstarts,newends),axis=0)
