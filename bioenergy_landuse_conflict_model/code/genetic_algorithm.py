#!/usr/bin/env python
# coding: utf-8

# ## Genetic algorithm to calibrate parameters ##

# ### fitness function ###

# In[ ]:


# remember to comment-out the parameters you calibrating in the main bioenergy model / run loop for only 7 time steps

# In[1]:


def cal_pop_fitness(pop):
    # Calculating the fitness value of each solution in the current population.
    global cost_bioenergy, yield_bioenergy, init_price_bioenergy, total_demand_bioenergy                      
    
    numsim = 3 # number of replicates simulation
    FITNESS = [] #  to contain average  of replicates fitness 
    realdat =[2306000, 2900000, 3032000, 3203000, 3401000] # real maize production (metric tonnes) data in Ghana 2018-2022 (remember to run the bioenergy model to time=7)
    realdat=[0.22*s for s in realdat] # real maize production (metric tonnes) data in Brong-AAhafo (set at 22% * national production) 2018-2022
    
    for solution in range(pop.shape[0]): 
        
        # create folder within 'generation dat' folder to contain solution data
        folder_sol = 'solution_' + str(solution)
        folder_sol = os.path.join(folder_gen,folder_sol)
        os.makedirs(folder_sol)
        
        # assign parameters of interest 
        cost_bioenergy = pop[solution,0] # cost of producing bioenergy crop 
        yield_bioenergy = pop[solution,1] # bioenergy yield 
        init_price_bioenergy = pop[solution,2] # initial bioenergy price
        total_demand_bioenergy = pop[solution,3] # total_demand for bioenergy
        
        rep_fitness = [] # to contain fitness of replicates
        
        # open a file to write to-
        outfname = 'simdat' + '.csv' 
        folder_rep=os.path.join(folder_sol, outfname)
        with open(folder_rep, 'w') as outfile:
            allsimdat = csv.writer(outfile)
             
            for rep in range(numsim):
                exec(open(os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/code/Bioenergy_Landuse_Conflict_Model.py")).read(),globals()) # execute the main script
                read_simdat = pd.read_csv(os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/bioenergy_model_simulation.csv")) # read simulation data
                simdat = read_simdat.harvest_food.tolist() # convert csv column(harvest food) to list
                simdat = simdat[1:] # remove time zero value (bcos it contain initialization value)
                MSE = np.square(np.subtract(realdat,simdat)).mean() 
                RMSE = math.sqrt(MSE) # compute the root mean square error
                rep_fitness.append(RMSE)
                
                # read the simulation output, and append replicate number
                with open(os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/bioenergy_model_simulation.csv"), 'r') as csvfile:
                    onesimdat = csv.reader(csvfile, delimiter=',')
                    header = next(onesimdat)
                    header.append('NoSim')
                    if rep==0:
                        allsimdat.writerow(header)
                    for row in onesimdat:
                        row.append(str(rep))
                        allsimdat.writerow(row)

            FITNESS.append(statistics.mean(rep_fitness))
    return FITNESS


# ### parents selection function ###

# In[2]:


def select_mating_pool(pop, fitness, num_parents):
    # Selecting the best individuals in the current generation as parents for producing the offspring of the next generation based on fitness
    parents = np.empty((num_parents, pop.shape[1]))
    for parent_num in range(num_parents):
        max_fitness_idx = np.where(fitness == np.min(fitness)) # index of solution in population (bcos fitness index aligns with pop index) with best/lowest RMSE
        max_fitness_idx = max_fitness_idx[0][0] # get index as number from array structure
        parents[parent_num, :] = pop[max_fitness_idx, :] # place the solurtion with best/lowest fitness in the parent array
        fitness[max_fitness_idx] = 1000e100 # so that it cant be selected again as the solution lowest RMSE
    return parents


# ### crossover function ###

# In[3]:


def crossover(parents, offspring_size):
    offspring = np.empty(offspring_size)
    # The point at which crossover takes place between two parents. Usually it is at the center.
    crossover_point = np.uint8(offspring_size[1]/2)

    for k in range(offspring_size[0]):
        # Index of the first parent to mate.
        parent1_idx = k%parents.shape[0]
        # Index of the second parent to mate.
        parent2_idx = (k+1)%parents.shape[0]
        # The new offspring will have its first half of its genes taken from the first parent.
        offspring[k, 0:crossover_point] = parents[parent1_idx, 0:crossover_point]
        # The new offspring will have its second half of its genes taken from the second parent.
        offspring[k, crossover_point:] = parents[parent2_idx, crossover_point:]
    return offspring


# ### mutation function ###

# In[ ]:


def mutation(offspring_crossover,input_limits):
    # Mutation changes a single gene in each offspring randomly.
    mutate_offspring_crossover = np.random.uniform(input_limits[0], input_limits[1], size=offspring_crossover.shape)
    for idx in range(offspring_crossover.shape[0]):
        # The random value to be added to the gene
        random_value=np.random.choice(np.arange(0, offspring_crossover.shape[1]))
        offspring_crossover[idx, random_value] =  mutate_offspring_crossover[idx, random_value] 
    return offspring_crossover


# ### execute functions for genetic algorithm (GA) ##

# In[ ]:


# import necessary libraries
import shutil, os
import numpy as np
import pandas as pd
import math
from math import atan2
import random
import statistics
import csv

sol_per_pop = 20  # number of solutions per population 
num_parameters = 4 # number of parameters 
pop_size = (sol_per_pop,num_parameters) # population size. The population will have sol_per_pop chromosome where each chromosome has num_parameters genes.
selection_rate = 0.5 # fraction selected from a population as parents for mating
num_parents_mating = math.floor(selection_rate * sol_per_pop) # number of individuals selected to mate on each iteration

#tuple containing the minimum and maximum allowed parameters.
input_limits = (         # minimum values of bioenergy crop
                (300,  # bioenergy cost
                 1,  # bioenergy yield
                 600 , # bioenergy initial price
                 5e6)    # total_demand_bioenergy - set at 0.5% of food
                 ,
                       # maximum values of bioenergy crop
                (6000,  # bioenergy cost
                 4,    # bioenergy yield
                 3000,   # bioenergy initial price
                 111e6 )    # total_demand_bioenergy - 10% of food 
               )
                        
## create folder to contain calibration data
folder_cal = os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work")
folder_cal = os.path.join(folder_cal, 'genetic_calibration_data')
if os.path.exists(folder_cal):
    shutil.rmtree(folder_cal) # delete directory
os.makedirs(folder_cal) # create directory

#Creating the initial population.
new_population = np.random.uniform(input_limits[0], input_limits[1], size=pop_size)
# print(new_population)

num_generations = 1000
for generation in range(num_generations):
    
    # create folder within 'genetic_calibration_data' folder to contain generation data
    folder_gen = 'generation_' + str(generation)
    folder_gen = os.path.join(folder_cal,folder_gen)
    os.makedirs(folder_gen)
    
    # Measing the fitness of each solution in the population.
    fitness = cal_pop_fitness(new_population)
    COPY_fitness= fitness.copy() # to print
    #print(COPY_fitness)

    # Selecting the best parents in the population for mating.
    parents = select_mating_pool(new_population, fitness, num_parents_mating)
    #COPY_parents= parents.copy() # to print
    #print(COPY_parents)

    # Generating next generation using crossover.
    offspring_crossover = crossover(parents, offspring_size=(pop_size[0]-parents.shape[0], num_parameters))

    # Adding some variations to the offsrping using mutation.
    offspring_mutation = mutation(offspring_crossover,input_limits)

    #Create a csv file of population, fitness, and generation
    fitness_array=np.array(COPY_fitness).reshape(new_population.shape[0],1) # change fitness from list to array and shape to fit population
    new_population_array = np.append(new_population,fitness_array, axis=1) #append the new array fitness to population
    new_population_array = np.insert(new_population_array,0,generation, axis=1) #insert generation number to column 0 of population

    head = ['GENERATION', 'COST_FOOD', 'YIELD_BIOENERGY', 'INIT_PRICE_BIOENERGY' ,'AMOUNT_DEMAND_BIOENERGY', 'FITNESS']
    header = np.array(head)
    
    if generation==0:
        with open(os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/genetic_calibration.csv"), 'w') as csvfile:
            write = csv.writer(csvfile)
            write.writerow(header) # header only on generation zero
            write.writerows(new_population_array)
    else :
        with open(os.path.expanduser("~/labspaces/bioenergy_landuse_conflict_model/data/work/genetic_calibration.csv"), 'a') as csvfile:
            write = csv.writer(csvfile)
            write.writerows(new_population_array)
 
    # Creating the new population based on the parents and offspring.
    new_population[0:parents.shape[0], :] = parents
    new_population[parents.shape[0]:, :] = offspring_mutation

    # The best result in the current iteration.
    print("Best solution in generation %i is"%(generation), new_population[0,:]) # bcos the first row of parents has the most minimum fitness
    #print("Best solution fitness in generation %i is"%(generation), np.min(COPY_fitness))


# In[ ]:




