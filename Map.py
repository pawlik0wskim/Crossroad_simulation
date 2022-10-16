import pygame
from Road import Road
import numpy as np
from Car import Car
from Node import Node

FPS = 60

class Map:
    def __init__(self, roads, nodes, starting_nodes):
        self.roads = roads
        self.nodes = nodes
        self.starting_nodes = starting_nodes
        self.cars = []

    # Draws all paths cars travel along 
    def show_paths(self, win):
        for road in self.roads:
            road.draw_path(win)

    # Draws all cars
    def show_vehicles(self, win):
        for road in self.roads:
            for car in road.cars:
                car.draw(win)
    
    #Adds car on random spawning position        
    def spawn_car(self, WIDTH, HEIGHT):
        node = self.starting_nodes[np.random.randint(0, len(self.starting_nodes))]
        if node.pos[1] == 0:
            angle = 180
        elif node.pos[1] == HEIGHT:
            angle = 0
        elif node.pos[0] == WIDTH:
            angle = 90
        else:
            angle = 270
        car = Car(node.pos, angle, WIDTH, HEIGHT)
        node.exiting_roads[0].cars.append(car)
        self.cars.append(car)

    def move_cars(self):
        for road in self.roads:
            for car in road.cars:
                road.calculate_car_next_pos(car)
    



WIDTH, HEIGHT = (1000,1000)
def generate_crossroad(WIDTH, HEIGHT):
    #nodes
    node1 = Node((7/18*WIDTH, 0))
    node2 = Node((11/18*WIDTH, 0))
    node3 = Node((7/18*WIDTH, HEIGHT/3))
    node4 = Node((11/18*WIDTH, 1/3*HEIGHT))
    node5 = Node((7/18*WIDTH, 2/3*HEIGHT))
    node6 = Node((11/18*WIDTH, 2/3*HEIGHT))
    node7 = Node((7/18*WIDTH, HEIGHT))
    node8 = Node((11/18*WIDTH, HEIGHT))
    node9 = Node((2*WIDTH/3, HEIGHT*7/18))
    node10 = Node((WIDTH*2/3, HEIGHT*11/18))
    node11 = Node((WIDTH/3, HEIGHT*7/18))
    node12 = Node((WIDTH/3, HEIGHT*11/18))
    node13 = Node((WIDTH, HEIGHT*7/18))
    node14 = Node((WIDTH, HEIGHT*11/18))
    node15 = Node((0, HEIGHT*7/18))
    node16 = Node((0, HEIGHT*11/18))
    
    nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14, node15, node16]
    

    roads = []
    #Vertical
    roads.append(Road(node1, node3, "straight", road_direction = "vertical_down"))#top
    roads.append(Road(node4, node2, "straight", road_direction = "vertical_up"))
    roads.append(Road(node5, node7, "straight", road_direction = "vertical_down"))#bottom
    roads.append(Road(node8, node6, "straight", road_direction = "vertical_up"))
    #Horrizontal
    roads.append(Road(node11, node15, "straight", road_direction = "horizontal_left"))#left
    roads.append(Road(node16, node12, "straight", road_direction="horizontal_right"))
    roads.append(Road(node13, node9, "straight", road_direction = "horizontal_left"))#right
    roads.append(Road(node10, node14, "straight", road_direction="horizontal_right"))
    #Bottom turns
    roads.append(Road(node6,node10, type = "arc", curve = "right"))
    roads.append(Road(node6,node11, type = "arc", curve = "left", road_direction = "vertical_up_left"))
    roads.append(Road(node6,node4, "straight", road_direction = "vertical_up"))
    #Left turns
    roads.append(Road(node12,node5, type = "arc", curve = "right"))
    roads.append(Road(node12,node4, type = "arc", curve = "left", road_direction="horizontal_right_left"))
    roads.append(Road(node12,node10, "straight", road_direction="horizontal_right"))
    #Top turns
    roads.append(Road(node3,node11, type = "arc", curve = "right"))
    roads.append(Road(node3,node10, type = "arc", curve = "left", road_direction = "vertical_down_left"))
    roads.append(Road(node3,node5, "straight", road_direction = "vertical_down"))
    #Right turns
    roads.append(Road(node9,node4, type = "arc", curve = "right"))
    roads.append(Road(node9,node5, type = "arc", curve = "left", road_direction = "horizontal_left_left"))
    roads.append(Road(node9,node11, "straight", road_direction = "horizontal_left"))
    return Map(roads, nodes, [node1, node8, node13, node16])



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
    nodes = [node1, node2, node3, node4, node5, node6, node7, node8]
    
    
    roads = []
    #Vertical
    roads.append(Road(node1, node3, "straight"))
    roads.append(Road(node3,node5, "straight"))
    roads.append(Road(node5, node7, "straight"))

    roads.append(Road(node6, node4, "straight"))
    roads.append(Road(node8, node6, "straight"))#bottom
    roads.append(Road(node4, node2, "straight"))
  

    

    return Map(roads, nodes, [node1, node8])
  


 
def test(map):    
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock=pygame.time.Clock()
    i=0
    while(True):
        rect = pygame.Rect(0,0,WIDTH, HEIGHT)
        pygame.draw.rect(win,"Black", rect)
        i+=1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()    
        map.show_paths(win)
        map.show_vehicles(win)
        
        if i%FPS == 0:
        # if i == 10:
            map.spawn_car(WIDTH, HEIGHT)
        for k in range(len(map.cars)):
            # pygame.draw.rect(win, [255, 255, 255], map.cars[k].rect)
            pygame.draw.rect(win, [255, 0, 0], map.cars[k].vision)
        map.move_cars()
        pygame.display.update()
        clock.tick(FPS)
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
