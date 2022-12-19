
from tkinter import *
from  utilities import kilometers_per_hour_to_pixels
import customtkinter
from RangeSlider import RangeSliderH 
import tkinter as tk
import sys
from tkinter import messagebox
from copy import deepcopy
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)  
import numpy as np

BG_COLOR = "#212325" 

class PlotWidget:
    def __init__(self, row, entries=[0.1, 0.2, 0.6, 0.7], starting_light="Red"):
        self.entries = entries
        self.starting_light = starting_light
        self.row = row
        
    def plot(self):
        plot_data = deepcopy(self.entries)
        plot_data.append(1)
        plot_data = np.sort(plot_data)
        fig = Figure(figsize = (3,1/4))
        plot1 = fig.add_subplot(111)
        colors=["Limegreen","Gold","r","Gold"]
        
        for i in range(5):
            if self.starting_light=="Red":
                col=colors[i] if i<4 else colors[0] 
            else:
                col=colors[i+2] if i<2 else colors[i-2] 
            plot1.barh([0],plot_data[-i-1],color=col, height=1/3)
        plot1.axis('off')
        fig.set_facecolor(BG_COLOR)
        output = FigureCanvasTkAgg(fig, master = root)
        output.draw()

        # placing the canvas on the Tkinter window 
        output.get_tk_widget().grid(row = self.row, column = 13, columnspan = 8)
        
    
