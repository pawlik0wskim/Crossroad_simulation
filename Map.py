import pygame
from Road import Road
import numpy as np
from Car import Car
from Node import Node
import time
from utilities import visualize, cross_product, l2_dist, WIDTH, HEIGHT, FPS

Collisions = 0
Flow = 0

class Map:
    def __init__(self, roads, starting_nodes, light_cycle_time = 10*FPS):
        self.roads=roads
        self.starting_nodes = starting_nodes
        self.light_cycle_time = light_cycle_time

    # Draws all paths cars travel along 
    def show_paths(self, win):
        for road in self.roads:
            road.draw_path(win)

    # Draws all cars
    def show_vehicles(self, win):
        for road in self.roads:
            for car in road.cars:
                car.draw(win)
                pygame.draw.rect(win, [255, 255, 255], car.vision, width=3)
                # pygame.draw.rect(win, [255, 0, 0], car.rect)
    
    # Adds car on random spawning position        
    def spawn_car(self, WIDTH, HEIGHT):
        rand = np.random.randint(0, len(self.starting_nodes))
        rand1 = rand+1
        node = self.starting_nodes[rand]
        if len(node.exiting_roads[0].cars)>0:
            previous_car = node.exiting_roads[0].cars[-1].rect # we don't want cars to spawn inside one another
            while np.abs(previous_car.center[0]-node.pos[0]+previous_car.center[1]-node.pos[1])<np.max([previous_car.width, previous_car.height]) and rand1!=rand:
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
        car = Car(node.pos, angle, WIDTH, HEIGHT)
        node.exiting_roads[0].cars.append(car)

    def move_cars(self):
        global Flow
        for road in self.roads:
            for car in road.cars:
                Flow+=road.calculate_car_next_pos(car)
    

    #Removes cars that collided with each other            
    def check_for_car_collision(self):
        global Collisions
        for road in self.roads:
            for car in road.cars:
                for road2 in self.roads:
                    for car2 in road2.cars:
                        if car.collide(car2) != None and car in road.cars and car2 in road2.cars and car != car2:
                            road.cars.remove(car) 
                            road2.cars.remove(car2)
                            Collisions+=1
                            print("collision")
                            continue
                        
    #Method returns nearest car visible for the driver
    def get_nearest_car(self, car, road_type, road_direction):
        min_dist = np.Inf # distance to nearest car(if it exists)
        c = None # nearest car(if it exists)
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
                        c = road.cars[idx]
                        min_dist = dist


        return c
    
    def update_traffic_lights(self, i):
        for road in self.roads:
            if road.light:
                for cycle in road.light_cycle:
                    if i%self.light_cycle_time==cycle*self.light_cycle_time:
                        road.light_color = road.light_color + 1 if road.light_color<3 else 0
    
    # updates car vision and finds new nearest car
    def process_car(self, car, road):
        car.update_vision(road.direction, road.type, road.curve)
        car.nearest_car = self.get_nearest_car(car, road.type, road.direction)
        if car.nearest_car is not None:
            if car.nearest_car.nearest_car is car:
                if car.dist_driven > car.nearest_car.dist_driven:
                    car.nearest_car = None
                else:
                    car.nearest_car.nearest_car = None







def generate_crossroad(WIDTH, HEIGHT):
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
    roads.append(Road(node1, node3, "straight", light = True))#top
    roads.append(Road(node4, node2, "straight"))
    roads.append(Road(node5, node7, "straight"))#bottom
    roads.append(Road(node8, node6, "straight", light = True))
    #Horrizontal
    roads.append(Road(node11, node15, "straight"))#left
    roads.append(Road(node16, node12, "straight", light = True))
    roads.append(Road(node13, node9, "straight", light = True))#right
    roads.append(Road(node10, node14, "straight"))
    #Bottom turns
    roads.append(Road(node6,node10, type = "arc", curve = "right"))
    roads.append(Road(node6,node11, type = "arc", curve = "left"))
    roads.append(Road(node6,node4, "straight"))
    #Left turns
    roads.append(Road(node12,node5, type = "arc", curve = "right"))
    roads.append(Road(node12,node4, type = "arc", curve = "left"))
    roads.append(Road(node12,node10, "straight"))
    #Top turns
    roads.append(Road(node3,node11, type = "arc", curve = "right"))
    roads.append(Road(node3,node10, type = "arc", curve = "left"))
    roads.append(Road(node3,node5, "straight"))
    #Right turns
    roads.append(Road(node9,node4, type = "arc", curve = "right"))
    roads.append(Road(node9,node5, type = "arc", curve = "left"))
    roads.append(Road(node9,node11, "straight"))
    return Map(roads, [ node1, node8, node13, node16]) 



def test_map(WIDTH, HEIGHT):
    
    
    #Outer nodes
    node1 = Node((7/18*WIDTH, 0))
    node2 = Node((11/18*WIDTH, 0))
    node3 = Node((7/18*WIDTH, HEIGHT/3))
    node4 = Node((11/18*WIDTH, 1/3*HEIGHT))
    node5 = Node((7/18*WIDTH, 2/3*HEIGHT))
    node6 = Node((11/18*WIDTH, 2/3*HEIGHT))
    node7 = Node((7/18*WIDTH, HEIGHT))
    node8 = Node((11/18*WIDTH, HEIGHT))
    
    
    roads = []
    #Vertical
    roads.append(Road(node1, node3, "straight"))
    roads.append(Road(node3,node5, "straight"))
    roads.append(Road(node5, node7, "straight"))

    roads.append(Road(node6, node4, "straight"))
    roads.append(Road(node8, node6, "straight"))#bottom
    roads.append(Road(node4, node2, "straight"))
  

    

    return Map(roads, [node1, node8])
  


 
