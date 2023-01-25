import pygame
import sys

vel = 5

pygame.init()

screen = pygame.display.set_mode((800,600))

pygame.display.set_caption('captions')
icon = pygame.image.load('images/down/car.png')
pygame.display.set_icon(icon)

playerimg = pygame.image.load('images/down/car.png')
playerimg2 = pygame.image.load('images/up/car.png')
playerx = 370
playery = 480
playerimgrect = playerimg.get_rect(topleft = [150,200])
playerimg2rect = playerimg2.get_rect(topleft = [300, 200])


def player():
    # this links a particular image to a rectangle so that if a rectangle moves, the image will too
    # there is an easier way to do this with less code using sprites (might look into that if cannot get )
    screen.blit(playerimg, playerimgrect) 
    screen.blit(playerimg2, playerimg2rect) 
    

running = True
while running:

    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and playerx > vel:
            playerx += vel
    
    playerimgrect.right += 1
    rect1 = playerimg.get_rect() # for collision detection must define this in a variable beforehand (otherwise the rectangle created in the very beginning will be the only one getting used )
    rect2 = playerimg2.get_rect()
    collide = playerimgrect.colliderect(playerimg2rect) # if playerimg.get_rect().colliderect(playerimg2.get_rect() used this won't work)
    if collide:
        print('collision')
        pygame.draw.rect(screen, (255,0,0), playerimgrect, 4) # how to draw a red outline around one of the rectangles (that image is attached to)
        sys.exit()
    player()
    pygame.display.update()