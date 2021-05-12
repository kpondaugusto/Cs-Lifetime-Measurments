#! /usr/bin/env python 3.9.1

######################################
#Written by Wolfgang Klassen, 2020
#Review and migration to Python 3.0 by Kiera Pond Augusto, 2021
#Developed for the TUCAN physics collaboration
#Seperate script that runs the data indepedently of the equipment
######################################

import pyvisa    # imports pyvisa 1.11.3
import numpy as np
import time #1.8
import os #0.1.4
import json #0.1.1
import matplotlib.pyplot as plt #3.4.2
from matplotlib.widgets import TextBox
import T2_setup as setup 
from datetime import datetime
import pandas as pd #1.2.4 
import find_indices as find
import fit_FIDs as fit
import show_data as show
import scipy.optimize #scipy 1.6.2
import T2_setup as setup

fileName = "21_05_10_14_23"

show.show_data(fileName,30)

