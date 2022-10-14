import pygame
import numpy as np
from Node import Node

ROAD_COLOR = "Red"
NODE_COLOR = "Yellow"
eps = 10**(-5)

class Road:
    def __init__(self, start_node, end_node, type, curve = None):
        self.start_node = start_node
        self.end_node = end_node
        self.start_point = start_node.pos
        self.end_point = end_node.pos
        start_node.exiting_roads.append(self)
        end_node.entering_roads.append(self)
        if type not in ["arc", "straight"]: #two lines of code that will help with possible missspells during development 
            print("Road can only be an arc or a straight line")
            return None
        
        if type == "arc":
            eps = 10**(-5) 
            tan = np.abs((self.start_point[1]-self.end_point[1])/(self.start_point[0]-self.end_point[0]))#We assume that all turns will be 90 degrees with circular trajectory
            if tan<1-eps or tan>1+eps: 
                print("Error!!! No 90 degree arc of a circle between start and end node")
                return None
        
        self.type = type
        self.curve = curve
        self.center = self.calculate_center() if self.type == "arc" else None
        self.radius = np.abs(self.start_point[1] - self.end_point[1]) if self.type == "arc" else None
        self.direction = (np.sign(self.start_point[0]-self.end_point[0]),np.sign(self.start_point[1]-self.end_point[1]))
        self.cars = []
        
    #calculates center of an arc road
    def calculate_center(self):
        if self.curve == "right":
            center = (self.start_point[0], self.end_point[1]) if (self.start_point[1]-self.end_point[1])/(self.start_point[0]-self.end_point[0])>0 else  (self.end_point[0], self.start_point[1]) #center is determined based on tg(alpha) of the line connecting start and end points
        else: 
            center = (self.end_point[0], self.start_point[1]) if (self.start_point[1]-self.end_point[1])/(self.start_point[0]-self.end_point[0])>0 else  (self.start_point[0], self.end_point[1])
        return center   
         
    # draws cars path on selected surface
    def draw_path(self, win):
        if self.type == "arc":
            if self.curve == "right":
                if(self.start_point[0]<self.center[0]):
                    start_angle, end_angle =  np.pi/2, np.pi
                elif(self.start_point[0]>self.center[0]):
                    start_angle, end_angle = 3*np.pi/2, 2*np.pi
                elif(self.start_point[1]>self.center[1]):
                    start_angle, end_angle = np.pi, 3*np.pi/2
                else:
                    start_angle, end_angle = 0, np.pi/2
            else: 
                if(self.start_point[0]<self.center[0]):
                    start_angle, end_angle =  np.pi, 3*np.pi/2
                elif(self.start_point[0]>self.center[0]):
                    start_angle, end_angle = 0, np.pi/2
                elif(self.start_point[1]>self.center[1]):
                    start_angle, end_angle = 3*np.pi/2, np.pi*2
                else:
                    start_angle, end_angle = np.pi/2, np.pi  
            
            rect = pygame.Rect(self.center[0]-self.radius, self.center[1]-self.radius, 2* self.radius, 2*self.radius)
            pygame.draw.arc(win, ROAD_COLOR, rect, start_angle, end_angle)
        else:
            pygame.draw.line(win, ROAD_COLOR, self.start_point, self.end_point)
        pygame.draw.circle(win, NODE_COLOR, self.start_point,3)
        pygame.draw.circle(win, NODE_COLOR, self.end_point,3)


    def get_next_road(self):
        if len(self.end_node.exiting_roads)==0: return None
        next_road = self.end_node.exiting_roads[np.random.randint(0,len(self.end_node.exiting_roads))]
        return next_road           

    def calculate_car_next_pos(self, car, dist = None):
        if dist == None:
            dist = car.velocity
        elif self.type == "straight":
            if self.direction[0]==0: car.angle =90*(-self.direction[1]+1)
            else: car.angle =180 + 90*(-self.direction[0])
            
        if self.type != "arc":
            pos = car.rect.center
            new_pos = (pos[0]-car.velocity*self.direction[0],pos[1]-car.velocity*self.direction[1])
            dist_from_start = (np.abs((new_pos[0]-self.start_point[0])*self.direction[0]),np.abs((new_pos[1]-self.start_point[1])*self.direction[1]))
            length = (np.abs(self.start_point[0]-self.end_point[0]),np.abs(self.start_point[1]-self.end_point[1]))
            if dist_from_start[0] > length[0] or dist_from_start[1] > length[1]:
                next_road = self.get_next_road()
                self.cars.remove(car)
                if next_road!=None:
                    car.rect = car.img.get_rect(center=next_road.start_point) 
                    next_road.cars.append(car)
                    next_road.calculate_car_next_pos(car, dist_from_start[0] - length[0] + dist_from_start[1] - length[1])
                else:
                    del car  
            else:
                car.rect = car.img.get_rect(center=new_pos)
        else:
            angle = dist/2/np.pi/self.radius*360
            new_angle = car.angle + angle*(int(self.curve=="right")-1/2)*2
            pos = car.rect.center
            new_pos = (self.radius*np.cos((new_angle+90*(1-self.direction[0]*self.direction[1]))/180*np.pi)+self.center[0],self.radius*np.sin((new_angle+90*(1-self.direction[0]*self.direction[1]))/180*np.pi)+self.center[1])
            if np.abs(new_angle)%90 < np.abs(angle) - eps:
                next_road = self.get_next_road()
                self.cars.remove(car)
                if next_road!=None:
                    car.rect = car.img.get_rect(center=next_road.start_point) 
                    next_road.cars.append(car)
                    next_road.calculate_car_next_pos(car, 3)
                else:
                    del car  
            else:
                car.angle = new_angle
                car.visable_angle -= angle*(int(self.curve=="right")-1/2)*2
                car.rect = car.img.get_rect(center=new_pos)

def test():
    win = pygame.display.set_mode((400, 400))
    clock=pygame.time.Clock()
    while(True):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
        #right turn test
        test_road = Road(Node((30,30)),Node((0,0)), "arc", "right")
        test_road.draw_path(win)
        test_road2 = Road(Node((30,30)),Node((60,0)), "arc", "right")
        test_road2.draw_path(win)
        test_road3 = Road(Node((30,30)),Node((60,60)), "arc", "right")
        test_road3.draw_path(win)
        test_road4 = Road(Node((30,30)),Node((0,60)), "arc", "right")
        test_road4.draw_path(win)
        #left turn test
        test_road5 = Road(Node((130,130)),Node((100,100)), "arc", "left")
        test_road5.draw_path(win)
        test_road6 = Road(Node((130,130)),Node((160,100)), "arc", "left")
        test_road6.draw_path(win)
        test_road7 = Road(Node((130,130)),Node((160,160)), "arc", "left")
        test_road7.draw_path(win)
        test_road8 = Road(Node((130,130)),Node((100,160)), "arc", "left")
        test_road8.draw_path(win)
        #radius test
        test_road6 = Road(Node((230,230)),Node((200,200)), "arc", "left")
        test_road6.draw_path(win)
        test_road7 = Road(Node((230,230)),Node((210,210)), "arc", "left")
        test_road7.draw_path(win)
        test_road8 = Road(Node((230,230)),Node((220,220)), "arc", "left")
        test_road8.draw_path(win)
        #straight road
        test_road6 = Road(Node((330,230)),Node((300,200)), "straight")
        test_road6.draw_path(win)
        test_road7 = Road(Node((330,230)),Node((330,210)), "straight")
        test_road7.draw_path(win)
        test_road8 = Road(Node((330,200)),Node((360,200)), "straight")
        test_road8.draw_path(win)
        pygame.display.update()
        clock.tick(60)
#test()