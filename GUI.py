from tkinter import *
from  utilities import unit
import customtkinter
from RangeSlider import RangeSliderH 
import tkinter as tk

class TraficLigthsWidget:
    def __init__(self, x, y, width = 180, starting_light = "Red", starting_row = 4):
        self.x, self.y = x, y
        self.width = width
        self.starting_row = starting_row
        self.generate_lights_sliders(starting_light=starting_light)
        
        self.entries = [customtkinter.CTkEntry(width=self.width/4.5,placeholder_text=int(self.sliders[i//2].getValues()[i-i//2*2]*100)/100) for i in range(4)]
        for i in range(4):
            # self.entries[i].place(x=x+self.width/40*(i*10+1), y=self.y)
            self.entries[i].grid(row = starting_row + (self.y-30)//150, column = i+6)
        self.button = customtkinter.CTkButton(master=root, text="Refresh", command=self.button_replace_function, width=self.width/3)
        # self.button.place(x=x+self.width, y=self.y)
        self.button.grid(row = starting_row + (self.y-30)//150, column = 10, columnspan = 2)
        l0 = tk.Label(root, text='     \n   ', bg = BG_COLOR)
        l1 = tk.Label(root, text='     \n   ', bg = BG_COLOR)
        l2 = tk.Label(root, text='     \n   ', bg = BG_COLOR)
        l0.grid(column=12, row= starting_row + (self.y-30)//150)
        l2.grid(column=21, row= starting_row + (self.y-30)//150)
        l1.grid(column=5, row= starting_row + (self.y-30)//150)
        label = customtkinter.CTkLabel(root, text=f'Traffic light {(self.y-30)//150}' )
        label.grid(column=0, row= starting_row + (self.y-30)//150, columnspan = 4)
        
    def generate_lights_sliders(self, values=[1/6,1/3], values2=[2/3,5/6], starting_light = "Red"):
        color1, color2 = ("Red", "Green") if starting_light == "Red" else ("Green", "Red")
        sliders = []
        sliders.append(RangeSliderH(root, [DoubleVar(), DoubleVar()], Width=self.width, Height=24, min_val=0, max_val=1/2, show_value= True, padX=11, bgColor=BG_COLOR, font_size =1, right_color=color1, left_color=color2, values = values))
        sliders.append(RangeSliderH(root, [DoubleVar(), DoubleVar()], Width=self.width, Height=24, min_val=1/2, max_val=1, show_value= True, padX=11, bgColor=BG_COLOR, font_size =1, right_color=color2, left_color=color1, values = values2))
        for i in range(2):
            #sliders[i].place(x=self.x+self.width*(i+1.4),y=self.y)
            sliders[i].grid(row = self.starting_row + (self.y-30)//150, column = 13+i*4, columnspan = 4)
        self.sliders = sliders
        
    
    def button_replace_function(self):
        self.generate_lights_sliders( values = [float(self.entries[0].entry.get()), float(self.entries[1].entry.get())], values2 = [float(self.entries[2].entry.get()), float(self.entries[3].entry.get())])
    
    def get_values(self):
        values = []
        for i in range(2):
            value = self.sliders[i].getValues()
            values.append(value[0])
            values.append(value[1])
        return values
        
def button_function(modules):
        print("button pressed")
        for module in modules:
            print(module.get_values())
        

    




def on_closing():
    root.destroy()
    
def optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)   
            
BG_COLOR = "#212325"        
def run_gui():
    global rs1, rs2, entry, entry2, entry3, entry4, Width
    global traffic_light_data, traffic_light_labels, mode, speed_limit, speed_limit_label, debug_checkbutton, visualise_btn, optimise_btn, root
    # Create object 
    customtkinter.set_default_color_theme("blue")
    customtkinter.set_appearance_mode("Dark")
    root = customtkinter.CTk()
    
    # Adjust size
    root.geometry("720x720")
    l0 = tk.Label(root, bg=BG_COLOR)
    l0.grid(column=0, row=3, columnspan=21)
    l1 = tk.Label(root, bg=BG_COLOR)
    l1.grid(column=0, row=0, columnspan=21)
    l2 = tk.Label(root, bg=BG_COLOR)
    l2.grid(column=0, row=8, columnspan=21)
    ligths = [TraficLigthsWidget(30,30+150*i) for i in range(4)]
    
    button = customtkinter.CTkButton(master=root, text="CTkButton", command=lambda: button_function(ligths))
    # button.place(relx=0.5, rely=0.9, anchor=customtkinter.CENTER)
    button.grid(sticky = "s", row =11, column =8, columnspan = 4)
    options = [
        "visualisation",
        "genetic algorithm",
        "simulated annealing"
    ]
    drop = customtkinter.CTkOptionMenu(root  ,values = options,command=optionmenu_callback)
    drop.grid(column = 8, row = 1, columnspan =5, sticky = "n")
    
    root.mainloop()
    # # Tkinter variables  
    # mode = StringVar()
    # mode.set( "visualisation" )
    # mode.trace("w", alter_widgtes)

    # debug = BooleanVar()
    
    # # Tkinter widgets
    # options = [
    #     "genetic algorithm",
    #     "simulated annealing",
    #     "visualisation"
    # ]
    # drop = OptionMenu(root , mode , *options)
    # drop.place(relx=0.4, rely=0.1)

    # debug_checkbutton = Checkbutton(root,
    #                                 text='Debug mode',
    #                                 variable=debug,
    #                                 onvalue=True,
    #                                 offvalue=False)
    

    # # simulation widgets
    # traffic_light_data = [[Entry(root, width=5) for i in range(4)] for j in range(4)]
    # traffic_light_labels = [Label(root, text='traffic light '+str(i+1)) for i in range(4)]
    # speed_limit = Entry(root, width=5)
    # speed_limit_label = Label(root, text="Speed limit")
    # visualise_btn = Button(root, text ="Visualise", command = visualise)

    # # optimisation widgets
    # optimise_btn = Button(root, text ="Optimise", command = optimise)
    
    # show_simulation_data()
    # root.protocol("WM_DELETE_WINDOW", on_closing)
    # root.mainloop()
    speed_limit , left_prob , right_prob , light_cycle_time , simulation_length , acceleration_exponent, frames_per_car = 10, 0.1, 0.2, 300, 10000, 4, 10
    return speed_limit * unit , left_prob , right_prob , light_cycle_time , simulation_length , acceleration_exponent, frames_per_car
    

run_gui()

