import unittest
from Controller import *
from utilities import *
from Car import *
from Application import *
from OptimizationAlgorithm import OptimizationAlgorithm
from copy import copy, deepcopy
import csv

zero = 10**(-100)

class Test(unittest.TestCase):
    #Main simulation loop with car spawning and traffic jam recognising mechanisms removed
    def main_loop(self, test_map, visualise, max_iter = 300, break_on_flow = False):
        if visualise:
            win = pygame.display.set_mode((WIDTH, HEIGHT))   
            clock=pygame.time.Clock()
            test_map.img = pygame.transform.scale(pygame.image.load(r"images/black.jpg"),(WIDTH,HEIGHT)).convert()
            test_map.rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        Collisions = 0
        Flow = 0
        i=0
        while(True):
            i+=1
            if visualise:
                test_map.draw(win, True)
            for road in test_map.roads:
                for car in road.cars:
                    car.update_vision(road.direction, road.type, road.curve)
                    test_map.process_car_neighborhood(car, road)
            test_map.update_traffic_lights(i, 300)
            f, _ =test_map.move_cars( 0, 0)
            Flow += f
            Collisions+=test_map.check_for_car_collision()
            if i >= max_iter or(Flow and break_on_flow):
                break
            if visualise:
                pygame.display.update()
                clock.tick(FPS)
                
        return Collisions, Flow
    
    #     #Test if cars correctly elave intersection
    def test_00_car_leaves_intersection(self):
        test_map = generate_test_map(1000,1000, False)
        
        car = test_map.spawn_car(4)
        
        _ , Flow = self.main_loop(test_map, visualise, max_iter = 300)
        
        for road in test_map.roads:
            self.assertEqual(len(road.cars), 0)
        self.assertEqual(Flow, 1) #Car has to leave intersection
    
    #Test of collision mechanisms
    def test_01_collisions(self):
        test_map = generate_test_map(1000,1000, False)
        
        car = test_map.spawn_car(zero)
        car.rect.center = (test_map.roads[0].end_node.pos[0],test_map.roads[0].end_node.pos[1]*3/4)
        car2 = test_map.spawn_car(6)
        car2.maximum_deceleration = zero
        
        Collisions , _ = self.main_loop(test_map, visualise, max_iter = 100)
        for road in test_map.roads:
            self.assertEqual(len(road.cars), 0)       
        self.assertEqual(Collisions, 1) #Cars have to collide
        
    #Test if cars will stop on red light
    def test_02_stopping_on_red_light(self):
        test_map = generate_test_map(1000,1000, True)
        for i in range(len(test_map.roads_with_lights)):
            test_map.roads_with_lights[i].light_cycle = [2,2,2,2] 
            test_map.roads_with_lights[i].light = 2
        
        car = test_map.spawn_car(3)
        _ , Flow = self.main_loop(test_map, visualise, max_iter = 200)
                
        self.assertEqual(Flow, 0) #Car can't leave road segment
        self.assertGreater(1/2, car.velocity) #Car has to stop(velocity smaller than 1/2)
        self.assertGreater(test_map.roads[0].end_node.pos[1], car.rect.center[1]+car.rect.height/2) #Car has to stop before end of segment
    
    #Test if cars stop when driver sees another stationary vehicle
    def test_03_stopping_to_vehicle(self):
        test_map = generate_test_map(1000,1000, False)
        
        car = test_map.spawn_car(zero**2)
        car.rect.center = test_map.roads[0].end_node.pos
        
        car2 = test_map.spawn_car(3)
        _ , Flow = self.main_loop(test_map, visualise, max_iter = 200)
                
        self.assertEqual(Flow, 0) #Cars can't leave road segment
        self.assertGreater(1, car2.velocity) #Car has to stop(velocity smaller than 1)
        self.assertGreaterEqual(car.rect.center[1], car2.rect.center[1]+car2.minimum_dist) #Car has to leave some space before vehicles
     
    #Test if car will slow down if positioned behined slower vehicle   
    def test_04_adjusting_velocity(self):
        test_map = generate_test_map(1000,1000, False)
        
        car = test_map.spawn_car(4)
        car.rect.center = (test_map.roads[0].end_node.pos[0],test_map.roads[0].end_node.pos[1]*3/4)
        
        car2 = test_map.spawn_car(6)
        Collisions , _ = self.main_loop(test_map, visualise, max_iter = 100)
                
        self.assertGreater(6, car2.velocity) #Second car has to lower velocity
        self.assertGreaterEqual(car2.velocity, 4) #Second car can't go slower than the first one
        self.assertGreaterEqual(car.rect.center[1], car2.rect.center[1]+car2.minimum_dist) #Car has to leave some space before vehicles
        self.assertEqual(Collisions, 0) #Cars cannot collide

    #Test if car driving straight will have priority on car turning left
    def test_05_car_priority_straight(self):
        test_map = generate_one_straight_one_left_turn(1000,1000)
        
        node = test_map.starting_nodes[0]
        car = Car(node.pos, 180, WIDTH, HEIGHT, 3)
        node.exiting_roads[0].cars.append(car)
        
        node2 = test_map.starting_nodes[1]
        car2 = Car(node2.pos, 0, WIDTH, HEIGHT, 3)
        node2.exiting_roads[0].cars.append(car2)
        
        Collisions , Flow = self.main_loop(test_map, visualise, max_iter = 350)
        
        cars = []
        for road in test_map.roads:
            for car in road.cars:
                cars.append(car)
                
        self.assertEqual(Flow, 1) #One car has o leave intersection
        self.assertEqual(len(cars), 1)
        self.assertEqual(cars[0], car) #It has to be a car driving in a straight line
        self.assertEqual(Collisions, 0) #Cars cannot collide
    
    #Test if car that has already turned will have priority over car driving straight
    def test_06_car_priority_turning(self):
        test_map = generate_one_straight_one_left_turn(1000,1000)
        
        node = test_map.starting_nodes[0]
        car = Car(node.pos, 180, WIDTH, HEIGHT, 3.7)
        node.exiting_roads[0].cars.append(car)
        
        node2 = test_map.starting_nodes[1]
        car2 = Car(node2.pos, 0, WIDTH, HEIGHT, 3)
        node2.exiting_roads[0].cars.append(car2)
        
        Collisions , Flow = self.main_loop(test_map, visualise, max_iter = 400, break_on_flow = True)
        
        cars = []
        for road in test_map.roads:
            for car in road.cars:
                cars.append(car)
                
        self.assertEqual(Flow, 1) #One car has o leave intersection
        self.assertEqual(len(cars), 1)
        self.assertEqual(cars[0], car2) #It has to be a car turning
        self.assertEqual(Collisions, 0) #Cars cannot collide
    
    #Test if crossover mechanism works correctly  
    def test_07_crossover(self):
        np.random.seed(123)
        ga = GeneticAlgorithm(10, 1000, speed_limit_optimization=True, traffic_light_optimization=True, elite_part=0.3, population_size=10, population_number=5, mutation_probability=0.2, speed_limit=10, crossover_probability=0.2, migration_part=0.1)
        parent1 = {'speed_limit': 10, 'light_cycles': [[0.2, 0.1, 0.8, 0.5], [0.2, 0.1, 0.8, 0.5], [0.2, 0.1, 0.8, 0.5], [0.2, 0.1, 0.8, 0.5]]}
        parent2 = {'speed_limit': 25, 'light_cycles': [[0.0, 0.7, 0.3, 0.9], [0.0, 0.7, 0.3, 0.9], [0.0, 0.7, 0.3, 0.9], [0.0, 0.7, 0.3, 0.9]]}
        child = ga.crossover(parent1, parent2)
        
        self.assertEqual(child['speed_limit'], 10)
        expected_tl = [[0.0, 0.7, 0.3, 0.9], [0.0, 0.7, 0.3, 0.9], [0.2, 0.1, 0.8, 0.5], [0.0, 0.7, 0.3, 0.9]]
        for i in range(4):
            self.assertEqual(child['light_cycles'][i], expected_tl[i])
    

    #Test if mutation changes parameters
    def test_08_mutation(self):
        #Test if mutation changes random parameter
        oa = OptimizationAlgorithm(iterations=1, simulation_length=1, speed_limit_optimization=True, traffic_light_optimization=True)
        speed_limit, light_cycles = (5,[[0.1,0.2,0.6,0.7],[0.1,0.2,0.6,0.7],[0.1,0.2,0.6,0.7],[0.1,0.2,0.6,0.7]])
        
        new_speed_limit, new_light_cycles = oa.mutate(copy(speed_limit),copy(light_cycles))
        variables = light_cycles
        variables.append(speed_limit)
        variables_new = new_light_cycles
        variables_new.append(new_speed_limit)
        
        self.assertNotEqual(variables, variables_new)#we want parameters changed
        
    #Test if mutation changes correct parameters   
    def test_09_mutation_specific(self):
        #Test if mutation changes speed limit
        oa = OptimizationAlgorithm(iterations=1, simulation_length=1, speed_limit_optimization=True, traffic_light_optimization=False)
        speed_limit, light_cycles = (5,[[0.1,0.2,0.6,0.7],[0.1,0.2,0.6,0.7],[0.1,0.2,0.6,0.7],[0.1,0.2,0.6,0.7]])
        new_speed_limit, new_light_cycles = oa.mutate(copy(speed_limit),copy(light_cycles))
        
        self.assertNotEqual(speed_limit, new_speed_limit)#we want speed limit changed
        self.assertEqual(light_cycles, new_light_cycles)#we want light cycles unchanged
        
        #Test if mutation changes light cycles
        oa = OptimizationAlgorithm(iterations=1, simulation_length=1, speed_limit_optimization=False, traffic_light_optimization=True)
        speed_limit, light_cycles = (5,[[0.1,0.2,0.6,0.7],[0.1,0.2,0.6,0.7],[0.1,0.2,0.6,0.7],[0.1,0.2,0.6,0.7]])
        new_speed_limit, new_light_cycles = oa.mutate(speed_limit,light_cycles)
        
        self.assertEqual(speed_limit, new_speed_limit)#we want speed limit unchanged
        self.assertNotEqual(light_cycles, new_light_cycles)#we want light cycles changed
        
    # Test if conversion of units is done correctly   
    def test_10_name(self):
        from utilities import kilometers_per_hour_to_pixels, pixels_to_kmh
        self.assertAlmostEqual(kilometers_per_hour_to_pixels(pixels_to_kmh(10)), 10)
        
    # Test if Pareto comparison is implemented correctly
    def test_11_Pareto_comparison(self):
        ga = GeneticAlgorithm(100, 100, True, True,
                        elite_part=0.1, 
                        population_size=10, 
                        speed_limit=20, 
                        crossover_probability=0.2, 
                        mutation_probability=0.6, 
                        population_number=2,
                        migration_part=0.2) 
        
        # Pareto comparison checks relation of two statistic vectors, which have form of [Flow, -Collision]
        # vector1 dominates vector2 iff one statistic from vector1 is > than same statistic of vector2 
        # and other statistic of vector1 is not less than the corresponding statistic of vector2
        # if it is less, than none of vectors is dominating, same applies if vectors have equal statistics
        self.assertEqual(ga.pareto_compare([1, -1], [1, -1]), 0)
        self.assertEqual(ga.pareto_compare([2, -2], [1, -1]), 0)
        self.assertEqual(ga.pareto_compare([1, 0], [1, -1]), 1)
        self.assertEqual(ga.pareto_compare([2, -1], [1, -1]), 1)
        self.assertEqual(ga.pareto_compare([1, -1], [1, 0]), 2)
    
    # Test if champions list in genetic algorithm is updated correctly
    def test_12_champions_update(self):
        # potential champions(units, which were not dominated in their populations)
        # during cost calculations are appended to self.champions
        # (their stats go to self.champions_stats)
        # later some candidates are filtered out, if there are champions on the list, which dominate them
        # this test checks if this filtering/update is done correctly

        # sample GeneticAlgorithm instance
        ga = GeneticAlgorithm(100, 100, True, True,
                        elite_part=0.1, 
                        population_size=10, 
                        speed_limit=20, 
                        crossover_probability=0.2, 
                        mutation_probability=0.6, 
                        population_number=2,
                        migration_part=0.2) 
        
        champions = [{'tl': [[0.1, 0.2, 0.3, 0.4], [0.1, 0.2, 0.3, 0.4], [0.1, 0.2, 0.3, 0.4], [0.1, 0.2, 0.3, 0.4]], # candidate 1
                      's': 20.0},
                    {'tl': [[0.1, 0.4, 0.9, 0.8], [0.1, 0.4, 0.9, 0.8], [0.1, 0.4, 0.9, 0.8], [0.1, 0.4, 0.9, 0.8]], # candidate 2
                     's': 10.3},
                    {'tl': [[0.5, 0.5, 0.7, 0.4], [0.5, 0.5, 0.7, 0.4], [0.5, 0.5, 0.7, 0.4], [0.5, 0.5, 0.7, 0.4]], # candidate 3
                     's': 14.0},
                    {'tl': [[0.0, 0.4, 0.5, 0.6], [0.0, 0.4, 0.5, 0.6], [0.0, 0.4, 0.5, 0.6], [0.0, 0.4, 0.5, 0.6]], # candidate 4
                     's': 23.1}]
        ga.champions = deepcopy(champions)
        champions_stats = [[200, -0.33], # stats of candidate 1
                           [300, -0.33], # stats of candidate 2
                           [100, -0.0], # stats of candidate 3
                           [400, -2.33]] # stats of candidate 4
        ga.champions_stats = deepcopy(champions_stats)
        
        ga.update_champions()

        # only candidate with index 0 should be filtered out as he is dominated by candidate with index 1
        self.assertEqual(len(ga.champions), 3)
        self.assertEqual(len(ga.champions_stats), 3)
        
        self.assertEqual(ga.champions[0]['tl'], champions[1]['tl'])
        self.assertEqual(ga.champions[0]['s'], champions[1]['s'])
        self.assertEqual(ga.champions_stats[0], champions_stats[1])

        self.assertEqual(ga.champions[1]['tl'], champions[2]['tl'])
        self.assertEqual(ga.champions[1]['s'], champions[2]['s'])
        self.assertEqual(ga.champions_stats[1], champions_stats[2])

        self.assertEqual(ga.champions[2]['tl'], champions[3]['tl'])
        self.assertEqual(ga.champions[2]['s'], champions[3]['s'])
        self.assertEqual(ga.champions_stats[2], champions_stats[3])
        
        
    #Testing if cars decelerate correctly
    def test_13_deceleration(self):
        n = 500
        x_range = np.array(range(n))
        y_range = [0 for i in range((n))]
        
        WIDTH, HEIGHT = 1000, 1000
        position, angle, speed_limit = (100, 100), 180, 15
        car = Car(position, angle, WIDTH, HEIGHT, speed_limit)
        car.velocity = 10
        car.reaction_time = 30/20
        car.minimum_dist = 1000//11*5/3
        for x in x_range:
            leading_dist=x + 1000//11*5/3
            car2 = Car((position[0] + leading_dist, position[1]), angle, WIDTH, HEIGHT, 5)
            car.nearest_car = car2
            car2.minimum_dist = 1000//11*5/3
            car2.reaction_time = 30/20
            car.update_acceleration()
            y_range[x] = car.acceleration
            car.velocity = 10

        for x in x_range:
            self.assertAlmostEqual(y_range[x],  y_range_expected[x])
        
    #Testing is Pareto relation works as intended
    def test_14_compare_units(self):
        # dummy ga instance 
        ga = GeneticAlgorithm(100, 100, True, True,
                        elite_part=0.1, 
                        population_size=10, 
                        speed_limit=20, 
                        crossover_probability=0.2, 
                        mutation_probability=0.6, 
                        population_number=2,
                        migration_part=0.2) 

        # 4 units to compare
        unit1 = {"light_cycles": [[0.22, 0.30, 0.1, 0.1], 
                                  [0.1, 0.50, 0.6, 0.1], 
                                  [0.12, 0.30, 0.18, 0.1],
                                  [0.22, 0.30, 0.81, 0.9]],
                "speed_limit": 25}
        unit2 = {"light_cycles": [[0.22, 0.30, 0.1, 0.1], 
                                  [0.22, 0.30, 0.1, 0.1], 
                                  [0.22, 0.30, 0.1, 0.1],
                                  [0.22, 0.30, 0.1, 0.1]],
                "speed_limit": 25}
        unit3 = {"light_cycles": [[0.22, 0.30, 0.1, 0.1], 
                                  [0.1, 0.50, 0.6, 0.1], 
                                  [0.12, 0.30, 0.18, 0.1],
                                  [0.22, 0.30, 0.81, 0.9]],
                "speed_limit": 25}
        unit4 = {"light_cycles": [[0.22, 0.30, 0.1, 0.1], 
                                  [0.1, 0.50, 0.6, 0.1], 
                                  [0.12, 0.30, 0.18, 0.1],
                                  [0.22, 0.30, 0.81, 0.9]],
                "speed_limit": 30}
        
        self.assertEqual(ga.compare_units(unit1, unit1), True)
        self.assertEqual(ga.compare_units(unit1, unit2), False)
        self.assertEqual(ga.compare_units(unit1, unit3), True)
        self.assertEqual(ga.compare_units(unit1, unit4), False)
            
    
    
    
        
    
            
        
        
if __name__ == '__main__':
    global visualise
    visualise = False
    n = 500
    x_range = np.array(range(n))
    y_range_expected = [0 for i in range((n))]
    
    WIDTH, HEIGHT = 1000, 1000
    position, angle, speed_limit = (100, 100), 180, 15
    car = Car(position, angle, WIDTH, HEIGHT, speed_limit)
    car.velocity = 10
    
    #Parameters that are usually random. For the sake of testing wwe set them to values as below
    car.minimum_dist = 1000//11*5/3
    car.reaction_time = 30/20
    
    for x in x_range:
        leading_dist=x + 1000//11*5/3
        car2 = Car((position[0] + leading_dist, position[1]), angle, WIDTH, HEIGHT, 5)
        
        car2.reaction_time = 30/20 
        car2.minimum_dist = 1000//11*5/3
        
        car.nearest_car = car2
        car.update_acceleration()
        y_range_expected[x] = car.acceleration
        car.velocity = 10
    for i in range(100):
        unittest.main(exit = False)
