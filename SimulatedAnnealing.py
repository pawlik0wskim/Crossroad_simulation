from OptimizationAlgorithm import OptimizationAlgorithm as oa
from utilities import *
import numpy as np
import time
import json

class SimulatedAnnealing(oa):
    def __init__(self, iterations, simulation_length, speed_limit_optimization, traffic_light_optimization, initial_temp, cooling_rate):
        
        self.temp = initial_temp
        self.cooling_rate = cooling_rate #rate of temperature decrease
        super().__init__(iterations, simulation_length, speed_limit_optimization, traffic_light_optimization)
        self.stats_file = 'annealing_' + self.stats_file
        self.champions_file = 'annealing_' + self.champions_file
    
    
    #main optimization method
    def optimise(self, simulation, text, opt_progress, sim_progress, duration_label, initial_parameters):
        speed_limit, light_cycles = initial_parameters["speed_limit"], initial_parameters["light_cycles"]
        
        #Create column names for future stats file
        cols = ["Main index", "Small index", "Speed limit(km/h)"]
        for i in range(len(light_cycles)):
            for j in range(4):
                cols+=[f"Traffic light {i}_{j}"]
        cols +=["Flow", "Collisions", "Stopped", "Iterations"]
        self.stats = [cols]
        self.save_stats()
        self.stats = []
        
        #Run baseline simulation
        Flow, Collisions, stopped, iteration, elapsed_time = simulation.simulate(speed_limit, light_cycles,
                                                                   text=text, loading_bar=sim_progress) 
        
        #Analyse results, save them to stats and prepare for next simulations
        self.elapsed_time = elapsed_time
        simulation.reset_map()
        stat = [-1,0,pixels_to_kmh(speed_limit)]
        for light in light_cycles:
            stat+=light
        stat += [ Flow, Collisions, stopped, iteration]
        self.stats.append(stat)
        loss_value = cost_function(Flow, Collisions)
        
        #Create stats for the best set of parameters
        loss_best=loss_value
        self.champions.append({"light_cycles": light_cycles, "speed_limit": speed_limit})
        self.champions_stats.append([Flow, Collisions])
        
        #Main loop
        for i in range(int(self.iterations)):
            #Generate new parameters
            new_speed_limit, new_light_cycles = self.mutate(speed_limit, light_cycles)
            Flow_mean, Collisions_mean = 0, 0
            
            #Test them running 3 simulations and average the results
            for j in range(3):
                iter_conducted = 3*i + j + 1
                estimated_duration = (3*self.iterations - iter_conducted) * self.elapsed_time/iter_conducted
                self.update_estimated_duration(duration_label, estimated_duration)
                Flow, Collisions, stopped, iteration, elapsed_time = simulation.simulate(new_speed_limit, new_light_cycles, 
                                                                           sim = j, sim_max = 3, 
                                                                           it=i, iter_max = self.iterations,
                                                                           text=text, loading_bar=sim_progress) 
                simulation.reset_map()
                Flow_mean, Collisions_mean = Flow_mean + Flow/3, Collisions_mean + Collisions/3
                
                #Save data to statistics
                stat = [i,j,pixels_to_kmh(new_speed_limit)]
                for light in light_cycles:
                    stat+=light
                stat += [ Flow, Collisions, stopped, iteration]
                self.stats.append(stat)
                self.elapsed_time += elapsed_time
                
            #Analyse the results
            loss_value_new = cost_function(Flow_mean, Collisions_mean)
            simulation.reset_map()
            stat = [i,None,pixels_to_kmh(new_speed_limit)]
            for light in light_cycles:
                stat+=light
            stat += [ Flow_mean, Collisions_mean, None, None]
            self.stats.append(stat)
            diff = loss_value_new - loss_value
            #Make decision whether to make a step or not
            if diff<0  or np.random.rand()<np.exp(-diff/self.temp): 
                loss_value = loss_value_new
                speed_limit, light_cycles = new_speed_limit, new_light_cycles 
                if loss_value_new - loss_best<0:
                    loss_best=loss_value
                    self.champions[0]["speed_limit"] = new_speed_limit
                    self.champions[0]["light_cycles"] = new_light_cycles 
                    self.champions_stats[0] = [Flow_mean, Collisions_mean]
            #Update the temperature
            self.temp *= self.cooling_rate
            opt_progress['value'] = int(100*(i+1)/self.iterations)
        
        duration_label.configure(text='Finished')
        #Save stats and champion
        self.save_stats()
        self.stats = [] 
        self.save_champions() 
