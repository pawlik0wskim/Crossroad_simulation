import pygame
import numpy as np
from utilities import *
import cv2


dir = r""
class Car:
    def __init__(self, position, angle, WIDTH, HEIGHT, speed_limit, acceleration_exponent):
        global unit
        w, h = WIDTH//30, HEIGHT//11
        rand = np.random.rand()
        if rand < 1/4:
            image = cv2.imread(dir + 'car_black.png', cv2.IMREAD_UNCHANGED)
        elif rand < 2/4:
            image = cv2.imread(dir + 'car_red.png', cv2.IMREAD_UNCHANGED)
        elif rand < 3/4:
            image = cv2.imread(dir + 'car_green.png', cv2.IMREAD_UNCHANGED)
        else:
            image = cv2.imread(dir + 'car_yellow.png', cv2.IMREAD_UNCHANGED)

        self.img = cv2.resize(image, (w, h), interpolation=cv2.INTER_LINEAR)
        

        
        self.rect = pygame.Rect(position[0] - w/2, position[1] - h/2, w, h)
        self.angle = angle
        self.visable_angle = angle
        self.dist_driven = np.Inf # part of distance driven on current road since its start
        self.nearest_car = None

        self.stopping = False
        self.maximum_acceleration = unit*4
        
        self.velocity = speed_limit
        self.vision = pygame.Rect(self.rect.center, [10, 10])
        self.acceleration = unit
        self.speed_limit = speed_limit
        self.acceleration_exponent = acceleration_exponent
        
        self.reaction_time = 1
        self.minimum_dist = np.max([self.rect.h,self.rect.w])*5/3
        self.maximum_deceleration = self.acceleration*2
        
        self.mask = pygame.mask.from_surface(Car.get_img_as_surface(self.rotate_image()))
        self.color = "Red"

    # returns rotated image according to visible angle
    def rotate_image(self):

        height, width = self.img.shape[:2]
        img_center = (width/2, height/2)

        rotation_matrix = cv2.getRotationMatrix2D(img_center, self.visable_angle, 1)

        rotation_angle_cos, rotation_angle_sin = np.abs(rotation_matrix[0,0:2])

        # find new width and height so that rotated image wouldnt be cropped
        new_w = int(height * rotation_angle_sin + width * rotation_angle_cos)
        new_h = int(height * rotation_angle_cos + width * rotation_angle_sin)

        # update rotation matrix accordingly to new dimensions 
        rotation_matrix[0, 2] += new_w/2 - img_center[0]
        rotation_matrix[1, 2] += new_h/2 - img_center[1]

        # return result of rotation of bigger image
        return cv2.warpAffine(self.img, rotation_matrix, (new_w, new_h))

    # returns rect with dimensions like self.img has and with center in the given center
    def get_img_rect(self, center):
        img = self.rotate_image()
        w, h = img.shape[1], img.shape[0]
        rect = pygame.Rect(0, 0, w, h)
        rect.center = center
        return rect
    
    # casts img(which is supposed to be numpy array) to pygame.Surface
    def get_img_as_surface(img):
        return pygame.image.frombuffer(img.tobytes(), img.shape[1::-1], "RGBA")
    
    # updates vision based on type and direction of the road
    def update_vision(self, direction, type, curve):
        if type == "straight":
            center_new_x = self.rect.center[0] - direction[0]*self.rect.width*3/2
            center_new_y = self.rect.center[1] - direction[1]*self.rect.height*3/2
            w, h = self.rect.w*(1 + abs(direction[0])), self.rect.h*(1 + abs(direction[1]))
            self.vision = pygame.Rect(center_new_x - w,
                                      center_new_y - h, 
                                      2*w, 
                                      2*h)
        else:
            if curve == "left":
                alpha, beta = 2, 2
                dim = max(self.rect.w, self.rect.h)
                # new_x = alpha*dim if direction[0] > 0 else -self.rect.w
                # new_y = beta*dim if direction[1] > 0 else -self.rect.h
                # new_x = self.rect.bottomright[0] - new_x
                # new_y = self.rect.bottomright[1] - new_y
                new_x = self.rect.center[0] - self.rect.w*alpha + self.rect.w/2 if direction[0]>0 else self.rect.center[0]  - self.rect.w/2
                new_y = self.rect.center[1] - self.rect.h*beta + self.rect.h/2 if direction[1]>0 else self.rect.center[1]  - self.rect.h/2
                self.vision = pygame.Rect(new_x, new_y, self.rect.w*alpha, self.rect.h*beta)
            else:
                if direction[0]*direction[1] > 0:
                    alpha, beta = 0.7, 1.5
                else:
                    alpha, beta = 1.5, 0.7
                center_new_x, center_new_y = self.rect.centerx, self.rect.centery
                center_new_x += alpha*self.rect.w if direction[0] < 0 else 0
                center_new_y += beta*self.rect.h if direction[1] < 0 else 0
                self.vision = pygame.Rect(center_new_x - alpha*self.rect.w,
                                          center_new_y - beta*self.rect.h, 
                                          alpha*self.rect.w, 
                                          beta*self.rect.h)
                
    ### Calculates current car acceleration based on its distance to nearest car
    def update_acceleration(self, nearest_node=None, first = False):
        
        new_acceleration = 1 - (self.velocity/self.speed_limit)**self.acceleration_exponent
        print(self.nearest_car)
        if self.nearest_car is not None:
            sign = np.sign(np.cos(self.visable_angle - self.nearest_car.visable_angle))
            desired_dist = self.minimum_dist + self.velocity*self.reaction_time + self.velocity*(self.velocity - sign*self.nearest_car.velocity)/(2*np.sqrt(self.maximum_acceleration*self.maximum_deceleration))   
            real_dist = np.sqrt(l2_dist(self.rect.center, self.nearest_car.rect.center))
            new_acceleration -= (desired_dist/real_dist)**2
        
        if self.stopping and first: 
            desired_dist = np.max([self.rect.h, self.rect.w])/2+7*unit+self.velocity*self.reaction_time + self.velocity*(self.velocity)/(2*np.sqrt(self.maximum_acceleration*self.maximum_deceleration))   
            real_dist = np.sqrt(l2_dist(self.rect.center, nearest_node.pos))
            new_acceleration -= (desired_dist/real_dist)**2
        self.acceleration = new_acceleration*self.maximum_acceleration
        
        self.velocity = self.acceleration + self.velocity if self.velocity + self.acceleration< self.speed_limit else self.speed_limit
        if self.velocity<0:
            self.velocity = 0
            
     #Draws vehicle on provided surface       
    def draw(self, win):
        center = self.rect.center
        rotated_img = self.rotate_image()
        self.rect = self.get_img_rect(center)
        self.rect.center = center
        if self.rect.center!=center: print(f"{self.rect.center}, {center}")
        surface = pygame.image.frombuffer(rotated_img.tobytes(), rotated_img.shape[1::-1], "RGBA")
        win.blit(surface, self.rect)
        
    
    #Checks for collision with other car    
    def collide(self, other):
        offset = (int(-other.rect.topleft[0]+self.rect.topleft[0]), int(-other.rect.topleft[1]+self.rect.topleft[1]))#(int(self.rect.x - other.rect.x), int(self.rect.y - other.rect.y))
        poi = other.mask.overlap(self.mask, offset)
        return poi
    
    

def test():  #rotation around the center of vehicle
    i = 0 
    WIDTH, HEIGHT = 800, 800
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock=pygame.time.Clock()
    while(True):
        i+=1
        rect = pygame.Rect(0,0,WIDTH, HEIGHT)
        pygame.draw.rect(win,"Black", rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()    
        car = Car((WIDTH/2, HEIGHT/2), i*3, WIDTH, HEIGHT, 6*unit, 4)
        
        car.draw(win)
        pygame.display.update()
        clock.tick(60)
        car.update_acceleration(car, 5)
#test()