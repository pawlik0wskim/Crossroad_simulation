import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Graphical User Interface class

class GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        w, h = 1000, 500
        self.geometry(str(w) + 'x' + str(h))

        self.fig = Figure(figsize = (5, 5), dpi = 100)
        self.canvas = FigureCanvasTkAgg(self.fig,
                                master = self)  
        self.canvas.draw()
        self.canvas.get_tk_widget().configure(width=300, height=300)

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
        self.speed_limit = tk.Scale(self, from_=0.0, to=100.0, orient='horizontal', resolution=1)
        self.speed_limit_label = tk.Label(self, text="Speed limit")
        self.debug_checkbutton = tk.Checkbutton(self,
                                                text='Debug mode',
                                                onvalue=1,
                                                offvalue=0)
        
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
        max_iter = tk.Scale(self, from_=1000, to=40000, orient='horizontal', resolution=100)
        max_iter_label = tk.Label(self, text='Maximum iterations')
        self.annealing_widgets.append(max_iter)
        self.genetic_widgets.append(max_iter)
        self.annealing_labels.append(max_iter_label)
        self.genetic_labels.append(max_iter_label)

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
        self.canvas.get_tk_widget().place(relx=0.6, rely=0.2)

    def hide_annealing_widgets(self):
        for i in range(len(self.annealing_widgets)):
            self.annealing_widgets[i].place_forget()
            self.annealing_labels[i].place_forget()
        self.canvas.get_tk_widget().place_forget()

    def hide_genetic_widgets(self):
        for i in range(len(self.genetic_widgets)):
            self.genetic_widgets[i].place_forget()
            self.genetic_labels[i].place_forget()
        self.canvas.get_tk_widget().place_forget()

    def collect_data(self):
        self.data['mode'] = self.mode.get()
        if self.data['mode'] == 'visualisation':
            # collect visualisations data
            traffic_lights = []
            for tl in self.traffic_light_widgets:
                tl_data = []
                for l in tl:
                    tl_data.append(l.get())
                traffic_lights.append(tl_data)
            self.data['traffic_lights'] = traffic_lights
            self.data['speed_limit'] = self.speed_limit.get()
            # self.data['debug'] = self.debug_checkbutton.get()
        else:
            if self.data['mode'] == 'simulated annealing':
                widgets = self.annealing_widgets
            else:
                widgets = self.genetic_widgets
            data = []
            for widget in widgets:
                data.append(widget.get())
            self.data[self.data['mode']] = data
        
    def press_submit(self):
        self.collect_data()
        # self.quit()
        # self.destroy()

if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()
    for key in gui.data:
        print(gui.data[key])