import pygame
import numpy as np
WIDTH, HEIGHT = 800, 800 
class Car:
    def __init__(self, position, angle, WIDTH, HEIGHT):
        self.img = pygame.transform.scale(pygame.image.load(r"C:\Users\Maciek\Documents\Studia\semestr 7\Crossroad_simulation\car_red.png").convert_alpha(),(WIDTH/70,HEIGHT/25))
        self.rect = self.img.get_rect(center=position)
        self.angle = angle
        self.visable_angle = angle
        self.velocity = 3
        
    def draw(self, win):
        rotated_img = pygame.transform.rotate(self.img, self.visable_angle)  
        self.rect  = rotated_img.get_rect(center = self.img.get_rect(topleft = self.rect.topleft).center)
        win.blit(rotated_img, self.rect)

def test():  #rotation around the center of vehicle
    i = 0 
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