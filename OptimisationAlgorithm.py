import numpy as np

class OptimisationAlgorithm:
    def __init__(self, iterations, simulation_length):
        self.iterations = iterations
        self.simulation_length = simulation_length
        self.stats = []
    def visualise_learning(self):
        pass
    def optimise(self, simulation):
        pass
    def mutate(self, speed_limit, light_cycles, speed_limit_optimisation , traffic_light_optimisation ):
        new_speed_limit, new_light_cycles = speed_limit, light_cycles
        p = np.random.rand()
        p=0
        parameter_number = len(light_cycles[0])*len(light_cycles)+1
        if p<1/parameter_number or 1-traffic_light_optimisation:
            new_speed_limit+=np.random.normal(0,self.step_size)
        for i in range(parameter_number-1):
            if p<1/parameter_number*(i+2) and p>1/parameter_number*(i+1):
                new_light_cycles[i//len(new_light_cycles)][i-i//len(new_light_cycles)*len(new_light_cycles)]+=np.random.normal()
        return new_speed_limit, new_light_cycles