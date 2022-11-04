from tkinter import *
from  utilities import unit

def alter_widgtes(*args):
    if mode.get() == "visualisation":
        hide_optimisation_data()
        show_simulation_data()
    else:
        hide_simulation_data()
        show_optimisation_data()

def show_simulation_data():
    y = 0.25
    for i in range(len(traffic_light_data)):
        
        traffic_light_labels[i].place(relx=0.1, rely=y)
        x = 0.3
        for e in traffic_light_data[i]:
            e.place(relx=x, rely=y)
            x += 0.1
        y += 0.1
    
    speed_limit.place(relx=0.3, rely=0.65)
    speed_limit_label.place(relx=0.1, rely=0.65)
    debug_checkbutton.place(relx=0.3, rely=0.8)
    visualise_btn.place(relx=0.45, rely=0.9)

def hide_simulation_data():
    for i in range(len(traffic_light_data)):
        traffic_light_labels[i].place_forget()
        for e in traffic_light_data[i]:
            e.place_forget()

    speed_limit.place_forget()
    speed_limit_label.place_forget()
    debug_checkbutton.place_forget()
    visualise_btn.place_forget()

def show_optimisation_data():
    optimise_btn.place(relx=0.45, rely=0.9)

def hide_optimisation_data():
    optimise_btn.place_forget()

def visualise():
    pass

def optimise():
    pass

def on_closing():
    root.destroy()
    
        
        
        
def run_gui():
    global traffic_light_data, traffic_light_labels, mode, speed_limit, speed_limit_label, debug_checkbutton, visualise_btn, optimise_btn, root
    # Create object
    root = Tk()
    
    # Adjust size
    root.geometry("500x500")
    

    # Tkinter variables  
    mode = StringVar()
    mode.set( "visualisation" )
    mode.trace("w", alter_widgtes)

    debug = BooleanVar()
    
    # Tkinter widgets
    options = [
        "genetic algorithm",
        "simulated annealing",
        "visualisation"
    ]
    drop = OptionMenu(root , mode , *options)
    drop.place(relx=0.4, rely=0.1)

    debug_checkbutton = Checkbutton(root,
                                    text='Debug mode',
                                    variable=debug,
                                    onvalue=True,
                                    offvalue=False)
    

    # simulation widgets
    traffic_light_data = [[Entry(root, width=5) for i in range(4)] for j in range(4)]
    traffic_light_labels = [Label(root, text='traffic light '+str(i+1)) for i in range(4)]
    speed_limit = Entry(root, width=5)
    speed_limit_label = Label(root, text="Speed limit")
    visualise_btn = Button(root, text ="Visualise", command = visualise)

    # optimisation widgets
    optimise_btn = Button(root, text ="Optimise", command = optimise)
    
    show_simulation_data()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
    speed_limit , left_prob , right_prob , light_cycle_time , simulation_length , acceleration_exponent, frames_per_car = 5, 0.1, 0.2, 300, 10000, 4, 30
    return speed_limit * unit , left_prob , right_prob , light_cycle_time , simulation_length , acceleration_exponent, frames_per_car
    




