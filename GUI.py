import tkinter as tk

# Graphical User Interface class

class GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        w, h = 1000, 500
        self.geometry(str(w) + 'x' + str(h))

        # tracing variables  
        self.mode = tk.StringVar()
        self.mode.set("visualisation")
        # call alter_widgets method any time the value of mode variable was changed
        self.mode.trace("w", self.alter_widgtes)
        self.debug = tk.BooleanVar()

        # main widgets
        options = [
            "genetic algorithm",
            "simulated annealing",
            "visualisation"
        ]
        self.drop = tk.OptionMenu(self, self.mode, *options)
        self.drop.place(relx=0.4, rely=0.1)
        self.submit = tk.Button(self, text="Visualise", command=self.press_submit)
        self.submit.place(relx=0.45, rely=0.9)

        # simulation widgets
        self.traffic_light_widgets = [[tk.Scale(self, from_=0.0, to=1.0, orient='horizontal', resolution=0.1) for i in range(4)] for j in range(4)]
        self.traffic_light_labels = [tk.Label(self, text='traffic light '+str(i+1)) for i in range(4)]
        self.speed_limit = tk.Scale(self, from_=0.0, to=100.0, orient='horizontal', resolution=1)
        self.speed_limit_label = tk.Label(self, text="Speed limit")
        self.debug_checkbutton = tk.Checkbutton(self,
                                                text='Debug mode',
                                                variable=self.debug,
                                                onvalue=True,
                                                offvalue=False)
        
        self.show_simulation_widgets()


    # hides and shows appropriate widgets based on chosen mode
    def alter_widgtes(self, *args):
        if self.mode.get() == "visualisation":
            self.hide_optimisation_widgets()
            self.show_simulation_widgets()
        else:
            self.hide_simulation_widgets()
            self.show_optimisation_widgets()

    # shows widgets that allow user to provide simulation data
    def show_simulation_widgets(self):
        y = 0.25
        for i in range(len(self.traffic_light_widgets)):
            self.traffic_light_labels[i].place(relx=0.2, rely=y+0.04)
            x = 0.3
            for slider in self.traffic_light_widgets[i]:
                slider.place(relx=x, rely=y)
                x += 0.1
            y += 0.1
        
        self.speed_limit.place(relx=0.3, rely=0.65)
        self.speed_limit_label.place(relx=0.2, rely=0.69)
        self.debug_checkbutton.place(relx=0.3, rely=0.8)
        self.submit.configure(text='Visualise')

    def hide_simulation_widgets(self):
        for i in range(len(self.traffic_light_widgets)):
            self.traffic_light_labels[i].place_forget()
            for slider in self.traffic_light_widgets[i]:
                slider.place_forget()

        self.speed_limit.place_forget()
        self.speed_limit_label.place_forget()
        self.debug_checkbutton.place_forget()

    def show_optimisation_widgets(self):
        self.submit.configure(text='Optimise')

    def hide_optimisation_widgets(self):
        pass

    def press_submit(self):
        self.destroy()

if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()