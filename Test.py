import unittest
from Map import *
from utilities import *
from Car import *
from Node import Node
from Application import *

zero = 10**(-100)

class Test(unittest.TestCase):
    def main_loop(self, test_map, visualise, max_iter = 100):
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
    
    def test_car_leaves_road(self):
        test_map = generate_test_map(1000,1000, False)
        
        car = test_map.spawn_car(4,4)
        
        _ , Flow = self.main_loop(test_map, visualise, max_iter = 300)
                
        self.assertEqual(Flow, 1) #Car has to leave intersection
    
    # def test_collisions(self):
    #     test_map = generate_test_map(1000,1000, False)
        
    #     car = test_map.spawn_car(zero,4)
    #     car.rect.center = (test_map.roads[0].end_node.pos[0],test_map.roads[0].end_node.pos[1]*3/4)
    #     car2 = test_map.spawn_car(6,4)
    #     car2.maximum_deceleration = zero
        
    #     Collisions , _ = self.main_loop(test_map, visualise, max_iter = 300)
                
    #     self.assertEqual(Collisions, 1) #Car has to leave intersection   
        
    def test_stopping_on_red_light(self):
        test_map = generate_test_map(1000,1000, True)
        for i in range(len(test_map.roads_with_lights)):
            test_map.roads_with_lights[i].light_cycle = [2,2,2,2] 
            test_map.roads_with_lights[i].light = 2
        
        car = test_map.spawn_car(3,4)
        _ , Flow = self.main_loop(test_map, visualise)
                
        self.assertEqual(Flow, 0) #Car can't leave road segment
        self.assertGreater(1/2, car.velocity) #Car has to stop(velocity smaller than 1/2)
        self.assertGreater(test_map.roads[0].end_node.pos[1], car.rect.center[1]+car.rect.height/2) #Car has to stop before end of segment
    
    def test_stopping_to_vehicle(self):
        test_map = generate_test_map(1000,1000, False)
        
        car = test_map.spawn_car(zero,4)
        car.rect.center = test_map.roads[0].end_node.pos
        
        car2 = test_map.spawn_car(3,4)
        _ , Flow = self.main_loop(test_map, visualise)
                
        self.assertEqual(Flow, 0) #Cars can't leave road segment
        self.assertGreater(1/2, car2.velocity) #Car has to stop(velocity smaller than 1/2)
        self.assertGreaterEqual(car.rect.center[1], car2.rect.center[1]+car2.minimum_dist) #Car has to leave some space before vehicles
        
    def test_adjustting_velocity(self):
        test_map = generate_test_map(1000,1000, False)
        
        car = test_map.spawn_car(4,4)
        car.rect.center = (test_map.roads[0].end_node.pos[0],test_map.roads[0].end_node.pos[1]*3/4)
        
        car2 = test_map.spawn_car(6,4)
        _ , Flow = self.main_loop(test_map, visualise)
                
        self.assertGreater(6, car2.velocity) #Second car has to lower velocity
        self.assertGreaterEqual(car2.velocity, 4) #Second car can't go slower than the first one
        self.assertGreaterEqual(car.rect.center[1], car2.rect.center[1]+car2.minimum_dist) #Car has to leave some space before vehicles
        self.assertEqual(Collisions, 0) #Cars cannot collide
    
    
    
    
        
    
            
        
        
if __name__ == '__main__':
    global visualise
    visualise = True
    unittest.main(exit = False)