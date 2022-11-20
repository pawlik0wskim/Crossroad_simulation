import pygame
import numpy as np

# is True the simultion will be visualized
# visualize = True
# #if True the car paths and visions will be  visualised(only if visualisation is turned on)
# debug = False
# # left_prob, right_prob = 1, 0
# left_prob, right_prob = 0.2, 0.3
WIDTH, HEIGHT = (700,700)
ROAD_COLOR = "Red"
NODE_COLOR = "Yellow"
dir = r""
FPS = 30
# light_cycle = [0.25, 0.4, 0.85, 0.9] 
# light_cycle_time = 10*FPS
# max_time = 300 # simulation will be run up to this time in seconds
unit = (1/2000*WIDTH+1/2000*HEIGHT) #unit used to calculate velocity so that window size doesn't matter
# acceleration_exponent = 4
# frames_per_car = 30
def meters_to_pixels(dist):
    return dist/3*70*unit

def kilometers_per_hour_to_pixels(dist):
    return dist/FPS/36*10/3*70*unit

def pixels_to_kmh(dist):
    meters_per_frame = dist/70*3/unit
    return meters_per_frame*FPS*3600/1000

def rotate_image(win, image, top_left, angle):
    rotated_img = pygame.transform.rotate(image, angle)
    rotated_rect = rotated_img.get_rect(center = image.get_rect(topleft = top_left).center)
    win.blit(rotated_img, rotated_rect)


def scale(image, factor):
    size = round(image.get_width() * factor), round(image.get_hight()*factor)
    return pygame.transform.scale(image, size)

# L2 norm of difference of two vectors in 2D
def l2_dist(a, b):
    return (a[0] - b[0])**2 + (a[1] - b[1])**2

# returns cross product of two vectors in 2D
def cross_product(x, y):
    return (x[0]*y[0] + x[1]*y[1])

# returns cross product of two vectors in 2D
def cross_product(x, y):
    return (x[0]*y[0] + x[1]*y[1])

def cost_function(flow, collisions, iter, stopped):
    return (collisions*np.log(collisions + 1) - flow)