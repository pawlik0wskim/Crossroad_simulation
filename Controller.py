import pygame
from Segment import Segment
import numpy as np
from Car import Car
from Node import Node
from utilities import *

# Collisions = 0
# Flow = 0

class Controller:
    def __init__(self, roads, starting_nodes, img=None, rect=None):
        self.roads=roads
        self.starting_nodes = starting_nodes
        self.roads_with_lights = []
        self.img= img
        self.rect = rect
        for road in roads:
            if road.light:
                self.roads_with_lights.append(road)
        

    

    # Draws all cars
    def draw(self, win, debug):
        win.blit(self.img, self.rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()    
            
        
        for road in self.roads:
            if debug:
                road.draw_path(win)
            road.draw_traffic_light(win)
            for car in road.cars:
                if debug:
                    pygame.draw.rect(win, [255, 255, 255], car.vision, width=3)
                    pygame.draw.rect(win, car.color, car.rect)
                car.draw(win)
    
    # Adds car on random spawning position        
    def spawn_car(self, speed_limit):
        rand = np.random.randint(0, len(self.starting_nodes))
        rand1 = rand+1
        node = self.starting_nodes[rand]
        if len(node.exiting_roads[0].cars)>0:
            previous_car = node.exiting_roads[0].cars[-1].rect # we don't want cars to spawn inside one another
            while np.abs(previous_car.center[0]-node.pos[0]+previous_car.center[1]-node.pos[1])<np.max([previous_car.width*(1+speed_limit/10), previous_car.height*(1+speed_limit/10)]) and rand1!=rand:
                rand1 = rand1+1 if rand1 < len(self.starting_nodes)-1 else 0
                node = self.starting_nodes[np.random.randint(0, len(self.starting_nodes))]
                if len(node.exiting_roads[0].cars)>0:
                    previous_car = node.exiting_roads[0].cars[-1].rect
            if rand1==rand:
                return None
        if node.pos[1]==0:
            angle = 180
        elif node.pos[1]==HEIGHT:
            angle = 0
        elif node.pos[0]==WIDTH:
            angle = 90
        else:
            angle = 270
        car = Car(node.pos, angle, WIDTH, HEIGHT, speed_limit)
        node.exiting_roads[0].cars.append(car)
        return car
        
        
    #Moves each car forward
    def move_cars(self, right_prob, left_prob):
        curr_flow = 0
        curr_red_lights = 0
        for road in self.roads:
            for car in road.cars:
                flow, red_lights = road.calculate_car_next_pos(car, right_prob, left_prob)
                curr_flow += flow
                curr_red_lights += red_lights
                car.mask = pygame.mask.from_surface(Car.get_img_as_surface(car.rotate_image()))
        return curr_flow, curr_red_lights
    

    #Removes cars that collided with each other            
    def check_for_car_collision(self):
        curr_collisions = 0
        for road in self.roads:
            for car in road.cars:
                for road2 in self.roads:
                    for car2 in road2.cars:
                        if car.collide(car2) != None and car in road.cars and car2 in road2.cars and car != car2:
                            road.cars.remove(car) 
                            road2.cars.remove(car2)
                            curr_collisions+=1
                            continue
        return curr_collisions
                        
    #Method manages what does car and the nearest car to it see as hindrance
    def process_car_neighborhood(self, car, road):
        road_type, road_direction = road.type, road.direction
        min_dist = np.Inf # distance to nearest car(if it exists)
        nearest_car = None # nearest car(if it exists)
        r = None # road type of nearest car(if it exists)
        r_direction = None # road direction of nearest car(if it exists)
        for road in self.roads:
            collided_idxs = car.vision.collidelistall(road.cars)
            for idx in collided_idxs:
                dist = l2_dist(car.rect.center, road.cars[idx].rect.center)
                if dist < min_dist and car is not road.cars[idx]:
                    
                    r = road.type
                    r_direction = road.direction
                    if not (r == "arc" and road_type == "arc" and cross_product(road_direction, r_direction) < 0):
                        nearest_car = road.cars[idx]
                        min_dist = dist
        
        if nearest_car is not None:
            if nearest_car.nearest_car == car:
                if car.dist_driven > nearest_car.dist_driven:
                    nearest_car.color  = "Green"
                    nearest_car = None
                    car.color = "Yellow"
                    
                else:
                    nearest_car.nearest_car = None
                    nearest_car.color  = "Yellow"
                    car.color = "Green"
        car.nearest_car = nearest_car
        
    # Changes the traffic lights according to light cycles of all roads 
    def update_traffic_lights(self, i, light_cycle_time):
        for road in self.roads_with_lights:
            for cycle in road.light_cycle:
                if i%light_cycle_time==np.round(cycle*light_cycle_time):
                    road.light_color = road.light_color + 1 if road.light_color<3 else 0
    
   
        



#Method generates main crossroad map
def generate_crossroad(WIDTH, HEIGHT):
    light_cycle = [0.25, 0.4, 0.85, 0.9]
    #nodes
    node1 = Node((11/24*WIDTH, 0))
    node2 = Node((13/24*WIDTH, 0))
    node3 = Node((11/24*WIDTH, HEIGHT/3))
    node4 = Node((13/24*WIDTH, 1/3*HEIGHT))
    node5 = Node((11/24*WIDTH, 2/3*HEIGHT))
    node6 = Node((13/24*WIDTH, 2/3*HEIGHT))
    node7 = Node((11/24*WIDTH, HEIGHT))
    node8 = Node((13/24*WIDTH, HEIGHT))
    node9 = Node((2*WIDTH/3, HEIGHT*11/24))
    node10 = Node((WIDTH*2/3, HEIGHT*13/24))
    node11 = Node((WIDTH/3, HEIGHT*11/24))
    node12 = Node((WIDTH/3, HEIGHT*13/24))
    node13 = Node((WIDTH, HEIGHT*11/24))
    node14 = Node((WIDTH, HEIGHT*13/24))
    node15 = Node((0, HEIGHT*11/24))
    node16 = Node((0, HEIGHT*13/24))
    
    

    roads = []
    #Vertical
    roads.append(Segment(node1, node3, "straight", light = True, light_cycle = light_cycle))#top
    roads.append(Segment(node4, node2, "straight"))
    roads.append(Segment(node5, node7, "straight"))#bottom
    roads.append(Segment(node8, node6, "straight", light = True, light_cycle = light_cycle))
    #Horrizontal
    roads.append(Segment(node11, node15, "straight"))#left
    roads.append(Segment(node16, node12, "straight", light = True, light_cycle = light_cycle))
    roads.append(Segment(node13, node9, "straight", light = True, light_cycle = light_cycle))#right
    roads.append(Segment(node10, node14, "straight"))
    #Bottom turns
    roads.append(Segment(node6,node10, type = "arc", curve = "right"))
    roads.append(Segment(node6,node11, type = "arc", curve = "left"))
    roads.append(Segment(node6,node4, "straight"))
    #Left turns
    roads.append(Segment(node12,node5, type = "arc", curve = "right"))
    roads.append(Segment(node12,node4, type = "arc", curve = "left"))
    roads.append(Segment(node12,node10, "straight"))
    #Top turns
    roads.append(Segment(node3,node11, type = "arc", curve = "right"))
    roads.append(Segment(node3,node10, type = "arc", curve = "left"))
    roads.append(Segment(node3,node5, "straight"))
    #Right turns
    roads.append(Segment(node9,node4, type = "arc", curve = "right"))
    roads.append(Segment(node9,node5, type = "arc", curve = "left"))
    roads.append(Segment(node9,node11, "straight"))
    return Controller(roads, [ node1, node8, node13, node16]) 


#Method generates map used for testing
def generate_one_straight_one_left_turn(WIDTH, HEIGHT):
    node1 = Node((11/24*WIDTH, 0))
    node2 = Node((13/24*WIDTH, 0))
    node3 = Node((11/24*WIDTH, HEIGHT/3))
    node4 = Node((13/24*WIDTH, 1/3*HEIGHT))
    node14 = Node((WIDTH, HEIGHT*13/24))
    node10 = Node((WIDTH*2/3, HEIGHT*13/24))
    node8 = Node((13/24*WIDTH, HEIGHT))
    node6 = Node((13/24*WIDTH, 2/3*HEIGHT)) 

    roads = []
    roads.append(Segment(node1, node3, "straight"))
    roads.append(Segment(node4, node2, "straight"))
    roads.append(Segment(node8, node6, "straight"))
    roads.append(Segment(node10, node14, "straight"))
    roads.append(Segment(node6,node4, "straight"))
    roads.append(Segment(node3,node10, type = "arc", curve = "left"))
    return Controller(roads, [node1, node8]) 


#Method generates map used for testing
def generate_test_map(WIDTH, HEIGHT, lights):
    
    
    #Outer nodes
    node1 = Node((11/24*WIDTH, 0))
    node2 = Node((11/24*WIDTH, HEIGHT/3))
    node3 = Node((11/24*WIDTH, 2/3*HEIGHT))
    node4 = Node((11/24*WIDTH, HEIGHT))
    
    roads = []
    #Vertical
    roads.append(Segment(node1, node2, "straight", light = lights))
    roads.append(Segment(node2,node3, "straight"))
    roads.append(Segment(node3, node4, "straight"))
    

    return Controller(roads, [node1])
  


 











# def generate_roundabout(WIDTH, HEIGHT):
#     roads = []
#     #Vertical
#     roads.append(Segment((7/13*WIDTH, HEIGHT*2/13),(7/13*WIDTH, 0), "straight"))#top
#     roads.append(Segment((6/13*WIDTH, 0),(6/13*WIDTH, HEIGHT*2/13), "straight"))
#     roads.append(Segment((7/13*WIDTH, HEIGHT),(7/13*WIDTH, HEIGHT*11/13), "straight"))#bottom
#     roads.append(Segment((6/13*WIDTH, HEIGHT*11/13),(6/13*WIDTH, HEIGHT), "straight"))
#     #Horrizontal
#     roads.append(Segment((0, HEIGHT*7/13),(WIDTH*2/13, HEIGHT*7/13), "straight"))#left
#     roads.append(Segment((WIDTH*2/13, HEIGHT*6/13),(0, HEIGHT*6/13), "straight"))
#     roads.append(Segment((WIDTH*11/13, HEIGHT*7/13),(WIDTH, HEIGHT*7/13), "straight"))#right
#     roads.append(Segment((WIDTH, HEIGHT*6/13),(WIDTH*11/13, HEIGHT*6/13), "straight"))
#     #Entering roundabout
#     #Vertical
#     roads.append(Segment((7/13*WIDTH, HEIGHT*2/13),(8/13*WIDTH, HEIGHT*3/13), "arc", "left"))#top
#     roads.append(Segment((6/13*WIDTH, HEIGHT*2/13),(5/13*WIDTH, HEIGHT*3/13), "arc", "right"))
#     roads.append(Segment((7/13*WIDTH, HEIGHT*11/13),(8/13*WIDTH, HEIGHT*10/13), "arc", "right"))#bottom
#     roads.append(Segment((6/13*WIDTH, HEIGHT*11/13),(5/13*WIDTH, HEIGHT*10/13), "arc", "left"))
#     #Horrizontal
#     roads.append(Segment((WIDTH*2/13, HEIGHT*7/13),(WIDTH*3/13, HEIGHT*8/13), "arc", "right"))#left
#     roads.append(Segment((WIDTH*2/13, HEIGHT*6/13),(WIDTH*3/13, HEIGHT*5/13), "arc", "left"))
#     roads.append(Segment((WIDTH*11/13, HEIGHT*7/13),(WIDTH*10/13, HEIGHT*8/13), "arc", "left"))#right
#     roads.append(Segment((WIDTH*11/13, HEIGHT*6/13),(WIDTH*10/13, HEIGHT*5/13), "arc", "right"))
    
#     #####Roundobout
#     #Straight
#     roads.append(Segment((8/13*WIDTH, HEIGHT*3/13),(5/13*WIDTH, HEIGHT*3/13), "straight"))
#     roads.append(Segment((5/13*WIDTH, HEIGHT*10/13),(8/13*WIDTH, HEIGHT*10/13), "straight"))
#     roads.append(Segment((WIDTH*3/13, HEIGHT*5/13),(WIDTH*3/13, HEIGHT*8/13), "straight"))
#     roads.append(Segment((WIDTH*10/13, HEIGHT*8/13),(WIDTH*10/13, HEIGHT*5/13), "straight"))
#     #Arc
#     roads.append(Segment((5/13*WIDTH, HEIGHT*3/13),(WIDTH*3/13, HEIGHT*5/13), "arc", "left"))
#     roads.append(Segment((WIDTH*3/13, HEIGHT*8/13),(5/13*WIDTH, HEIGHT*10/13), "arc", "left"))
#     roads.append(Segment((8/13*WIDTH, HEIGHT*10/13),(WIDTH*10/13, HEIGHT*8/13), "arc", "left"))
#     roads.append(Segment((WIDTH*10/13, HEIGHT*5/13),(8/13*WIDTH, HEIGHT*3/13), "arc", "left"))
#     return Map(roads)   
