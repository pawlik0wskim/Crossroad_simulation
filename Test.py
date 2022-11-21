import unittest
from Map import *
from utilities import *
from Car import *
from Node import Node
from Application import *
from GeneticAlgorithm import GeneticAlgorithm
import numpy as np

zero = 10**(-100)

class Test(unittest.TestCase):
    #Main simulation loop with car spawning and traffic jam recognising mechanisms removed
    def main_loop(self, test_map, visualise, max_iter = 300):
        if visualise:
            win = pygame.display.set_mode((WIDTH, HEIGHT))   
            clock=pygame.time.Clock()
            test_map.img = pygame.transform.scale(pygame.image.load(r"map_crossroad.png"),(WIDTH,HEIGHT)).convert()
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
            Flow+=test_map.move_cars( 0, 0)
            Collisions+=test_map.check_for_car_collision()
            if i >= max_iter:
                break
            if visualise:
                pygame.display.update()
                clock.tick(FPS)
                
        return Collisions, Flow
    
    #Test if cars correctly elave intersection
    def test_0_car_leaves_intersection(self):
        test_map = generate_test_map(1000,1000, False)
        
        car = test_map.spawn_car(4,4)
        
        _ , Flow = self.main_loop(test_map, visualise, max_iter = 300)
                
        self.assertEqual(Flow, 1) #Car has to leave intersection
    
    #Test of collision mechanisms
    def test_1_collisions(self):
        test_map = generate_test_map(1000,1000, False)
        
        car = test_map.spawn_car(zero,4)
        car.rect.center = (test_map.roads[0].end_node.pos[0],test_map.roads[0].end_node.pos[1]*3/4)
        car2 = test_map.spawn_car(6,4)
        car2.maximum_deceleration = zero
        
        Collisions , _ = self.main_loop(test_map, visualise, max_iter = 100)
                
        self.assertEqual(Collisions, 1) #Cars have to collide
        
    #Test if cars will stop on red light
    def test_2_stopping_on_red_light(self):
        test_map = generate_test_map(1000,1000, True)
        for i in range(len(test_map.roads_with_lights)):
            test_map.roads_with_lights[i].light_cycle = [2,2,2,2] 
            test_map.roads_with_lights[i].light = 2
        
        car = test_map.spawn_car(3,4)
        _ , Flow = self.main_loop(test_map, visualise, max_iter = 200)
                
        self.assertEqual(Flow, 0) #Car can't leave road segment
        self.assertGreater(1/2, car.velocity) #Car has to stop(velocity smaller than 1/2)
        self.assertGreater(test_map.roads[0].end_node.pos[1], car.rect.center[1]+car.rect.height/2) #Car has to stop before end of segment
    
    #Test if cars stop when driver sees another stationaary vehicle
    def test_3_stopping_to_vehicle(self):
        test_map = generate_test_map(1000,1000, False)
        
        car = test_map.spawn_car(zero,4)
        car.rect.center = test_map.roads[0].end_node.pos
        
        car2 = test_map.spawn_car(3,4)
        _ , Flow = self.main_loop(test_map, visualise, max_iter = 200)
                
        self.assertEqual(Flow, 0) #Cars can't leave road segment
        self.assertGreater(1/2, car2.velocity) #Car has to stop(velocity smaller than 1/2)
        self.assertGreaterEqual(car.rect.center[1], car2.rect.center[1]+car2.minimum_dist) #Car has to leave some space before vehicles
     
    #Test if car will slow down if positioned behined slower vehicle   
    def test_4_adjustting_velocity(self):
        test_map = generate_test_map(1000,1000, False)
        
        car = test_map.spawn_car(4,4)
        car.rect.center = (test_map.roads[0].end_node.pos[0],test_map.roads[0].end_node.pos[1]*3/4)
        
        car2 = test_map.spawn_car(6,4)
        Collisions , _ = self.main_loop(test_map, visualise, max_iter = 100)
                
        self.assertGreater(6, car2.velocity) #Second car has to lower velocity
        self.assertGreaterEqual(car2.velocity, 4) #Second car can't go slower than the first one
        self.assertGreaterEqual(car.rect.center[1], car2.rect.center[1]+car2.minimum_dist) #Car has to leave some space before vehicles
        self.assertEqual(Collisions, 0) #Cars cannot collide

    #Test if car driving straight will have priority on car turning left
    def test_5_car_priority_straight(self):
        test_map = generate_one_straight_one_left_turn(1000,1000)
        
        node = test_map.starting_nodes[0]
        car = Car(node.pos, 180, WIDTH, HEIGHT, 3, 4)
        node.exiting_roads[0].cars.append(car)
        
        node2 = test_map.starting_nodes[1]
        car2 = Car(node2.pos, 0, WIDTH, HEIGHT, 3, 4)
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
    def test_6_car_priority_turning(self):
        test_map = generate_one_straight_one_left_turn(1000,1000)
        
        node = test_map.starting_nodes[0]
        car = Car(node.pos, 180, WIDTH, HEIGHT, 3.5, 4)
        node.exiting_roads[0].cars.append(car)
        
        node2 = test_map.starting_nodes[1]
        car2 = Car(node2.pos, 0, WIDTH, HEIGHT, 3, 4)
        node2.exiting_roads[0].cars.append(car2)
        
        Collisions , Flow = self.main_loop(test_map, visualise, max_iter = 350)
        
        cars = []
        for road in test_map.roads:
            for car in road.cars:
                cars.append(car)
                
        self.assertEqual(Flow, 1) #One car has to leave intersection
        self.assertEqual(len(cars), 1)
        self.assertEqual(cars[0], car2) #It has to be a car turning
        self.assertEqual(Collisions, 0) #Cars cannot collide
    
    # Test if crossover mechanism works correctly
    def test_7_crossover(self):
        np.random.seed(123)
        ga = GeneticAlgorithm(10, 1000, elite_part=0.3, population_size=10, population_number=5, mutation_probability=0.2)
        parent1 = {'s': 10, 'tl': [[0.2, 0.1, 0.8, 0.5], [0.2, 0.1, 0.8, 0.5], [0.2, 0.1, 0.8, 0.5], [0.2, 0.1, 0.8, 0.5]]}
        parent2 = {'s': 25, 'tl': [[0.0, 0.7, 0.3, 0.9], [0.0, 0.7, 0.3, 0.9], [0.0, 0.7, 0.3, 0.9], [0.0, 0.7, 0.3, 0.9]]}
        child = ga.crossover(parent1, parent2)
        
        self.assertEqual(child['s'], 25)
        expected_tl = [[0.0, 0.7, 0.3, 0.9], [0.2, 0.1, 0.8, 0.5], [0.0, 0.7, 0.3, 0.9], [0.2, 0.1, 0.8, 0.5]]
        for i in range(4):
            self.assertEqual(child['tl'][i], expected_tl[i])
    
    # Test if elite number(number of organisms, which will be taken through selection without any changes)
    # is calculated correctly
    def test_8_elite_num(self):
        ga = GeneticAlgorithm(10, 1000, elite_part=0.3, population_size=10, population_number=5, mutation_probability=0.2)
        self.assertEqual(ga.elite_num, int(0.3*10))
    
    # Test if default parameters are inserted correctly
    def test_9_default_parameters(self):
        ga = GeneticAlgorithm(10, 1000)
        self.assertEqual(ga.pop_size, 3)
        self.assertEqual(len(ga.populations), 3)
        self.assertEqual(ga.mutation_prob, 0.6)
        self.assertEqual(ga.elite_num, int(0.2*3))
        
        
        
    
    
    
    
        
    
            
        
        
if __name__ == '__main__':
    global visualise
    visualise = True
    unittest.main(exit = False)
