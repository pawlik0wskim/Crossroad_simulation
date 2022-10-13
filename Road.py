import pygame
import numpy as np

ROAD_COLOR = "Red"
NODE_COLOR = "Yellow"

class Road:
    def __init__(self, start_point, end_point, type, curve = None):
        self.start_point = start_point
        self.end_point = end_point
        
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
            
            
def test():
    win = pygame.display.set_mode((400, 400))
    clock=pygame.time.Clock()
    while(True):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
        #right turn test
        test_road = Road((30,30),(0,0), "arc", "right")
        test_road.draw_path(win)
        test_road2 = Road((30,30),(60,0), "arc", "right")
        test_road2.draw_path(win)
        test_road3 = Road((30,30),(60,60), "arc", "right")
        test_road3.draw_path(win)
        test_road4 = Road((30,30),(0,60), "arc", "right")
        test_road4.draw_path(win)
        #left turn test
        test_road5 = Road((130,130),(100,100), "arc", "left")
        test_road5.draw_path(win)
        test_road6 = Road((130,130),(160,100), "arc", "left")
        test_road6.draw_path(win)
        test_road7 = Road((130,130),(160,160), "arc", "left")
        test_road7.draw_path(win)
        test_road8 = Road((130,130),(100,160), "arc", "left")
        test_road8.draw_path(win)
        #radius test
        test_road6 = Road((230,230),(200,200), "arc", "left")
        test_road6.draw_path(win)
        test_road7 = Road((230,230),(210,210), "arc", "left")
        test_road7.draw_path(win)
        test_road8 = Road((230,230),(220,220), "arc", "left")
        test_road8.draw_path(win)
        #straight road
        test_road6 = Road((330,230),(300,200), "straight")
        test_road6.draw_path(win)
        test_road7 = Road((330,230),(330,210), "straight")
        test_road7.draw_path(win)
        test_road8 = Road((330,200),(360,200), "straight")
        test_road8.draw_path(win)
        pygame.display.update()
        clock.tick(60)
test()