def test(map): 
    if visualize:
        win = pygame.display.set_mode((WIDTH, HEIGHT))   
        clock=pygame.time.Clock()
        map_img = pygame.transform.scale(pygame.image.load(r"map_crossroad.png"),(WIDTH,HEIGHT))
    start_time = time.time()
    # map_rect = map_img.get_rect(topleft = (0,0))
    map_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
    i=0
    prev_flow = 0
    while(True):
        loop_start = time.time()
        if visualize:
            win.blit(map_img, map_rect)
        map.check_for_car_collision()
        i+=1
        if visualize:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()    
            map.show_paths(win)
            map.show_vehicles(win)
        
        for road in map.roads:
            if visualize:
                road.draw_traffic_light(win)
            for car in road.cars:
                 map.process_car(car, road)

        if i%FPS == 0:
            map.spawn_car(WIDTH, HEIGHT)
        map.update_traffic_lights(i)
        map.move_cars()
        if visualize:
            pygame.display.update()
            clock.tick(FPS)
        loop_time = (- loop_start + time.time())
        if i%600*FPS == 0:
            print(f"Flow: {Flow}, Collisions: {Collisions}, Time: {(time.time() - start_time)}, FPS: {1/loop_time}")
            # if prev_flow==Flow:
            #     break
            # prev_flow = Flow
test(generate_crossroad(WIDTH, HEIGHT))














# def generate_roundabout(WIDTH, HEIGHT):
#     roads = []
#     #Vertical
#     roads.append(Road((7/13*WIDTH, HEIGHT*2/13),(7/13*WIDTH, 0), "straight"))#top
#     roads.append(Road((6/13*WIDTH, 0),(6/13*WIDTH, HEIGHT*2/13), "straight"))
#     roads.append(Road((7/13*WIDTH, HEIGHT),(7/13*WIDTH, HEIGHT*11/13), "straight"))#bottom
#     roads.append(Road((6/13*WIDTH, HEIGHT*11/13),(6/13*WIDTH, HEIGHT), "straight"))
#     #Horrizontal
#     roads.append(Road((0, HEIGHT*7/13),(WIDTH*2/13, HEIGHT*7/13), "straight"))#left
#     roads.append(Road((WIDTH*2/13, HEIGHT*6/13),(0, HEIGHT*6/13), "straight"))
#     roads.append(Road((WIDTH*11/13, HEIGHT*7/13),(WIDTH, HEIGHT*7/13), "straight"))#right
#     roads.append(Road((WIDTH, HEIGHT*6/13),(WIDTH*11/13, HEIGHT*6/13), "straight"))
#     #Entering roundabout
#     #Vertical
#     roads.append(Road((7/13*WIDTH, HEIGHT*2/13),(8/13*WIDTH, HEIGHT*3/13), "arc", "left"))#top
#     roads.append(Road((6/13*WIDTH, HEIGHT*2/13),(5/13*WIDTH, HEIGHT*3/13), "arc", "right"))
#     roads.append(Road((7/13*WIDTH, HEIGHT*11/13),(8/13*WIDTH, HEIGHT*10/13), "arc", "right"))#bottom
#     roads.append(Road((6/13*WIDTH, HEIGHT*11/13),(5/13*WIDTH, HEIGHT*10/13), "arc", "left"))
#     #Horrizontal
#     roads.append(Road((WIDTH*2/13, HEIGHT*7/13),(WIDTH*3/13, HEIGHT*8/13), "arc", "right"))#left
#     roads.append(Road((WIDTH*2/13, HEIGHT*6/13),(WIDTH*3/13, HEIGHT*5/13), "arc", "left"))
#     roads.append(Road((WIDTH*11/13, HEIGHT*7/13),(WIDTH*10/13, HEIGHT*8/13), "arc", "left"))#right
#     roads.append(Road((WIDTH*11/13, HEIGHT*6/13),(WIDTH*10/13, HEIGHT*5/13), "arc", "right"))
    
#     #####Roundobout
#     #Straight
#     roads.append(Road((8/13*WIDTH, HEIGHT*3/13),(5/13*WIDTH, HEIGHT*3/13), "straight"))
#     roads.append(Road((5/13*WIDTH, HEIGHT*10/13),(8/13*WIDTH, HEIGHT*10/13), "straight"))
#     roads.append(Road((WIDTH*3/13, HEIGHT*5/13),(WIDTH*3/13, HEIGHT*8/13), "straight"))
#     roads.append(Road((WIDTH*10/13, HEIGHT*8/13),(WIDTH*10/13, HEIGHT*5/13), "straight"))
#     #Arc
#     roads.append(Road((5/13*WIDTH, HEIGHT*3/13),(WIDTH*3/13, HEIGHT*5/13), "arc", "left"))
#     roads.append(Road((WIDTH*3/13, HEIGHT*8/13),(5/13*WIDTH, HEIGHT*10/13), "arc", "left"))
#     roads.append(Road((8/13*WIDTH, HEIGHT*10/13),(WIDTH*10/13, HEIGHT*8/13), "arc", "left"))
#     roads.append(Road((WIDTH*10/13, HEIGHT*5/13),(8/13*WIDTH, HEIGHT*3/13), "arc", "left"))
#     return Map(roads)   
