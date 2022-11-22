import numpy as np
import copy

class OptimisationAlgorithm:
    def __init__(self, iterations, simulation_length):
        self.iterations = int(iterations)
        self.simulation_length = int(simulation_length)
        self.stats = []
    def visualise_learning(self):
        pass
    def optimise(self, simulation):
        pass
    #Returns randomly changed input parameters
    def mutate(self, speed_limit, light_cycles, speed_limit_optimisation = True , traffic_light_optimisation = True ):
        new_speed_limit, new_light_cycles = speed_limit, copy.deepcopy(light_cycles)
        p = np.random.rand()
        parameter_number = len(light_cycles[0])*len(light_cycles)+1
        if ( p<1/parameter_number or 1-traffic_light_optimisation) and speed_limit_optimisation:
            new_speed_limit+=np.random.normal(0,2)
        
        if ( p<1/parameter_number and 1-speed_limit_optimisation):
            parameter_number-=1
        
        for i in range(parameter_number-1):
            if p<1/parameter_number*(i+2) and p>1/parameter_number*(i+1) and traffic_light_optimisation:
                prev_value = new_light_cycles[i//len(new_light_cycles)][i-i//len(new_light_cycles)*len(new_light_cycles)]
                new_value = np.random.rand()/2+1/2 if prev_value>1/2 else np.random.rand()/2
                new_light_cycles[i//len(new_light_cycles)][i-i//len(new_light_cycles)*len(new_light_cycles)]=new_value
                
        return new_speed_limit, new_light_cycles