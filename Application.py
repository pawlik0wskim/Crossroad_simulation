from Map import *
from utilities import *
from GUI import *
from SimulatedAnnealing import SimulatedAnnealing
class Application:   
    def __init__(self, max_iter, frames_per_car, light_cycle_time, acceleration_exponent):
        
        self.map = generate_crossroad(WIDTH, HEIGHT)
        self.max_iter = max_iter 
        self.frames_per_car = frames_per_car
        self.light_cycle_time = light_cycle_time
        self.acceleration_exponent = acceleration_exponent
        
    def reset_map(self):
        self.map = generate_crossroad(WIDTH, HEIGHT)
        
    def set_traffic_lights(self, light_cycles):
        for i in range(len(light_cycles)):
            self.map.roads_with_lights[i].light_cycle = light_cycles[i]
            
    def simulate(self, speed_limit, light_cycles, visualise = False, debug = False): 
        self.set_traffic_lights( light_cycles)
        Collisions = 0
        Flow = 0
        
        if visualise:
            win = pygame.display.set_mode((WIDTH, HEIGHT))   
            clock=pygame.time.Clock()
            # map_img = pygame.transform.scale(pygame.image.load(r"map_crossroad.png"),(WIDTH,HEIGHT)).convert()
            # map_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
            self.map.img = pygame.transform.scale(pygame.image.load(r"map_crossroad.png"),(WIDTH,HEIGHT)).convert()
            self.map.rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        start_time = time.time()
        
        i=0
        prev_flow = -1
        
        stopped = False
        FPS_counter = 0
        while(True):

            iter_start_time = time.time()
            i+=1
            
            if visualise:
                self.map.show_vehicles(win, debug)
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

        
        

speed_limit , left_prob , right_prob , light_cycle_time , simulation_length , acceleration_exponent, frames_per_car = run_gui()
app = Application(simulation_length, frames_per_car, light_cycle_time, acceleration_exponent)

light_cycles = [[0.1,0.2,0.6,0.7],[0.1,0.2,0.6,0.7],[0.1,0.2,0.6,0.7],[0.1,0.2,0.6,0.7]]
Flow, Collisions= app.simulate(speed_limit, light_cycles, visualise = True, debug = False)
app.set_traffic_lights(light_cycles)
sa = SimulatedAnnealing(100,2,1,0) 
sa.optimise(app, {"speed_limit": speed_limit, "light_cycles": light_cycles})