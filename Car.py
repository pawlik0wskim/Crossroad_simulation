import pygame
import numpy as np


dir = r"C:\Users\Maciek\Documents\Studia\semestr 7\Crossroad_simulation"

class Car:
    def __init__(self, position, angle, WIDTH, HEIGHT):
        rand = np.random.rand()
        if rand < 1/4:
            image = pygame.image.load(dir +"\car_black.png")
        elif rand < 2/4:
            image = pygame.image.load(dir +"\car_red.png")
        elif rand < 3/4:
            image = pygame.image.load(dir +"\car_green.png")
        else:
            image = pygame.image.load(dir + "\car_yellow.png")
        
        self.img = pygame.transform.scale(image.convert_alpha(),(WIDTH/30,HEIGHT/11)) 
        self.rect = self.img.get_rect(center=position)
        self.angle = angle
        self.visable_angle = angle
        self.velocity = 4*(1/2000*WIDTH+1/2000*HEIGHT)
        self.stopping = False
        self.acceleration = (1/2000*WIDTH+1/2000*HEIGHT)/2
        self.limit = 5*(1/2000*WIDTH+1/2000*HEIGHT)
        self.dist_to_nearest_car = np.Inf
        self.vision = pygame.Rect(self.rect.center, [10, 10])
        
    def __getx2_rect_from_center(x, y, w, h):
        return pygame.Rect(x - w, y - h, 2*w, 2*h)
    def rotate(self): # rotates car image and rect based on current visible angle
        rotated_img = pygame.transform.rotate(self.img, self.visable_angle)  
        self.rect  = rotated_img.get_rect(center = self.img.get_rect(topleft = self.rect.topleft).center)
        return rotated_img
    def update_vision(self, direction, type, curve): # updates vision based on type and direction of the road
        # _ = self.rotate()
        if type == "straight":
            center_new_x = self.rect.center[0] - direction[0]*self.rect.width*3/2 - direction[1]*self.rect.width/2
            center_new_y = self.rect.center[1] + direction[0]*self.rect.height/2 - direction[1]*self.rect.height*3/2
            self.vision = Car.__getx2_rect_from_center(center_new_x, center_new_y, self.rect.width, self.rect.height)
        else:
            if curve == "left":
                center_new_x = self.rect.center[0] - direction[0]*self.rect.width*3/2
                center_new_y = self.rect.center[1] - direction[1]*self.rect.height*3/2
                self.vision = Car.__getx2_rect_from_center(center_new_x, center_new_y, self.rect.width, self.rect.height)
            else:
                center_new_x, center_new_y = 0, 0
                if direction[0] == -1 and direction[1] == 1:
                    center_new_x = self.rect.center[0] + self.rect.width/2
                    center_new_y = self.rect.center[1] - self.rect.height*3/2
                else:
                    center_new_x = self.rect.center[0] - direction[0]*self.rect.width*3/2
                    center_new_y = self.rect.center[1] - direction[1]*self.rect.height/2
                self.vision = Car.__getx2_rect_from_center(center_new_x, center_new_y, self.rect.width, self.rect.height)

        
    def draw(self, win):
        center = self.rect.center
        rotated_img = self.rotate()
        self.rect  = rotated_img.get_rect()
        self.rect.center = center
        #pygame.draw.rect(win, "Red", self.rect)
        win.blit(rotated_img, self.rect)
        
    
    #Checks for colision with other car    
    def collide(self, other):
        mask1 = pygame.mask.from_surface(pygame.transform.rotate(self.img, self.visable_angle))
        mask2 = pygame.mask.from_surface(pygame.transform.rotate(other.img, other.visable_angle))
        offset = (int(-other.rect.center[0]+self.rect.center[0]), int(-other.rect.center[1]+self.rect.center[1]))
        poi = mask2.overlap(mask1, offset)
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
        car = Car((WIDTH/2, HEIGHT/2), i*3,WIDTH, HEIGHT)
        car.draw(win)
        pygame.display.update()
        clock.tick(60)
#test()