from Controller import *
from utilities import *

from GUI import *
from SimulatedAnnealing import SimulatedAnnealing
from GeneticAlgorithm import GeneticAlgorithm
import time
from tkinter import END, NORMAL, DISABLED, messagebox
from threading import Thread
import sys
from tkinter.ttk import Progressbar

class Application:   
    def __init__(self, max_iter, frames_per_car, light_cycle_time, right_prob, left_prob, load_ratio):
        
        self.map = generate_crossroad(WIDTH, HEIGHT, load_ratio)
        self.max_iter = max_iter 
        self.frames_per_car = frames_per_car
        self.light_cycle_time = light_cycle_time
        self.right_prob, self.left_prob = right_prob, left_prob
        self.load_ratio = load_ratio
    
    #Method clears the intersection    
    def reset_map(self):
        self.map = generate_crossroad(WIDTH, HEIGHT, self.load_ratio)
    
    #Method sets traffic lights with accordance to provided light cycles    
    def set_traffic_lights(self, light_cycles):
        for i in range(len(light_cycles)):
            self.map.roads_with_lights[i].light_cycle = light_cycles[i]
    
    #Main method responsible for simulation        
    def simulate(self, speed_limit, light_cycles, text=None, loading_bar=None, visualise = False, debug = False): 
        self.set_traffic_lights( light_cycles)

        Collisions = 0
        Flow = 0
        
        if visualise:
            win = pygame.display.set_mode((WIDTH, HEIGHT))   
            clock=pygame.time.Clock()
            self.map.img = pygame.transform.scale(pygame.image.load(images_dir+"map_crossroad.png"),(WIDTH,HEIGHT)).convert()
            self.map.rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        start_time = time.time()
        
        i=0
        prev_flow = -1
        
        stopped = False
        
        while(True):
            if loading_bar is not None:
                loading_bar['value'] = int(100*i/self.max_iter)
            i+=1
            
            if visualise:
                self.map.draw(win, debug)
            for road in self.map.roads:
                

                for car in road.cars:
                    car.update_vision(road.direction, road.type, road.curve)
                    self.map.process_car_neighborhood(car, road)

            if i%self.frames_per_car == 0:
                self.map.spawn_car(speed_limit)
            
            self.map.update_traffic_lights(i, self.light_cycle_time)
            curr_flow, red_lights = self.map.move_cars( self.right_prob, self.left_prob)
            Flow+=curr_flow - 2*red_lights
            Collisions+=self.map.check_for_car_collision() + red_lights/4
            if visualise:
                pygame.display.update()
                clock.tick(FPS)
            
            if i%(30*FPS) == 0: 
                #Ends simulation if the crossroad got stuck
                if Flow == prev_flow:
                    stopped = True
                    iteration = i
                    break
                prev_flow = Flow
            iteration = i
            #Ends simulation if enough time has passed
            if i >= self.max_iter:
                break
            
        
        elapsed_time = time.time() - start_time
        if text is not None:
            text.configure(state=NORMAL)
            text.insert(END, f"Flow: {Flow}, Collisions: {Collisions}, Time: {(round(elapsed_time, 3))}, Cost: {round(cost_function(Flow, Collisions), 3)}, Stopped: {stopped}\n")
            text.configure(state=DISABLED)

        return Flow, Collisions, stopped, iteration, elapsed_time

def run_progress_gui(oa, app, init_params=None):
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if len(oa.stats) > 0:
                oa.save_stats()
            if len(oa.champions) > 0:
                if isinstance(oa, GeneticAlgorithm):
                    oa.update_champions()
                oa.save_champions()
            
            root.destroy()
            sys.exit()

    root = customtkinter.CTk()
    root.geometry("1000x500")
    root.resizable(False, False)

    duration_label = customtkinter.CTkLabel(root, text='Estimated duration: Will appear after first simulation')
    duration_label.place(relx=0.6, rely=0.04)

    sim_progress = Progressbar(root, orient=HORIZONTAL, length=100, mode='determinate')
    opt_progress = Progressbar(root, orient=HORIZONTAL, length=100, mode='determinate')

    text = Text(root, bg='#ebebeb', fg='black')
    text.configure(state=DISABLED)

    scrollbar = Scrollbar(root, orient='vertical', command=text.yview)
    scrollbar.place(relx=0.86, rely=0.2, relheight=0.71, anchor='ne')

    text['yscrollcommand'] = scrollbar.set
    text.place(relx=0.2, rely=0.2)


    opt_progress.place(relx=0.5, rely=0.05)
    customtkinter.CTkLabel(text="Optimalisation progress: ").place(relx=0.35, rely=0.04)

    sim_progress.place(relx=0.5, rely=0.1)
    customtkinter.CTkLabel(text="Current simulation: ").place(relx=0.35, rely=0.09)

    thread = Thread(target=oa.optimise, 
                    args=[app, text, opt_progress, sim_progress, duration_label, init_params],
                    daemon=True)
    root.after_idle(thread.start)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

        
if __name__=='__main__':
    
    light_cycles, speed_limit, left_prob, right_prob, light_cycle_time, load_ratio, simulation_length, frames_per_car, mode, number_of_iterations, initial_temp, cooling_rate, elite_part, mutation_probability, population_size, population_number, migration_part, speed_limit_optimization, traffic_light_optimization = run_gui()
    
    # code used for GUI validation
    values = [light_cycles, speed_limit, left_prob, right_prob, light_cycle_time, load_ratio, simulation_length, frames_per_car, mode, number_of_iterations, initial_temp, cooling_rate, elite_part, mutation_probability, population_size, population_number, migration_part, speed_limit_optimization, traffic_light_optimization]
    names = ["light_cycles", "speed_limit", "left_prob", "right_prob", "light_cycle_time", "load_ratio", "simulation_length", "frames_per_car", "mode", "number_of_iterations", "initial_temp", "cooling_rate", "elite_part", "mutation_probability", "population_size", "population_number", "migration_part", "speed_limit_optimization", "traffic_light_optimization"]
    for name, value in zip(names, values):
        print(f"{name} = {value}")

    app = Application(simulation_length, frames_per_car, light_cycle_time, right_prob, left_prob, load_ratio)

    if mode == "visualisation":
        Flow, Collisions, stopped, iteration, elapsed_time= app.simulate(speed_limit, light_cycles, visualise = True, debug = False)
        
    if mode =="simulated annealing":  
        app.set_traffic_lights(light_cycles)
        sa = SimulatedAnnealing(number_of_iterations, simulation_length, speed_limit_optimization, traffic_light_optimization, initial_temp, cooling_rate) 
        run_progress_gui(sa, app, {"speed_limit": speed_limit, "light_cycles": light_cycles})
        
    if mode == "genetic algorithm":
        ga = GeneticAlgorithm(number_of_iterations, simulation_length, 
                              speed_limit_optimization, traffic_light_optimization,
                              elite_part=elite_part, 
                              population_size=population_size, 
                              traffic_lights=light_cycles, 
                              speed_limit=speed_limit, 
                              mutation_probability=mutation_probability, 
                              population_number=population_number,
                              migration_part=migration_part) 
        run_progress_gui(ga, app)

