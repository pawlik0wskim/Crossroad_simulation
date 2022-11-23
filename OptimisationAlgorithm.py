import numpy as np
from copy import deepcopy

class OptimisationAlgorithm:
    def __init__(self, iterations, simulation_length, speed_limit_optimization, traffic_light_optimization):
        self.iterations = int(iterations)
        self.simulation_length = int(simulation_length)
        self.stats = []
        self.speed_limit_optimization = speed_limit_optimization
        self.traffic_light_optimization = traffic_light_optimization
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