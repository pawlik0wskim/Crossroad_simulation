import pygame
import numpy as np
WIDTH, HEIGHT = 1000, 1000 
class Car:
    def __init__(self, position, angle, WIDTH, HEIGHT):
        self.img = pygame.transform.scale(pygame.image.load(r"car_red.png").convert_alpha(),(WIDTH//70,HEIGHT//25))
        self.rect = self.img.get_rect(center=position)
        self.angle = angle
        self.visable_angle = angle
        self.velocity = 3
        self.vision = pygame.Rect(self.rect.center, [10, 10])
        self.dist_to_nearest_car = np.Inf
    
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
        rotated_img = self.rotate()
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