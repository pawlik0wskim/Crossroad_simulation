from OptimisationAlgorithm import OptimisationAlgorithm
import numpy as np
from utilities import pixels_to_kmh
import copy
import json
from csv import writer

class GeneticAlgorithm(OptimisationAlgorithm):
    def __init__(self, iterations, simulation_length, speed_limit_optimization, traffic_light_optimization, **kwargs):
        super().__init__(iterations, simulation_length, speed_limit_optimization, traffic_light_optimization)

        self.pop_size = int(kwargs['population_size'])
        self.populations = [[{'tl' : None, 
                              's': None}
                              for j in range(self.pop_size)] 
                              for i in range(int(kwargs['population_number']))]

        # initialize populations
        for i in range(len(self.populations)):
            for j in range(self.pop_size):

                if self.traffic_light_optimization:
                    self.populations[i][j]['tl'] = np.random.uniform(0, 1, (4, 4)).tolist()
                else:
                    self.populations[i][j]['tl'] = copy.deepcopy(kwargs['traffic_lights'])
                
                if self.speed_limit_optimization:
                    self.populations[i][j]['s'] = np.random.uniform(0.8, 1.2) * kwargs['speed_limit']
                else:
                    self.populations[i][j]['s'] = kwargs['speed_limit']

        self.mutation_prob = kwargs['mutation_probability']
        self.crossover_prob = kwargs['crossover_probability']

        # number of simulation repetitions
        self.simulation_repetitions = 3

        # how many top units pass selection unchaged
        self.elite_num = int(self.pop_size*kwargs['elite_part'])

        # how many top units will migrate
        self.migration_num = int(self.pop_size*kwargs['migration_part'])

        # how often(in iterations) does migration happen
        self.migration_freq = 10

        # list of not dominated(in Pareto sense) units
        self.champions = []
        # list of statistics(Flow, Collisions) of not dominated units
        self.champions_stats = []
    
    def optimise(self, simulation):

        cols = ["Main index", "Population", "Unit", "Small index", "Speed limit(km/h)"]
        for i in range(len(self.populations[0][0]['tl'])):
            for j in range(4):
                cols+=[f"Traffic light {i}_{j}"]
        cols +=["Flow", "Collisions", "Stopped", "Iterations"]
        self.stats = [cols]
        self.__save_stats()
        self.stats = []

        for i in range(1, self.iterations+1):

            # calculate fitness of organisms in current populations
            costs = self.calculate_cost(simulation, i)

            self.__save_stats()
            self.stats = []

            # update champions
            self.__update_champions()
            print('------------------------------------')
            print('Champions:')
            for champ, stat in zip(self.champions, self.champions_stats):
                print(champ)
                print(stat)
            print('------------------------------------')

            # sort organisms and their costs by values of costs
            for j in range(len(self.populations)):
                ind = np.argsort(costs[j])
                self.populations[j] = self.__permute(self.populations[j], ind)
                costs[j] = self.__permute(costs[j], ind)

            # migration of top units to next population
            # perform migration only if there is more than one population
            # migration frequency is defined with self.migration_freq
            if len(self.populations) > 1 and i % self.migration_freq == 0:
                print('Migration!')
                for j in range(len(self.populations)):
                    if j < len(self.populations) - 1:
                        outgoing_pop, ingoing_pop = j, j+1
                    else: 
                        # if this is the last population, migration happens to the first one
                        outgoing_pop, ingoing_pop = -1, 0
                    self.populations[ingoing_pop] += self.populations[outgoing_pop][0:self.migration_num]
                    costs[ingoing_pop] += costs[outgoing_pop][0:self.migration_num]
                    self.populations[outgoing_pop] = self.populations[outgoing_pop][self.migration_num:len(costs[outgoing_pop])]
                    costs[outgoing_pop] = costs[outgoing_pop][self.migration_num:len(costs[outgoing_pop])]

            # create new populations
            new_populations = []
            for pop, pop_costs in zip(self.populations, costs):
                new_populations.append(self.generate_new_population(pop, pop_costs))
            self.populations = new_populations
        
        for i in range(len(self.champions)):
            self.champions[i]['stats'] = self.champions_stats[i]
            self.champions[i]['s'] = pixels_to_kmh(self.champions[i]['s'])
        with open('champions.json', 'w') as fp:
            json.dump(self.champions, fp)
            fp.close()


    # calculates values of cost function for all units in all populations
    # returns 2d list, which has same dimensions as self.populations,
    # but contains costs of corresponding units
    def calculate_cost(self, simulation, iteration):
        costs = []

        for p, population in enumerate(self.populations):
            pop_stats = []

            for u, unit in enumerate(population):
                Flow, Collisions = 0, 0

                for j in range(self.simulation_repetitions):
                    f, c, stopped, iter = simulation.simulate(unit['s'], unit['tl'], 
                                                              sim=j, sim_max=self.simulation_repetitions, 
                                                              it=iteration, iter_max=self.iterations)
                    self.__append_stats(iteration, p, u, j, f, c, unit['s'], unit['tl'], stopped, iter)
                    simulation.reset_map()
                    Flow += f
                    Collisions += c

                Flow /= self.simulation_repetitions
                Collisions /= self.simulation_repetitions
                pop_stats.append([Flow, -Collisions])
                self.__append_stats(iteration, p, u, None, Flow, Collisions, unit['s'], unit['tl'], None, None)
            
            costs.append(self.__get_pareto_scores(pop_stats, p))
        
        return costs
    
    # returns list of Pareto scores - number of units, which dominate concrete unit + 1
    # units, which are not dominated, receive Pareto score equal to 1
    # pop_stats - list of unit statistics, which are Flow and Collisions
    # pop_num - population number, used to save not dominated unit for futher processing as potential champions
    def __get_pareto_scores(self, pop_stats, pop_num):
        pop_costs = [1] * self.pop_size

        for i in range(len(pop_stats)):
            for j in range(i+1, len(pop_stats)):
                domination = self.__pareto_compare(pop_stats[i], pop_stats[j])
                if domination == 1:
                    pop_costs[j] += 1
                if domination == 2:
                    pop_costs[i] += 1
            
            # if unit is not dominated, it may be a potential champion
            # real champions will be distinguished later
            if pop_costs[i] == 1:
                self.champions.append(copy.deepcopy(self.populations[pop_num][i]))
                self.champions_stats.append(pop_stats[i].copy())
        
        return pop_costs
                
    # compares units statistics in Pareto sense
    def __pareto_compare(self, stats1, stats2):
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

    # filters dominated champions out and leaves only not dominated ones and their statistics
    def __update_champions(self):
        print(self.champions_stats)
        new_champions = []
        new_champions_stats = []
        for i in range(len(self.champions)):
            dominated = False
            for j in range(len(self.champions)):
                # if currently processed unit is dominated by some other unit,
                # current unit has to be filtered out of champions list
                if self.__pareto_compare(self.champions_stats[i], self.champions_stats[j]) == 2:
                    dominated = True
                    break
            if not dominated:
                new_champions.append(self.champions[i])
                new_champions_stats.append(self.champions_stats[i])
        
        self.champions, self.champions_stats = new_champions, new_champions_stats


    # returns list of units, obtained with elitism, mutation and crossover from provided population,
    # order of pop_costs must match the order of units in population
    def generate_new_population(self, population, pop_costs):
        new_population = []

        # rescale costs to probabilities of being chosen for selection
        # so that units with smallest cost have the highest probability
        pop_costs = np.array(pop_costs)
        pop_costs = np.max(pop_costs) - pop_costs + 1
        pop_costs = pop_costs/np.sum(pop_costs)

        # sort to choose top organisms without changes
        ind = np.argsort(pop_costs)
        population = self.__permute(population, ind)
        pop_costs = pop_costs[ind]

        # add the best units without any changes
        new_population += population[0:self.elite_num]

        # fill remaining units in population by mutated or crossovered units from original population
        while len(new_population) < self.pop_size:

            if np.random.uniform(0, 1) < self.crossover_prob:
                unit = self.crossover(*np.random.choice(population, 2, p=pop_costs, replace=False))
            else:
                unit = np.random.choice(population, 1, p=pop_costs)[0]

            if np.random.uniform(0, 1) < self.mutation_prob:
                unit['s'], unit['tl'] = self.mutate(unit['s'], unit['tl'])
            
            new_population.append(unit)
        
        return new_population

    # returns child unit, which inherits parameters from its two parents
    # each parameter has equal probability of being inherited from parent1 or parent2
    def crossover(self, parent1, parent2):
        child = {}

        # if speed limit is not optimised, child will always have same speed limit as all other units
        # if it is optimised, one of the parents values is chosen with equal probability
        child['s'] = parent1['s'] if np.random.uniform(0, 1) < 0.5 else parent2['s']

        if self.traffic_light_optimization:
            # if traffic light cycles are optimised, take parameters for each traffic light
            # from the corresponding traffic light of randomy chosen parent 
            child_tl = []
            for i in range(len(parent1['tl'])):
                child_tl.append(parent1['tl'][i].copy() if np.random.uniform(0, 1) < 0.5 else parent2['tl'][i].copy())
            child['tl'] = child_tl
        else:
            # if traffic light cycles are not optimised, 
            # just copy traffic light parameters from one of the parents to speed up the crossover
            child['tl'] = copy.deepcopy(parent1['tl'])

        return child
    
    # help function
    # returns permutation of list ls based on index list ind
    def __permute(self, ls, ind):
        return [ls[ind[i]] for i in range(len(ls))]
    
    # help function
    # appends simulation statistics to self.stats field
    def __append_stats(self, main_index, population_num, unit_num, small_index, Flow, Collisions, speed_limit, light_cycles, stopped, iter_num):
        stat = [main_index, population_num, unit_num, small_index, pixels_to_kmh(speed_limit)]
        for light in light_cycles:
            stat += light
        stat += [ Flow, Collisions, stopped, iter_num]
        self.stats.append(stat)
    
    # saves statistics from self.stats to log file
    def __save_stats(self):
        with open('stats.csv', 'a') as f:
            writer_object = writer(f, lineterminator='\n')
            writer_object.writerows(self.stats)
        
            f.close()






if __name__ == '__main__':
    pass