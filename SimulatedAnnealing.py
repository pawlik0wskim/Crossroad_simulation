from OptimisationAlgorithm import OptimisationAlgorithm as oa
from utilities import *
import numpy as np
import time
class SimulatedAnnealing(oa):
    def __init__(self, iterations, simulation_length, speed_limit_optimization, traffic_light_optimization, initial_temp, cooling_rate):
        
        self.temp = initial_temp
        self.cooling_rate = cooling_rate
        super().__init__(iterations, simulation_length, speed_limit_optimization, traffic_light_optimization)
    
    
    
    def optimise(self, simulation, initial_parameters):
        start_time = time.time()
        speed_limit, light_cycles = initial_parameters["speed_limit"], initial_parameters["light_cycles"]
        print(f"Speed:  {pixels_to_kmh(speed_limit)} km/h / {speed_limit} pix")
        Flow, Collisions, stopped, iteration = simulation.simulate(speed_limit, light_cycles) 
        simulation.reset_map()
        stat = [-1,0,pixels_to_kmh(speed_limit)]
        for light in light_cycles:
            stat+=light
        stat += [ Flow, Collisions, stopped, iteration]
        self.stats.append(stat)
        loss_value = cost_function(Flow, Collisions, iteration, stopped)
        for i in range(int(self.iterations)):
            new_speed_limit, new_light_cycles = self.mutate(speed_limit, light_cycles)
            Flow_mean, Collisions_mean = 0, 0
            print(f"Speed:  {pixels_to_kmh(new_speed_limit)} km/h / {new_speed_limit} pix")
            for j in range(3):
                Flow, Collisions, stopped, iteration = simulation.simulate(new_speed_limit, new_light_cycles, sim = j, sim_max = 3, it=i, iter_max = self.iterations) 
                simulation.reset_map()
                Flow_mean, Collisions_mean = Flow_mean + Flow/3, Collisions_mean + Collisions/3
                stat = [i,j,pixels_to_kmh(new_speed_limit)]
                for light in light_cycles:
                    stat+=light
                stat += [ Flow, Collisions, stopped, iteration]
                self.stats.append(stat)
            loss_value_new = cost_function(Flow_mean, Collisions_mean, iteration, stopped)
            simulation.reset_map()
            stat = [i,None,pixels_to_kmh(new_speed_limit)]
            for light in light_cycles:
                stat+=light
            stat += [ Flow_mean, Collisions_mean, None, None]
            self.stats.append(stat)
            print(f"Loss value: :  {loss_value_new}")
            diff = loss_value_new - loss_value
            if diff<0  or np.random.rand()<np.exp(-diff/self.temp): 
                loss_value = loss_value_new
                speed_limit, light_cycles = new_speed_limit, new_light_cycles 
                print("______________________better______________________")
            self.temp *= self.cooling_rate
        
        print(f"Best speed:  {pixels_to_kmh(speed_limit)} km/h / {speed_limit} pix")
        print(f"Best light cycles:  {light_cycles} ")
        time_final = time.time()-start_time
        print(f'Total time: {int(time_final//3600)}:{int((time_final-time_final//3600*3600)//60)}:{(time_final-(time_final-time_final//3600)//60*60)}')
        
