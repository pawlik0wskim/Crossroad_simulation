import pygame
import numpy as np
WIDTH, HEIGHT = 1000, 1000 
class Car:
    def __init__(self, position, angle, WIDTH, HEIGHT):
        self.img = pygame.transform.scale(pygame.image.load(r"car_red.png").convert_alpha(),(WIDTH//70,HEIGHT//25))
        self.rect = self.img.get_rect(center=position)
        self.angle = angle
        self.visible_angle = angle
        self.velocity = 3
        self.vision = pygame.Rect(self.rect.center[0], self.rect.center[1], 10, 10)
        self.dist_to_nearest_car = np.Inf
    
    # updates placement of vision area depending on road of the car
    def update_vision(self, direction_type):
        x, y = self.rect.center[0], self.rect.center[1]
        if direction_type == "horizontal_right":
            self.vision = pygame.Rect(x + WIDTH//25, y - HEIGHT//6, WIDTH//2, HEIGHT//3)
        elif direction_type == "vertical_down":
            self.vision = pygame.Rect(x - WIDTH//6, y + HEIGHT//30, WIDTH//3, HEIGHT//2)
        elif direction_type == "vertical_up":
            self.vision = pygame.Rect(x - WIDTH//6, y - HEIGHT//2.7, WIDTH//3, HEIGHT//3)
        elif direction_type == "horizontal_left":
            self.vision = pygame.Rect(x - WIDTH//3, y - HEIGHT//10, WIDTH//3.3, HEIGHT//3.5)
        elif direction_type == "vertical_down_left":
            self.vision = pygame.Rect(x + WIDTH//80, y + HEIGHT//30, WIDTH//8, HEIGHT//10)
        elif direction_type == "vertical_up_left":
            self.vision = pygame.Rect(x - WIDTH//8, y - HEIGHT//10, WIDTH//10, HEIGHT//8)
        elif direction_type == "horizontal_left_left":
            self.vision = pygame.Rect(x - WIDTH//8, y + HEIGHT//30, WIDTH//8, HEIGHT//10)
        elif direction_type == "horizontal_right_left":
            self.vision = pygame.Rect(x - WIDTH//80, y - HEIGHT//8, WIDTH//8, HEIGHT//10)
        elif direction_type == "horizontal_right_right":
            self.vision = pygame.Rect(x + WIDTH//100, y - HEIGHT//8, WIDTH//10, HEIGHT//10)
        else:
            self.vision = pygame.Rect(x, y, 10, 10)
        
    def draw(self, win):
        rotated_img = pygame.transform.rotate(self.img, self.visible_angle)  
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