from OptimizationAlgorithm import OptimizationAlgorithm
import numpy as np
import pandas as pd
from utilities import pixels_to_kmh, kilometers_per_hour_to_pixels
import copy

class GeneticAlgorithm(OptimizationAlgorithm):
    def __init__(self, iterations, simulation_length, speed_limit_optimization, traffic_light_optimization, **kwargs):
        super().__init__(iterations, simulation_length, speed_limit_optimization, traffic_light_optimization)

        self.pop_size = int(kwargs['population_size'])
        self.populations = [[{"light_cycles" : None, 
                              "speed_limit": None}
                              for j in range(self.pop_size)] 
                              for i in range(int(kwargs['population_number']))]

        # initialize populations
        for i in range(len(self.populations)):
            for j in range(self.pop_size):

                speed_limit_modified, light_cycles_modified = self.mutate(kwargs["speed_limit"], kwargs["light_cycles"])

                if self.traffic_light_optimization:
                    self.populations[i][j]["light_cycles"] = light_cycles_modified
                else:
                    self.populations[i][j]["light_cycles"] = copy.deepcopy(np.around(kwargs["traffic_lights"], 2).tolist())
                
                if self.speed_limit_optimization:
                    self.populations[i][j]["speed_limit"] = speed_limit_modified
                else:
                    self.populations[i][j]["speed_limit"] = round(kwargs["speed_limit"])

        self.mutation_prob = kwargs['mutation_probability']

        # number of simulation repetitions
        self.simulation_repetitions = 3

        # how many top units pass selection unchaged
        self.elite_num = int(self.pop_size*kwargs["elite_part"])

        # how many top units will migrate
        self.migration_num = int(self.pop_size*kwargs["migration_part"])

        # how often(in iterations) does migration happen
        self.migration_freq = 10

        # number of simulations left till the end of optimisation
        self.simulations_number = self.pop_size * len(self.populations) * self.simulation_repetitions * self.iterations
        # number of simulations that were already conducted
        self.simulations_conducted = 0

        self.stats_file = 'genetic_' + self.stats_file
        self.champions_file = 'genetic_' + self.champions_file

    def optimise(self, simulation, text, opt_progress, sim_progress, duration_label, init_params=None):

        cols = ["Main index", "Population", "Unit", "Small index", "Speed limit(km/h)"]
        for i in range(len(self.populations[0][0]["light_cycles"])):
            for j in range(4):
                cols+=[f"Traffic light {i}_{j}"]
        cols +=["Flow", "Collisions", "Stopped", "Iterations"]
        self.stats = [cols]
        self.save_stats()
        self.stats = []

        for i in range(1, self.iterations+1):

            # calculate fitness of organisms in current populations
            costs = self.calculate_cost(simulation, i, text, sim_progress, duration_label)

            self.save_stats()
            self.stats = []

            opt_progress['value'] = int(100*i/self.iterations)

            if i == self.iterations:
                break

            # sort organisms and their costs by values of costs
            for j in range(len(self.populations)):
                ind = np.argsort(costs[j])
                self.populations[j] = self.permute(self.populations[j], ind)
                costs[j] = self.permute(costs[j], ind)

            # migration of top units to next population
            # perform migration only if there is more than one population
            # migration frequency is defined with self.migration_freq
            if len(self.populations) > 1 and i % self.migration_freq == 0:
                for j in range(len(self.populations)):
                    if j < len(self.populations) - 1:
                        outgoing_pop, ingoing_pop = j, j+1
                    else: 
                        # if this is the last population, migration happens to the first one
                        outgoing_pop, ingoing_pop = -1, 0
                    self.populations[ingoing_pop] += copy.deepcopy(self.populations[outgoing_pop][0:self.migration_num])
                    costs[ingoing_pop] += costs[outgoing_pop][0:self.migration_num].copy()
                    self.populations[outgoing_pop] = self.populations[outgoing_pop][self.migration_num:len(costs[outgoing_pop])]
                    costs[outgoing_pop] = costs[outgoing_pop][self.migration_num:len(costs[outgoing_pop])]

            # create new populations
            new_populations = []
            for pop, pop_costs in zip(self.populations, costs):
                new_populations.append(self.generate_new_population(pop, pop_costs))
            self.populations = new_populations
        
        duration_label.configure(text='Finished')
    
    # calculates costs for all units in all populations
    # returns 2d list, which has same dimensions as self.populations,
    # but contains costs of corresponding units
    def calculate_cost(self, simulation, iteration, text, sim_progress, duration_label):
        costs = []

        for p, population in enumerate(self.populations):
            pop_stats = []

            for u, unit in enumerate(population):
                Flow, Collisions = 0, 0
                stopped = False

                for j in range(self.simulation_repetitions):
                    f, c, s, iter, elapsed_time = simulation.simulate(unit["speed_limit"], unit["light_cycles"], 
                                                              sim=j, sim_max=self.simulation_repetitions, 
                                                              it=iteration, iter_max=self.iterations,
                                                              text=text, loading_bar=sim_progress)
                    self.append_stats(iteration, p, u, j, f, c, unit["speed_limit"], unit["light_cycles"], s, iter)
                    simulation.reset_map()
                    Flow += f
                    Collisions += c
                    self.elapsed_time += elapsed_time
                    stopped = stopped or s

                    self.simulations_conducted += 1
                    mean_sim_time = self.elapsed_time/(self.simulations_conducted)
                    estimated_duration = mean_sim_time * (self.simulations_number - self.simulations_conducted)
                    self.update_estimated_duration(duration_label, estimated_duration)

                Flow /= self.simulation_repetitions
                Collisions /= self.simulation_repetitions
                self.append_stats(iteration, p, u, None, Flow, Collisions, unit["speed_limit"], unit["light_cycles"], None, None)
                
                if not stopped:
                    pop_stats.append([Flow, -Collisions])
                else:
                    pop_stats.append([-np.Inf, -np.Inf]) # if crossroad has blocked itself at least one time - give it the worst possible stats 
            
            costs.append(self.get_pareto_scores(pop_stats))
        
        return costs
    
    # returns list of Pareto scores - number of units, which dominate concrete unit + 1
    # units, which are not dominated, receive Pareto score equal to 1
    # pop_stats - list of unit statistics, which are Flow and Collisions
    # pop_num - population number, used to save not dominated unit for further processing as potential champions
    def get_pareto_scores(self, pop_stats):
        pop_costs = [1] * self.pop_size

        for i in range(len(pop_stats)):
            for j in range(i+1, len(pop_stats)):
                domination = self.pareto_compare(pop_stats[i], pop_stats[j])
                pop_costs[j] += int(domination == 1)
                pop_costs[i] += int(domination == 2)
        
        return pop_costs
                
    # compares units statistics in Pareto sense
    def pareto_compare(self, stats1, stats2):
        # if none of units dominates, return 0
        if (stats1[0] > stats2[0] and stats1[1] < stats2[1]) or (stats1[0] < stats2[0] and stats1[1] > stats2[1]):
            return 0
        if stats1[0] == stats2[0] and stats1[1] == stats2[1]:
            return 0
        
        # if unit1 dominates return 1
        if stats1[0] > stats2[0] or stats1[1] > stats2[1]:
            return 1
        
        # if unit2 dominates return 2
        return 2


    # returns list of units, obtained through elitism, mutation and crossover from provided population,
    # order of pop_costs must match the order of units in population
    def generate_new_population(self, population, pop_costs):
        new_population = []

        pop_costs = np.array(pop_costs)
        # sort to choose top organisms without changes
        ind = np.argsort(pop_costs)
        population = self.permute(population, ind)
        pop_costs = pop_costs[ind]

        # rescale costs to probabilities of being chosen for selection
        # so that units with smallest cost have the highest probability
        pop_costs = np.max(pop_costs) - pop_costs + 1
        pop_costs = pop_costs/np.sum(pop_costs)

        # add the best units without any changes
        new_population += population[0:self.elite_num]

        # fill remaining units in population by mutated or crossovered units from original population
        while len(new_population) < self.pop_size:

            unit = self.crossover(*np.random.choice(population, 2, p=pop_costs, replace=False))

            if np.random.uniform(0, 1) < self.mutation_prob:
                unit["speed_limit"], unit["light_cycles"] = self.mutate(unit["speed_limit"], unit["light_cycles"])
            
            new_population.append(unit)
        
        return new_population

    # returns child unit, which inherits parameters from its two parents
    # each parameter has equal probability of being inherited from parent1 or parent2
    def crossover(self, parent1, parent2):
        child = {}

        # if speed limit is not optimised, child will always have same speed limit as all other units
        # if it is optimised, one of the parents values is chosen with equal probability
        child["speed_limit"] = parent1["speed_limit"] if np.random.uniform(0, 1) < 0.5 else parent2["speed_limit"]

        if self.traffic_light_optimization:
            # if traffic light cycles are optimised, take parameters for each traffic light
            # from the corresponding traffic light of randomy chosen parent 
            child_tl = []
            for i in range(len(parent1["light_cycles"])):
                child_tl.append(parent1["light_cycles"][i].copy() if np.random.uniform(0, 1) < 0.5 else parent2["light_cycles"][i].copy())
            child["light_cycles"] = child_tl
        else:
            # if traffic light cycles are not optimised, 
            # just copy traffic light parameters from one of the parents to speed up the crossover
            child["light_cycles"] = copy.deepcopy(parent1["light_cycles"])

        return child

    # finds non dominated units and stores them in self.champion field
    def find_champions(self):

        units, stats = self.get_units()
        dominated = [0] * len(units)

        for i in range(len(units)):
            # if current unit was dominated by some prior unit, no need to check further
            if dominated[i] == 1:
                continue

            for j in range(i+1, len(units)):
                domination = self.pareto_compare(stats[i], stats[j])
                # if current unit dominates, save that information
                if domination == 1:
                    dominated[j] = 1
                # if current unit is dominated, no need to check further
                if domination == 2:
                    dominated[i] = 1
                    break
            # if no dominating units found, current unit is one of true champions
            if dominated[i] == 0:
                self.champions.append(units[i])
                self.champions_stats.append(stats[i])
    
    # returns list of units that did not get stuck and their stats
    def get_units(self):
        
        df = pd.read_csv(self.log_dir + self.stats_file)
        # if there were no simulations recorded simply return empty list of units and their stats
        if df.shape[0] == 0:
            return [], []

        # find units that have no stuck simulations
        df1 = df.groupby(['Main index', 'Population', 'Unit']).agg({'Iterations': 'sum'})
        df1.reset_index(inplace=True)
        df1 = df1[df1['Iterations'] == self.simulation_repetitions*self.simulation_length]

        # leave summary rows of units which did not get stuck
        df['tmp'] = list(zip(df['Main index'], df['Population'], df['Unit']))
        df = df[df['tmp'].isin(list(zip(df1['Main index'], df1['Population'], df1['Unit'])))]
        df = df[df['Stopped'].isna()]

        data = df.values.tolist()

        stats = []
        units = []

        for row in data:
            stats.append([row[21], -row[22]])
            unit = {'speed_limit': kilometers_per_hour_to_pixels(row[4]), 'light_cycles': []}
            for i in range(4):
                unit['light_cycles'].append(row[5+4*i: 5+4*(i+1)])
            units.append(unit)

        return units, stats
            
    # help function
    # returns permutation of list ls based on index list ind
    def permute(self, ls, ind):
        return [ls[ind[i]] for i in range(len(ls))]
    
    # help function
    # compares two units in terms of their parameters
    def compare_units(self, unit1, unit2):
        if unit1["speed_limit"] != unit2["speed_limit"]:
            return False
        return np.sum(np.sort(unit1["light_cycles"]) == np.sort(unit2["light_cycles"])) == len(unit1["light_cycles"]) * len(unit1["light_cycles"][0])
    
    # help function
    # appends simulation statistics to self.stats field
    def append_stats(self, main_index, population_num, unit_num, small_index, Flow, Collisions, speed_limit, light_cycles, stopped, iter_num):
        stat = [main_index, population_num, unit_num, small_index, round(pixels_to_kmh(speed_limit))]
        for light in light_cycles:
            stat += light
        stat += [ Flow, Collisions, stopped, iter_num]
        self.stats.append(stat)
