#!/usr/bin/env python
# coding: utf-8

# In[82]:


# import sys
# sys.version_info


# ### import relevant libraries


import shutil, os
import numpy as np
import pandas as pd
import math
from math import atan2
import random
import statistics
import csv
from scipy.optimize import minimize

# get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from matplotlib import rcParams, cycler
import matplotlib.gridspec as gridspec
from matplotlib.ticker import ScalarFormatter
from mpl_toolkits.axes_grid1.inset_locator import inset_axes,  zoomed_inset_axes
# from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes

import geopandas as gpd
import shapely.geometry
from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiPolygon, box, mapping
from shapely.ops import cascaded_union, unary_union, nearest_points
import warnings
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning) 
#import shapely.speedups

import rasterio
import rasterstats
from rasterio.mask import mask
from rasterio.plot import show
from rasterio import Affine # or from affine import Affine
from rasterio.plot import plotting_extent
from glob import glob 

import xarray as xr 
import rioxarray as rio 
import cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
from cartopy.util import add_cyclic_point
import cartopy
import cartopy.feature as cfeature
# from xrspatial import slope
import cmocean

import osmnx as ox
import networkx as nx
ox.settings.log_console=True
ox.__version__


# ### open raster data
#new
fp = os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/inbox/Brong_Ahafo_IPCC_CCI_2020.ipcc.tif") # Brong-Ahafo 2020, 300m resolution
raster = rio.open_rasterio(fp, masked=False) # open the file
raster.rio.write_crs(4326, inplace=True) # set crs
# raster[0,:,:].plot()


# ### download boundary of region from openstreetmap 
#new
# Brong-Ahafo region (now consists of Bono, Ahafo, and Bono East region)
boundaries_list = []
Brong_Ahafo_Boundary=gpd.GeoDataFrame(geometry='geometry',columns=['geometry'],crs=raster.rio.crs)
for region in ['Bono Region', 'Ahafo Region', 'Bono East Region']:
    boundary  = ox.geocode_to_gdf(region)
    boundary = boundary.to_crs(raster.rio.crs)
    polygon = boundary.at[0,'geometry']
    boundaries_list.append(polygon)
    
union_three_regions=unary_union(boundaries_list)
Brong_Ahafo_Boundary.at[0,'geometry'] = union_three_regions
Brong_Ahafo_Boundary_Regions=gpd.GeoDataFrame(boundaries_list, geometry='geometry',columns=['geometry'])



# ### mask out data beyond region of interest
#new
raster_clipped = raster.rio.clip(Brong_Ahafo_Boundary.geometry.values, Brong_Ahafo_Boundary.crs, drop=False, invert=False)
# raster_clipped[0,:,:].plot()


# ### mask other landuses except cropland
#new
cropland = raster_clipped.where(raster_clipped == 3)


# ### cropland contained in the region boundary
#new 
#output directory
output_folder = output_folder = os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/inbox/")  # output_folder = r"" 
result_folder = os.path.join(output_folder, 'all_cropland')
if os.path.exists(result_folder):
    shutil.rmtree(result_folder) # delete the whole folder
os.makedirs(result_folder)
#os.chdir(result_folder) # move to subfolder

# extract the row, columns, and elevation of the valid values
row, col = np.where(raster_clipped[0,:,:] == 3) 
elev = np.extract(raster_clipped[0,:,:] == 3, raster_clipped)
# transform between the pixel and projected coordinates with out_transform as the affine transform for the subset data    
T1 = raster_clipped.rio.transform() * Affine.translation(0.5, 0.5) # reference the pixel centre
rc2xy = lambda r, c: T1 * (c, r)

dummy_geometry = np.array([Point(0, 0)]*len(row)) # A dummy geometry to initialize the geodataframe
region = gpd.GeoDataFrame({'col':col,'row':row,'elev':elev, 'geometry':dummy_geometry}, geometry='geometry',crs=raster_clipped.rio.crs) # create empty geodataframe
region['x'] = region.apply(lambda row: rc2xy(row['row'],row['col'])[0], axis=1) # coordinate transformation
region['y'] = region.apply(lambda row: rc2xy(row['row'],row['col'])[1], axis=1)
region['geometry'] =region.apply(lambda row: Point(row['x'], row['y']), axis=1) # corresponding geometry point
#region['time_fall'] = region.apply(lambda row: 1, axis=1)

# format the filename 
output_name = "region.shp"
outpath = os.path.join(result_folder, output_name)
region.to_file(outpath)