class TraficLigthsWidget:
    def __init__(self, x, y, width = 180, starting_light = "Red", starting_row = 4):
        self.starting_light = starting_light
        self.x, self.y = x, y
        self.width = width
        self.starting_row = starting_row
        self.plot=PlotWidget(self.starting_row + (self.y-30)//150, starting_light=starting_light) 
        
        self.entries = False
        #Add and place text entry widgets
        self.entries = [self.generate_entry(int(self.plot.entries[i]*100)/100, i+6) for i in range(4)]
            
        #Add and place refresh button   
        self.button = customtkinter.CTkButton(master=root, text="Refresh", command=self.button_replace_function, width=self.width/3)
        self.button.grid(row = starting_row + (self.y-30)//150, column = 10, columnspan = 2)
        
        #Add few empty lines to increase readibility
        l0 = tk.Label(root, text='     \n   ', bg = BG_COLOR)
        l1 = tk.Label(root, text='     \n   ', bg = BG_COLOR)
        l2 = tk.Label(root, text='     \n   ', bg = BG_COLOR)
        l0.grid(column=12, row= starting_row + (self.y-30)//150)
        l2.grid(column=21, row= starting_row + (self.y-30)//150)
        l1.grid(column=5, row= starting_row + (self.y-30)//150)
        
        #Add and place traffic light label
        label = customtkinter.CTkLabel(root, text=f'Traffic light {(self.y-30)//150}' )
        label.grid(column=0, row= starting_row + (self.y-30)//150, columnspan = 4)
        self.plot.plot()
        
    

        
    # # Method creates double range sliders representing traffic light cycle   
    # def generate_lights_sliders(self, values=[0.1,0.2], values2=[0.6,0.7], starting_light = "Red"):
    #     color1, color2 = ("Red", "Green") if starting_light == "Red" else ("Green", "Red")
    #     sliders = []
    #     sliders.append(RangeSliderH(root, [DoubleVar(), DoubleVar()], Width=self.width, Height=24, min_val=0, max_val=1/2, show_value= True, padX=11, bgColor=BG_COLOR, font_size =1, right_color=color1, left_color=color2, values = values))
    #     sliders.append(RangeSliderH(root, [DoubleVar(), DoubleVar()], Width=self.width, Height=24, min_val=1/2, max_val=1, show_value= True, padX=11, bgColor=BG_COLOR, font_size =1, right_color=color2, left_color=color1, values = values2))
    #     for i in range(2):
    #         #sliders[i].place(x=self.x+self.width*(i+1.4),y=self.y)
    #         sliders[i].grid(row = self.starting_row + (self.y-30)//150, column = 13+i*4, columnspan = 4)
    #     self.sliders = sliders
    
    #Function validating inputs provided by the user   
    def validate_function(self, val, col):
        if len(val)>1:
            i=col-6
            try:
                fl = float(val)
                if self.entries:
                    if fl>1:
                        self.entries[i].placeholder_text = "<1"
                        self.entries[i].delete(0,END)
                    elif fl<0 and (len(val)>2 or col==6):
                        self.entries[i].placeholder_text = f">0"
                        self.entries[i].delete(0,END)  
                return True
            except ValueError:
                return False
        return False
    
    #Method creating entry field in selected column with determined placeholder value
    def generate_entry(self, place_holder, col) :
        vcmd  = (root.register(lambda val: self.validate_function(val,col)),"%P")
        entry = customtkinter.CTkEntry(master=root, width=self.width/4.5,placeholder_text=place_holder, validatecommand=vcmd, validate = "key")
        entry.grid(row = self.starting_row + (self.y-30)//150, column = col)
        return entry
           
    #Method check for correctness of traffic light cycle, gives user hints how to repair input and if everything was correct updates sliders
    def button_replace_function(self):
        for i in range(len(self.entries)):
            fl =None
            try:
                fl = float(self.entries[i].entry.get())
                if fl>1:
                    self.entries[i] = self.generate_entry("<1", i+6)
                elif fl<0:
                    self.entries[i] = self.generate_entry(">0", i+6)
                elif i ==len(self.entries)-1:
                    self.plot.entries=[np.round(float(self.entries[0].entry.get()),2), np.round(float(self.entries[1].entry.get()),2), np.round(float(self.entries[2].entry.get()),2), np.round(float(self.entries[3].entry.get()),2)]
                    self.plot.plot()
            except ValueError:
                if i!=3 or 1-isinstance(fl, float):
                    self.entries[i].placeholder_text = self.plot.entries[i]
                    self.entries[i].delete(0,END)
                    
    #Returns light cycle of traffic light        
    def get_values(self):
        return self.plot.entries

#Class representing entry field and label for all variables that are singular int, float value
class EntryVariable:
    def __init__(self, row, col, text, value = "placeholder", type =int, entry_type="entry", command=None, variable=None):
        self.label = customtkinter.CTkLabel(root, text=text)
        self.label.grid(column=col, row= row, columnspan = 4)
        self.entry_type = entry_type
        self.type = type
        if entry_type == "entry":
            vcmd  = (root.register(lambda val: self.validate_function(val)),"%P")
            self.entry = customtkinter.CTkEntry(master = root, width=Width/3,placeholder_text=value, validatecommand=vcmd, validate = "key")
            self.entry.grid(column=col+4, row= row, columnspan = 1)
        elif entry_type=="check_box":
            self.entry = customtkinter.CTkCheckBox(master=root, width=Width/3, text="", command=command, variable=variable)
            self.entry.grid(column=col+4, row= row, columnspan = 1)
            self.entry.select()
        
        self.row = row
        self.col = col
        self.type_name = "int" if type == int else "float"
        
    # Method returns field value. If its incorrect False value will be returned    
    def get_values(self):
        fl = False
        if(self.entry_type=="entry" and self.entry.entry.get()=="<0,1>"):
            return False
        try:
            fl = self.type(self.entry.entry.get()) if self.entry_type=="entry" else  self.entry.get()+1
            
        except ValueError:
            self.entry = customtkinter.CTkEntry(width=Width/3,placeholder_text=f"{self.type_name}")
            self.entry.grid(column=self.col+4, row= self.row, columnspan = 1)
        if self.entry_type=="entry" and 1-fl and self.type_name == "float" and (fl<0 or fl>1):
            self.entry = customtkinter.CTkEntry(width=Width/3,placeholder_text="<0,1>")
            self.entry.grid(column=self.col+4, row= self.row, columnspan = 1)
            fl = False
        return fl
    
    #Function validating inputs provided by the user   
    def validate_function(self, val):
        try:
            if self.type==int and len(val)==0:
                return True
            fl = self.type(val)
            if (fl>1 or fl<0) and self.type == float:
                self.entry.placeholder_text = "<0,1>"
                self.entry.delete(0,END)
                
            return True
        except ValueError:
            return False
    
#Main class of Graphical User Interface        
class GUI:
    def __init__(self):
        self.lights = [TraficLigthsWidget(30,30+150*i, starting_light = "Red") if i>1 else TraficLigthsWidget(30,30+150*i, starting_light = "Green") for i in range(4)]
        self.main_modules =  self.generate_main_modules()     
        self.annealing_modules = self.generate_annealing_modules() 
        self.genetic_modules = self.generate_genetic_modules()
        self.common_optimization_modules = self.generate_common_optimization_modules()
        self.hide(self.annealing_modules)
        self.hide(self.genetic_modules)
        self.hide(self.common_optimization_modules)
        self.drop_menu = self.generate_drop_menu()
        self.button = self.generate_button()
        self.values = None
    
    #Returns submit button    
    def generate_button(self):
        button = customtkinter.CTkButton(master=root, text="Submit", command=lambda: self.get_module_values())
        button.grid(sticky = "s", row =22, column =8, columnspan = 4)  
        return button         
        
    #Hides selected modules from the user
    def hide(self,modules):
        for module in modules:
            module.label.grid_remove()
            module.entry.grid_remove()
    
    #Generates entry fields for simulated annealing mode       
    def generate_annealing_modules(self):
        initial_temp_variable = EntryVariable(16,7,"Initial temperature: ","50")
        cooling_rate_variable = EntryVariable(16,1,"Cooling rate: ","0.99", float)
        annealing_modules = [initial_temp_variable, cooling_rate_variable]
        return annealing_modules
    
    #Generates entry fields for genetic algorithm mode       
    def generate_genetic_modules(self):
        Elite_part_variable  = EntryVariable(18,1,"Elitism: ","0.3", float)
        mutation_probability_variable  = EntryVariable(16,7,"Mutation probability: ","0.2", float)
        crossover_probability_variable = EntryVariable(16,13,"Crossover probability: ","0.2", float)
        population_size_variable = EntryVariable(16,1,"Population size: ","100")
        population_number_variable = EntryVariable(18,7,"Number of populations: ","10")
        migration_part_variable = EntryVariable(18,13,"Chance of migrations: ","0.2", float)
        genetic_modules = [Elite_part_variable, mutation_probability_variable, crossover_probability_variable, population_size_variable, population_number_variable, migration_part_variable]
        return genetic_modules

    #Generates entry fields common for all optimization modes  
    def generate_common_optimization_modules(self):
        iterations_variable = EntryVariable(14,1,"Number of iterations: ","100")
        speed_check_variable = EntryVariable(14,7,"Speed limit optimization: ","0.2", float, "check_box", command=self.toggle_checkboxes)
        light_check_variable = EntryVariable(14,13,"Traffic light optimization: ","0.2", float, "check_box", command=self.toggle_checkboxes)
        common_modules = [iterations_variable, speed_check_variable, light_check_variable]
        return common_modules

    #Generates entry fields common for all modes  
    def generate_main_modules(self):
        speed_limit_variable = EntryVariable(9,1,"Speed limit(km/h): ","25")
        maximum_iter_variable = EntryVariable(9,7,"Length of simulation: ","10000")
        frames_per_car_variable = EntryVariable(9,13,"Frames per car: ","10")
        left_prob_variable = EntryVariable(11,1,"Left turn probability: ","0.1", float)
        right_prob_variable = EntryVariable(11,7,"Right turn probability: ","0.2", float)
        light_cycle_time = EntryVariable(11,13,"Length of light cycle: ","300")
        modules =[speed_limit_variable, maximum_iter_variable, frames_per_car_variable, left_prob_variable, right_prob_variable, light_cycle_time]
        return modules
    
    #Generates drop menu allowing mode changing
    def generate_drop_menu(self):
        options = [
            "visualisation",
            "genetic algorithm",
            "simulated annealing"
        ]
        drop = customtkinter.CTkOptionMenu(root  ,values = options,command=self.optionmenu_callback)
        drop.grid(column = 8, row = 1, columnspan =5, sticky = "n")
        return drop
    
    #Method controlling GUi during mode change
    def optionmenu_callback(self, choice):
        if choice=="visualisation":
            self.hide(self.annealing_modules)
            self.hide(self.genetic_modules)
            self.hide(self.common_optimization_modules)
        elif choice=="simulated annealing":
            self.hide(self.common_optimization_modules)
            self.annealing_modules = self.generate_annealing_modules()
            self.hide(self.genetic_modules)
            self.common_optimization_modules = self.generate_common_optimization_modules()
        elif choice=="genetic algorithm":
            self.hide(self.common_optimization_modules)
            self.genetic_modules = self.generate_genetic_modules()
            self.hide(self.annealing_modules)
            self.common_optimization_modules = self.generate_common_optimization_modules()
    
    #Function behind "Submit" button that collects values and destroys root if all of the values were correct       
    def get_module_values(self):
        self.values = []
        modules = self.lights + self.main_modules + self.common_optimization_modules + self.annealing_modules + self.genetic_modules
        for module in modules:
            self.values.append(module.get_values())
            print(module.get_values())
        if all(self.values):
            root.destroy()
    
    def toggle_checkboxes(self):
        if self.common_optimization_modules[1].entry.get():
            self.common_optimization_modules[2].entry.configure(state=NORMAL)
        else:
            self.common_optimization_modules[2].entry.configure(state=DISABLED)
        
        if self.common_optimization_modules[2].entry.get():
            self.common_optimization_modules[1].entry.configure(state=NORMAL)
        else:
            self.common_optimization_modules[1].entry.configure(state=DISABLED)
            
            
 
        
#Function addinng empty line to GUI(used to improve visual layer of the application)
def add_empty_line(row):
    l0 = tk.Label(root, bg=BG_COLOR)
    l0.grid(column=0, row=row, columnspan=21)

#function, which handles window closing
def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
            sys.exit()
 
 #Main gui method    
def run_gui():
    
    global  Width
    global mode, speed_limit, root
    # Create object 
    customtkinter.set_default_color_theme("blue")
    customtkinter.set_appearance_mode("Dark")
    root = customtkinter.CTk()
    Width =180
    # Adjust size
    root.geometry("1072x603")
    # Add handling of window closing
    root.protocol("WM_DELETE_WINDOW", on_closing)
    #Adding few empty rodes to improve visual effect of GUI
    for line in [0, 3, 8, 10, 12, 13, 15, 17, 20]:
        add_empty_line(line)
    
    
    gui = GUI()
    root.mainloop()
    if gui.values!=None:
        values = gui.values[:4] + [float(value) for value in gui.values[4:]]
        mode = gui.drop_menu.current_value
        speed_limit, simulation_length, frames_per_car, left_prob , right_prob, light_cycle_time, number_of_iterations, speed_limit_optimization, traffic_light_optimization, initial_temp, cooling_rate, elite_part, mutation_probability, crossover_probability, population_size, population_number, migration_part = values[4:]
        light_cycles = [values[i]for i in range(4)]
        speed_limit_optimization-=1
        traffic_light_optimization-=1
        return light_cycles, kilometers_per_hour_to_pixels(speed_limit) , left_prob , right_prob , light_cycle_time , simulation_length , frames_per_car, mode, number_of_iterations, initial_temp, cooling_rate, elite_part, mutation_probability, crossover_probability, population_size, population_number, migration_part, speed_limit_optimization, traffic_light_optimization
    return None
    
if __name__=="__main__":
    run_gui()


