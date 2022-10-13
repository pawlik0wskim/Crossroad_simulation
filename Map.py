import pygame
from Road import Road
class Map:
    def __init__(self, roads):
        self.roads=roads
    def show_paths(self, win):
        for road in self.roads:
            road.draw_path(win)
    



WIDTH, HEIGHT = (1000,1000)
def generate_crossroad(WIDTH, HEIGHT):
    roads = []
    #Vertical
    roads.append(Road((7/18*WIDTH, HEIGHT/3),(7/18*WIDTH, 0), "straight"))#top
    roads.append(Road((11/18*WIDTH, 0),(11/18*WIDTH, HEIGHT/3), "straight"))
    roads.append(Road((7/18*WIDTH, 2/3*HEIGHT),(7/18*WIDTH, HEIGHT), "straight"))#bottom
    roads.append(Road((11/18*WIDTH, HEIGHT),(11/18*WIDTH, 2/3*HEIGHT), "straight"))
    #Horrizontal
    roads.append(Road((0, HEIGHT*11/18),(WIDTH/3, HEIGHT*11/18), "straight"))#left
    roads.append(Road((WIDTH/3, HEIGHT*7/18),(0, HEIGHT*7/18), "straight"))
    roads.append(Road((WIDTH*2/3, HEIGHT*11/18),(WIDTH, HEIGHT*11/18), "straight"))#right
    roads.append(Road((WIDTH, HEIGHT*7/18),(WIDTH*2/3, HEIGHT*7/18), "straight"))
    #Bottom turns
    roads.append(Road((11/18*WIDTH, 2/3*HEIGHT),(WIDTH*2/3, HEIGHT*11/18), type = "arc", curve = "right"))
    roads.append(Road((11/18*WIDTH, 2/3*HEIGHT),(WIDTH/3, HEIGHT*7/18), type = "arc", curve = "left"))
    roads.append(Road((11/18*WIDTH, HEIGHT),(11/18*WIDTH, 1/3*HEIGHT), "straight"))
    #Left turns
    roads.append(Road((WIDTH/3, HEIGHT*11/18),(7/18*WIDTH, 2/3*HEIGHT), type = "arc", curve = "right"))
    roads.append(Road((WIDTH/3, HEIGHT*11/18),(11/18*WIDTH, 1/3*HEIGHT), type = "arc", curve = "left"))
    roads.append(Road((WIDTH/3, HEIGHT*11/18),(WIDTH*2/3, HEIGHT*11/18), "straight"))
    #Top turns
    roads.append(Road((7/18*WIDTH, HEIGHT/3),(WIDTH/3, HEIGHT*7/18), type = "arc", curve = "right"))
    roads.append(Road((7/18*WIDTH, HEIGHT/3),(WIDTH*2/3, HEIGHT*11/18), type = "arc", curve = "left"))
    roads.append(Road((7/18*WIDTH, HEIGHT/3),(7/18*WIDTH, 2/3*HEIGHT), "straight"))
    #Right turns
    roads.append(Road((WIDTH*2/3, HEIGHT*7/18),(11/18*WIDTH, 1/3*HEIGHT), type = "arc", curve = "right"))
    roads.append(Road((WIDTH*2/3, HEIGHT*7/18),(7/18*WIDTH, 2/3*HEIGHT), type = "arc", curve = "left"))
    roads.append(Road((WIDTH*2/3, HEIGHT*7/18),(WIDTH/3, HEIGHT*7/18), "straight"))
    return Map(roads)
  
def generate_roundabout(WIDTH, HEIGHT):
    roads = []
    #Vertical
    roads.append(Road((7/13*WIDTH, HEIGHT*2/13),(7/13*WIDTH, 0), "straight"))#top
    roads.append(Road((6/13*WIDTH, 0),(6/13*WIDTH, HEIGHT*2/13), "straight"))
    roads.append(Road((7/13*WIDTH, HEIGHT),(7/13*WIDTH, HEIGHT*11/13), "straight"))#bottom
    roads.append(Road((6/13*WIDTH, HEIGHT*11/13),(6/13*WIDTH, HEIGHT), "straight"))
    #Horrizontal
    roads.append(Road((0, HEIGHT*7/13),(WIDTH*2/13, HEIGHT*7/13), "straight"))#left
    roads.append(Road((WIDTH*2/13, HEIGHT*6/13),(0, HEIGHT*6/13), "straight"))
    roads.append(Road((WIDTH*11/13, HEIGHT*7/13),(WIDTH, HEIGHT*7/13), "straight"))#right
    roads.append(Road((WIDTH, HEIGHT*6/13),(WIDTH*11/13, HEIGHT*6/13), "straight"))
    #Entering roundabout
    #Vertical
    roads.append(Road((7/13*WIDTH, HEIGHT*2/13),(8/13*WIDTH, HEIGHT*3/13), "arc", "left"))#top
    roads.append(Road((6/13*WIDTH, HEIGHT*2/13),(5/13*WIDTH, HEIGHT*3/13), "arc", "right"))
    roads.append(Road((7/13*WIDTH, HEIGHT*11/13),(8/13*WIDTH, HEIGHT*10/13), "arc", "right"))#bottom
    roads.append(Road((6/13*WIDTH, HEIGHT*11/13),(5/13*WIDTH, HEIGHT*10/13), "arc", "left"))
    #Horrizontal
    roads.append(Road((WIDTH*2/13, HEIGHT*7/13),(WIDTH*3/13, HEIGHT*8/13), "arc", "right"))#left
    roads.append(Road((WIDTH*2/13, HEIGHT*6/13),(WIDTH*3/13, HEIGHT*5/13), "arc", "left"))
    roads.append(Road((WIDTH*11/13, HEIGHT*7/13),(WIDTH*10/13, HEIGHT*8/13), "arc", "left"))#right
    roads.append(Road((WIDTH*11/13, HEIGHT*6/13),(WIDTH*10/13, HEIGHT*5/13), "arc", "right"))
    
    #####Roundobout
    #Straight
    roads.append(Road((8/13*WIDTH, HEIGHT*3/13),(5/13*WIDTH, HEIGHT*3/13), "straight"))
    roads.append(Road((5/13*WIDTH, HEIGHT*10/13),(8/13*WIDTH, HEIGHT*10/13), "straight"))
    roads.append(Road((WIDTH*3/13, HEIGHT*5/13),(WIDTH*3/13, HEIGHT*8/13), "straight"))
    roads.append(Road((WIDTH*10/13, HEIGHT*8/13),(WIDTH*10/13, HEIGHT*5/13), "straight"))
    #Arc
    roads.append(Road((5/13*WIDTH, HEIGHT*3/13),(WIDTH*3/13, HEIGHT*5/13), "arc", "left"))
    roads.append(Road((WIDTH*3/13, HEIGHT*8/13),(5/13*WIDTH, HEIGHT*10/13), "arc", "left"))
    roads.append(Road((8/13*WIDTH, HEIGHT*10/13),(WIDTH*10/13, HEIGHT*8/13), "arc", "left"))
    roads.append(Road((WIDTH*10/13, HEIGHT*5/13),(8/13*WIDTH, HEIGHT*3/13), "arc", "left"))
    return Map(roads)   


 
def test(map):    
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock=pygame.time.Clock()
    while(True):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()    
        map.show_paths(win)
        pygame.display.update()
        clock.tick(60)
test(generate_crossroad(WIDTH, HEIGHT))