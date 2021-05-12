#! /usr/bin/env python 3.9.1

######################################
#Written by Wolfgang Klassen, 2020
#Review and migration to Python 3.0 by Kiera Pond Augusto, 2021
#Developed for the TUCAN physics collaboration
#1 loop to fit and trim data
######################################

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import scipy.optimize

def fitfun(x,a,b,c,d,f):
	return a*np.exp(-b*(x)) + c*np.exp(-d*(x)) + f

def fit_data(probedata,timedata,inds,trim):

	tdata = timedata.to_numpy()[inds[0,0]+trim:inds[1,0]-2*trim]
	ydata = probedata.to_numpy()[inds[0,0]+trim:inds[1,0]-2*trim]
	tdata = tdata - np.min(tdata)#eliminate horizontal offset
	offsetGuess = np.mean(ydata[-100:-1])
	sig = np.std(ydata[-100:-1])
	guess = [3,5,-3,100,offsetGuess]
	bounds = [[-15,0.2,-15,5,offsetGuess-0.01*np.abs(offsetGuess)],
			[15,10,15,200,offsetGuess+0.01*np.abs(offsetGuess)]]
	try:    #first fit initializes data structs, if you get this one working the rest should work
		popt, pcov = scipy.optimize.curve_fit(fitfun, tdata, ydata, 
				p0 = guess, maxfev=50000, bounds = bounds, ftol = 1e-15, gtol = 1e-15, xtol = 1e-15)
		params = np.array([popt])
		perr = [np.sqrt(np.diag(pcov))]
		
	except:
		print("could not initialize fit")
	#this is an incredibly hacky way to do all of this, I have improved the T2 version
	#print(params[0,:])
	#fig, ax = plt.subplots()
	#ax.plot(tdata,ydata)
	#ax.plot(tdata,fitfun(tdata,*popt),'r',label = "fit")
	#plt.show()
	
	for i in range(1,np.shape(inds)[1]):
		tdata = timedata.to_numpy()[inds[0,i]+trim:inds[1,i]-2*trim]
		tdata = tdata - np.min(tdata)
		ydata = probedata.to_numpy()[inds[0,i]+trim:inds[1,i]-2*trim]
		offsetGuess = np.mean(ydata[-100:-1])
		sig = np.std(ydata[-100:-1])
		guess = [3,5,-3,100,offsetGuess]
		bounds = [[-15,0.2,-15,5,offsetGuess-0.01*np.abs(offsetGuess)],
				[15,10,15,200,offsetGuess+0.01*np.abs(offsetGuess)]]
		popt, pcov = scipy.optimize.curve_fit(fitfun, tdata, ydata, 
				p0 = guess, maxfev=50000, bounds = bounds, ftol = 1e-15, gtol = 1e-15, xtol = 1e-15)
		padd = np.array([popt])
		perr = np.append(perr, [np.sqrt(np.diag(pcov))], axis=0)
		params = np.append(params, padd, axis=0)
#		fig, ax = plt.subplots()
#		ax.plot(tdata,ydata)
#		ax.plot(tdata,fitfun(tdata,*popt),'r',label = "fit")
#		plt.show()
		
	return params,perr
