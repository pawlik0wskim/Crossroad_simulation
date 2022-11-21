from OptimisationAlgorithm import OptimisationAlgorithm
import numpy as np
from utilities import cost_function
import copy

class GeneticAlgorithm(OptimisationAlgorithm):
    def __init__(self, iterations, simulation_length, **kwargs):
        super().__init__(iterations, simulation_length)
        self.elite_num = int(kwargs['elite_part'] * kwargs['population_size'])
        # self.populations = [[{'tl' : kwargs['traffic_lights'] if kwargs['traffic_lights'] is not None else np.random.uniform(0, 1, (4, 4)), 
        #                       's': kwargs['speed_limit'] if kwargs['speed_limit'] is not None else np.random.randint(20, 100)}
        #                     for j in range(kwargs['population_size'])] for i in range(kwargs['population_number'])]
        self.populations = [[{'tl' : np.random.uniform(0, 1, (4, 4)), 
                              's': min(np.random.randint(20, 100), 5)}
                            for j in range(kwargs['population_size'])] for i in range(kwargs['population_number'])]
        self.mutation_prob = kwargs['mutation_probability']
        self.pop_size = kwargs['population_size']
        self.champ = None
        self.champ_cost = np.Inf
    
    def optimise(self, simulation):
        i = 0
        while i < self.iterations:
            i += 1

            # calculate fitness of organisms in current populations
            costs = self.calculate_cost(simulation, j=i)

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

            # migration of top organisms to next population
            if len(self.populations) > 1:
                for j in range(len(self.populations)):
                    n = 2
                    if j < len(self.populations) - 1:
                        k, h = j, j+1
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

    
    def calculate_cost(self, simulation, j=0):
        costs = []
        for population in self.populations:
            pop_costs = []
            for unit in population:
                Flow, Collisions = 0, 0
                for i in range(3):
                    f, c, iter, stopped = simulation.simulate(unit['s'], unit['tl'], sim = i, sim_max = 3, it=j, iter_max = self.iterations )
                    simulation.reset_map()
                    Flow += f
                    Collisions += c
                Flow /= 3
                Collisions /= 3
                pop_costs.append(cost_function(Collisions, Flow, iter, stopped))
            costs.append(pop_costs)
        return costs
    
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

    def crossover(self, parent1, parent2, speed_limit_optimisation=True, traffic_light_optimisation=True):
        child = {}
        child['s'] = parent1['s'] if np.random.uniform(0, 1) < 0.5 else parent2['s']
        child_tl = []
        for i in range(len(parent1['tl'])):
            child_tl.append(parent1['tl'][i].copy() if np.random.uniform(0, 1) < 0.5 else parent2['tl'][i].copy())
        child['tl'] = child_tl
        return child

    def update_champ(self, costs):
        for population, pop_costs in zip(self.populations, costs):
            if pop_costs[0] < self.champ_cost:
                self.champ, self.champ_cost = copy.deepcopy(population[0]), pop_costs[0]
    
    def __permute(self, ls, ind):
        return [ls[ind[i]] for i in range(len(ls))]






if __name__ == '__main__':
    pop_costs = [1, 2, 5, 3, 7]
    a = [1, 4, 2]
    print(pop_costs + a)

    
