import cv2
import pygame
import numpy as np

def rotate_image(mat, angle):
  # angle in degrees

  height, width = mat.shape[:2]
  image_center = (width/2, height/2)

  rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

  abs_cos = abs(rotation_mat[0,0])
  abs_sin = abs(rotation_mat[0,1])

  bound_w = int(height * abs_sin + width * abs_cos)
  bound_h = int(height * abs_cos + width * abs_sin)

  rotation_mat[0, 2] += bound_w/2 - image_center[0]
  rotation_mat[1, 2] += bound_h/2 - image_center[1]

  rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
  return rotated_mat


WIDTH, HEIGHT = (1000,1000)
w, h = WIDTH//30, HEIGHT//11

image = cv2.imread('car_black.png', cv2.IMREAD_UNCHANGED)

image = cv2.resize(image, (w, h), interpolation=cv2.INTER_LINEAR)
# M = cv2.getRotationMatrix2D((w//2, h//2), 2, 1)
# print(M)
# print(image.shape)
# rotated = cv2.warpAffine(image, M, (w, h))

rotated = rotate_image(image, 30)
# cv2.imshow("Rotated by 45 Degrees", rotated)
# cv2.waitKey()


print(rotated.shape)
surface = pygame.image.frombuffer(rotated.tobytes(), rotated.shape[1::-1], "RGBA")
print(surface)

mask1 = pygame.mask.from_surface(surface)

print(rotated.shape)



pygame.init()

#### Create a canvas on which to display everything ####
window = (400,400)
screen = pygame.display.set_mode(window)

screen.fill([255, 255, 255])
screen.blit(surface,(200,200))
pygame.display.update()
done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
#### Update the the display and wait ####

pygame.quit()

