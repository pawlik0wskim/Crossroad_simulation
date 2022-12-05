import numpy as np
from copy import deepcopy
from csv import writer
from utilities import seconds_to_dhm

class OptimisationAlgorithm:
    def __init__(self, iterations, simulation_length, speed_limit_optimization, traffic_light_optimization):
        self.iterations = int(iterations)
        self.simulation_length = int(simulation_length)
        self.stats = []
        self.speed_limit_optimization = speed_limit_optimization
        self.traffic_light_optimization = traffic_light_optimization
        self.elapsed_time = 0
    
    def visualise_learning(self):
        pass
    
    def optimise(self, simulation):
        pass
    
    #Returns randomly changed input parameters
    def mutate(self, speed_limit, light_cycles):
        new_speed_limit, new_light_cycles = speed_limit, deepcopy(light_cycles)
        p = np.random.rand()
        parameter_number = len(light_cycles[0])*len(light_cycles)+1
        if ( p<1/parameter_number or 1-self.traffic_light_optimization) and self.speed_limit_optimization:
            new_speed_limit+=np.random.normal(0,2)
        
        if (1-self.speed_limit_optimization):
            parameter_number-=1
        for i in range(len(light_cycles[0])*len(light_cycles)):
            if p<1/parameter_number*(i+1) and p>=1/parameter_number*i and self.traffic_light_optimization:
                prev_value = light_cycles[i//len(light_cycles)][i-i//len(light_cycles)*len(light_cycles)]
                new_value = np.random.rand()/2+1/2 if prev_value>1/2 else np.random.rand()/2
                new_light_cycles[i//len(new_light_cycles)][i-i//len(new_light_cycles)*len(new_light_cycles)]=new_value
                break
                
        return new_speed_limit, new_light_cycles
    
    # saves statistics from self.stats to log file
    def save_stats(self):
        with open('stats.csv', 'a') as f:
            writer_object = writer(f, lineterminator='\n')
            writer_object.writerows(self.stats)
        
            f.close()
    
    def update_estimated_duration(self, duration_label, estimated_duration):
        dhm = seconds_to_dhm(estimated_duration)
        tmp = [' days ', ' hours ', ' minutes ']
        duration_text = 'Estimated duration: '
        for k in range(3):
            if dhm[k] != 0:
                duration_text += str(dhm[k]) + tmp[k]
        duration_label.configure(text=duration_text)