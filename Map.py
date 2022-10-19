import pygame
from Road import Road
import numpy as np
from Car import Car
from Node import Node

FPS = 30

class Map:
    def __init__(self, roads, starting_nodes):
        self.roads=roads
        self.starting_nodes = starting_nodes

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
    
    #Adds car on random spawning position        
    def spawn_car(self, WIDTH, HEIGHT):
        rand = np.random.randint(0, len(self.starting_nodes))
        rand1 = rand+1
        node = self.starting_nodes[rand]
        if len(node.exiting_roads[0].cars)>0:
            previous_car = node.exiting_roads[0].cars[-1].rect # we don't want to spawn one car inside of one another
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
        for road in self.roads:
            for car in road.cars:
                road.calculate_car_next_pos(car)
    

    #Removes cars that colided ith each other            
    def check_for_car_collision(self):
        for road in self.roads:
            for car in road.cars:
                for road2 in self.roads:
                    for car2 in road2.cars:
                        if car.collide(car2) != None and car in road.cars and car2 in road2.cars and car != car2:
                            road.cars.remove(car) 
                            road2.cars.remove(car2)
                            continue
                        

    def find_min_dist_to_other_car(self, car):
        min_dist = np.Inf
        for road in self.roads:
            collided_idxs = car.vision.collidelistall(road.cars)
            for idx in collided_idxs:
                dist = (car.rect.center[0] - road.cars[idx].rect.center[0])**2 + (car.rect.center[1] - road.cars[idx].rect.center[1])**2
                if dist < min_dist and car is not road.cars[idx]:
                    min_dist = dist
        return min_dist




WIDTH, HEIGHT = (1000,1000)


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
    roads.append(Road(node1, node3, "straight"))#top
    roads.append(Road(node4, node2, "straight"))
    roads.append(Road(node5, node7, "straight"))#bottom
    roads.append(Road(node8, node6, "straight"))
    #Horrizontal
    roads.append(Road(node11, node15, "straight"))#left
    roads.append(Road(node16, node12, "straight"))
    roads.append(Road(node13, node9, "straight"))#right
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
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock=pygame.time.Clock()
    
    map_img = pygame.transform.scale(pygame.image.load(r"C:\Users\Maciek\Documents\Studia\semestr 7\Crossroad_simulation\map_crossroad.png"),(WIDTH,HEIGHT))
    map_rect = map_img.get_rect(topleft = (0,0))
    i=0
    while(True):
        win.blit(map_img, map_rect)
        map.check_for_car_collision()
        i+=1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()    
        map.show_paths(win)
        map.show_vehicles(win)
        
        for road in map.roads:
            for car in road.cars:
                 car.update_vision(road.direction, road.type, road.curve)
                 car.dist_to_nearest_car = map.find_min_dist_to_other_car(car)
        if i%FPS == 0:
            map.spawn_car(WIDTH, HEIGHT)
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
