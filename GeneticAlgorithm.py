from OptimisationAlgorithm import OptimisationAlgorithm
import numpy as np
from utilities import cost_function
import copy
from utilities import pixels_to_kmh

class GeneticAlgorithm(OptimisationAlgorithm):
    def __init__(self, iterations, simulation_length, **kwargs):
        super().__init__(iterations, simulation_length)
        # number of units in one population
        self.pop_size = kwargs.get('population_size', 3)
        # number of best units, which will be pass selection without any changes
        self.elite_num = int(kwargs.get('elite_part', 0.2) * self.pop_size)
        pop_number = kwargs.get('population_number', 3)
        # self.populations = [[{'tl' : kwargs['traffic_lights'] if kwargs['traffic_lights'] is not None else np.random.uniform(0, 1, (4, 4)), 
        #                       's': kwargs['speed_limit'] if kwargs['speed_limit'] is not None else np.random.randint(20, 100)}
        #                     for j in range(kwargs['population_size'])] for i in range(kwargs['population_number'])]
        
        # list of populations
        self.populations = [[{'tl' : np.random.uniform(0, 1, (4, 4)), 
                              's': np.random.randint(5, 20)}
                            for j in range(self.pop_size)] for i in range(pop_number)]
        # probability of mutation
        self.mutation_prob = kwargs.get('mutation_probability', 0.6)
        # global best unit
        self.champ = None
        # global best unit score
        self.champ_cost = np.Inf
    
    def optimise(self, simulation):
        i = 0
        while i < self.iterations:
            i += 1

            # calculate costs of organisms in current populations
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
                print(f'Champion updated! New Champion cost {self.champ_cost}')
                print(self.champ)
                print('---------------------------------')

            # migration of top units to next population
            if len(self.populations) > 1:
                for j in range(len(self.populations)):
                    n = 2
                    # top n units are moved to next population
                    if j < len(self.populations) - 1:
                        k, h = j, j+1
                    # units from last population are moved to first one
                    else:
                        k, h = -1, 0
                    self.populations[h] += self.populations[k][0:n]
                    costs[h] += costs[k][0:n]
                    self.populations[k] = self.populations[k][n:len(costs[k])]
                    costs[k] = costs[k][n:len(costs[k])]

            # create new populations
            new_populations = []
            for pop, pop_costs in zip(self.populations, costs):
                new_populations.append(self.generate_new_population(pop, pop_costs))
            self.populations = new_populations

    # returns nested list of costs of each unit from each population
    # iter - current iteration number, used for statistics
    def calculate_cost(self, simulation, iter):
        costs = []
        for j in range(len(self.populations)):
            pop_costs = []
            for unit in self.populations[j]:
                Flow, Collisions = 0, 0
                # run simulation several times for same unit
                for i in range(3):
                    f, c, stopped, iteration = simulation.simulate(unit['s'], unit['tl'], sim = i, sim_max = 3, it=iter, iter_max = self.iterations )
                    simulation.reset_map()
                    stat = [iter,j,i,pixels_to_kmh(unit['s'])]
                    for light in unit['tl']:
                        for i in range(len(light)):
                            stat.append(light[i])
                    stat += [f, c, stopped, iteration]
                    self.stats.append(stat)
                    Flow += f
                    Collisions += c
                Flow /= 3
                Collisions /= 3
                stat = [iter,j,None,pixels_to_kmh(unit['s'])]
                for light in unit['tl']:
                    for i in range(len(light)):
                        stat.append(light[i])
                stat += [ Flow, Collisions, None, None]
                self.stats.append(stat)
                # save cost function of units mean stats as its cost
                pop_costs.append(cost_function(Collisions, Flow, iter, stopped))
            costs.append(pop_costs)
        return costs
    
    # returns list of new populations with elite, mutated or crossovered units 
    def generate_new_population(self, population, pop_costs):
        new_population = []

        # rescale costs to probabilities
        pop_costs = np.array(pop_costs)
        pop_costs = np.max(pop_costs) - pop_costs + 1
        pop_costs = pop_costs/np.sum(pop_costs)
        # print(pop_costs)

        crossover_prob = 0.2

        # sort after migration
        ind = np.argsort(pop_costs)
        population = self.__permute(population, ind)
        pop_costs = pop_costs[ind]

        # add the best units without any changes
        new_population += population[0:min(self.elite_num, self.pop_size)]

        # fill remaining units in population by mutated or crossovered units from original population
        while len(new_population) < self.pop_size:

            if np.random.uniform(0, 1) < crossover_prob:
                unit = self.crossover(*np.random.choice(population, 2, p=pop_costs, replace=False))
            else:
                unit = np.random.choice(population, 1, p=pop_costs)[0]

            if np.random.uniform(0, 1) < self.mutation_prob:
                unit['s'], unit['tl'] = self.mutate(unit['s'], unit['tl'], True, True)
            
            new_population.append(unit)
        
        return new_population

    # returns child unit, which inherits parameters from its two parents
    # each parameter has equal probability of being inherited from parent1 or parent2
    def crossover(self, parent1, parent2, speed_limit_optimisation=True, traffic_light_optimisation=True):
        child = {}
        child['s'] = parent1['s'] if np.random.uniform(0, 1) < 0.5 else parent2['s']
        child_tl = []
        for i in range(len(parent1['tl'])):
            child_tl.append(parent1['tl'][i].copy() if np.random.uniform(0, 1) < 0.5 else parent2['tl'][i].copy())
        child['tl'] = child_tl
        return child
    
    # checks if there is a better unit in current populations than the globa best found till the call of this function
    # assumes that populations are sorted by costs
    def update_champ(self, costs):
        for population, pop_costs in zip(self.populations, costs):
            if pop_costs[0] < self.champ_cost:
                self.champ, self.champ_cost = copy.deepcopy(population[0]), pop_costs[0]
    
    # help method, returns permutation of a list based on given indexes list - ind
    def __permute(self, ls, ind):
        return [ls[ind[i]] for i in range(len(ls))]






if __name__ == '__main__':
    ga = GeneticAlgorithm(10, 1000, elite_part=0.2, population_size=10, population_number=5, mutation_probability=0.2)
    print('====Crossover====')
    # only speed limit and parameters of 1st traffic light differ
    parent1 = {'s': 10, 'tl': [[0.2, 0.1, 0.8, 0.5], [0.2, 0.1, 0.8, 0.5], [0.2, 0.1, 0.8, 0.5], [0.2, 0.1, 0.8, 0.5]]}
    parent2 = {'s': 25, 'tl': [[0.0, 0.7, 0.3, 0.9], [0.2, 0.1, 0.8, 0.5], [0.2, 0.1, 0.8, 0.5], [0.2, 0.1, 0.8, 0.5]]}
    child = ga.crossover(parent1, parent2)
    for k in child.keys():
        print(k, child[k])
    
    print('====Elite num====')
    # elite number is number of organisms, which will be taken through selection without any changes
    print(ga.elite_num == 0.2*10)

    print('====Default arguments====')
    ga = GeneticAlgorithm(10, 1000, elite_part=0.2)
    print('Default population size:', ga.pop_size)
    print('Default population number:', len(ga.populations))
    print('Default mutation probability:', ga.mutation_prob)
