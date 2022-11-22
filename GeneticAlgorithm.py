from OptimisationAlgorithm import OptimisationAlgorithm
import numpy as np
from utilities import cost_function, pixels_to_kmh
import copy
from utilities import pixels_to_kmh

class GeneticAlgorithm(OptimisationAlgorithm):
    def __init__(self, iterations, simulation_length, speed_limit_optimization, traffic_light_optimization, **kwargs):
        super().__init__(iterations, simulation_length, speed_limit_optimization, traffic_light_optimization)
        # self.populations = [[{'tl' : kwargs['traffic_lights'] if kwargs['traffic_lights'] is not None else np.random.uniform(0, 1, (4, 4)), 
        #                       's': kwargs['speed_limit'] if kwargs['speed_limit'] is not None else np.random.randint(20, 100)}
        #                     for j in range(kwargs['population_size'])] for i in range(kwargs['population_number'])]
        self.pop_size = int(kwargs['population_size'])
        self.populations = [[{'tl' : np.random.uniform(0, 1, (4, 4)).tolist(), 
                              's': np.random.randint(kwargs['speed_limit']*0.75, kwargs['speed_limit']*1.15)}
                            for j in range(self.pop_size)] 
                            for i in range(int(kwargs['population_number']))]
        self.mutation_prob = kwargs['mutation_probability']
        self.crossover_prob = kwargs['crossover_probability']
        self.elite_num = int(self.pop_size*kwargs['elite_part'])
        self.migration_num = int(self.pop_size*kwargs['migration_part'])
        self.champ = None
        # global best unit score
        self.champ_cost = np.Inf
    
    def optimise(self, simulation):

        for i in range(1, self.iterations+1):

            # calculate fitness of organisms in current populations
            costs = self.calculate_cost(simulation, i)

            # sort organisms and their costs by values of costs
            for j in range(len(self.populations)):
                ind = np.argsort(costs[j])
                self.populations[j] = self.__permute(self.populations[j], ind)
                costs[j] = self.__permute(costs[j], ind)


            # update champion
            tmp = self.champ_cost
            self.update_champ(costs)
            if tmp > self.champ_cost:
                print('---------------------------------')
                print(f'Champion updated! New Champion cost {self.champ_cost}')
                print(self.champ)
                print('---------------------------------')

            # migration of top units to next population
            if len(self.populations) > 1:
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

    # calculates values of cost function for all units in all populations
    # returns 2d list, which has same dimensions as self.populations,
    # but contains costs of corresponding units
    def calculate_cost(self, simulation, iteration):
        costs = []

        for p, population in enumerate(self.populations):
            pop_costs = []

            for u, unit in enumerate(population):
                Flow, Collisions = 0, 0

                for j in range(3):
                    f, c, iter, stopped = simulation.simulate(unit['s'], unit['tl'], sim=j, sim_max=3, it=iteration, iter_max=self.iterations )
                    self.__append_stats(iteration, p, u, j, f, c, unit['s'], unit['tl'], stopped, iter)
                    simulation.reset_map()
                    Flow += f
                    Collisions += c

                Flow /= 3
                Collisions /= 3
                pop_costs.append(cost_function(Flow, Collisions, iter, stopped))
                self.__append_stats(iteration, p, u, None, Flow, Collisions, unit['s'], unit['tl'], None, None)
            
            costs.append(pop_costs)
        
        return costs
    
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
    def crossover(self, parent1, parent2, speed_limit_optimization=True, traffic_light_optimization=True):
        child = {}
        child['s'] = parent1['s'] if np.random.uniform(0, 1) < 0.5 else parent2['s']
        child_tl = []
        for i in range(len(parent1['tl'])):
            child_tl.append(parent1['tl'][i].copy() if np.random.uniform(0, 1) < 0.5 else parent2['tl'][i].copy())
        child['tl'] = child_tl
        return child

    # updates champion(global best unit)
    # assumes, that provided costs and self.populations are sorted
    def update_champ(self, costs):
        for population, pop_costs in zip(self.populations, costs):
            if pop_costs[0] < self.champ_cost:
                self.champ, self.champ_cost = copy.deepcopy(population[0]), pop_costs[0]
    
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






if __name__ == '__main__':
    pass
