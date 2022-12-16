import numpy as np
from copy import deepcopy
from csv import writer
from utilities import seconds_to_dhm
from datetime import datetime
from utilities import pixels_to_kmh
import json

class OptimizationAlgorithm:
    def __init__(self, iterations, simulation_length, speed_limit_optimization, traffic_light_optimization):
        # number of iterations of optimization algorithm
        self.iterations = int(iterations)
        self.simulation_length = int(simulation_length)
        self.stats = []
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # name of file, where stats will be saved
        self.stats_file = 'stats_' + timestamp + '.csv'
        # name of file, where champions will be saved
        self.champions_file = 'champions_' + timestamp + '.json'
        # boolean flag which shows if speed limit is optimised
        self.speed_limit_optimization = speed_limit_optimization
        # boolean flag which shows if traffic lights are optimised
        self.traffic_light_optimization = traffic_light_optimization
        # time elapsed since beginning of simulation
        self.elapsed_time = 0
        # list of not dominated(in Pareto sense) units
        self.champions = []
        # list of statistics(Flow, Collisions) of not dominated units
        self.champions_stats = []
    
    def visualise_learning(self):
        pass
    
    def optimise(self, simulation):
        pass

    def save_champions(self):
        for i in range(len(self.champions)):
            self.champions[i]["flow"] = self.champions_stats[i][0]
            self.champions[i]["collisions"] = -self.champions_stats[i][1]
            self.champions[i]["speed_limit"] = pixels_to_kmh(self.champions[i]["speed_limit"])
        with open(self.champions_file, "w") as fp:
            json.dump(self.champions, fp)
            fp.close()
    
    #Returns randomly changed input parameters
    def mutate(self, speed_limit, light_cycles):
        new_speed_limit = speed_limit
        p = np.random.rand()
        parameter_number = len(light_cycles[0])*len(light_cycles)+1
        if ( p<1/parameter_number or 1-self.traffic_light_optimization) and self.speed_limit_optimization:
            new_speed_limit+=np.random.normal(0,2)
        
        if (1-self.speed_limit_optimization):
            parameter_number-=1
        new_light_cycles = self.mutate_parameter(p, parameter_number, light_cycles) if np.random.uniform(0, 1) < 0.5 else self.mutate_shift(light_cycles)
                
        return round(new_speed_limit), np.around(new_light_cycles, 2).tolist()
    
    def mutate_parameter(self, p, parameter_number, light_cycles):
        new_light_cycles = deepcopy(light_cycles)
        for i in range(len(light_cycles[0])*len(light_cycles)):
            if p<1/parameter_number*(i+1) and p>=1/parameter_number*i and self.traffic_light_optimization:
                prev_value = light_cycles[i//len(light_cycles)][i-i//len(light_cycles)*len(light_cycles)]
                new_value = np.random.rand()/2+1/2 if prev_value>1/2 else np.random.rand()/2
                new_light_cycles[i//len(new_light_cycles)][i-i//len(new_light_cycles)*len(new_light_cycles)]=new_value
                break
        return new_light_cycles
        
    
    def mutate_shift(self, light_cycles):
        light_cycles_new = deepcopy(light_cycles)
        n = np.random.randint(len(light_cycles))
        traffic_light = light_cycles[n]
        shift = np.random.uniform(0, 1)
        traffic_light_new = [traffic_light[i] + shift if traffic_light[i] + shift <= 1 else  traffic_light[i] + shift - 1 for i in range(len(light_cycles[0]))]
        light_cycles_new[n] = traffic_light_new
        return light_cycles_new

    # saves statistics from self.stats to log file
    def save_stats(self):
        with open(self.stats_file, 'a') as f:
            writer_object = writer(f, lineterminator='\n')
            writer_object.writerows(self.stats)
        
            f.close()
    
    def update_estimated_duration(self, duration_label, estimated_duration):
        dhm = seconds_to_dhm(estimated_duration)
        unit = [[' day ', ' days '], [' hour ', ' hours '], [' minute ', ' minutes ']]
        duration_text = 'Estimated duration: '
        all_zero = True
        for k in range(3):
            if dhm[k] != 0:
                duration_text += str(dhm[k]) + unit[k][int(dhm[k] > 1)]
                all_zero = False
        if all_zero:
            duration_text += 'less than 1 minute'
        duration_label.configure(text=duration_text)