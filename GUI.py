import tkinter as tk

# Graphical User Interface class
class GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        w, h = 1000, 500
        self.geometry(str(w) + 'x' + str(h))

        # data which user provides
        self.data = {}

        # tracing variables  
        self.mode = tk.StringVar()
        self.mode.set("visualisation")
        # call alter_widgets method any time the value of mode variable was changed
        self.mode.trace("w", self.alter_widgtes)

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
        self.speed_limit = tk.Scale(self, from_=1.0, to=100.0, orient='horizontal', resolution=1)
        self.speed_limit_label = tk.Label(self, text="Speed limit")
        self.debug = tk.IntVar(value=0)
        self.debug_checkbutton = tk.Checkbutton(self,
                                                text='Debug mode',
                                                onvalue=1,
                                                offvalue=0,
                                                variable=self.debug)
        
        self.show_visualisation_widgets()

        # simulated annealing widgets
        from_tmp = [0.0, 0.0]
        to_tmp = [3.0, 0.999]
        resolution_tmp = [0.1, 0.001]
        labels_tmp = ['Initial temperature', 'Decrease rate']
        self.annealing_widgets = [tk.Scale(self, from_=from_tmp[i], to=to_tmp[i], orient='horizontal', resolution=resolution_tmp[i]) for i in range(len(to_tmp))]
        self.annealing_labels = [tk.Label(self, text=labels_tmp[i]) for i in range(len(to_tmp))]

        # genetic algorithm widgets
        from_tmp = [10, 1, 0.0, 0.0]
        to_tmp = [100, 10, 1.0, 1.0]
        resolution_tmp = [1, 1, 0.01, 0.01]
        labels_tmp = ['Population size', 'Population number', 'Elite part', 'Mutation probability']
        self.genetic_widgets = [tk.Scale(self, from_=from_tmp[i], to=to_tmp[i], orient='horizontal', resolution=resolution_tmp[i]) for i in range(len(to_tmp))]
        self.genetic_labels = [tk.Label(self, text=labels_tmp[i]) for i in range(len(to_tmp))]


        # mutual optimisation widgets
        from_tmp = [1000, 10, 0.0, 0.0]
        to_tmp = [40000, 60, 1.0, 1.0]
        resolution_tmp = [100, 1, 0.01, 0.01]
        labels_tmp = ['Maximum iterations', 'Frames per car', 'Left turn prob', 'Right turn prob']
        
        self.mutual_widgets = [tk.Scale(self, from_=from_tmp[i], to=to_tmp[i], orient='horizontal', resolution=resolution_tmp[i]) for i in range(len(to_tmp))]
        self.mutual_widgets[2].bind("<ButtonRelease-1>", self.update_right_turn_prob)
        self.mutual_labels = [tk.Label(self, text=labels_tmp[i]) for i in range(len(to_tmp))]

        y = 0.25
        padx = 0.75
        for i in range(len(self.mutual_widgets)):
            self.mutual_widgets[i].place(relx=padx, rely=y)
            self.mutual_labels[i].place(relx=padx-0.13, rely=y+0.04)
            y += 0.1
    
    def update_right_turn_prob(self, event):
        self.mutual_widgets[3].configure(to=1-self.mutual_widgets[2].get())

    # hides and shows appropriate widgets based on chosen mode
    def alter_widgtes(self, *args):
        if self.mode.get() == "visualisation":
            self.hide_annealing_widgets()
            self.hide_genetic_widgets()
            self.show_visualisation_widgets()
        elif self.mode.get() == "simulated annealing":
            self.hide_visualisation_widgets()
            self.hide_genetic_widgets()
            self.show_optimisation_widgets(self.annealing_widgets, self.annealing_labels)
        else:
            self.hide_visualisation_widgets()
            self.hide_annealing_widgets()
            self.show_optimisation_widgets(self.genetic_widgets, self.genetic_labels)

    def show_visualisation_widgets(self):
        y = 0.25
        padx = 0.15
        for i in range(len(self.traffic_light_widgets)):
            self.traffic_light_labels[i].place(relx=padx-0.1, rely=y+0.04)
            x = padx
            for slider in self.traffic_light_widgets[i]:
                slider.place(relx=x, rely=y)
                x += 0.1
            y += 0.1
        
        self.speed_limit.place(relx=padx, rely=0.65)
        self.speed_limit_label.place(relx=padx-0.1, rely=0.69)
        self.debug_checkbutton.place(relx=padx, rely=0.8)
        self.submit.configure(text='Visualise')

    def hide_visualisation_widgets(self):
        for i in range(len(self.traffic_light_widgets)):
            self.traffic_light_labels[i].place_forget()
            for slider in self.traffic_light_widgets[i]:
                slider.place_forget()

        self.speed_limit.place_forget()
        self.speed_limit_label.place_forget()
        self.debug_checkbutton.place_forget()

    def show_optimisation_widgets(self, widgets, labels):
        y = 0.25
        for i in range(len(widgets)):
            widgets[i].place(relx=0.3, rely=y)
            labels[i].place(relx=0.17, rely=y+0.04)
            y += 0.1
        self.submit.configure(text='Optimise')

    def hide_annealing_widgets(self):
        for i in range(len(self.annealing_widgets)):
            self.annealing_widgets[i].place_forget()
            self.annealing_labels[i].place_forget()
        # self.canvas.get_tk_widget().place_forget()

    def hide_genetic_widgets(self):
        for i in range(len(self.genetic_widgets)):
            self.genetic_widgets[i].place_forget()
            self.genetic_labels[i].place_forget()
        # self.canvas.get_tk_widget().place_forget()

    def collect_data(self):
        self.data['mode'] = self.mode.get()
        # collect data from mutual widgets
        for widget, label in zip(self.mutual_widgets, self.mutual_labels):
            self.data[label['text']] = widget.get()

        if self.data['mode'] == 'visualisation':
            # collect visualisations data
            traffic_lights = []
            for tl in self.traffic_light_widgets:
                tl_data = []
                for l in tl:
                    tl_data.append(l.get())
                traffic_lights.append(tl_data)
            self.data['Traffic lights'] = traffic_lights
            self.data['Speed limit'] = self.speed_limit.get()
            self.data['Debug'] = self.debug.get()
        else:
            # collect optimisation algorithm data
            if self.data['mode'] == 'simulated annealing':
                widgets = self.annealing_widgets
                labels = self.annealing_labels
            else:
                widgets = self.genetic_widgets
                labels = self.genetic_labels
            for widget, label in zip(widgets, labels):
                self.data[label['text']] = widget.get()
        
    def press_submit(self):
        self.collect_data()
        self.quit()
        self.destroy()

if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()
    for key in gui.data:
        print(key, gui.data[key])