# ### read and plot cropland in boundary
# read file and set the CRS
ALL_CROPLAND = gpd.read_file(os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/inbox/all_cropland/region.shp"))
# fraction of cropland not cultivted with maize
frac_cropland_maize = int(len(ALL_CROPLAND) - 27777) #fraction of cropland cultivated for maize crop set at 250000 ha, divided by 9 gives the number (27777) of points needed
crop_index = random.sample(range(len(ALL_CROPLAND)), frac_cropland_maize) #randomly sample fraction of cropland not to be cultivated
ALL_CROPLAND.drop(crop_index,inplace=True) # remove fraction not cultivated with maize from geodataframe
ALL_CROPLAND.reset_index(drop=True, inplace=True)  # reset the index of geodataframe
# len(ALL_CROPLAND)


# ### assign cropland to farmer agents
output_folder = os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/inbox/")  #output directory
result_folder = os.path.join(output_folder, 'farmer_agents')
if os.path.exists(result_folder):
    shutil.rmtree(result_folder) # delete the whole folder
os.makedirs(result_folder)
#os.chdir(result_folder) # move to subfolder

counter = 0 # set counter for agent name
while True:
    # while True:
    #     farmsize = round(random.gauss(50,100)) # average household farmsize
    #     if farmsize >= 50:
    #         break
    
    farmsize = round(random.uniform(5,25)) # average farmsize , will chnage this later 
    if farmsize < len(ALL_CROPLAND): # selected farmsize must be less than geodataframe
        farmland = ALL_CROPLAND.iloc[0 : farmsize].copy() # select consecutive farmsize-nth for a farmer
        ALL_CROPLAND = ALL_CROPLAND.drop(ALL_CROPLAND.index[range(0, farmsize)]) # drop corresponding index from geodataframe
        ALL_CROPLAND.reset_index(drop=True, inplace=True)  # reset the index of geodataframe
        
    else : #selected farmsize greater than length of geodataframe
        farmland = ALL_CROPLAND.copy() # set farmsize to geodataframe
        ALL_CROPLAND = ALL_CROPLAND.drop(ALL_CROPLAND.index[range(0,len(ALL_CROPLAND))]) 
               
    farmland['SOC'] = farmland.apply(lambda row: round(random.uniform(0.98,1),4), axis=1) # apply land fertility  to farmer agent

    counter += 1 # update counter
    output_name = "agent_{}.shp".format(counter)  # Format the filename 
    outpath = os.path.join(result_folder, output_name)
    farmland.to_file(outpath)
        
    if len(ALL_CROPLAND) == 0:
        break  
        


# ### sort agents created by name and plot farmsize distribution

filenames = sorted(glob(os.path.join(os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/inbox/farmer_agents"), '*.shp')))
# filenames = sorted(filenames, key=lambda s: int(s[87:-4])) # remove the first 20 characters, and last 4 charasters, lefts with only the number and integer it
filenames = sorted(filenames, key=lambda s: int(s[94:-4])) # server



# ### initialization

initialize parameters
cost_food = 2416.33 # cost of producing food crop-MAIZE (GHS/ha) - 41.3% return on investment of cultivating between 2018-2022 (using average price and average yield)
cost_bioenergy = 2933.207 #1433 cost of producing bioenergy crop-JATHROPHA (GHC/ha)

yield_food = 2.4 # food yield (mt/ha) - average yield 2018-2022
yield_bioenergy = 3.517983  #3 bioenergy yield (mt/ha)

init_price_food = 1713.96 # initial value of food price (GHS/mt) for average of 2018-2022
init_price_bioenergy = 2175.63  #840  initial value of food price (GHC/mt)

actualhav_food = 1 # fraction of food biomass harvested per hectare
actualhav_bioenergy = 1 # fraction of bioenergy biomass harvested per hectare

total_demand_food = 111e7 #(GHS/year) demand for food crop (in GHC) for Brong-Ahafo expressed as 22% of estimted 2018-2022 average national production mutlipled by 20018-2022 price 
total_demand_bioenergy = 32184409   #11e6  set at 1% of amount_demand_food

   
class agent:  # create an empty class
    pass     
      
def initialize():
    global agents, time, time1, cost_food, cost_bioenergy, yield_food, yield_bioenergy, init_price_food, init_price_bioenergy, price_food, price_bioenergy
    global num_consumers, actualhav_food, actualhav_bioenergy, per_capita_food, per_capita_bioenergy, frac_cal, total_demand_food, total_demand_bioenergy, treatment
    global CAPITAL, ACTION_FOOD, ACTION_BIOENERGY, INTERACTION_NO, INTERACTION_YES,  HARVEST_FOOD, HARVEST_BIOENERGY, LAND_FERTILITY, PRIORITY_FOOD, PRIORITY_BIOENERGY, PRIORITY_FALLOW, LAND_FOOD, LAND_BIOENERGY 
    
    agents = [] # storing the agents
    time = 0 # time for updating (years)
    time1 = [time]
    treatment = ['interaction']
    
    price_food = [init_price_food] # unit price of food crop (GHS/mt)
    price_bioenergy = [init_price_bioenergy] # unit price of bioenergy crop (GHS/mt)
    
    HARVEST_FOOD = [0] # tracking total food crop harvested (mt)
    HARVEST_BIOENERGY =[0] # tracking total bioenergy crop harvested (mt)
    
    # per_capita_food = (4318 / num_consumers) * 227   # per capita food consumption (mt) in 2017 x price of food ($/mt) in 2017 rate
    # #per_capita_bioenergy = frac_cal * per_capita_food    # capita bioenergy consumption for calibration
    # per_capita_bioenergy = 0 #  per capita bioenergy consumption / looping with this constant value  

    # loop to initialize variables for agents
    for j in range(len(filenames)):   
        ag = agent()
        ag.name = 'agent%d'% (j+1) # name of agents
        ag.region = gpd.read_file(filenames[j]) # region under the control of an agent represented by geodataframe
        
        ag.food_crop = gpd.GeoDataFrame(geometry='geometry',columns=['geometry']) # empty geodataframe for food crop
        ag.bioenergy_crop= gpd.GeoDataFrame(geometry='geometry',columns=['geometry'])
        ag.idle_land= gpd.GeoDataFrame(geometry='geometry',columns=['geometry'])
        
        ag.land_size = len(ag.region) # land size (hectares), but note each point represents 9 hectares of land so needs to be multipled by 9 when computing equations 
        ag.action = 0 if j < int(0.95*len(filenames)) else 1  # initially 95% of agents devot-greater portion of land to food crop (i.e. 0) and the remaining devot-greater portion to bioenergy (i.e. 1)
        ag.profit_threshold = 2/3 #1# threshold of profit success-below this value agents will change action after 2 consecutive times (years)
        ag.trust_biocompanies = random.gauss(0.15,0.01) # initial trust level in bioenergy companies
        ag.interaction = 'no' 
        
        ag.capital = [(9 * ag.land_size) * cost_food] # initial capital of agent enough to cover total-cost of using entire land for cultivating food crop (GHS), multiplied by 9 bcos each point represents 9 hectares 
        ag.invest_food = [] # amount invested in food crop (GHS)
        ag.invest_bioenergy = [] # amount invested in bioenergy crop
        ag.total_invest = [] # amount invested in both crops
        
        ag.hav_food = [] # amount of food crop harvested (mt)
        ag.hav_bioenergy = [] # amount of bioenergy crop harvested
        ag.total_hav = [] # amount harvested for both crops
        
        ag.profit_food = [] # profit from food crop (GHS)
        ag.profit_bioenergy = [] # profit from bioenergy crop
        ag.total_profit = [] # profit from both crops 
        
        ag.priority_food = [0] # priority of land devoted to food crop
        ag.priority_bioenergy = [0] # priority of land devoted to bioenergy crop
       
        ag.accuracy_decision = [] # accuracy of action adopted (whether made a profit-1 or loss-0)
        ag.moore_neighbors = [] # moore neighborhood

        agents.append(ag) # store  all the agents
        
        
    LAND_FERTILITY = [statistics.mean([ag.region['SOC'].mean() for ag in agents])] # mean land fertlity (soc: soil organic carbon) across the region
    PRIORITY_FOOD = [statistics.mean([ag.priority_food[-1] for ag in agents])] # mean priority of food crop across the region
    PRIORITY_BIOENERGY = [statistics.mean([ag.priority_bioenergy[-1] for ag in agents])] # mean priority of bioenergy crop across the region
    PRIORITY_FALLOW = [1 - (PRIORITY_FOOD[-1] + PRIORITY_BIOENERGY[-1])] # mean priority of fallow across the region
    
    LAND_FOOD = [(sum([ag.priority_food[-1] * (9 * ag.land_size) for ag in agents]) / sum([(9 * ag.land_size) for ag in agents])) * 100 ] # percentage of land used for food
    LAND_BIOENERGY = [(sum([ag.priority_bioenergy[-1] * (9 * ag.land_size) for ag in agents]) / sum([(9 * ag.land_size) for ag in agents])) * 100] # percentage of land used for bioenergy
    CAPITAL = [statistics.mean([ag.capital[-1] for ag in agents])] # mean capital
    
    ACTION_FOOD = [sum([1 for ag in agents if ag.action == 0])] # number of agents adopting food direction
    ACTION_BIOENERGY = [sum([1 for ag in agents if ag.action == 1])] # number of agents adopting bioenergy direction
    
    INTERACTION_NO = [sum([1 for ag in agents if ag.interaction == 'no'])] # number of agents interacting with biocompanies
    INTERACTION_YES = [sum([1 for ag in agents if ag.interaction == 'yes'])] # number of agents not-interacting with biocompanies
    


# In[ ]:


# initialize() 


# ### updating (interaction with biocompanies)

# In[18]:


def update_interaction():
 
    global agents, time, time1, cost_food, cost_bioenergy, yield_food, yield_bioenergy, init_price_food, init_price_bioenergy, price_food, price_bioenergy
    global num_consumers, actualhav_food, actualhav_bioenergy, per_capita_food, per_capita_bioenergy, frac_cal, total_demand_food, total_demand_bioenergy, treatment
    global CAPITAL, ACTION_FOOD, ACTION_BIOENERGY, INTERACTION_NO, INTERACTION_YES,  HARVEST_FOOD, HARVEST_BIOENERGY, LAND_FERTILITY, PRIORITY_FOOD, PRIORITY_BIOENERGY, PRIORITY_FALLOW, LAND_FOOD, LAND_BIOENERGY 
    
    for ag in agents :
        
        #interaction with extension officers from biofuel companies (on / off)
        # if time >= 25:
        #     ag.interaction = 'yes'  if random.random() < ag.trust_biocompanies else 'no'
        # else:
        #     pass
        
        ag.interaction = 'yes'  if random.random() < ag.trust_biocompanies else 'no'
    
        # objective function for maximizing profit
        def objective(r, sign = -1): 
            r0 = r[0] # for food
            r1 = r[1] # for bioenergy

            #harvest (under the assumption of perfect mean land fertility, i.e. 1)
            ass_hav_food =  r0 * (9 * ag.land_size) * yield_food * actualhav_food # food harvest
            ass_hav_bioenergy= r1 * (9 * ag.land_size) * yield_bioenergy * actualhav_bioenergy # bioenergy harvest
            ass_hav = ass_hav_food + ass_hav_bioenergy # total harvest
            
            #income
            ass_income_food = (price_food[-1]/1000) * ass_hav_food
            ass_income_bioenergy = (price_bioenergy[-1]/1000) * ass_hav_bioenergy
            ass_income = ass_income_food + ass_income_bioenergy

            #investment cost
            ass_cost_food = r0 * (9 * ag.land_size) * (cost_food/1000)
            ass_cost_bioenergy = r1 * (9 * ag.land_size) * (cost_bioenergy/1000)
            ass_cost = ass_cost_food +  ass_cost_bioenergy
            
            #profit
            ass_profit = ass_income - ass_cost        
            return sign * (ass_profit) #the negative sign means maximizing profit, since we will use optimize.minimize 

        
        # setting the constraints
        def constraint1(r):
            r0 = r[0]
            r1 = r[1]
            
            #investment cost
            ass_cost_food = r0 * (9 * ag.land_size) * (cost_food/1000)
            ass_cost_bioenergy = r1 * (9 * ag.land_size) * (cost_bioenergy/1000)
            ass_cost = ass_cost_food +  ass_cost_bioenergy
            
            return  (ag.capital[-1]/1000) - ass_cost # total investment cost should be less than capital


        def constraint2(r):
            r0 = r[0]
            r1 = r[1]

            # associated cost
            ass_cost_food = r0 * (9 * ag.land_size) * (cost_food/1000)
            ass_cost_bioenergy = r1 * (9 * ag.land_size) * (cost_bioenergy/1000)
            ass_cost = ass_cost_food +  ass_cost_bioenergy

           
            if all([ag.action == 0, ag.interaction == 'no']): # priority-direction is food 
                # return ass_cost_food - ass_cost_bioenergy   # invest more into food than bioenergy
                return r1 - 0*r0
            
            elif all([ag.action == 0, ag.interaction == 'yes']): # priority-direction is food 
                # return ass_cost_food - ass_cost_bioenergy   # invest more into food than bioenergy
                # return r1 - round(random.uniform(0,0.25),2)*r0 
                return r1 - round(random.uniform(0,0.25),2)*r0 
            
            elif all([ag.action == 1, ag.interaction == 'no']): # priority-direction is bioenergy
                # return ass_cost_bioenergy - ass_cost_food  # invest more into bioenergy than food
                # return r1 - round(random.uniform(0,0.03),2)*r0
                return r1 - round(random.uniform(0.25,0.5),2)*r0
            
            elif all([ag.action == 1, ag.interaction == 'yes']): # priority-direction is bioenergy
                # return ass_cost_bioenergy - ass_cost_food  # invest more into bioenergy than food
                # return r0 - round(random.uniform(0.1,0.5),2)*r1
                return r0 - round(random.uniform(0.5,1),2)*r1
            
            

        def constraint3(r):
            r0 = r[0]
            r1 = r[1]
            return 1 - (r0 + r1) # sum of r0 and r1 should not be greater than 1
        

#         def constraint4(r):
#             r0 = r[0]
#             r1 = r[1]

#             #associated cost
#             ass_cost_food = r0  * (9 * ag.land_size) * (cost_food/1000)
#             ass_cost_bioenergy = r1  * (9 * ag.land_size) * (cost_bioenergy/1000)
#             ass_cost = ass_cost_food +  ass_cost_bioenergy

#             if ag.interaction == 'yes':
#                 return ass_cost_bioenergy - 0.25 * 0.5 * (ag.capital[-1]/1000)  #. when interaction occurs, investment cost in bioenergy should not be less than 25% of 50% of capital
#                 # return r1 - (0.25 * r0)
#             else : 
#                 return 1 - (r0 + r1)
                

        #range of variables
        b = (0,1)
        bnds = (b, b)

        con1 = {'type': 'ineq', 'fun': constraint1}
        con2 = {'type': 'eq', 'fun': constraint2}
        con3 = {'type': 'ineq', 'fun': constraint3}
        # con4 = {'type': 'ineq', 'fun': constraint4}
        
        cons = ([con1,con2,con3]) #([con1,con2,con3,con4])
        
     
        if ag.capital[-1] > 0 : # for positive capital
            while True :
                # initial guesses
                x0 = [random.uniform(0,1), random.uniform(0,1)] # set random to terminate successfully

                # optimize to maximize profit
                solution = minimize(objective,x0,method='SLSQP',bounds=bnds,constraints=cons) 
       
                if  all([ 
                     (solution.x[0] + solution.x[1] <= 1), 
                     ((solution.x[0] * (9 * ag.land_size) * cost_food) + (solution.x[1] * (9 * ag.land_size) * cost_bioenergy)) < (ag.capital[-1]) 
                     ]) : # if sums of priority is below 1, and total cost below capital/ (0.5*ag.capital[-1]) 
                    (ag.priority_food).append(round(solution.x[0],5)) # putting r0 into priority_food
                    (ag.priority_bioenergy).append(round(solution.x[1],5)) # putting r1 into priority_bioenergy
                    # print(solution.message)
                    # print(solution.x)
                    # print(solution.fun)
                    # print(solution)
                    break

        else : #negative capital 
            (ag.priority_food).append(0) # putting r0 into priority_food
            (ag.priority_bioenergy).append(0) # putting r1 into priority_bioenergy
#             print([ag.priority_food[-1],ag.priority_bioenergy[-1]])



# ### updating land fertility

# In[19]:


def bioenergy_cultivated_land(soc):
    global half_life_bioenergy
    half_life_bioenergy = 1000 # (yrs)
    decay_const = np.log(2) / half_life_bioenergy
    time_interval = 1
    return soc * np.exp(-decay_const * time_interval)    

def food_cultivated_land(soc):
    global half_life_food
    half_life_food = 1000 # (yrs)
    decay_const = np.log(2) / half_life_food
    time_interval = 1
    return soc * np.exp(-decay_const * time_interval)
        
# def fallow_prob(time_fallow):
#     growth_limit = 1
#     decay_const = 1
#     return growth_limit * (1 - np.exp(-decay_const * time_fallow))

def fallow_changes(row):
#     row['time_fall'] += 1
    row['SOC'] += 0.1
    row['SOC'] = 1 if row['SOC'] > 1 else row['SOC'] 
    return row



def update_soil():
    
    global agents, time, time1, cost_food, cost_bioenergy, yield_food, yield_bioenergy, init_price_food, init_price_bioenergy, price_food, price_bioenergy
    global num_consumers, actualhav_food, actualhav_bioenergy, per_capita_food, per_capita_bioenergy, frac_cal, total_demand_food, total_demand_bioenergy, treatment
    global CAPITAL, ACTION_FOOD, ACTION_BIOENERGY, INTERACTION_NO, INTERACTION_YES,  HARVEST_FOOD, HARVEST_BIOENERGY, LAND_FERTILITY, PRIORITY_FOOD, PRIORITY_BIOENERGY, PRIORITY_FALLOW, LAND_FOOD, LAND_BIOENERGY 
    
    for ag in agents :  
        
        ## ASSIGN LAND FOR BOTH CROPS AND FALLOW
        ## consecutively selects for food crop
        random_start_row = random.randint(0, (ag.land_size - int(ag.priority_food[-1] * ag.land_size))) # randomly select a number
        ag.food_crop = ag.region.iloc[random_start_row : random_start_row + int(ag.priority_food[-1] * ag.land_size)].copy()
        # remaining region left
        region_remaining = ag.region.drop(ag.region.index[range(random_start_row, random_start_row + int(ag.priority_food[-1] * ag.land_size))]) 
        #region_remaining.reset_index(drop=True, inplace=True)  # reset the index of geodataframe
        
        ## consecutively selects for bioenergy crop
        random_start_row1 = random.randint(0, (len(region_remaining) - round(ag.priority_bioenergy[-1] * ag.land_size)))
        ag.bioenergy_crop = region_remaining.iloc[random_start_row1 : random_start_row1 + round(ag.priority_bioenergy[-1] * ag.land_size)].copy()
        # remaining region left
        region_remaining1 = region_remaining.drop(region_remaining.index[range(random_start_row1, random_start_row1 + round(ag.priority_bioenergy[-1] * ag.land_size))])
        #region_remaining1.reset_index(drop=True, inplace=True)  # reset the index of geodataframe
        
        ## consecutively selects for fallow land
        ag.idle_land = region_remaining1.copy()
        
        
        ## COMPUTE CORRESPONDING HARVEST AND INVESTMENT TO ASSIGNED LAND
        (ag.hav_food).append(ag.priority_food[-1] * (9 * ag.land_size) * (yield_food * np.nan_to_num(ag.food_crop['SOC'].mean())) * actualhav_food) 
        (ag.hav_bioenergy).append(ag.priority_bioenergy[-1] * (9 * ag.land_size) * (yield_bioenergy * np.nan_to_num(ag.bioenergy_crop['SOC'].mean())) * actualhav_bioenergy)
        (ag.total_hav).append(ag.hav_bioenergy[-1] + ag.hav_food[-1])
       
        # investment cost resulting from the different priorities 
        (ag.invest_food).append(ag.priority_food[-1] * (9 * ag.land_size) * cost_food)
        (ag.invest_bioenergy).append(ag.priority_bioenergy[-1] * (9 * ag.land_size) * cost_bioenergy)
        (ag.total_invest).append(ag.invest_bioenergy[-1] + ag.invest_food[-1]) 
        
        
        # UPDATE THE LAND FERTILITY
        ag.region['SOC'] = ag.region.apply(lambda row: food_cultivated_land(row['SOC']) \
                                       if row.name in ag.food_crop.index else row['SOC'], axis=1)
    
        ag.region['SOC'] = ag.region.apply(lambda row: bioenergy_cultivated_land(row['SOC']) \
                                if row.name in ag.bioenergy_crop.index else row['SOC'], axis=1)
    
        ag.region = ag.region.apply(lambda row: fallow_changes(row) \
                                if row.name in ag.idle_land.index else row, axis=1) 
        


# In[ ]:


# update_soil() 


# ### computing market dynamics 

# In[ ]:


def update_market():
    
    global agents, time, time1, cost_food, cost_bioenergy, yield_food, yield_bioenergy, init_price_food, init_price_bioenergy, price_food, price_bioenergy
    global num_consumers, actualhav_food, actualhav_bioenergy, per_capita_food, per_capita_bioenergy, frac_cal, total_demand_food, total_demand_bioenergy, treatment
    global CAPITAL, ACTION_FOOD, ACTION_BIOENERGY, INTERACTION_NO, INTERACTION_YES,  HARVEST_FOOD, HARVEST_BIOENERGY, LAND_FERTILITY, PRIORITY_FOOD, PRIORITY_BIOENERGY, PRIORITY_FALLOW, LAND_FOOD, LAND_BIOENERGY 
    
    np.seterr(divide='ignore', invalid='ignore') # ignore division by zero warning
    # computing market price
    # total_demand_food = per_capita_food * num_consumers # total demand for food (per capita consumption)
    total_harvest_food = sum([ag.hav_food[-1] for ag in agents])
    (price_food).append(np.nan_to_num(total_demand_food /  total_harvest_food, posinf=total_demand_food))
   
    # total_demand_bioenergy = per_capita_bioenergy * num_consumers  # total demand for bioenergy
    total_harvest_bioenergy = sum([ag.hav_bioenergy[-1] for ag in agents])
    (price_bioenergy).append(np.nan_to_num(total_demand_bioenergy /  total_harvest_bioenergy, posinf=total_demand_bioenergy))
    
    # computing income, profits and capital from the market price
    for ag in agents :
        
        # income
        income_food = price_food[-1] * ag.hav_food[-1]
        income_bioenergy = price_bioenergy[-1] * ag.hav_bioenergy[-1]
        income = income_food + income_bioenergy
        
        # profit
        (ag.profit_food).append(income_food - ag.invest_food[-1])
        (ag.profit_bioenergy).append(income_bioenergy - ag.invest_bioenergy[-1])
        (ag.total_profit).append(income - ag.total_invest[-1])
    
        # capital
        (ag.capital).append(ag.capital[-1] - ag.total_invest[-1] + ag.total_profit[-1])

        
        # trust dynamics with biofuel companies
        if all([ag.interaction == 'yes', ag.total_profit[-1] > 0]):
            ag.trust_biocompanies += random.uniform(0,0.5) # prior interaction resulting in positive profit increase propensity to interact again
            ag.trust_biocompanies = 0.9 if ag.trust_biocompanies > 1 else ag.trust_biocompanies
        elif all([ag.interaction == 'yes', ag.total_profit[-1] < 0]):
            ag.trust_biocompanies -= random.uniform(0,0.3) # prior interaction with negative profit decrease propensity to interact again
            ag.trust_biocompanies = 0.1 if ag.trust_biocompanies < 0 else ag.trust_biocompanies
            
            
        # changing strategies dynamics (negative profits - 0, positive profits - 1)
        if ag.total_profit[-1] > 0  : 
            (ag.accuracy_decision).append(1)
        elif ag.total_profit[-1] <= 0 :
            (ag.accuracy_decision).append(0)
            
              
        # check after every 3 years whether to change strategy 
        if all([time % 3 == 0, ag.action == 0])  :
            if statistics.mean(ag.accuracy_decision[-3:]) < ag.profit_threshold  : 
                ag.action = 1 # change action
            else :  
                ag.action = 0 # mantain action
#             ag.accuracy_decision *= 0 # empty list 
            
        elif all([time % 3 == 0, ag.action == 1])  :
            if statistics.mean(ag.accuracy_decision[-3:]) < ag.profit_threshold  : 
                ag.action = 0 
            else : 
                ag.action = 1
#             ag.accuracy_decision *= 0 # empty list  

            
    HARVEST_BIOENERGY.append(sum([ag.hav_bioenergy[-1] for ag in agents]))
    HARVEST_FOOD.append(sum([ag.hav_food[-1] for ag in agents]))
    
    LAND_FERTILITY.append(statistics.mean([ag.region['SOC'].mean() for ag in agents]))
    
    PRIORITY_FOOD.append(statistics.mean([ag.priority_food[-1] for ag in agents]))
    PRIORITY_BIOENERGY.append(statistics.mean([ag.priority_bioenergy[-1] for ag in agents]))
    PRIORITY_FALLOW.append(1 - (PRIORITY_FOOD[-1] + PRIORITY_BIOENERGY[-1]))
    
    LAND_FOOD.append((sum([ag.priority_food[-1] * (9 * ag.land_size) for ag in agents]) / sum([(9 * ag.land_size) for ag in agents])) * 100 ) # percent land used for food
    LAND_BIOENERGY.append((sum([ag.priority_bioenergy[-1] * (9 * ag.land_size) for ag in agents]) / sum([(9 * ag.land_size) for ag in agents])) * 100) # percent land used for bioenergy
    
    CAPITAL.append(statistics.mean([ag.capital[-1] for ag in agents]))
    ACTION_FOOD.append(sum([1 for ag in agents if ag.action == 0])) # number of agents adopting food direction
    ACTION_BIOENERGY.append(sum([1 for ag in agents if ag.action == 1])) # number of agents adopting bioenergy direction

    INTERACTION_NO.append(sum([1 for ag in agents if ag.interaction == 'no'])) # number of agents adopting food direction
    INTERACTION_YES.append(sum([1 for ag in agents if ag.interaction == 'yes'])) # number of agents adopting food direction

    # treatment.append('interaction') if time >= 25 else treatment.append('no_interaction') # set treatment
    # treatment.append('no_interaction') 
    treatment.append('interaction') 
    
    # create a csv-file output 
    csvfile = os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/bioenergy_model_simulation.csv")
    # csvfile = "simulation_data.csv"   
    header = ['time','price_bioenergy','price_food','harvest_bioenergy','harvest_food', 'land_fertility', 'priority_food', 'priority_bioenergy', 'priority_fallow', 'land_food', 'land_bioenergy', 'capital','food_direction','bioenergy_direction','no_interaction','yes_interaction','treatment']
    main_data = [time1,price_bioenergy, price_food, HARVEST_BIOENERGY, HARVEST_FOOD, LAND_FERTILITY, PRIORITY_FOOD, PRIORITY_BIOENERGY, PRIORITY_FALLOW, LAND_FOOD, LAND_BIOENERGY, CAPITAL, ACTION_FOOD, ACTION_BIOENERGY, INTERACTION_NO, INTERACTION_YES, treatment ]
    with open(csvfile, "w") as output:
        writer = csv.writer(output) 
        writer.writerow(header)
        writer.writerows(zip(*main_data))  
                


# In[ ]:


# update_market()


# ### observation

# In[ ]:


def update_observe():
    
    global agents, time, time1, cost_food, cost_bioenergy, yield_food, yield_bioenergy, init_price_food, init_price_bioenergy, price_food, price_bioenergy
    global num_consumers, actualhav_food, actualhav_bioenergy, per_capita_food, per_capita_bioenergy, frac_cal, total_demand_food, total_demand_bioenergy, treatment
    global CAPITAL, ACTION_FOOD, ACTION_BIOENERGY, INTERACTION_NO, INTERACTION_YES,  HARVEST_FOOD, HARVEST_BIOENERGY, LAND_FERTILITY, PRIORITY_FOOD, PRIORITY_BIOENERGY, PRIORITY_FALLOW, LAND_FOOD, LAND_BIOENERGY 
 
    fig, ax = plt.subplots(figsize=(18,8))
    minx1, miny1, maxx1, maxy1 = Brong_Ahafo_Boundary['geometry'].total_bounds # Brong-Ahafo bounds
     
    # create a legend: we'll plot empty lists with the desired color, label, symbol
    for facecol, label, edgecol, symb, alph in [('royalblue','Food crop','royalblue','o', 1),
                                                ('mediumseagreen','Bioenergy crop','mediumseagreen','o', 1) ,
                                                ('grey','Idle land','grey','o', 1) ]:
        ax.scatter([], [], facecolor=facecol, s=100, label=label, alpha=alph, edgecolors=edgecol, marker=symb,linewidths=1.5 )
        ax.legend(facecolor="white", edgecolor="black",prop={"size":12}, loc="upper right", ncol=1) #loc=(0.5,0.02)
     
    
    for ag in agents:
        
        if time == 0 : # run only for intial time
            ## consecutively selects for food crop
            random_start_row = random.randint(0, (ag.land_size - int(ag.priority_food[-1] * ag.land_size))) # ranadonly select a number
            ag.food_crop = ag.region.iloc[random_start_row : random_start_row + int(ag.priority_food[-1] * ag.land_size)]
            if len(ag.food_crop) > 0:
                    ag.food_crop.plot(ax=ax, alpha=1, facecolor='royalblue', edgecolor='none', marker = '.', markersize=4)

            # remaining region left
            region_remaining = ag.region.drop(ag.region.index[range(random_start_row, random_start_row + int(ag.priority_food[-1] * ag.land_size))]) 
            region_remaining.reset_index(drop=True, inplace=True)  # reset the index of geodataframe

            ## consecutively selects for bioenergy crop
            random_start_row1 = random.randint(0, (len(region_remaining) - round(ag.priority_bioenergy[-1] * ag.land_size)))
            ag.bioenergy_crop = region_remaining.iloc[random_start_row1 : random_start_row1 + round(ag.priority_bioenergy[-1] * ag.land_size)]
            if len(ag.bioenergy_crop) > 0:
                    ag.bioenergy_crop.plot(ax=ax, alpha=1, facecolor='mediumseagreen', edgecolor='none', marker = '.', markersize=4)

            # remaining region left
            region_remaining1 = region_remaining.drop(region_remaining.index[range(random_start_row1, random_start_row1 + round(ag.priority_bioenergy[-1] * ag.land_size))])
            region_remaining1.reset_index(drop=True, inplace=True)  # reset the index of geodataframe

            ## consecutively selects for fallow land
            ag.idle_land = region_remaining1
            if len(ag.idle_land) > 0:
                    ag.idle_land.plot(ax=ax, alpha=1, facecolor='grey', edgecolor='none', marker = '.', markersize=4)
                    
        else: # run this every time excapt intil=al at time zero
            
            if len(ag.food_crop) > 0:
                ag.food_crop.plot(ax=ax,alpha=1 ,facecolor='royalblue', edgecolor='none', marker = '.',markersize=4)
                
            if len(ag.bioenergy_crop) > 0:
                ag.bioenergy_crop.plot(ax=ax,alpha=1 ,facecolor='mediumseagreen', edgecolor='none', marker = '.',markersize=4)

            if len(ag.idle_land) > 0:
                ag.idle_land.plot(ax=ax,alpha=1, facecolor='grey', edgecolor='none', marker = '.',markersize=4)

    
    # boundary plot
    Brong_Ahafo_Boundary.boundary.plot(ax=ax, color='black', linewidth=1) 
    ax.set_title('Spatial dynamics of food and bioenergy crops in Brong-Ahafo Region, Ghana, time =' + str(int(time)),fontsize=15) # title
    ax.set_xlabel('X Coordinates',fontsize=15)
    ax.set_ylabel('Y Coordinates',fontsize=15)
    ax.set_xlim(([minx1, maxx1]))
    ax.set_ylim(([miny1, maxy1]))
    
   # make insert figure within the main plot
    ax1 = inset_axes(ax, width='40%', height='40%', bbox_to_anchor=(0.01, 0.07, 0.65, 0.5), bbox_transform=ax.transAxes, loc='lower right') # (x0, y0, width, height)
    ax2 = inset_axes(ax, width='40%', height='40%', bbox_to_anchor=(0.35, 0.07, 0.65, 0.5), bbox_transform=ax.transAxes, loc='lower right') # 
    
    # harvest dynamics
    ax1.plot(HARVEST_BIOENERGY, color='mediumseagreen', alpha = 1, lw=1)
    ax1.plot(HARVEST_FOOD, color='royalblue', alpha = 1, lw=1)
    ax1.set_xlabel('Time (years)',fontsize=12)
    ax1.set_ylabel('Harvest (mt)',fontsize=12)

    # capital dynamics
    ag_capital= [ag.capital[-1] for ag in agents]
    names = np.arange(len(ag_capital))
    ax2.bar(x=names, height=ag_capital, color="maroon", linewidth = 1)
    ax2.set_xlabel('Agents',fontsize=12)
    ax2.set_ylabel('Capital (GHS)',fontsize=12)
    plt.xlim(0, len(ag_capital))
    plt.ylim(0, max(ag_capital))

    # Save the figure as png file 
    plt.savefig(os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/year_%04d.png")%time, bbox_inches='tight', pad_inches=0.1, dpi=2000) 


# In[ ]:


# update_observe()


# ### interaction with biocompanies 
# 

# In[ ]:


def update_one_unit_time():
    
    global agents, time, time1, cost_food, cost_bioenergy, yield_food, yield_bioenergy, init_price_food, init_price_bioenergy, price_food, price_bioenergy
    global num_consumers, actualhav_food, actualhav_bioenergy, per_capita_food, per_capita_bioenergy, frac_cal, total_demand_food, total_demand_bioenergy, treatment
    global CAPITAL, ACTION_FOOD, ACTION_BIOENERGY, INTERACTION_NO, INTERACTION_YES,  HARVEST_FOOD, HARVEST_BIOENERGY, LAND_FERTILITY, PRIORITY_FOOD, PRIORITY_BIOENERGY, PRIORITY_FALLOW, LAND_FOOD, LAND_BIOENERGY 
 
    time += 1  # update time
    update_interaction() # interaction with biocompanies 
    update_soil() # updating soil dynamics
    update_market() # update market dynamics
    time1.append(time) # update time
    


# In[ ]:


# update_one_unit_time()


# ### loop through functions

# In[ ]:


initialize() # initialization
# update_observe()  # observation
    
for j in range(1,27):  #bcos lagging by 2 time steps
    update_one_unit_time()
    # update_observe()

# os.system("ffmpeg -v quiet -r 5 -i /Users/kwabx/labspaces/bioenergy_landuse_conflict_model/data/work/year_%04d.png -vcodec mpeg4  -y -s:v 1920x1080 /Users/kwabx/labspaces/bioenergy_landuse_conflict_model/data/work/bioenergy_model_simulation.mp4") # convert files to a movie
# os.system("ffmpeg -v quiet -r 5 -i /home/kwabena.owusu/labspaces/bioenergy_landuse_conflict_model/data/work/year_%04d.png -vcodec mpeg4  -y -s:v 1920x1080 /home/kwabena.owusu/labspaces/bioenergy_landuse_conflict_model/data/work/bioenergy_model_simulation.mp4") # server

