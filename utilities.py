import pygame
import numpy as np

# is True the simultion will be visualized
visualize = True


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