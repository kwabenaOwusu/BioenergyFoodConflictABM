#!/usr/bin/env python
# coding: utf-8

# In[ ]:



## SENSITIVITY ANALYSIS FOR YIELD FOOD##
import shutil, os
import numpy as np
import pandas as pd
import math
from math import atan2
import random
import statistics
import csv
import time as mytime

numsim = 4 # number of replicates
start_time=mytime.time() # server time for starting

YIELD_FOOD = [1.2, 3.6] # plus or minus of parmater value 
for number in YIELD_FOOD:
    
    cost_food = 2416.33 # cost of producing food crop-MAIZE (GHS/ha) - 41.3% return on investment of cultivating between 2018-2022 (using average price and average yield)
    cost_bioenergy = 2933.207 #1433 cost of producing bioenergy crop-JATHROPHA (GHC/ha)

    # yield_food = 2.4 # food yield (mt/ha) - average yield 2018-2022
    yield_bioenergy = 3.517983  #3 bioenergy yield (mt/ha)

    init_price_food = 1713.96 # initial value of food price (GHS/mt) for average of 2018-2022
    init_price_bioenergy = 2175.63  #840  initial value of food price (GHC/mt)

    actualhav_food = 1 # fraction of food biomass harvested per hectare
    actualhav_bioenergy = 1 # fraction of bioenergy biomass harvested per hectare

    total_demand_food = 111e7 #(GHS/year) demand for food crop (in GHC) for Brong-Ahafo expressed as 22% of estimted 2018-2022 average national production mutlipled by 20018-2022 price 
    total_demand_bioenergy = 32184409   #11e6  set at 1% of amount_demand_food

    # focal paramater 
    yield_food = number
    outfname  = os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/" + 'yield_food_' + str(number) + '.csv')
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
            #os.rename('sim_movie.mp4', 'movie_eff_quarantined_%.2f_rep_%i.mp4' %(eff_quarantined,rep+1) ) \            


# In[ ]:


## SENSITIVITY ANALYSIS FOR YIELD BIOENERGY##
import shutil, os
import numpy as np
import pandas as pd
import math
from math import atan2
import random
import statistics
import csv
import time as mytime

numsim = 4 # number of replicates
start_time=mytime.time() # server time for starting

YIELD_BIOENERGY = [1.76, 5.23] # plus or minus of parmater value 
for number in YIELD_BIOENERGY:
    
    cost_food = 2416.33 # cost of producing food crop-MAIZE (GHS/ha) - 41.3% return on investment of cultivating between 2018-2022 (using average price and average yield)
    cost_bioenergy = 2933.207 #1433 cost of producing bioenergy crop-JATHROPHA (GHC/ha)

    yield_food = 2.4 # food yield (mt/ha) - average yield 2018-2022
    # yield_bioenergy = 3.517983  #3 bioenergy yield (mt/ha)

    init_price_food = 1713.96 # initial value of food price (GHS/mt) for average of 2018-2022
    init_price_bioenergy = 2175.63  #840  initial value of food price (GHC/mt)

    actualhav_food = 1 # fraction of food biomass harvested per hectare
    actualhav_bioenergy = 1 # fraction of bioenergy biomass harvested per hectare

    total_demand_food = 111e7 #(GHS/year) demand for food crop (in GHC) for Brong-Ahafo expressed as 22% of estimted 2018-2022 average national production mutlipled by 20018-2022 price 
    total_demand_bioenergy = 32184409   #11e6  set at 1% of amount_demand_food

    # focal paramater 
    yield_bioenergy = number
    outfname  = os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/" + 'yield_bioenergy_' + str(number) + '.csv')
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
            #os.rename('sim_movie.mp4', 'movie_eff_quarantined_%.2f_rep_%i.mp4' %(eff_quarantined,rep+1) ) \            


# In[ ]:


## SENSITIVITY ANALYSIS FOR COST FOOD##
import shutil, os
import numpy as np
import pandas as pd
import math
from math import atan2
import random
import statistics
import csv
import time as mytime

numsim = 4 # number of replicates
start_time=mytime.time() # server time for starting

COST_FOOD = [1208, 3624] # plus or minus of parmater value 
for number in COST_FOOD:
    
    #cost_food = 2416.33 # cost of producing food crop-MAIZE (GHS/ha) - 41.3% return on investment of cultivating between 2018-2022 (using average price and average yield)
    cost_bioenergy = 2933.207 #1433 cost of producing bioenergy crop-JATHROPHA (GHC/ha)

    yield_food = 2.4 # food yield (mt/ha) - average yield 2018-2022
    yield_bioenergy = 3.517983  #3 bioenergy yield (mt/ha)

    init_price_food = 1713.96 # initial value of food price (GHS/mt) for average of 2018-2022
    init_price_bioenergy = 2175.63  #840  initial value of food price (GHC/mt)

    actualhav_food = 1 # fraction of food biomass harvested per hectare
    actualhav_bioenergy = 1 # fraction of bioenergy biomass harvested per hectare

    total_demand_food = 111e7 #(GHS/year) demand for food crop (in GHC) for Brong-Ahafo expressed as 22% of estimted 2018-2022 average national production mutlipled by 20018-2022 price 
    total_demand_bioenergy = 32184409   #11e6  set at 1% of amount_demand_food

    # focal paramater 
    cost_food = number
    outfname  = os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/" + 'cost_food_' + str(number) + '.csv')
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
            #os.rename('sim_movie.mp4', 'movie_eff_quarantined_%.2f_rep_%i.mp4' %(eff_quarantined,rep+1) ) \            


# In[ ]:


## SENSITIVITY ANALYSIS FOR COST BIOENERGY##
import shutil, os
import numpy as np
import pandas as pd
import math
from math import atan2
import random
import statistics
import csv
import time as mytime

numsim = 4 # number of replicates
start_time=mytime.time() # server time for starting

COST_BIOENERGY = [1466,4399] # plus or minus of parmater value 
for number in COST_BIOENERGY:
    
    cost_food = 2416.33 # cost of producing food crop-MAIZE (GHS/ha) - 41.3% return on investment of cultivating between 2018-2022 (using average price and average yield)
    # cost_bioenergy = 2933.207 #1433 cost of producing bioenergy crop-JATHROPHA (GHC/ha)

    yield_food = 2.4 # food yield (mt/ha) - average yield 2018-2022
    yield_bioenergy = 3.517983  #3 bioenergy yield (mt/ha)

    init_price_food = 1713.96 # initial value of food price (GHS/mt) for average of 2018-2022
    init_price_bioenergy = 2175.63  #840  initial value of food price (GHC/mt)

    actualhav_food = 1 # fraction of food biomass harvested per hectare
    actualhav_bioenergy = 1 # fraction of bioenergy biomass harvested per hectare

    total_demand_food = 111e7 #(GHS/year) demand for food crop (in GHC) for Brong-Ahafo expressed as 22% of estimted 2018-2022 average national production mutlipled by 20018-2022 price 
    total_demand_bioenergy = 32184409   #11e6  set at 1% of amount_demand_food

    # focal paramater 
    cost_bioenergy = number
    outfname  = os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/" + 'cost_bioenergy_' + str(number) + '.csv')
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
            #os.rename('sim_movie.mp4', 'movie_eff_quarantined_%.2f_rep_%i.mp4' %(eff_quarantined,rep+1) ) \            


# In[ ]:


## SENSITIVITY ANALYSIS FOR TOTAL DEMAND FOOD##
import shutil, os
import numpy as np
import pandas as pd
import math
from math import atan2
import random
import statistics
import csv
import time as mytime

numsim = 4 # number of replicates
start_time=mytime.time() # server time for starting

TOTAL_DEMAND_FOOD = [56e7,167e7] # plus or minus of parmater value 
for number in TOTAL_DEMAND_FOOD:
    
    cost_food = 2416.33 # cost of producing food crop-MAIZE (GHS/ha) - 41.3% return on investment of cultivating between 2018-2022 (using average price and average yield)
    cost_bioenergy = 2933.207 #1433 cost of producing bioenergy crop-JATHROPHA (GHC/ha)

    yield_food = 2.4 # food yield (mt/ha) - average yield 2018-2022
    yield_bioenergy = 3.517983  #3 bioenergy yield (mt/ha)

    init_price_food = 1713.96 # initial value of food price (GHS/mt) for average of 2018-2022
    init_price_bioenergy = 2175.63  #840  initial value of food price (GHC/mt)

    actualhav_food = 1 # fraction of food biomass harvested per hectare
    actualhav_bioenergy = 1 # fraction of bioenergy biomass harvested per hectare

    #total_demand_food = 111e7 #(GHS/year) demand for food crop (in GHC) for Brong-Ahafo expressed as 22% of estimted 2018-2022 average national production mutlipled by 20018-2022 price 
    total_demand_bioenergy = 32184409   #11e6  set at 1% of amount_demand_food

    # focal paramater 
    total_demand_food = number
    outfname  = os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/" + 'total_demand_food_' + str(number) + '.csv')
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
            #os.rename('sim_movie.mp4', 'movie_eff_quarantined_%.2f_rep_%i.mp4' %(eff_quarantined,rep+1) ) \            


# In[ ]:


## SENSITIVITY ANALYSIS FOR TOTAL DEMAND BIOENERGY##
import shutil, os
import numpy as np
import pandas as pd
import math
from math import atan2
import random
import statistics
import csv
import time as mytime

numsim = 4 # number of replicates
start_time=mytime.time() # server time for starting

TOTAL_DEMAND_BIOENERGY = [16e6,48e6] # plus or minus of parmater value 
for number in TOTAL_DEMAND_BIOENERGY:
    
    cost_food = 2416.33 # cost of producing food crop-MAIZE (GHS/ha) - 41.3% return on investment of cultivating between 2018-2022 (using average price and average yield)
    cost_bioenergy = 2933.207 #1433 cost of producing bioenergy crop-JATHROPHA (GHC/ha)

    yield_food = 2.4 # food yield (mt/ha) - average yield 2018-2022
    yield_bioenergy = 3.517983  #3 bioenergy yield (mt/ha)

    init_price_food = 1713.96 # initial value of food price (GHS/mt) for average of 2018-2022
    init_price_bioenergy = 2175.63  #840  initial value of food price (GHC/mt)

    actualhav_food = 1 # fraction of food biomass harvested per hectare
    actualhav_bioenergy = 1 # fraction of bioenergy biomass harvested per hectare

    total_demand_food = 111e7 #(GHS/year) demand for food crop (in GHC) for Brong-Ahafo expressed as 22% of estimted 2018-2022 average national production mutlipled by 20018-2022 price 
    # total_demand_bioenergy = 32184409   #11e6  set at 1% of amount_demand_food

    # focal paramater 
    total_demand_bioenergy = number
    outfname  = os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/" + 'total_demand_bioenergy_' + str(number) + '.csv')
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
            #os.rename('sim_movie.mp4', 'movie_eff_quarantined_%.2f_rep_%i.mp4' %(eff_quarantined,rep+1) ) \            


# In[ ]:





# In[ ]:




