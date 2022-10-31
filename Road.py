import pygame
import numpy as np
from Node import Node
from utilities import l2_dist, speed_limit
from os.path import join
from utilities import left_prob, right_prob, ROAD_COLOR, NODE_COLOR, dir

eps = 10**(-5)
light_color_dict = {3:"yellow",2:"red", 1:"yellow", 0:"green"}

class Road:
    def __init__(self, start_node, end_node, type, curve = None, light = False, light_cycle = [0.25, 0.4, 0.85, 0.9]):
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
        self.light = light
        self.light_color = 0 if np.abs(self.direction[0]) else 2  
        self.light_cycle = light_cycle
        
    #calculates center of an arc road
    def calculate_center(self):
        if self.curve == "right":
            center = (self.start_point[0], self.end_point[1]) if (self.start_point[1]-self.end_point[1])/(self.start_point[0]-self.end_point[0])>0 else  (self.end_point[0], self.start_point[1]) #center is determined based on tg(alpha) of the line connecting start and end points
        else: 
            center = (self.end_point[0], self.start_point[1]) if (self.start_point[1]-self.end_point[1])/(self.start_point[0]-self.end_point[0])>0 else  (self.start_point[0], self.end_point[1])
        return center   
    
    
    #draws traffic light of correct color on selected surface
    def draw_traffic_light(self, win):
        if self.type=="straight" and self.light:
            color = light_color_dict[self.light_color]+"_light.png"
            WIDTH,HEIGHT = win.get_size()
            image = pygame.transform.scale(pygame.image.load(join(dir , color)).convert_alpha(),(WIDTH//45,HEIGHT//15))
            position = (self.end_point[0]+self.direction[1]*WIDTH//12,self.end_point[1]-self.direction[0]*HEIGHT//12)
            rect = image.get_rect(center=position)
            win.blit(image, rect)
            
            
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

    #determines where car will turn when reaching intersection with accorrdance to predetermined probabilities of turning
    def get_next_road(self):
        if len(self.end_node.exiting_roads)==0: return None
        prob = np.random.rand()
        road_types = [ x.curve for x in self.end_node.exiting_roads]
        roads = {x.curve:x for x in self.end_node.exiting_roads}
        if "right" in road_types and prob<right_prob:
            next_road = roads["right"]
        elif "left" in road_types and prob<right_prob+left_prob:
            next_road = roads["left"]
        else:
            next_road = roads[None]
        return next_road    
    
    #Checks if car should stop       
    def check_stopping(self):
        if self.light:
            ans = True if self.light_color in [1,2] else False
            return ans
        return False
        
    #Moves car to next position
    def calculate_car_next_pos(self, car, dist = None):
        car.update_acceleration(nearest_node = self.end_node, first = self.cars[0]==car)
        car.velocity = car.acceleration + car.velocity if car.velocity + car.acceleration< speed_limit else speed_limit
        if car.velocity<0:
            car.velocity = 0
            
        if dist == None:
            dist = car.velocity
        elif self.type == "straight":
            if self.direction[0]==0:
                car.angle =90*(-self.direction[1]+1)
            else: 
                car.angle = 180 + 90*(-self.direction[0])
            car.visable_angle = car.angle
            
        if self.type != "arc":
            
            pos = car.rect.center

            
            if self.direction[0]==0: 
                new_pos = (self.end_point[0], pos[1] - dist*self.direction[1])
            elif self.direction[1]==0:
                new_pos = (pos[0] - dist*self.direction[0], self.end_point[1])
            else:
                new_pos = (pos[0] - dist*self.direction[0], pos[1] - dist*self.direction[1])
            dist_from_start = (np.abs((new_pos[0]-self.start_point[0])*self.direction[0]),np.abs((new_pos[1]-self.start_point[1])*self.direction[1]))
            length = (np.abs(self.start_point[0]-self.end_point[0]),np.abs(self.start_point[1]-self.end_point[1]))
            #Checking stopping conditions
            slowing_road = np.sum(np.abs(length)) * 0.4
            remaining_road = np.abs(dist_from_start[0] - length[0]) + np.abs( dist_from_start[1] - length[1])-np.max([car.rect.height, car.rect.width])/2
            
            if remaining_road - car.velocity < slowing_road and remaining_road > slowing_road and 1-car.stopping or car.stopping:
                car.stopping = self.check_stopping()

            # update driven distance of the car
            car.dist_driven = l2_dist(new_pos, self.start_point)/l2_dist(self.start_point, self.end_point)
            #Checking if car moved to another road
            if dist_from_start[0] > length[0] or dist_from_start[1] > length[1]:
                next_road = self.get_next_road()
                self.cars.remove(car)
                if next_road!=None:
                    car.rect = car.get_img_rect(center=next_road.start_point) 
                    next_road.cars.append(car)
                    next_road.calculate_car_next_pos(car, dist_from_start[0] - length[0] + dist_from_start[1] - length[1])
                else:
                    del car  
                    return 1
            else:
                car.rect = car.get_img_rect(center=new_pos)
        else:
            
            angle = dist/2/np.pi/self.radius*360
            new_angle = car.angle + angle*(int(self.curve=="right")-1/2)*2
            pos = car.rect.center
            new_pos = (self.radius*np.cos((new_angle+90*(1-self.direction[0]*self.direction[1]))/180*np.pi)+self.center[0],self.radius*np.sin((new_angle+90*(1-self.direction[0]*self.direction[1]))/180*np.pi)+self.center[1])
            
            # update driven distance of the car
            car.dist_driven = 2**((90 - (int(self.curve=="left")*new_angle)%90)/90)-1
            
            if np.abs(new_angle)%90 < np.abs(angle) - eps:
                next_road = self.get_next_road()
                self.cars.remove(car)
                if next_road!=None:
                    car.rect = car.get_img_rect(center=next_road.start_point) 
                    next_road.cars.append(car)
                    remaining_distance = np.abs(new_angle)%90/180*np.pi*self.radius
                    next_road.calculate_car_next_pos(car, remaining_distance)
                else:
                    del car
                    return 1  
            else:
                car.angle = new_angle
                car.visable_angle -= angle*(int(self.curve=="right")-1/2)*2
                car.rect = car.get_img_rect(center=new_pos)
        return 0

#Draws set of roads checking if all angles, traffic lights and roaad lengths are drawn properly
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
        test_road6 = Road(Node((300,230)),Node((300,200)), "straight", light = True)
        test_road6.draw_path(win)
        test_road7 = Road(Node((330,210)),Node((330,240)), "straight", light = True)
        test_road7.draw_path(win)
        test_road8 = Road(Node((330,200)),Node((360,200)), "straight", light = True)
        test_road8.draw_path(win)
        test_road6.draw_traffic_light(win)
        test_road7.draw_traffic_light(win)
        test_road8.draw_traffic_light(win)
        pygame.display.update()
        clock.tick(60)
#test()