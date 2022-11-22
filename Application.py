from Controller import *
from utilities import *

from GUI import *
from SimulatedAnnealing import SimulatedAnnealing
from GeneticAlgorithm import GeneticAlgorithm
import pandas as pd
from datetime import datetime
import time


class Application:   
    def __init__(self, max_iter, frames_per_car, light_cycle_time, acceleration_exponent):
        
        self.map = generate_crossroad(WIDTH, HEIGHT)
        self.max_iter = max_iter 
        self.frames_per_car = frames_per_car
        self.light_cycle_time = light_cycle_time
        self.acceleration_exponent = acceleration_exponent
    
    #Method clears the intersection    
    def reset_map(self):
        self.map = generate_crossroad(WIDTH, HEIGHT)
    
    #Method sets traffic lights with accordance to provided light cycles    
    def set_traffic_lights(self, light_cycles):
        for i in range(len(light_cycles)):
            self.map.roads_with_lights[i].light_cycle = light_cycles[i]
    
    #Main method responsible for simulation        
    def simulate(self, speed_limit, light_cycles, visualise = False, debug = False, sim=0,sim_max = 0, it=0, iter_max=0): 
        self.set_traffic_lights( light_cycles)

        Collisions = 0
        Flow = 0
        
        if visualise:
            win = pygame.display.set_mode((WIDTH, HEIGHT))   
            clock=pygame.time.Clock()
            self.map.img = pygame.transform.scale(pygame.image.load(r"map_crossroad.png"),(WIDTH,HEIGHT)).convert()
            self.map.rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        start_time = time.time()
        
        i=0
        prev_flow = -1
        
        stopped = False
        FPS_counter = 0
        
        while(True):
            bar="-"*int(40*i/self.max_iter)+"_"*int(40*(self.max_iter-i)/self.max_iter)
            print(f'_____Iteration: [{it}/{iter_max}]_______Simulation: {sim}/{sim_max}_______[{bar}]_{int(100*i/self.max_iter)}%__', end='\r')
            iter_start_time = time.time()
            i+=1
            
            if visualise:
                self.map.draw(win, debug)
            for road in self.map.roads:
                

                for car in road.cars:
                    car.update_vision(road.direction, road.type, road.curve)
                    self.map.process_car_neighborhood(car, road)

            if i%frames_per_car == 0:
                self.map.spawn_car(speed_limit, self.acceleration_exponent)
            
            self.map.update_traffic_lights(i, light_cycle_time)
            Flow+=self.map.move_cars( right_prob, left_prob)
            Collisions+=self.map.check_for_car_collision()
            if visualise:
                pygame.display.update()
                clock.tick(FPS)

            elapsed_time = time.time() - start_time
            
            if i%600*FPS == 0:
                if (iter_start_time-time.time())!=0:
                    FPS_counter = -1/(iter_start_time-time.time())
                # print(f"Flow: {Flow}, Collisions: {Collisions}, Time: {(elapsed_time)}, Cost: {cost_function(Flow, Collisions, i)}, FPS: {-1/(iter_start_time-time.time())}")
                if Flow == prev_flow:
                    stopped = True
                    iteration = i
                    break
                prev_flow = Flow
            #Ends simulation if enough time has passed or if the crossroad got stuck
            if i >= self.max_iter:
                break
            iteration = i
            
        print(f"Flow: {Flow}, Collisions: {Collisions}, Time: {(elapsed_time)}, Cost: {cost_function(Flow, Collisions, i, stopped)}, FPS: {FPS_counter}, Stopped: {stopped}")    
        return Flow, Collisions, stopped, iteration

        

        
if __name__=='__main__':
    
    light_cycles, speed_limit , left_prob , right_prob , light_cycle_time , simulation_length , frames_per_car, mode, number_of_iterations, initial_temp, cooling_rate, number_of_iterations_gen, elite_part, mutation_probability, crossover_probability, population_size, population_number, migration_part = run_gui()
    acceleration_exponent = 4
    app = Application(simulation_length, frames_per_car, light_cycle_time, acceleration_exponent)


    if mode == "visualisation":
        Flow, Collisions, stopped, iteration= app.simulate(speed_limit, light_cycles, visualise = True, debug = False)
        
    if mode =="simulated annealing"  :  
        app.set_traffic_lights(light_cycles)
        sa = SimulatedAnnealing(number_of_iterations, simulation_length, initial_temp, cooling_rate) 
        sa.optimise(app, {"speed_limit": kilometers_per_hour_to_pixels(speed_limit), "light_cycles": light_cycles})
        df = pd.DataFrame(sa.stats)
        cols = ["main_index", "small_index", "Speed limit(km/h)"]
        for i in range(len(light_cycles)):
            for j in range(4):
                cols+=[f"Traffic light {i}_{j}"]
        cols +=["Flow", "Collisions", "Stopped", "Iterations"]
        df.columns = cols
        print(df)
        time_ = datetime.now().strftime("%H-%M-%S")
        df.to_csv(f"{time_}.csv")
        
    if mode == "genetic algorithm":
        app.set_traffic_lights(light_cycles)
        ga = GeneticAlgorithm(number_of_iterations_gen, simulation_length, 
                              elite_part=elite_part, 
                              population_size=population_size, 
                              traffic_lights=light_cycles, 
                              speed_limit=speed_limit, 
                              crossover_probability=crossover_probability, 
                              mutation_probability=mutation_probability, 
                              population_number=population_number,
                              migration_part=migration_part) 
        ga.optimise(app)

        df = pd.DataFrame(ga.stats)
        cols = ["Main index", "Population", "Unit", "Small Index", "Speed limit(km/h)"]
        for i in range(len(light_cycles)):
            for j in range(4):
                cols+=[f"Traffic light {i}_{j}"]
        cols +=["Flow", "Collisions", "Stopped", "IterNum"]
        df.columns = cols
        print(df)
        time_ = datetime.now().strftime("%H-%M-%S")
        df.to_csv(f"{time_}.csv", index=False)

