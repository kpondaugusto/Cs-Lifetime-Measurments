#! /usr/bin/env python 3.9.1

######################################
#Written by Wolfgang Klassen, 2020
#Review and migration to Python 3.0 by Kiera Pond Augusto, 2021
#Developed for the TUCAN physics collaboration
#shows data for T1 run
######################################

import numpy as np
import find_indices as find
import fit_data as fit
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox

def fitfun(x,a,b,c,d,f):
	return a*np.exp(-b*(x)) + c*np.exp(-d*(x)) + f



def show_data(fileName,trim):

	data = pd.read_csv(fileName+".csv")
	inds = find.find_ind(data['Pump'])
	fitparams, fiterr = fit.fit_data(data['Probe'],data['Time'],inds,trim)
	fitNum = np.where(np.abs(fitparams[:,0]) == np.amax(np.abs(fitparams[:,0])))[0][0]
	
	fits = np.arange(0,len(fitparams[:,0]),1)

	tdata = data['Time'].to_numpy()[inds[0,fitNum]+trim:inds[1,fitNum]-2*trim]
	tdata = tdata - np.min(tdata)
	ydata = data['Probe'].to_numpy()[inds[0,fitNum]+trim:inds[1,fitNum]-2*trim]
	pdata = data['Pump'].to_numpy()[inds[0,fitNum]+trim:inds[1,fitNum]-2*trim]
	
	dataMean = np.mean(data['Probe'].to_numpy())
	dataAmp = np.max(data['Probe'].to_numpy()) - np.min(data['Probe'].to_numpy())
	fig, ax = plt.subplots(3,1,figsize=(15, 15))
	ax[0].plot(data['Time'][inds[0,0]:inds[1,-1]],0.01*data['Pump'][inds[0,0]:inds[1,-1]])
	ax[0].plot(data['Time'][inds[0,0]:inds[1,-1]],data['Probe'][inds[0,0]:inds[1,-1]]-dataMean+0.5*dataAmp)
	ax[1].errorbar(fits, fitparams[:,0], yerr = fiterr[:,0], fmt = 'r', label = "ampSlow")
	line2, = ax[1].plot(fitNum,fitparams[fitNum,0], 'r*')
	ax[1].errorbar(fits, fitparams[:,1], yerr = fiterr[:,1], fmt = 'b', label = "tConstSlow")
	line3, = ax[1].plot(fitNum,fitparams[fitNum,1], 'b*')
	ax[1].errorbar(fits, fitparams[:,2], yerr = fiterr[:,2], fmt = 'g', label = "ampFast")
	ax[1].errorbar(fits, fitparams[:,4], yerr = fiterr[:,4], fmt = 'm', label = "offset")
	line6, = ax[1].plot(fitNum,fitparams[fitNum,4], 'm*')
	ax[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
	ax[1].axhline(y=0, color='k')
	line0, = ax[2].plot(tdata,ydata)
	line1, = ax[2].plot(tdata,fitfun(tdata,*fitparams[fitNum,:]),'r',label = "fit")
	line8, = ax[2].plot(tdata,pdata,'b',label = "pump")
	graphHeight = np.max([np.max(ydata),np.max(pdata)]) - np.min([np.min(ydata),np.min(pdata)])
	text0 = plt.text(0.1,ax[2].get_ylim()[0]+0.1*graphHeight,"fit number "+str(fitNum))
	text1 = plt.text(0.1,ax[2].get_ylim()[0]+0.2*graphHeight,"offset = "+str(round(fitparams[fitNum,4],2)) + "+/-" + str(round(fiterr[fitNum,4],3)))
	text2 = plt.text(0.1,ax[2].get_ylim()[0]+0.3*graphHeight,"ampFast = "+str(round(fitparams[fitNum,2],2)) + "+/-" + str(round(fiterr[fitNum,2],3))+"   tFast = "+str(round(fitparams[fitNum,3],2)) + "+/-" + str(round(fiterr[fitNum,3],3)))
	text3 = plt.text(0.1,ax[2].get_ylim()[0]+0.4*graphHeight,"ampSlow = "+str(round(fitparams[fitNum,0],2)) + "+/-" + str(round(fiterr[fitNum,0],3))+"   tSlow = "+str(round(fitparams[fitNum,1],2)) + "+/-" + str(round(fiterr[fitNum,1],3)))
	fig.suptitle(fileName, fontsize=12)
	plt.tight_layout()
	plt.subplots_adjust(bottom=0.11)
	plt.subplots_adjust(top=0.95)
	plt.subplots_adjust(right=0.9)
	plt.legend()

	def submit(text):
		fitNum = int(text)

		tdata = data['Time'].to_numpy()[inds[0,fitNum]+trim:inds[1,fitNum]-2*trim]
		tdata = tdata - np.min(tdata)
		ydata = data['Probe'].to_numpy()[inds[0,fitNum]+trim:inds[1,fitNum]-2*trim]
		pdata = data['Pump'].to_numpy()[inds[0,fitNum]+trim:inds[1,fitNum]-2*trim]
		
		line0.set_data(tdata,ydata)
		line1.set_data(tdata,fitfun(tdata,*fitparams[fitNum,:]))
		line2.set_data(fitNum,fitparams[fitNum,0])
		line3.set_data(fitNum,fitparams[fitNum,1])
		#line4.set_data(fitNum,fitparams[fitNum,2])
		#line5.set_data(fitNum,fitparams[fitNum,3])
		line6.set_data(fitNum,fitparams[fitNum,4])
		line8.set_data(tdata,pdata)
	
		ax[2].set_ylim(np.min([np.min(ydata),np.min(pdata)]), np.max([np.max(ydata),np.max(pdata)]))
		graphHeight = np.max([np.max(ydata),np.max(pdata)]) - np.min([np.min(ydata),np.min(pdata)])
		text0.set_position([0.1,np.min(ydata)+0.1*graphHeight])
		text1.set_position([0.1,np.min(ydata)+0.2*graphHeight])
		text2.set_position([0.1,np.min(ydata)+0.3*graphHeight])
		text3.set_position([0.1,np.min(ydata)+0.4*graphHeight])
		text0.set_text("fit number "+str(fitNum))
		text1.set_text("offset = " +str(round(fitparams[fitNum,4],2)))
		text2.set_text("ampFast = "+str(round(fitparams[fitNum,2],2))+"   tFast = "+str(round(fitparams[fitNum,3],2)))
		text3.set_text("ampSlow = "+str(round(fitparams[fitNum,0],3))+"   tSlow = "+str(round(fitparams[fitNum,1],3)))
		plt.draw

	axbox = plt.axes([0.2, 0.03, 0.1, 0.04])
	text_box = TextBox(axbox, 'Fit to show:', initial=str(fitNum))
	text_box.on_submit(submit)

	plt.show()
