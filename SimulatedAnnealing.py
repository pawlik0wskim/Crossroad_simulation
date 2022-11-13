from OptimisationAlgorithm import OptimisationAlgorithm as oa
from utilities import *
import numpy as np
import time
class SimulatedAnnealing(oa):
    def __init__(self, iterations, simulation_length, step_size, initial_temp, cooling_rate = 0.99995):
        
        self.step_size = step_size
        self.temp = initial_temp
        self.cooling_rate = cooling_rate
        super().__init__(iterations, simulation_length)
    
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
    
    def optimise(self, simulation, initial_parameters, speed_limit_optimisation = True, traffic_light_optimisation = True):
        start_time = time.time()
        speed_limit, light_cycles = initial_parameters["speed_limit"], initial_parameters["light_cycles"]
        print(f"Speed:  {pixels_to_kmh(speed_limit)} km/h / {speed_limit} pix")
        Flow, Collisions, stopped, iteration = simulation.simulate(speed_limit, light_cycles) 
        simulation.reset_map()
        self.stats.append([-1,0,pixels_to_kmh(speed_limit),Flow, Collisions, stopped, iteration])
        loss_value = cost_function(Flow, Collisions, iteration, stopped)
        for i in range(self.iterations):
            new_speed_limit, new_light_cycles = self.mutate(speed_limit, light_cycles, speed_limit_optimisation, traffic_light_optimisation )
            Flow_mean, Collisions_mean = 0, 0
            print(f"Speed:  {pixels_to_kmh(new_speed_limit)} km/h / {new_speed_limit} pix")
            for j in range(3):
                Flow, Collisions, stopped, iteration = simulation.simulate(new_speed_limit, new_light_cycles) 
                simulation.reset_map()
                Flow_mean, Collisions_mean = Flow_mean + Flow/3, Collisions_mean + Collisions/3
                self.stats.append([i,j,pixels_to_kmh(new_speed_limit),Flow, Collisions, stopped, iteration])
            loss_value_new = cost_function(Flow_mean, Collisions_mean, iteration, stopped)
            simulation.reset_map()
            self.stats.append([i,None,pixels_to_kmh(new_speed_limit), Flow_mean, Collisions_mean, None, None])
            print(f"Loss value: :  {loss_value_new}")
            diff = loss_value_new - loss_value
            if diff<0  or np.random.rand()<np.exp(-diff/self.temp): 
                loss_value = loss_value_new
                speed_limit, light_cycles = new_speed_limit, new_light_cycles 
                print("______________________better______________________")
            self.temp *= self.cooling_rate
        
        print(f"Best speed:  {pixels_to_kmh(speed_limit)} km/h / {speed_limit} pix")
        time_final = time.time()-start_time
        print(f'Total time: {int(time_final//3600)}:{int((time_final-time_final//3600*3600)//60)}:{(time_final-(time_final-time_final//3600)//60*60)}')
        
a = 1  