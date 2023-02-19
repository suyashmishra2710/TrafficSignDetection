import pygame
import sys

vel = 5
collisionCheckDist = 100
upDownOffset = 25
leftRightOffset = 80
pygame.init()

screen = pygame.display.set_mode((800,600))

pygame.display.set_caption('captions')
icon = pygame.image.load('images/down/car.png')
pygame.display.set_icon(icon)

playerimg = pygame.image.load('images/up/car.png')
playerimg2 = pygame.image.load('images/up/car.png')
playerx = 370
playery = 480
playerimgrect = playerimg.get_rect(topright = [150,200])
playerimg2rect = playerimg2.get_rect(topright = [150, 200])


def player():
    # this links a particular image to a rectangle so that if a rectangle moves, the image will too
    # there is an easier way to do this with less code using sprites (might look into that if cannot get )
    screen.blit(playerimg, playerimgrect) 
    screen.blit(playerimg2, playerimg2rect) 

#We probably don't need this as cars don't generally drive in reverse on the road.
def checkDown(rect1, rect2):
    for i in range(1, collisionCheckDist):
        if (rect1.y + i == rect2.y and abs(rect1.x - rect2.x) < upDownOffset):
            print("Possible collision back")

def checkUp(rect1, rect2):
    for i in range(1, collisionCheckDist):
        if (rect1.y - i == rect2.y and abs(rect1.x - rect2.x) < upDownOffset):
            print("Possible collision top")

#I'm not sure how changing the heading of the car affects things so I added a left and right check.
def checkRight(rect1, rect2):
    for i in range(1, collisionCheckDist):
        if (rect1.x + i == rect2.x and abs(rect1.y - rect2.y) < leftRightOffset):
            print("Possible collision right")

def checkLeft(rect1, rect2):
    for i in range(1, collisionCheckDist):
        if (rect1.x - i == rect2.x and abs(rect1.y - rect2.y) < leftRightOffset):
            print("Possible collision left")
            
def printCoord(rect):
    print("(" + str(rect.x) + ", " + str(rect.y) + ")")


running = True
while running:

    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            playerimgrect.left += -1
            printCoord(playerimgrect)
            checkLeft(playerimgrect, playerimg2rect)
        if keys[pygame.K_w]:
            playerimgrect.top += -1
            printCoord(playerimgrect)
            checkUp(playerimgrect, playerimg2rect)
        if keys[pygame.K_s]:
            playerimgrect.bottom += 1
            printCoord(playerimgrect)
            checkDown(playerimgrect, playerimg2rect)
        if keys[pygame.K_d]:
            playerimgrect.right += 1
            printCoord(playerimgrect)
            checkRight(playerimgrect, playerimg2rect)
        
        if keys[pygame.K_LEFT]:
            playerimg2rect.right += -1
            printCoord(playerimgrect)
            checkLeft(playerimg2rect, playerimgrect)
        if keys[pygame.K_UP]:
            playerimg2rect.top += -1
            printCoord(playerimg2rect)
            checkUp(playerimg2rect, playerimgrect)
        if keys[pygame.K_DOWN]:
            playerimg2rect.bottom += 1
            printCoord(playerimg2rect)
            checkDown(playerimg2rect, playerimgrect)
        if keys[pygame.K_RIGHT]:
            playerimg2rect.left += 1
            printCoord(playerimg2rect)
            checkRight(playerimg2rect, playerimgrect)
    #playerimgrect.right += 1

    rect1 = playerimg.get_rect() # for collision detection must define this in a variable beforehand (otherwise the rectangle created in the very beginning will be the only one getting used )
    rect2 = playerimg2.get_rect()
    collide = playerimgrect.colliderect(playerimg2rect) # if playerimg.get_rect().colliderect(playerimg2.get_rect() used this won't work)
    if collide:
        #print('collision')
        pygame.draw.rect(screen, (0,255,0), playerimgrect, 4) # how to draw a red outline around one of the rectangles (that image is attached to)
        #sys.exit()
    player()
    pygame.display.update()
