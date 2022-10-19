import pygame
import numpy as np



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
        
    def draw(self, win):
        center = self.rect.center
        rotated_img = pygame.transform.rotate(self.img, self.visable_angle)  
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