#!/usr/bin/env python
# coding: utf-8

# In[ ]:




## simulations first 5 years without interaction and the remaining years with interactions
import shutil, os
import numpy as np
import pandas as pd
import math
from math import atan2
import random
import statistics
import csv
import time as mytime

numsim = 4  # number of replicates
start_time=mytime.time() # server time for starting

## create file to contain experiments results
outfname  = os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/experiments_simulation.csv")
with open(outfname,'w') as outfile:
    allsimdat=csv.writer(outfile)
    for rep in range(numsim):
        exec(open(os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/code/Bioenergy_Landuse_Conflict_Model.py")).read()) # execute 
        with open(os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/bioenergy_model_simulation.csv"), 'r') as csvfile:
            onesimdat = csv.reader(csvfile, delimiter=',')
            header = next(onesimdat)
            header.append('NoSim')
            if rep==0:
                allsimdat.writerow(header)
            for row in onesimdat:
                row.append(str(rep))
                allsimdat.writerow(row)
        print('Done, simulation %i, ended at %s '%(rep+1,mytime.ctime()))
        # os.rename('sim_movie.mp4', 'movie_standard_rep_%i.mp4' %(rep+1) )                 


# In[ ]:




