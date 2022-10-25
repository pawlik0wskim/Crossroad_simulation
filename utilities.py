import pygame
import numpy as np


visualize = True


def rotate_image(win, image, top_left, angle):
    rotated_img = pygame.transform.rotate(image, angle)
    rotated_rect = rotated_img.get_rect(center = image.get_rect(topleft = top_left).center)
    win.blit(rotated_img, rotated_rect)


def scale(image, factor):
    size = round(image.get_width() * factor), round(image.get_hight()*factor)
    return pygame.transform.scale(image, size)

def l2(a, b):
    return (a[0] - b[0])**2 + (a[1] - b[1])**2

def get_cos(x, y):
    return (x[0]*y[0] + x[1]*y[1])/np.sqrt(l2(x)*l2(y))