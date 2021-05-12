#! /usr/bin/env python 3.9.1

######################################
#Written by Wolfgang Klassen, 2020
#Review and migration to Python 3.0 by Kiera Pond Augusto, 2021
#Developed for the TUCAN physics collaboration
#fits data for T2
######################################

import numpy as np
import os
import pandas as pd
import find_indices as find
import scipy.optimize

def fitfun(x,a,b,c,d,f):
	return a*np.exp(-b*(x))*np.sin(c*(x)+d)+f

def fit_FIDs(metadata):
	## import data##################################################
	data = pd.read_csv(metadata['directory']+"/"+metadata['fileName']+".csv")

	## fit FIDs#####################################################
	for i in range(0,len(metadata['starts'])):
		ydata = data['Probe'].to_numpy()[metadata['starts'][i]:metadata['ends'][i]]
		tdata = data['Time'].to_numpy()[metadata['starts'][i]:metadata['ends'][i]]
		tdata = tdata - min(tdata)
		ampguess = abs(max(ydata)-min(ydata))/2
		tconstguess = 50
		wguess = 2*np.pi*metadata['centerFrequency']
		phaseguess = np.pi/4
		offsetguess = np.mean(ydata)
		guess = [ampguess,tconstguess,wguess,phaseguess,offsetguess]
		bounds = [[0,0,0,-2*np.pi,-ampguess],
			  [10,200,2*wguess,2*np.pi,ampguess]]
		popt, pcov = scipy.optimize.curve_fit(fitfun, tdata, ydata, bounds = bounds,
			p0 = guess, maxfev=50000, ftol = 1e-15, gtol = 1e-15, xtol = 1e-15)
		if i == 0:
			params = popt
			perr = np.sqrt(np.diag(pcov))
		else:
			params = np.vstack((params,popt))
			perr = np.vstack((perr,np.sqrt(np.diag(pcov))))
	return params, perr
